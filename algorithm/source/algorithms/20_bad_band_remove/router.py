"""HTTP 路由：坏波段剔除。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
