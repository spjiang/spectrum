"""HTTP 路由：低NDVI种子ACE目标检测。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
