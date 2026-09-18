from __future__ import annotations

"""宿主机 RabbitMQ worker：消费任务 → run_stages → 回传进度/事件。"""

import json
import logging
import threading
from pathlib import Path
from typing import Any

from ms_mosaic.control import ControlState
from ms_mosaic.progress import ProgressReporter
from ms_mosaic.stage_runner import run_stages

log = logging.getLogger("ms_mosaic.worker")

QUEUE_JOBS = "mosaic.jobs"
QUEUE_CONTROL = "mosaic.control"
QUEUE_PROGRESS = "mosaic.progress"
QUEUE_EVENTS = "mosaic.events"


class MqReporter:
    def __init__(self, channel, job_id: str) -> None:
        self.ch = channel
        self.job_id = job_id

    def _pub(self, queue: str, payload: dict[str, Any]) -> None:
        body = json.dumps({"schema_version": 1, "job_id": self.job_id, **payload}, ensure_ascii=False).encode()
        self.ch.basic_publish(exchange="", routing_key=queue, body=body)

    def stage_start(self, stage_id: str, message: str = "") -> None:
        self._pub(QUEUE_PROGRESS, {"stage_id": stage_id, "stage_progress": 0, "global_percent": 0, "message": message})
        self._pub(QUEUE_EVENTS, {"event": "running", "stage_id": stage_id})

    def progress(self, stage_id: str, stage_progress: float, global_percent: float, message: str = "", eta_seconds: int | None = None) -> None:
        self._pub(
            QUEUE_PROGRESS,
            {
                "stage_id": stage_id,
                "stage_progress": stage_progress,
                "global_percent": global_percent,
                "message": message,
                "eta_seconds": eta_seconds,
            },
        )

    def stage_done(self, stage_id: str, elapsed_s: float = 0.0) -> None:
        self._pub(QUEUE_EVENTS, {"event": "stage_done", "stage_id": stage_id, "elapsed_s": elapsed_s})

    def event(self, event: str, **payload: Any) -> None:
        self._pub(QUEUE_EVENTS, {"event": event, **payload})


def _control_listener(channel, job_id: str, control: ControlState, stop: threading.Event) -> None:
    def _cb(ch, method, _props, body):
        try:
            msg = json.loads(body.decode("utf-8"))
            if str(msg.get("job_id")) != job_id:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            action = msg.get("action")
            if action == "pause":
                control.request_pause()
            elif action == "resume":
                control.clear_pause()
            elif action == "cancel":
                control.request_cancel()
                stop.set()
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_CONTROL, on_message_callback=_cb)
    while not stop.is_set():
        channel.connection.process_data_events(time_limit=1)


def handle_job(channel, payload: dict[str, Any]) -> None:
    job_id = str(payload["job_id"])
    params = dict(payload.get("params_snapshot") or {})
    out = Path(params["output_dir"])
    ctrl_path = out / "log" / "control.json"
    control = ControlState(path=ctrl_path)
    reporter: ProgressReporter = MqReporter(channel, job_id)
    stop = threading.Event()
    t = threading.Thread(target=_control_listener, args=(channel, job_id, control, stop), daemon=True)
    t.start()
    try:
        result = run_stages(Path(params["input_dir"]), out, params=params, reporter=reporter, control=control)
        status = result.get("status", "succeeded")
        if status == "awaiting_continue":
            reporter.event("awaiting_continue", stage_id=result.get("completed_stage"), message=result.get("message"))
        elif status == "failed":
            reporter.event("failed", error=result.get("error"))
        elif status == "cancelled":
            reporter.event("cancelled")
        else:
            reporter.event("succeeded", n_shots=result.get("n_shots"))
    except Exception as exc:  # noqa: BLE001
        log.exception("job failed")
        reporter.event("failed", error=str(exc))
    finally:
        stop.set()


def main() -> int:
    import os

    import pika

    logging.basicConfig(level=logging.INFO)
    url = os.environ.get("RABBITMQ_URL", "amqp://mosaic:mosaic_secret@127.0.0.1:5672/")
    conn = pika.BlockingConnection(pika.URLParameters(url))
    ch = conn.channel()
    for q in (QUEUE_JOBS, QUEUE_CONTROL, QUEUE_PROGRESS, QUEUE_EVENTS):
        ch.queue_declare(queue=q, durable=True)
    ch.basic_qos(prefetch_count=1)

    def _on_job(ch_, method, _props, body):
        try:
            payload = json.loads(body.decode("utf-8"))
            handle_job(ch_, payload)
        finally:
            ch_.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=QUEUE_JOBS, on_message_callback=_on_job)
    log.info("worker listening on %s", QUEUE_JOBS)
    ch.start_consuming()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
