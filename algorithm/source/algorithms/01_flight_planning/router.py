"""HTTP 路由：航线规划与覆盖优化。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
