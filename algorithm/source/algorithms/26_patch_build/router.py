"""HTTP 路由：Patch/样本构建。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
