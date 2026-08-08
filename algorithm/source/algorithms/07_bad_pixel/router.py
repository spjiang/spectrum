"""HTTP 路由：坏线/坏像元修复。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
