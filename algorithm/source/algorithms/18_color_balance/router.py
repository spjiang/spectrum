"""HTTP 路由：匀色与接缝线优化。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
