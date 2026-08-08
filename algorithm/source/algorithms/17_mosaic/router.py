"""HTTP 路由：影像匹配与镶嵌。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
