"""L3 AI 参谋 HTTP 接口。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from common.l3_aide.knowledge import get_algorithm, list_algorithm_groups
from common.l3_aide.layers import get_layer, list_layers
from common.l3_aide.llm_client import client_from_config
from common.l3_aide.orchestrator import UnknownScenarioError
from common.l3_aide.service import interpret_from_stats, run_aide, run_layer, run_one_algorithm

router = APIRouter(prefix="/api/v1/l3-aide", tags=["L3 AI 参谋"])


@router.get("/health")
def aide_health() -> dict[str, str]:
    """参谋路由存活。"""
    return {"status": "ok", "scenarioId": "index_output_review"}


def _llm_meta(config: dict[str, Any] | None, llm: dict[str, Any]) -> dict[str, Any]:
    """回传模型标识，不回传密钥。"""
    cfg = config or {}
    llm["model"] = str(cfg.get("model") or "") or None
    llm["baseUrl"] = str(cfg.get("baseUrl") or cfg.get("base_url") or "") or None
    return llm


@router.post("/run")
async def aide_run(body: dict[str, Any]) -> Any:
    """运行已登记的输出对照演示。未知场景返回 400。"""
    scenario_id = body.get("scenarioId")
    if not scenario_id or not isinstance(scenario_id, str):
        return JSONResponse({"success": False, "message": "缺少 scenarioId"}, status_code=400)
    llm_cfg = body.get("llm") if isinstance(body.get("llm"), dict) else None
    try:
        out = await run_aide(scenario_id, llm_client=client_from_config(llm_cfg))
        out["llm"] = _llm_meta(llm_cfg, out.get("llm") or {})
        return out
    except UnknownScenarioError:
        return JSONResponse({"success": False, "message": "未知场景"}, status_code=400)
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=200)


@router.get("/layers")
def aide_layers() -> dict[str, Any]:
    """处理层案例目录。"""
    return {"layers": list_layers()}


@router.get("/layers/{layer_id}")
def aide_layer_detail(layer_id: str) -> Any:
    """一层案例：问题、传统做法、AI 赋能模板。"""
    doc = get_layer(layer_id)
    if doc is None:
        return JSONResponse({"success": False, "message": "未知处理层"}, status_code=404)
    return doc


@router.post("/layers/{layer_id}/run")
async def aide_layer_run(layer_id: str, body: dict[str, Any] = Body(default={})) -> Any:
    """跑本层代表算法或 L3 编排，再用大模型对照传统做法。"""
    if get_layer(layer_id) is None:
        return JSONResponse({"success": False, "message": "未知处理层"}, status_code=404)
    llm_cfg = body.get("llm") if isinstance(body.get("llm"), dict) else None
    try:
        out = await run_layer(layer_id, llm_client=client_from_config(llm_cfg))
        out["llm"] = _llm_meta(llm_cfg, out.get("llm") or {})
        return out
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=200)


@router.get("/algorithms")
def aide_algorithms() -> dict[str, Any]:
    """L3 目录三组。"""
    return {"groups": list_algorithm_groups()}


@router.get("/algorithms/{algorithm_id}")
def aide_algorithm_detail(algorithm_id: str) -> Any:
    """单算法三栏知识。"""
    doc = get_algorithm(algorithm_id)
    if doc is None:
        return JSONResponse({"success": False, "message": "未知算法"}, status_code=404)
    return doc


@router.post("/algorithms/{algorithm_id}/run")
async def aide_algorithm_run(algorithm_id: str, body: dict[str, Any] = Body(default={})) -> Any:
    """用 testdata 跑单个 L3 算法；可选带本次大模型配置。"""
    if get_algorithm(algorithm_id) is None:
        return JSONResponse({"success": False, "message": "未知算法"}, status_code=404)
    llm_cfg = body.get("llm") if isinstance(body.get("llm"), dict) else None
    try:
        out = await run_one_algorithm(algorithm_id, llm_client=client_from_config(llm_cfg))
        out["llm"] = _llm_meta(llm_cfg, out.get("llm") or {})
        return out
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=200)


def _parse_stats(raw: Any) -> dict[str, float] | None:
    """从接口返回里抽出 min/max/mean。"""
    if not isinstance(raw, dict):
        return None
    if any(key not in raw for key in ("min", "max", "mean")):
        return None
    return {"min": float(raw["min"]), "max": float(raw["max"]), "mean": float(raw["mean"])}


@router.post("/algorithms/{algorithm_id}/interpret")
async def aide_algorithm_interpret(algorithm_id: str, body: dict[str, Any] = Body(default={})) -> Any:
    """先由调用方跑完算法，再把返回统计交给大模型。"""
    if get_algorithm(algorithm_id) is None:
        return JSONResponse({"success": False, "message": "未知算法"}, status_code=404)
    data = body.get("data") if isinstance(body.get("data"), dict) else None
    stats = _parse_stats(body.get("stats") or data)
    files = body.get("files")
    llm_cfg = body.get("llm") if isinstance(body.get("llm"), dict) else None
    prompt = body.get("prompt") if isinstance(body.get("prompt"), dict) else None
    prompt_override = None
    if prompt:
        prompt_override = {
            "system": str(prompt.get("system") or ""),
            "user": str(prompt.get("user") or ""),
        }
    try:
        out = interpret_from_stats(
            algorithm_id,
            stats,
            llm_client=client_from_config(llm_cfg),
            data=data,
            files=files,
            prompt_override=prompt_override,
        )
        out["llm"] = _llm_meta(llm_cfg, out.get("llm") or {})
        return out
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=200)
