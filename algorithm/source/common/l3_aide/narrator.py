"""模板叙事为默认路径；LLM 只能润色，不能改选型。"""

from __future__ import annotations

import json
from typing import Any, Callable

from common.l3_aide.scenarios import SCENARIOS

LlmClient = Callable[[list[dict[str, str]]], str]

_NOT_PRESCRIPTION = "不是处方"


def build_llm_messages(facts: dict[str, Any]) -> list[dict[str, str]]:
    """只序列化低维事实，剥离路径、预览 URL 与数组。"""
    plan = facts.get("plan") or {}
    safe_results = []
    for row in facts.get("results") or []:
        stats = row.get("stats") if isinstance(row.get("stats"), dict) else {}
        quality = row.get("quality") if isinstance(row.get("quality"), dict) else {}
        safe_results.append(
            {
                "algorithmId": row.get("algorithmId"),
                "success": row.get("success"),
                "min": stats.get("min"),
                "max": stats.get("max"),
                "mean": stats.get("mean"),
                "qualityStatus": quality.get("status"),
            }
        )
    payload = {
        "scenarioId": facts.get("scenarioId"),
        "primaryAlgorithmId": (plan.get("primary") or {}).get("algorithmId"),
        "contrastAlgorithmId": (plan.get("contrast") or {}).get("algorithmId"),
        "results": safe_results,
    }
    return [
        {
            "role": "system",
            "content": (
                "你是高光谱 L3 参谋的中文润色器。不得更改 primaryAlgorithmId。"
                "不得给出施肥处方或公斤/亩剂量。只返回 JSON。"
            ),
        },
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def _template_advice(results: list[dict[str, Any]]) -> dict[str, Any]:
    """规则建议；缺图时不得给出肯定补氮判断。"""
    scene = SCENARIOS["rice_dense_max_n"]
    base = scene["advice"]
    incomplete = any(not row.get("success") for row in results)
    if incomplete:
        headline = "证据不完整，不能给补氮判断"
        bullets = [
            "主图或对照图未完整算出，不能把本次运行当成补氮依据。",
            "建议停留在检查输入与波段，" + _NOT_PRESCRIPTION + "。",
            "定量与亩均报表仍需地面化验和 L4 地块汇总（45）。",
        ]
    else:
        headline = str(base["headline"])
        bullets = list(base["bullets"])
    text = headline + "".join(bullets)
    if _NOT_PRESCRIPTION not in text:
        bullets.append("本次" + _NOT_PRESCRIPTION + "，不输出公斤/亩。")
    return {
        "headline": headline,
        "bullets": bullets,
        "isPrescription": False,
    }


def apply_narrative(
    plan: dict[str, Any],
    results: list[dict[str, Any]],
    llm_client: LlmClient | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """返回 advice 与 llm 元数据。模型改选型则整段丢弃，建议仍用模板。"""
    advice = _template_advice(results)
    if llm_client is None:
        return advice, {"used": False, "fallback": True, "reason": "no_key"}
    try:
        raw = llm_client(
            build_llm_messages(
                {
                    "scenarioId": "rice_dense_max_n",
                    "plan": plan,
                    "results": results,
                }
            )
        )
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError, ValueError, TimeoutError, OSError):
        return advice, {"used": False, "fallback": True, "reason": "invalid"}
    if parsed.get("primaryAlgorithmId") != plan["primary"]["algorithmId"]:
        return advice, {"used": False, "fallback": True, "reason": "plan_override_rejected"}
    merged = str(parsed.get("headline") or "") + "".join(
        str(item) for item in (parsed.get("bullets") or [])
    )
    if ("公斤" in merged or "kg/亩" in merged or "处方" in merged) and _NOT_PRESCRIPTION not in merged:
        return advice, {"used": False, "fallback": True, "reason": "invalid"}
    # 第一期演示以模板为准，避免现场措辞漂移；仅标记模型校验已通过。
    return advice, {"used": True, "fallback": False, "reason": "ok"}
