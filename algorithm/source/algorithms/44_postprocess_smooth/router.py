"""HTTP 路由：分类后处理平滑/小斑剔除。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
