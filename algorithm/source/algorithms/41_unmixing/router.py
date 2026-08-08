"""HTTP 路由：混合像元分解。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
