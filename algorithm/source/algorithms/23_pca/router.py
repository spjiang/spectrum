"""HTTP 路由：PCA/MNF降维。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
