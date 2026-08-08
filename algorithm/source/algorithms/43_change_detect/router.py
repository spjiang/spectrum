"""HTTP 路由：多时相变化检测。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
