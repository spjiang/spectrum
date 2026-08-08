"""HTTP 路由：光谱微笑/关键畸变校正。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
