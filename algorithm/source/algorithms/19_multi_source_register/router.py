"""HTTP 路由：多源配准 HSI-RGB-矢量。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
