"""HTTP 路由：辐射定标 DN→辐亮度。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
