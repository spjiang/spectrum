from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_roles
from app.config import Settings, get_settings
from app.db import get_db
from app.models import JobRun, User
from app.schemas import JobContinue, JobCreate, JobOut
from app.services import jobs as jobsvc
from app.services.deps import get_mq
from app.services.mq import MQPublisher

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobOut)
def create_job(
    body: JobCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    mq: MQPublisher = Depends(get_mq),
    user: User = Depends(require_roles("executor", "admin")),
) -> JobRun:
    return jobsvc.create_job(
        db,
        settings=settings,
        mq=mq,
        user_id=user.id,
        profile_id=body.profile_id,
        params=body.params,
        input_dir=body.input_dir,
        output_dir=body.output_dir,
    )


@router.get("", response_model=list[JobOut])
def list_jobs(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("executor", "viewer", "admin", "configurator")),
) -> list[JobRun]:
    return list(db.scalars(select(JobRun).order_by(JobRun.created_at.desc()).limit(200)))


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("executor", "viewer", "admin", "configurator")),
) -> JobRun:
    job = db.get(JobRun, job_id)
    if job is None:
        raise HTTPException(404, "任务不存在")
    return job


@router.post("/{job_id}/{action}", response_model=JobOut)
def job_action(
    job_id: uuid.UUID,
    action: str,
    body: JobContinue | None = None,
    db: Session = Depends(get_db),
    mq: MQPublisher = Depends(get_mq),
    _: User = Depends(require_roles("executor", "admin")),
) -> JobRun:
    stop = body.stop_after_stage if body else None
    return jobsvc.control_job(db, mq, job_id, action, stop_after=stop)


@router.get("/{job_id}/logs")
def job_logs(
    job_id: uuid.UUID,
    tail: int = 200,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("executor", "viewer", "admin", "configurator")),
) -> PlainTextResponse:
    job = db.get(JobRun, job_id)
    if job is None:
        raise HTTPException(404, "任务不存在")
    log_dir = Path(job.log_dir or "")
    candidates = sorted(log_dir.glob("*.log")) if log_dir.is_dir() else []
    if not candidates:
        run_log = Path(job.output_dir) / "log" / "run.log"
        text = run_log.read_text(encoding="utf-8", errors="replace") if run_log.is_file() else "(暂无日志文件)"
    else:
        text = candidates[-1].read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return PlainTextResponse("\n".join(lines[-tail:]))


@router.get("/{job_id}/report.pdf")
def job_report(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("executor", "viewer", "admin", "configurator")),
) -> FileResponse:
    job = db.get(JobRun, job_id)
    if job is None:
        raise HTTPException(404, "任务不存在")
    path = Path(job.report_pdf_path or "")
    if not path.is_file():
        raise HTTPException(404, "质量报告尚未生成")
    return FileResponse(path, filename="质量报告.pdf", media_type="application/pdf")
