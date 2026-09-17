"""模板叙事为默认路径；LLM 只能润色，不能改选型。"""

from __future__ import annotations

import json
from typing import Any, Callable

from common.l3_aide.scenarios import SCENARIOS

LlmClient = Callable[[list[dict[str, str]]], str]

_NOT_PRESCRIPTION = "不是处方"
_PRESCRIPTION_OK = (
    "不是处方",
    "不能当处方",
    "不能作为处方",
    "不可作为处方",
    "禁止处方",
    "非处方",
    "不得开处方",
    "不得作为处方",
)


def _comment_allowed(text: str) -> bool:
    """允许否定处方的表述，拦截剂量和强制业务动作。"""
    if any(word in text for word in ("公斤", "kg/亩", "必须执行")):
        return False
    if "处方" not in text:
        return True
    return any(token in text for token in _PRESCRIPTION_OK)


def _parse_run_comment(raw: str) -> str:
    """从模型正文取出 runComment；允许前后夹杂说明。"""
    text = raw.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return str(parsed.get("runComment") or "").strip()
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(text[start : end + 1])
            if isinstance(parsed, dict) and parsed.get("runComment"):
                return str(parsed.get("runComment") or "").strip()
        except json.JSONDecodeError:
            pass
    return text


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
                "不得推荐其他算法，不得输出处方或业务决策。只返回 JSON。"
            ),
        },
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def template_advice(results: list[dict[str, Any]]) -> dict[str, Any]:
    """规则建议；缺少返回时不得给出肯定业务判断。"""
    scene = SCENARIOS["index_output_review"]
    base = scene["advice"]
    incomplete = any(not row.get("success") for row in results)
    if incomplete:
        headline = "证据不完整，不能解释本次结果"
        bullets = [
            "算法结果未完整返回，不能把本次运行当成业务依据。",
            "下一步只检查当前算法的输入、波段参数与返回字段，" + _NOT_PRESCRIPTION + "。",
            "不得推荐其他算法，也不能直接决策。",
        ]
    else:
        headline = str(base["headline"])
        bullets = list(base["bullets"])
    text = headline + "".join(bullets)
    if _NOT_PRESCRIPTION not in text:
        bullets.append("本次" + _NOT_PRESCRIPTION + "，也不能直接决策。")
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
    advice = template_advice(results)
    if llm_client is None:
        return advice, {"used": False, "fallback": True, "reason": "no_key"}
    try:
        raw = llm_client(
            build_llm_messages(
                {
                    "scenarioId": "index_output_review",
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
    headline = str(parsed.get("headline") or "").strip() or advice["headline"]
    raw_bullets = parsed.get("bullets")
    bullets = [str(item).strip() for item in raw_bullets] if isinstance(raw_bullets, list) else list(advice["bullets"])
    bullets = [item for item in bullets if item]
    if not bullets:
        bullets = list(advice["bullets"])
    merged = headline + "".join(bullets)
    if ("公斤" in merged or "kg/亩" in merged) and _NOT_PRESCRIPTION not in merged:
        return advice, {"used": False, "fallback": True, "reason": "invalid"}
    if "处方" in merged and _NOT_PRESCRIPTION not in merged:
        return advice, {"used": False, "fallback": True, "reason": "invalid"}
    if _NOT_PRESCRIPTION not in merged:
        bullets.append("本次" + _NOT_PRESCRIPTION + "，也不能直接决策。")
    return (
        {"headline": headline, "bullets": bullets, "isPrescription": False},
        {"used": True, "fallback": False, "reason": "ok"},
    )


_DEFAULT_ALGO_SYSTEM = (
    "你是 L3 单算法运行的结果解读模块。只返回 JSON {\"runComment\": \"...\"}。"
    "必须对照 fieldGuides 解读 data 原始返回。按现象、边界、下一步写 3～5 句。"
    "禁止只复述 min/max/mean。必须写明不是处方。不得推荐其他算法，不得输出业务决策。"
)

_UNSAFE_MARKERS = (
    ".tif",
    ".tiff",
    ".png",
    ".npz",
    ".geojson",
    "outputs/",
    "http://",
    "https://",
    "/var/",
    "/tmp/",
    "/api/v1/console/",
)


def _unsafe_text(text: str) -> bool:
    """路径、预览地址或影像后缀不得进提示词。"""
    low = text.lower()
    return any(mark in low for mark in _UNSAFE_MARKERS)


def sanitize_run_value(value: Any, depth: int = 0) -> Any:
    """只保留可解读标量；丢掉数组、路径和影像地址。"""
    if depth > 6:
        return None
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        if len(value) > 240 or _unsafe_text(value):
            return None
        return value
    if isinstance(value, list):
        return {"_omitted": "array", "length": len(value)}
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            name = str(key)
            if _unsafe_text(name):
                continue
            kept = sanitize_run_value(item, depth + 1)
            if kept is not None:
                cleaned[name] = kept
        return cleaned
    return None


def file_keys_only(files: Any) -> list[str]:
    """只保留产物键名，丢掉路径。"""
    if isinstance(files, dict):
        return [str(key) for key in files if not _unsafe_text(str(key))]
    if isinstance(files, list):
        return [str(item) for item in files if isinstance(item, str) and not _unsafe_text(item)]
    return []


def field_guides_for(algorithm_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """从控制台输出知识抽出给模型的字段说明。"""
    from common.console_output_knowledge import get_algorithm_output_knowledge

    pack = get_algorithm_output_knowledge(algorithm_id)
    summary = pack.get("summary") if isinstance(pack.get("summary"), dict) else {}
    guides: list[dict[str, Any]] = []
    outputs = pack.get("outputs") if isinstance(pack.get("outputs"), dict) else {}
    for path, row in outputs.items():
        if not isinstance(row, dict):
            continue
        guides.append(
            {
                "path": path,
                "label": row.get("label"),
                "description": row.get("description"),
                "businessMeaning": row.get("businessMeaning"),
                "interpretation": row.get("interpretation"),
                "unit": row.get("unit"),
                "range": row.get("range"),
                "qualityCheck": row.get("qualityCheck"),
                "misuseWarning": row.get("misuseWarning"),
            }
        )
    return summary, guides


def build_algo_llm_messages(facts: dict[str, Any]) -> list[dict[str, str]]:
    """算法页解读：系统提示来自知识库，用户侧带原始 data 与字段说明，不含影像。"""
    from common.l3_aide.knowledge import get_algorithm

    stats = facts.get("stats") if isinstance(facts.get("stats"), dict) else {}
    quality = facts.get("quality") if isinstance(facts.get("quality"), dict) else {}
    raw_data = facts.get("data") if isinstance(facts.get("data"), dict) else {}
    if not raw_data and stats:
        raw_data = stats
    doc = get_algorithm(str(facts.get("id") or "")) or {}
    summary, guides = field_guides_for(str(facts.get("id") or ""))
    payload = {
        "id": facts.get("id"),
        "title": facts.get("title") or doc.get("title") or "",
        "definition": facts.get("definition") or doc.get("definition") or "",
        "task": "对照字段说明解读 data 里的原始返回。按现象、边界、下一步写，不要把三个统计数字当全文。",
        "data": sanitize_run_value(raw_data) or {},
        "filesProduced": file_keys_only(facts.get("files")),
        "fieldGuides": guides,
        "outputSummary": summary,
        "qualityStatus": quality.get("status"),
        "qualityLabel": quality.get("label"),
        "qualityDetail": quality.get("detail"),
    }
    system = str(facts.get("llmPrompt") or "").strip() or _DEFAULT_ALGO_SYSTEM
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def prompt_preview(messages: list[dict[str, str]]) -> dict[str, str]:
    """给页面展示实际将发送的系统 / 用户提示。"""
    by_role = {row.get("role"): str(row.get("content") or "") for row in messages}
    return {"system": by_role.get("system", ""), "user": by_role.get("user", "")}


def template_run_comment(
    algorithm_id: str | None = None,
    stats: dict[str, Any] | None = None,
    quality: dict[str, Any] | None = None,
) -> str:
    """无大模型时的领域解读，禁止只回显三个数字。"""
    from common.l3_aide.knowledge import get_algorithm

    doc = get_algorithm(str(algorithm_id or "")) or {}
    title = str(doc.get("title") or "本算法")
    if not stats or any(key not in stats for key in ("min", "max", "mean")):
        return f"{title}本次未提供全图 min/max/mean，不能编造区间或长势结论。这不是处方。"
    readout = [str(line) for line in (doc.get("readout") or [])]
    try:
        filled = [
            line.format(
                min=float(stats["min"]),
                max=float(stats["max"]),
                mean=float(stats["mean"]),
            )
            for line in readout
        ]
    except (KeyError, ValueError, IndexError):
        filled = []
    label = str((quality or {}).get("label") or "").strip()
    parts: list[str] = []
    if label:
        parts.append(label + "。")
    parts.extend(filled)
    text = "".join(parts) if filled else (
        f"{title}：全图均值 {float(stats['mean']):.2f}，"
        f"范围 {float(stats['min']):.2f}～{float(stats['max']):.2f}。"
        "这是相对格局，不是处方，也不能当业务验收。"
    )
    if _NOT_PRESCRIPTION not in text:
        text += "这不是处方。"
    return text


def apply_run_comment(
    algorithm_id: str,
    stats: dict[str, Any] | None,
    quality: dict[str, Any],
    llm_must_not: list[str],
    llm_client: LlmClient | None = None,
    llm_may: list[str] | None = None,
    llm_prompt: str = "",
    data: dict[str, Any] | None = None,
    files: Any = None,
    prompt_override: dict[str, str] | None = None,
) -> tuple[str, dict[str, Any], dict[str, str]]:
    """返回 runComment、llm 元数据、本次提示词预览。"""
    override = prompt_override if isinstance(prompt_override, dict) else {}
    system_override = str(override.get("system") or "").strip()
    user_override = str(override.get("user") or "").strip()
    comment = template_run_comment(algorithm_id, stats, quality)
    messages = build_algo_llm_messages(
        {
            "id": algorithm_id,
            "llmMay": llm_may or [],
            "llmMustNot": llm_must_not,
            "llmPrompt": system_override or llm_prompt,
            "stats": stats or {},
            "data": data or {},
            "files": files,
            "quality": quality,
        }
    )
    if user_override:
        messages = [
            {"role": "system", "content": messages[0]["content"] if messages else system_override},
            {"role": "user", "content": user_override},
        ]
    preview = prompt_preview(messages)
    if llm_client is None:
        return comment, {"used": False, "fallback": True, "reason": "no_key"}, preview
    try:
        raw = llm_client(messages)
        text = _parse_run_comment(raw)
    except TimeoutError as exc:
        return comment, {"used": False, "fallback": True, "reason": "timeout", "detail": str(exc)[:240]}, preview
    except OSError as exc:
        msg = str(exc)[:240]
        reason = "no_balance" if "余额不足" in msg else "http_error"
        return comment, {"used": False, "fallback": True, "reason": reason, "detail": msg}, preview
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return comment, {"used": False, "fallback": True, "reason": "invalid", "detail": str(exc)[:240]}, preview
    if not text:
        return comment, {"used": False, "fallback": True, "reason": "invalid"}, preview
    if not _comment_allowed(text):
        return comment, {"used": False, "fallback": True, "reason": "invalid"}, preview
    return text, {"used": True, "fallback": False, "reason": "ok"}, preview


_LAYER_SYSTEM = (
    "你是高光谱处理层参谋，对照「传统做法」说明这一层 AI 多做了什么。"
    "只返回 JSON {\"headline\": \"...\", \"aiMarkdown\": \"...\"}。"
    "aiMarkdown 用中文 Markdown。必须写明不是处方。不得推荐其他算法，不得输出业务决策。"
    "不得改写算法公式，不得把影像、路径或 URL 写进结论。"
)


def _parse_layer_ai(raw: str) -> tuple[str, str]:
    """从模型正文取出 headline 与 aiMarkdown。"""
    text = raw.strip()
    parsed: dict[str, Any] | None = None
    try:
        maybe = json.loads(text)
        if isinstance(maybe, dict):
            parsed = maybe
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                maybe = json.loads(text[start : end + 1])
                if isinstance(maybe, dict):
                    parsed = maybe
            except json.JSONDecodeError:
                parsed = None
    if parsed:
        headline = str(parsed.get("headline") or "").strip()
        markdown = str(parsed.get("aiMarkdown") or parsed.get("markdown") or "").strip()
        return headline, markdown
    return "", text


def build_layer_llm_messages(case: dict[str, Any]) -> list[dict[str, str]]:
    """按层对照：传统做法 + 消毒后的演示证据，不含影像。"""
    evidence = case.get("evidence") if isinstance(case.get("evidence"), dict) else {}
    payload = {
        "layerId": case.get("id"),
        "level": case.get("level"),
        "title": case.get("title"),
        "question": case.get("question"),
        "context": case.get("context") or [],
        "traditional": case.get("traditional") or {},
        "templateAi": (case.get("ai") or {}).get("markdown"),
        "mustNot": case.get("mustNot") or [],
        "evidence": sanitize_run_value(
            {
                "demoAlgorithmId": evidence.get("demoAlgorithmId"),
                "success": evidence.get("success"),
                "message": evidence.get("message"),
                "data": evidence.get("data") or {},
                "stats": evidence.get("stats") or {},
                "results": evidence.get("results") or [],
                "plan": evidence.get("plan") or {},
            }
        ),
    }
    return [
        {"role": "system", "content": _LAYER_SYSTEM},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def apply_layer_narrative(
    case: dict[str, Any],
    evidence: dict[str, Any],
    llm_client: LlmClient | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    """返回 AI 栏、llm 元数据、提示词预览。传统栏永远不走模型。"""
    template = {
        "headline": str((case.get("ai") or {}).get("headline") or ""),
        "markdown": str((case.get("ai") or {}).get("markdown") or ""),
    }
    messages = build_layer_llm_messages({**case, "evidence": evidence})
    preview = prompt_preview(messages)
    if llm_client is None:
        return template, {"used": False, "fallback": True, "reason": "no_key"}, preview
    try:
        raw = llm_client(messages)
        headline, markdown = _parse_layer_ai(raw)
    except TimeoutError as exc:
        return template, {"used": False, "fallback": True, "reason": "timeout", "detail": str(exc)[:240]}, preview
    except OSError as exc:
        return template, {"used": False, "fallback": True, "reason": "http_error", "detail": str(exc)[:240]}, preview
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return template, {"used": False, "fallback": True, "reason": "invalid", "detail": str(exc)[:240]}, preview
    if not markdown:
        return template, {"used": False, "fallback": True, "reason": "invalid"}, preview
    if not _comment_allowed(markdown):
        return template, {"used": False, "fallback": True, "reason": "invalid"}, preview
    if _NOT_PRESCRIPTION not in markdown:
        markdown += "\n\n这不是处方。"
    return (
        {"headline": headline or template["headline"], "markdown": markdown},
        {"used": True, "fallback": False, "reason": "ok"},
        preview,
    )
