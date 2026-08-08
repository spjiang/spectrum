"""HTTP 路由：光谱匹配分类(SAM)。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
