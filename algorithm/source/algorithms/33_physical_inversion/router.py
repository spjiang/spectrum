"""HTTP 路由：辐射传输物理反演。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
