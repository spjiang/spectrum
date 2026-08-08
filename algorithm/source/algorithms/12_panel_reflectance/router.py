"""HTTP 路由：白板/灰板反射率定标（示意）。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
