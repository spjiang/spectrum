"""HTTP 路由：EVI/SAVI/MSAVI。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
