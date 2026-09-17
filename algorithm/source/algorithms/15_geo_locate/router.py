"""HTTP 路由：POS中心点与GSD粗定位。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
