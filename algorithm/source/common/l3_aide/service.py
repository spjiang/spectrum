"""组装一次 L3 参谋运行。"""

from __future__ import annotations

from typing import Any

from common.l3_aide.interpreter import interpret_result
from common.l3_aide.knowledge import get_algorithm
from common.l3_aide.layers import get_layer
from common.l3_aide.narrator import (
    LlmClient,
    apply_layer_narrative,
    apply_narrative,
    apply_run_comment,
    template_advice,
    template_run_comment,
)
from common.l3_aide.orchestrator import build_plan, get_scenario
from common.l3_aide.runner import run_algorithm, run_algorithm_testdata


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
        "templateAdvice": template_advice(results),
        "llm": llm,
    }


async def run_one_algorithm(algorithm_id: str, llm_client: LlmClient | None = None) -> dict[str, Any]:
    """单算法 testdata 演示 + 本次解读。"""
    doc = get_algorithm(algorithm_id)
    if doc is None:
        raise KeyError(algorithm_id)
    raw = await run_algorithm_testdata(algorithm_id)
    ok = bool(raw.get("success"))
    stats = _stats(raw) if ok else None
    quality = interpret_result(algorithm_id, stats, "solo")
    comment, llm, prompt = apply_run_comment(
        algorithm_id,
        stats,
        quality,
        list(doc.get("llmMustNot") or []),
        llm_client=llm_client,
        llm_may=list(doc.get("llmMay") or []),
        llm_prompt=str(doc.get("llmPrompt") or ""),
        data=raw.get("data") if isinstance(raw.get("data"), dict) else None,
        files=raw.get("files"),
    )
    return {
        "success": ok,
        "algorithmId": algorithm_id,
        "message": "" if ok else str(raw.get("message") or "运行失败"),
        "stats": stats,
        "previewUrl": _preview_url(raw) if ok else None,
        "quality": quality,
        "runComment": comment,
        "templateComment": template_run_comment(algorithm_id, stats, quality),
        "prompt": prompt,
        "llm": llm,
    }


def interpret_from_stats(
    algorithm_id: str,
    stats: dict[str, Any] | None,
    llm_client: LlmClient | None = None,
    data: dict[str, Any] | None = None,
    files: Any = None,
    prompt_override: dict[str, str] | None = None,
) -> dict[str, Any]:
    """只解读已有接口返回，不再跑算法。"""
    doc = get_algorithm(algorithm_id)
    if doc is None:
        raise KeyError(algorithm_id)
    quality = interpret_result(algorithm_id, stats, "solo")
    comment, llm, prompt = apply_run_comment(
        algorithm_id,
        stats,
        quality,
        list(doc.get("llmMustNot") or []),
        llm_client=llm_client,
        llm_may=list(doc.get("llmMay") or []),
        llm_prompt=str(doc.get("llmPrompt") or ""),
        data=data,
        files=files,
        prompt_override=prompt_override,
    )
    return {
        "success": True,
        "algorithmId": algorithm_id,
        "stats": stats,
        "quality": quality,
        "runComment": comment,
        "templateComment": template_run_comment(algorithm_id, stats, quality),
        "prompt": prompt,
        "llm": llm,
    }


def _demo_from_raw(algorithm_id: str, raw: dict[str, Any]) -> dict[str, Any]:
    """把 testdata 运行压成页面可用的演示摘要。"""
    ok = bool(raw.get("success"))
    return {
        "algorithmId": algorithm_id,
        "success": ok,
        "message": "" if ok else str(raw.get("message") or "运行失败"),
        "stats": _stats(raw) if ok else None,
        "previewUrl": _preview_url(raw) if ok else None,
        "data": raw.get("data") if isinstance(raw.get("data"), dict) else {},
    }


def _safe_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """给模型的结果摘要，不含预览地址。"""
    out: list[dict[str, Any]] = []
    for row in rows:
        stats = row.get("stats") if isinstance(row.get("stats"), dict) else {}
        quality = row.get("quality") if isinstance(row.get("quality"), dict) else {}
        out.append(
            {
                "algorithmId": row.get("algorithmId"),
                "success": row.get("success"),
                "min": stats.get("min"),
                "max": stats.get("max"),
                "mean": stats.get("mean"),
                "qualityStatus": quality.get("status"),
                "qualityLabel": quality.get("label"),
            }
        )
    return out


async def run_layer(layer_id: str, llm_client: LlmClient | None = None) -> dict[str, Any]:
    """按层跑代表算法，再用大模型解释当前算法的输出边界。"""
    case = get_layer(layer_id)
    if case is None:
        raise KeyError(layer_id)
    evidence: dict[str, Any] = {}
    demo: dict[str, Any] | None = None
    results: list[dict[str, Any]] | None = None
    plan: dict[str, Any] | None = None
    algorithm_id = str(case.get("demoAlgorithmId") or "")
    raw = await run_algorithm_testdata(algorithm_id)
    demo = _demo_from_raw(algorithm_id, raw)
    evidence = {
        "demoAlgorithmId": algorithm_id,
        "success": demo["success"],
        "message": demo["message"],
        "data": demo.get("data") or {},
        "stats": demo.get("stats") or {},
    }
    ai, llm, prompt = apply_layer_narrative(case, evidence, llm_client=llm_client)
    return {
        "success": True,
        "layerId": layer_id,
        "level": case["level"],
        "title": case["title"],
        "question": case["question"],
        "hook": case["hook"],
        "context": case.get("context") or [],
        "traditional": case["traditional"],
        "ai": ai,
        "templateAi": case["ai"],
        "mustNot": case["mustNot"],
        "demo": demo,
        "plan": plan,
        "results": results,
        "prompt": prompt,
        "llm": llm,
    }
