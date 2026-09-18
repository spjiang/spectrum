from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import JobRun, ParamProfile, ParamProfileValue
from app.seed_params import RGB_PREVIEW_VALUES, PARAM_SEED
from app.services.mq import MQPublisher
from app.services.paths import validate_paths

STAGES = ["S0_io", "S1_catalog", "S2_at", "S3_dense", "S4_dsm", "S5_ortho", "S6_report"]
ACTIVE = {"queued", "running", "paused"}
TERMINAL = {"succeeded", "failed", "cancelled"}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _defaults() -> dict[str, Any]:
    return {row[0]: row[3] for row in PARAM_SEED}


def resolve_paths(params: dict[str, Any], input_dir: str, output_dir: str) -> dict[str, str]:
    out = Path(output_dir).expanduser().resolve()
    inp = Path(input_dir).expanduser().resolve()
    products = out / str(params.get("products_dir_name") or "拼图结果")
    return {
        "input_dir": str(inp),
        "output_dir": str(out),
        "cache_dir": str(Path(params["cache_dir"]).expanduser().resolve())
        if params.get("cache_dir")
        else str(out / "cache" / "features"),
        "log_dir": str(Path(params["log_dir"]).expanduser().resolve())
        if params.get("log_dir")
        else str(out / "log"),
        "process_dir": str(Path(params["process_dir"]).expanduser().resolve())
        if params.get("process_dir")
        else str(out / "附件"),
        "products_dir": str(products),
        "report_pdf_path": str(products / "质量报告.pdf"),
    }

def build_snapshot(db: Session, profile_id: int | None, overrides: dict[str, Any]) -> tuple[dict[str, Any], int | None, int | None]:
    snap = _defaults()
    profile_version = None
    if profile_id is not None:
        profile = db.get(ParamProfile, profile_id)
        if profile is None:
            raise HTTPException(404, "配置模板不存在")
        profile_version = profile.version
        rows = db.scalars(select(ParamProfileValue).where(ParamProfileValue.profile_id == profile_id)).all()
        for row in rows:
            snap[row.param_key] = row.value
        if profile.preset == "rgb_preview":
            snap.update(RGB_PREVIEW_VALUES)
    if overrides.get("preset") == "rgb_preview":
        snap.update(RGB_PREVIEW_VALUES)
    snap.update({k: v for k, v in overrides.items() if v is not None})
    return snap, profile_id, profile_version


def assert_single_running(db: Session) -> None:
    running = db.scalar(select(JobRun).where(JobRun.status == "running"))
    if running is not None:
        raise HTTPException(409, f"已有任务运行中: {running.id}")


