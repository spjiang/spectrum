"""HTTP 路由：地块汇总与专题统计。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
