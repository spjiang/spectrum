"""HTTP 路由：白板/灰板经验线法反射率定标。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
