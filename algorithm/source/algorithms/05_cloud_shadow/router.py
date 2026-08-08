"""HTTP 路由：云/云影检测。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
