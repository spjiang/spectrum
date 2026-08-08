"""HTTP 路由：POS解算（GPS+IMU）。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
