from pathlib import Path
from unittest.mock import MagicMock

from ms_mosaic.worker_main import _claim_job, _release_job, _run_payload, delivery_action, handle_job


def test_delivery_action_ignores_redelivery_of_running_job():
    assert delivery_action("job-1", True, "job-1") == "ignore"
    assert delivery_action("job-1", True, "job-2") == "busy"
    assert delivery_action(None, False, "job-1") == "run"
    assert delivery_action("job-1", False, "job-1") == "run"


def test_claim_job_blocks_second_job():
    assert _claim_job("job-1") == "run"
    try:
        assert _claim_job("job-1") == "ignore"
        assert _claim_job("job-2") == "busy"
    finally:
        _release_job("job-1")
    assert _claim_job("job-2") == "run"
    _release_job("job-2")


def test_run_payload_uses_worker_pid_not_wrapper(tmp_path: Path, monkeypatch):
    import os

    from ms_mosaic import worker_status
    from ms_mosaic.worker_main import _job_running

    inp = tmp_path / "in"
    out = tmp_path / "out"
    inp.mkdir()
    seen: dict = {}

    def fake_handle(channel, payload, *, rabbitmq_url, connect=None):
        snap = worker_status.snapshot()
        seen["job"] = dict(snap["current_job"] or {})
        seen["running"] = _job_running()
        seen["channel"] = channel

    monkeypatch.setattr("ms_mosaic.worker_main.handle_job", fake_handle)
    monkeypatch.setattr("ms_mosaic.worker_main.terminate_job_workers", lambda _pid: [])
    _run_payload(
        "amqp://mosaic:mosaic_secret@127.0.0.1:5672/",
        {
            "job_id": "job-live",
            "params_snapshot": {"input_dir": str(inp), "output_dir": str(out)},
        },
    )
    assert seen["channel"] is None
    assert seen["running"] is True
    assert seen["job"]["job_id"] == "job-live"
    assert seen["job"]["pid"] == os.getpid()
    assert not seen["job"].get("orphan_compute")
    assert _job_running() is False
    assert worker_status.snapshot().get("current_job") is None


def test_handle_job_runs_stages_and_reports_success(tmp_path: Path, monkeypatch):
    inp = tmp_path / "in"
    out = tmp_path / "out"
    inp.mkdir()
    seen: list[tuple] = []

    def fake_run_stages(input_dir, output_dir, params=None, reporter=None, control=None):
        seen.append((input_dir, output_dir, params))
        reporter.event("succeeded", n_shots=2)
        return {"status": "succeeded", "n_shots": 2}

    monkeypatch.setattr("ms_mosaic.worker_main.run_stages", fake_run_stages)
    channel = MagicMock()
    ctrl_conn = MagicMock()
    handle_job(
        channel,
        {
            "job_id": "job-1",
            "params_snapshot": {"input_dir": str(inp), "output_dir": str(out), "bands": ["Color"]},
        },
        rabbitmq_url="amqp://mosaic:mosaic_secret@127.0.0.1:5672/",
        connect=lambda _url: ctrl_conn,
    )
    assert seen[0][0] == inp
    assert seen[0][1] == out
    assert seen[0][2]["bands"] == ["Color"]
    published = b"".join(call.kwargs.get("body") or b"" for call in channel.basic_publish.call_args_list)
    assert b"succeeded" in published
