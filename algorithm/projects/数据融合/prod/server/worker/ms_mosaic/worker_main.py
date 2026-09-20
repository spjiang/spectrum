from __future__ import annotations

"""RabbitMQ worker：任务在本进程跑，没有独立包装进程。

计算进程池是 Worker 的子进程。队列通道断开、ack 超时都不能把计算父进程带走，
进度才能一直往前走。可视化 kill 只杀 spawn 计算池，不杀 Worker。
"""

import json
import logging
import os
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable

from ms_mosaic.control import ControlState
from ms_mosaic.job_proc import terminate_job_workers
from ms_mosaic.log_io import stamp_print_line
from ms_mosaic.mq_pub import MqReporter, QUEUES, amqp_params
from ms_mosaic.stage_runner import run_stages
from ms_mosaic import worker_status

log = logging.getLogger("ms_mosaic.worker")

QUEUE_JOBS = "mosaic.jobs"
QUEUE_CONTROL = "mosaic.control"
QUEUE_PROGRESS = "mosaic.progress"
QUEUE_EVENTS = "mosaic.events"

_job_lock = threading.Lock()
_job_id: str | None = None
_job_active = False
_incoming: queue.Queue[dict[str, Any]] = queue.Queue()


class _JobLogTee:
    """把 print / logging 同步写到任务 run.log，供可视化实时拉取。"""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._fp = path.open("a", encoding="utf-8")
        self._handler = logging.FileHandler(path, encoding="utf-8")
        self._handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logging.getLogger().addHandler(self._handler)
        self._stdout = sys.stdout
        self._buf = ""
        sys.stdout = self  # type: ignore[assignment]

    def write(self, s: str) -> int:
        self._stdout.write(s)
        self._buf += s
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._fp.write(stamp_print_line(line + "\n"))
        self._fp.flush()
        return len(s)

    def flush(self) -> None:
        self._stdout.flush()
        if self._buf:
            self._fp.write(stamp_print_line(self._buf))
            self._buf = ""
        self._fp.flush()

    def close(self) -> None:
        self.flush()
        sys.stdout = self._stdout
        logging.getLogger().removeHandler(self._handler)
        self._handler.close()
        self._fp.close()


def handle_job(
    channel,
    payload: dict[str, Any],
    *,
    rabbitmq_url: str,
    connect: Callable[[str], Any] | None = None,
) -> None:
    job_id = str(payload["job_id"])
    params = dict(payload.get("params_snapshot") or {})
    out = Path(params["output_dir"])
    ctrl_path = out / "log" / "control.json"
    control = ControlState(path=ctrl_path)
    reporter = MqReporter(channel, job_id, rabbitmq_url=rabbitmq_url, connect=connect)
    job_log = _JobLogTee(out / "log" / "run.log")
    log.info("job %s start input=%s out=%s", job_id, params.get("input_dir"), out)
    try:
        if control.checkpoint_barrier() == "cancel":
            reporter.event("cancelled")
            return
        result = run_stages(Path(params["input_dir"]), out, params=params, reporter=reporter, control=control)
        status = result.get("status", "succeeded")
        if status == "awaiting_continue":
            reporter.event("awaiting_continue", stage_id=result.get("completed_stage"), message=result.get("message"))
        elif status == "failed":
            reporter.event("failed", error=result.get("error"))
        elif status == "cancelled":
            reporter.event("cancelled")
        elif status == "paused":
            reporter.event("paused", stage_id=result.get("completed_stage"), message=result.get("message") or "已暂停，可继续运行")
        else:
            reporter.event("succeeded", n_shots=result.get("n_shots"))
    except Exception as exc:  # noqa: BLE001
        log.exception("job failed")
        reporter.event("failed", error=str(exc))
    finally:
        reporter.close()
        job_log.close()


def _job_running() -> bool:
    with _job_lock:
        return _job_active


def kill_current_job() -> str | None:
    """立刻杀掉当前任务的计算进程池，Worker 本身继续听队列。"""
    with _job_lock:
        jid = _job_id
    log.info("killing job %s compute workers", jid)
    leftover = terminate_job_workers(os.getpid())
    if leftover:
        log.info("compute still alive after kill: %s", leftover)
    return jid


def delivery_action(current_id: str | None, current_alive: bool, incoming_id: str) -> str:
    """同一任务重投时忽略；另有任务在跑则退回队列。"""
    if current_alive and current_id:
        if current_id == incoming_id:
            return "ignore"
        return "busy"
    return "run"


def _ack_quiet(channel, method) -> None:
    try:
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:  # noqa: BLE001
        log.exception("ack failed")


def _nack_requeue(channel, method) -> None:
    try:
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except Exception:  # noqa: BLE001
        log.exception("nack failed")


