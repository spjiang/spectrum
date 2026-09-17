"""HTTP 路由：RECI红边叶绿素指数。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
