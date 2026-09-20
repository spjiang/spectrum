import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.jobs import apply_event, apply_progress, stage_rank


def _job(**kwargs):
    base = dict(
        id=uuid.uuid4(),
        status="running",
        current_stage="S2_at",
        completed_stage="S2_at",
        global_percent=43.0,
        stage_progress=100.0,
        message="",
        eta_seconds=None,
        stage_timings={},
        n_shots=None,
        started_at=None,
        finished_at=None,
        updated_at=None,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def _db(job):
    db = MagicMock()
    db.get.return_value = job
    return db


def test_stage_rank_order():
    assert stage_rank("S2_at") < stage_rank("S4_dsm")
    assert stage_rank(None) == -1


def test_progress_does_not_rewind_current_stage():
    job = _job(current_stage="S4_dsm", completed_stage="S4_dsm", global_percent=71.0)
    apply_progress(_db(job), {"job_id": str(job.id), "stage_id": "S2_at", "stage_progress": 80, "global_percent": 40})
    assert job.current_stage == "S4_dsm"
    assert job.global_percent == 71.0


def test_stage_done_advances_current_if_behind():
    job = _job(current_stage="S2_at", completed_stage="S2_at")
    apply_event(_db(job), {"job_id": str(job.id), "event": "stage_done", "stage_id": "S4_dsm"})
    assert job.completed_stage == "S4_dsm"
    assert job.current_stage == "S4_dsm"
