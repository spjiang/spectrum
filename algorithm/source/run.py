#!/usr/bin/env python3
"""启动单进程算法服务。"""
from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from common.config import APP_HOST, APP_PORT  # noqa: E402


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=False,
    )
