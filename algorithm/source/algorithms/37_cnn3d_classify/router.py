"""HTTP 路由：2D/3D-CNN空谱分类。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
