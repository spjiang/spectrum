"""HTTP 路由：SIPI结构不敏感色素指数。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