def _control_matches(msg: dict[str, Any], current: str | None) -> bool:
    action = str(msg.get("action") or "").lower()
    if action == "kill_all":
        return True
    if action not in {"cancel", "kill"}:
        return False
    jid = msg.get("job_id")
    if not jid:
        return True
    return current is not None and str(jid) == current


def _control_supervisor(url: str, stop: threading.Event) -> None:
    import pika

    while not stop.is_set():
        try:
            conn = pika.BlockingConnection(amqp_params(url))
            ch = conn.channel()
            ch.queue_declare(queue=QUEUE_CONTROL, durable=True)

            def _cb(ch_, method, _props, body):
                try:
                    msg = json.loads(body.decode("utf-8"))
                    with _job_lock:
                        current = _job_id
                    if _control_matches(msg, current):
                        kill_current_job()
                except Exception:  # noqa: BLE001
                    log.exception("control handler failed")
                finally:
                    ch_.basic_ack(delivery_tag=method.delivery_tag)

            ch.basic_consume(queue=QUEUE_CONTROL, on_message_callback=_cb)
            while not stop.is_set():
                conn.process_data_events(time_limit=1)
            try:
                conn.close()
            except Exception:  # noqa: BLE001
                pass
        except Exception:  # noqa: BLE001
            log.exception("control supervisor reconnecting")
            time.sleep(2)


def _claim_job(job_id: str) -> str:
    global _job_id, _job_active
    with _job_lock:
        action = delivery_action(_job_id, _job_active, job_id)
        if action == "run":
            _job_id = job_id
            _job_active = True
        return action


def _release_job(job_id: str) -> None:
    global _job_id, _job_active
    with _job_lock:
        if _job_id == job_id:
            _job_id = None
            _job_active = False


def _consume_jobs(url: str, stop: threading.Event) -> None:
    """独立连接消费任务。先认领再 ack，通道断开不影响主线程里的计算。"""
    import pika

    while not stop.is_set():
        try:
            conn = pika.BlockingConnection(amqp_params(url))
            ch = conn.channel()
            for q in QUEUES:
                ch.queue_declare(queue=q, durable=True)
            ch.basic_qos(prefetch_count=1)
            worker_status.set_listening(True)

            def _on_job(ch_, method, _props, body):
                payload = json.loads(body.decode("utf-8"))
                job_id = str(payload.get("job_id") or "")
                log.info("job %s", job_id)
                action = _claim_job(job_id)
                if action == "ignore":
                    log.info("ignore redelivery of in-flight job %s", job_id)
                    _ack_quiet(ch_, method)
                    return
                if action == "busy":
                    log.warning("busy with current job, requeue %s", job_id)
                    _nack_requeue(ch_, method)
                    return
                _incoming.put(payload)
                _ack_quiet(ch_, method)

            ch.basic_consume(queue=QUEUE_JOBS, on_message_callback=_on_job)
            log.info("worker listening on %s", QUEUE_JOBS)
            while not stop.is_set():
                conn.process_data_events(time_limit=1)
            try:
                conn.close()
            except Exception:  # noqa: BLE001
                pass
        except Exception:  # noqa: BLE001
            worker_status.set_listening(False)
            log.exception("job consumer reconnecting")
            time.sleep(2)


def _run_payload(url: str, payload: dict[str, Any]) -> None:
    """在 Worker 主线程跑任务。心跳 pid 就是 Worker，进程池挂在本进程下面。"""
    global _job_id, _job_active
    job_id = str(payload.get("job_id") or "")
    with _job_lock:
        _job_id = job_id
        _job_active = True
    worker_status.set_current_job(
        {
            "job_id": job_id,
            "pid": os.getpid(),
            "input_dir": (payload.get("params_snapshot") or {}).get("input_dir"),
            "output_dir": (payload.get("params_snapshot") or {}).get("output_dir"),
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    )
    try:
        handle_job(None, payload, rabbitmq_url=url)
    finally:
        leftover = terminate_job_workers(os.getpid())
        if leftover:
            log.warning("compute leftover after job %s: %s", job_id, leftover)
        _release_job(job_id)
        worker_status.set_current_job(None, remember=False)


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    url = os.environ.get("RABBITMQ_URL", "amqp://mosaic:mosaic_secret@127.0.0.1:5672/")
    leftover = terminate_job_workers(os.getpid())
    if leftover:
        log.warning("startup leftover compute: %s", leftover)
    worker_status.start_heartbeat()
    stop = threading.Event()
    threading.Thread(target=_control_supervisor, args=(url, stop), daemon=True, name="worker-control").start()
    threading.Thread(target=_consume_jobs, args=(url, stop), daemon=True, name="worker-jobs").start()
    worker_status.set_listening(True)
    log.info("worker ready, jobs run in-process")
    try:
        while True:
            try:
                payload = _incoming.get(timeout=1.0)
            except queue.Empty:
                continue
            _run_payload(url, payload)
    except KeyboardInterrupt:
        stop.set()
        worker_status.set_listening(False)
        kill_current_job()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
