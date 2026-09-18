from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.bootstrap import bootstrap, health_payload
from app.config import get_settings
from app.db import SessionLocal, engine
from app.db import Base
from app.routers import auth, docs, jobs, profiles
from app.schemas import HealthOut
from app.services.progress_ws import start_consumers, websocket_job


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # ensure tables exist even if init SQL already ran
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        bootstrap(db, settings)
    finally:
        db.close()
    loop = asyncio.get_running_loop()
    try:
        start_consumers(loop)
    except Exception:  # noqa: BLE001
        pass
    yield


app = FastAPI(title="ms_mosaic visual_server", version="1.0.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(jobs.router)
app.include_router(docs.router)


@app.get("/api/health", response_model=HealthOut)
def health() -> HealthOut:
    db = SessionLocal()
    try:
        return HealthOut(**health_payload(db, get_settings()))
    finally:
        db.close()


@app.websocket("/ws/jobs/{job_id}")
async def ws_jobs(websocket: WebSocket, job_id: str) -> None:
    await websocket_job(websocket, job_id)
