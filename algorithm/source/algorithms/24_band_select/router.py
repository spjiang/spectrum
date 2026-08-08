"""HTTP 路由：波段/特征选择。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
