"""HTTP 路由：HSI-RGB全局平移配准。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
