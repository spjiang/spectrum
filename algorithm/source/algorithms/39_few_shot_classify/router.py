"""HTTP 路由：SAM均值原型少样本分类。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
