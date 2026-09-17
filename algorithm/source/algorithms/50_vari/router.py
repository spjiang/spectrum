"""HTTP 路由：VARI可见大气阻力指数。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