def create_job(
    db: Session,
    *,
    settings: Settings,
    mq: MQPublisher,
    user_id: int | None,
    profile_id: int | None,
    params: dict[str, Any],
    input_dir: str,
    output_dir: str,
) -> JobRun:
    validate_paths(settings, input_dir, output_dir)
    snap, pid, pver = build_snapshot(db, profile_id, params)
    snap["input_dir"] = input_dir
    snap["output_dir"] = output_dir
    paths = resolve_paths(snap, input_dir, output_dir)
    for k, v in paths.items():
        snap[k] = v

    run_mode = snap.get("run_mode") or "full"
    if run_mode == "until_stage" and not snap.get("stop_after_stage"):
        raise HTTPException(400, "until_stage 模式必须设置 stop_after_stage")

    queued = db.scalar(select(JobRun).where(JobRun.status == "queued"))
    # allow queue; only block second running
    job = JobRun(
        id=uuid.uuid4(),
        created_by=user_id,
        profile_id=pid,
        profile_version=pver,
        status="queued",
        params_snapshot=snap,
        input_dir=paths["input_dir"],
        output_dir=paths["output_dir"],
        cache_dir=paths["cache_dir"],
        log_dir=paths["log_dir"],
        process_dir=paths["process_dir"],
        products_dir=paths["products_dir"],
        report_pdf_path=paths["report_pdf_path"],
        message="已入队",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # If nothing running, mark running and publish; else stay queued
    try:
        assert_single_running(db)
        job.status = "running"
        job.started_at = _utcnow()
        job.updated_at = _utcnow()
        job.run_attempt = 1
        db.commit()
        mq.publish_job(
            {
                "schema_version": 1,
                "job_id": str(job.id),
                "run_attempt": job.run_attempt,
                "params_snapshot": snap,
                "action": "start",
            }
        )
    except HTTPException:
        db.rollback()
        db.refresh(job)
        # keep queued; worker or dispatcher will pick later — also publish for worker pull of queued
        mq.publish_job(
            {
                "schema_version": 1,
                "job_id": str(job.id),
                "run_attempt": job.run_attempt,
                "params_snapshot": snap,
                "action": "start",
            }
        )
        job = db.get(JobRun, job.id)
    db.refresh(job)
    return job


def control_job(db: Session, mq: MQPublisher, job_id: uuid.UUID, action: str, stop_after: str | None = None) -> JobRun:
    job = db.get(JobRun, job_id)
    if job is None:
        raise HTTPException(404, "任务不存在")
    action = action.lower()
    if action == "pause":
        if job.status != "running":
            raise HTTPException(400, "仅 running 可暂停")
        mq.publish_control({"schema_version": 1, "job_id": str(job.id), "action": "pause"})
        job.message = "暂停请求已发送（将在阶段边界生效）"
    elif action == "resume":
        if job.status != "paused":
            raise HTTPException(400, "仅 paused 可恢复")
        assert_single_running(db)
        job.status = "running"
        job.run_attempt += 1
        mq.publish_job(
            {
                "schema_version": 1,
                "job_id": str(job.id),
                "run_attempt": job.run_attempt,
                "params_snapshot": job.params_snapshot,
                "action": "resume",
            }
        )
        mq.publish_control({"schema_version": 1, "job_id": str(job.id), "action": "resume"})
    elif action == "cancel":
        if job.status in TERMINAL:
            raise HTTPException(400, "任务已结束")
        mq.publish_control({"schema_version": 1, "job_id": str(job.id), "action": "cancel"})
        job.status = "cancelled"
        job.finished_at = _utcnow()
        job.message = "已取消"
    elif action == "continue":
        if job.status != "awaiting_continue":
            raise HTTPException(400, "仅 awaiting_continue 可继续下一阶段")
        snap = dict(job.params_snapshot)
        if stop_after:
            snap["stop_after_stage"] = stop_after
            snap["run_mode"] = "until_stage"
        else:
            # advance one stage in step mode or clear stop to go full remaining
            completed = job.completed_stage or snap.get("start_stage") or "S0_io"
            if completed not in STAGES:
                raise HTTPException(400, f"未知 completed_stage: {completed}")
            idx = STAGES.index(completed)
            if idx >= len(STAGES) - 1:
                job.status = "succeeded"
                job.finished_at = _utcnow()
                job.message = "已达最后阶段"
                job.updated_at = _utcnow()
                db.commit()
                db.refresh(job)
                return job
            next_stage = STAGES[idx + 1]
            snap["start_stage"] = next_stage
            if snap.get("run_mode") == "step":
                snap["stop_after_stage"] = next_stage
                snap["run_mode"] = "until_stage"
            elif snap.get("run_mode") == "until_stage":
                # user continues beyond previous stop → run one more stage then wait again unless stop_after passed
                snap["stop_after_stage"] = next_stage
            else:
                snap["run_mode"] = "full"
                snap["stop_after_stage"] = None
        job.params_snapshot = snap
        assert_single_running(db)
        job.status = "running"
        job.run_attempt += 1
        job.started_at = job.started_at or _utcnow()
        job.finished_at = None
        mq.publish_job(
            {
                "schema_version": 1,
                "job_id": str(job.id),
                "run_attempt": job.run_attempt,
                "params_snapshot": snap,
                "action": "continue",
            }
        )
        job.message = "继续执行已下发"
    else:
        raise HTTPException(400, f"未知动作 {action}")
    job.updated_at = _utcnow()
    db.commit()
    db.refresh(job)
    return job


def apply_progress(db: Session, payload: dict[str, Any]) -> JobRun | None:
    job_id = payload.get("job_id")
    if not job_id:
        return None
    job = db.get(JobRun, uuid.UUID(str(job_id)))
    if job is None:
        return None
    job.current_stage = payload.get("stage_id") or job.current_stage
    if "stage_progress" in payload:
        job.stage_progress = float(payload["stage_progress"])
    if "global_percent" in payload:
        job.global_percent = float(payload["global_percent"])
    if "message" in payload:
        job.message = str(payload["message"])
    if "eta_seconds" in payload:
        job.eta_seconds = payload["eta_seconds"]
    job.updated_at = _utcnow()
    db.commit()
    db.refresh(job)
    return job


def apply_event(db: Session, payload: dict[str, Any]) -> JobRun | None:
    job_id = payload.get("job_id")
    if not job_id:
        return None
    job = db.get(JobRun, uuid.UUID(str(job_id)))
    if job is None:
        return None
    event = payload.get("event")
    stage = payload.get("stage_id")
    if event == "stage_done" and stage:
        job.completed_stage = stage
        timings = dict(job.stage_timings or {})
        if "elapsed_s" in payload:
            timings[stage] = payload["elapsed_s"]
        job.stage_timings = timings
    if event == "awaiting_continue":
        job.status = "awaiting_continue"
        job.message = payload.get("message") or "阶段完成，等待继续"
    elif event == "succeeded":
        job.status = "succeeded"
        job.global_percent = 100.0
        job.finished_at = _utcnow()
        job.message = payload.get("message") or "完成"
    elif event == "failed":
        job.status = "failed"
        job.error_summary = payload.get("error") or payload.get("message")
        job.finished_at = _utcnow()
    elif event == "cancelled":
        job.status = "cancelled"
        job.finished_at = _utcnow()
    elif event == "paused":
        job.status = "paused"
    elif event == "running":
        job.status = "running"
        job.started_at = job.started_at or _utcnow()
    if "n_shots" in payload:
        job.n_shots = payload["n_shots"]
    job.updated_at = _utcnow()
    db.commit()
    db.refresh(job)
    return job
