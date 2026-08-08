"""HTTP 路由：BRDF/观测几何校正。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
