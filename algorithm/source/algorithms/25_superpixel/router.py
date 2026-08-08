"""HTTP 路由：超像素/对象分割。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
