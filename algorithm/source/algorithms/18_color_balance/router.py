"""HTTP 路由：Wallis局部匀色。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
