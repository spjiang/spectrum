"""HTTP 路由：架次质检（丢帧/过曝）。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
