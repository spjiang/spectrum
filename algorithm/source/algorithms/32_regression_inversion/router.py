"""HTTP 路由：经验回归反演。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
