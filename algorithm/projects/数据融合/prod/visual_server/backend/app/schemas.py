from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    roles: list[str]


class LoginForm(BaseModel):
    username: str
    password: str


class ParamDefOut(BaseModel):
    key: str
    stage_id: str
    value_type: str
    default_value: Any
    description: str
    advanced: bool
    sort_order: int

    class Config:
        from_attributes = True


class ProfileCreate(BaseModel):
    name: str
    description: str = ""
    values: dict[str, Any] = Field(default_factory=dict)
    preset: str | None = None


class ProfileUpdate(BaseModel):
    description: str | None = None
    values: dict[str, Any] | None = None
    preset: str | None = None


class ProfileOut(BaseModel):
    id: int
    name: str
    description: str
    version: int
    preset: str | None
    values: dict[str, Any]
    updated_at: datetime

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    profile_id: int | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    input_dir: str
    output_dir: str


class JobContinue(BaseModel):
    stop_after_stage: str | None = None


class JobOut(BaseModel):
    id: UUID
    status: str
    run_attempt: int
    params_snapshot: dict[str, Any]
    input_dir: str
    output_dir: str
    cache_dir: str | None
    log_dir: str | None
    process_dir: str | None
    products_dir: str | None
    report_pdf_path: str | None
    current_stage: str | None
    completed_stage: str | None
    global_percent: float
    stage_progress: float
    message: str
    eta_seconds: int | None
    error_summary: str | None
    stage_timings: dict[str, Any]
    n_shots: int | None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    class Config:
        from_attributes = True


class HealthOut(BaseModel):
    status: str
    postgres: str
    rabbitmq: str
