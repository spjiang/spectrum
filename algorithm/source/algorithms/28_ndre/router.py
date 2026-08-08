"""HTTP 路由：NDRE红边植被指数。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
