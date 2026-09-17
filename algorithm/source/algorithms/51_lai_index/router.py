"""HTTP 路由：叶面积经验指数。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
