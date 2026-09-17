"""HTTP 路由：ARVI耐大气植被指数。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
