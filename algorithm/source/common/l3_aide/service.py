"""组装一次 L3 参谋运行。"""

from __future__ import annotations

from typing import Any

from common.l3_aide.interpreter import interpret_result
from common.l3_aide.narrator import LlmClient, apply_narrative
from common.l3_aide.orchestrator import build_plan, get_scenario
from common.l3_aide.runner import run_algorithm


def _preview_url(raw: dict[str, Any]) -> str | None:
    """从 files_http 取出 PNG 预览。"""
    http = raw.get("files_http") or {}
    png = http.get("preview_png") or {}
    url = png.get("url")
    return str(url) if url else None


def _stats(raw: dict[str, Any]) -> dict[str, float] | None:
    """抽取 min/max/mean；缺一则视为无统计。"""
    data = raw.get("data") or {}
    if any(key not in data for key in ("min", "max", "mean")):
        return None
    return {
        "min": float(data["min"]),
        "max": float(data["max"]),
        "mean": float(data["mean"]),
    }


async def _one_result(item: dict[str, Any], role: str) -> dict[str, Any]:
    """跑单个算法并解释。"""
    raw = await run_algorithm(item["algorithmId"], item["params"])
    ok = bool(raw.get("success"))
    stats = _stats(raw) if ok else None
    return {
        "algorithmId": item["algorithmId"],
        "success": ok,
        "message": "" if ok else str(raw.get("message") or "运行失败"),
        "stats": stats,
        "previewUrl": _preview_url(raw) if ok else None,
        "quality": interpret_result(item["algorithmId"], stats, role),
    }


async def run_aide(scenario_id: str, llm_client: LlmClient | None = None) -> dict[str, Any]:
    """问题、计划、两路结果、建议一次返回。"""
    scene = get_scenario(scenario_id)
    plan = build_plan(scenario_id)
    results = [
        await _one_result(scene["primary"], "primary"),
        await _one_result(scene["contrast"], "contrast"),
    ]
    advice, llm = apply_narrative(plan, results, llm_client=llm_client)
    return {
        "success": True,
        "scenarioId": scenario_id,
        "question": scene["question"],
        "plan": plan,
        "results": results,
        "advice": advice,
        "llm": llm,
    }
