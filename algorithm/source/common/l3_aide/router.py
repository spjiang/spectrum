"""L3 AI 参谋 HTTP 接口。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from common.l3_aide.orchestrator import UnknownScenarioError
from common.l3_aide.service import run_aide

router = APIRouter(prefix="/api/v1/l3-aide", tags=["L3 AI 参谋"])


@router.get("/health")
def aide_health() -> dict[str, str]:
    """参谋路由存活。"""
    return {"status": "ok", "scenarioId": "rice_dense_max_n"}


@router.post("/run")
async def aide_run(body: dict[str, Any]) -> Any:
    """一键跑默认长势链。未知场景返回 400。"""
    scenario_id = body.get("scenarioId")
    if not scenario_id or not isinstance(scenario_id, str):
        return JSONResponse({"success": False, "message": "缺少 scenarioId"}, status_code=400)
    try:
        return await run_aide(scenario_id)
    except UnknownScenarioError:
        return JSONResponse({"success": False, "message": "未知场景"}, status_code=400)
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=200)
