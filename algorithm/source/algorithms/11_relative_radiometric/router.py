"""HTTP 路由：相对辐射归一。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
