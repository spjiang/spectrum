"""HTTP 路由：POS轨迹平滑与杠杆臂校正。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
