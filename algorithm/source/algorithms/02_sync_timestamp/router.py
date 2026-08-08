"""HTTP 路由：同步曝光与时间戳对齐。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
