"""HTTP 路由：红边位置与光谱特征参数。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
