"""单进程 FastAPI 应用：挂载全部算法路由与可视化控制台 API。"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.catalog import ALGORITHMS  # noqa: E402
from common.config import APP_HOST, APP_PORT, OUTPUT_DIR  # noqa: E402
from common.console_router import router as console_router  # noqa: E402

app = FastAPI(
    title="高光谱算法服务",
    description=(
        "单服务聚合业界算法清单（45 项）。"
        "每个算法独立目录；统一 POST /api/v1/{algorithm_id}/run ；"
        "可视化控制台 API 位于 /api/v1/console/* 。"
    ),
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _register_algorithms() -> None:
    """按目录动态挂载 algorithms.<id>.router。"""
    for meta in ALGORITHMS:
        algo_id = meta["id"]
        module = importlib.import_module(f"algorithms.{algo_id}.router")
        app.include_router(
            module.router,
            prefix=f"/api/v1/{algo_id}",
            tags=[f"{algo_id} · {meta['title']}"],
        )


_register_algorithms()
app.include_router(console_router)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount(
    "/api/v1/console/outputs",
    StaticFiles(directory=str(OUTPUT_DIR)),
    name="console-outputs",
)


@app.get("/", tags=["system"])
def root():
    """服务入口说明。"""
    return {
        "service": "hyperspectral-algorithm-api",
        "mode": "single-process",
        "docs": "/docs",
        "algorithms": "/api/v1/algorithms",
        "console": "/api/v1/console/algorithms",
        "host": APP_HOST,
        "port": APP_PORT,
    }


@app.get("/health", tags=["system"])
def health():
    """进程健康检查。"""
    return {
        "status": "ok",
        "algorithms": len(ALGORITHMS),
        "implemented": sum(1 for a in ALGORITHMS if a["implemented"]),
    }


@app.get("/api/v1/algorithms", tags=["system"])
def list_algorithms():
    """列出全部算法及实现状态。"""
    return {
        "count": len(ALGORITHMS),
        "implemented_count": sum(1 for a in ALGORITHMS if a["implemented"]),
        "algorithms": [
            {
                "id": a["id"],
                "title": a["title"],
                "level": a["level"],
                "implemented": a["implemented"],
                "run_url": f"/api/v1/{a['id']}/run",
                "health_url": f"/api/v1/{a['id']}/health",
            }
            for a in ALGORITHMS
        ],
    }
