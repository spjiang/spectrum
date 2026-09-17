"""HTTP 路由：NDSI归一化差值雪指数。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
