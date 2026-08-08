"""HTTP 路由：标准化/归一化。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
