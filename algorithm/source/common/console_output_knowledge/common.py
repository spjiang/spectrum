"""输出知识公共构造器、格式级基础结构与质量规则类型。"""

from __future__ import annotations

from typing import Any


def _parse_output_path(path: str) -> tuple[str, str]:
    """从完整输出路径拆出 parent 与 apiKey。"""
    if not (path.startswith("files.") or path.startswith("data.")):
        raise ValueError(f"输出路径必须以 files. 或 data. 开头：{path}")
    parent, api_key = path.split(".", 1)
    if not api_key:
        raise ValueError(f"输出路径缺少 apiKey：{path}")
    return parent, api_key


def make_output(
    path: str,
    label: str,
    *,
    description: str,
    effect: str,
    business_meaning: str,
    interpretation: str,
    quality_check: str,
    abnormal_signs: list[str],
    downstream_use: str,
    unit: str = "—",
    range_text: str = "由输入数据与算法定义决定",
    format_name: str = "",
    vis: str = "none",
    optional: bool = False,
    conditional: str = "",
    bands: list[dict[str, Any]] | None = None,
    misuse_warning: str = "",
    related_outputs: list[str] | None = None,
    quality_rule: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """构造单条输出知识记录，path 决定 parent 与 apiKey。"""
    parent, api_key = _parse_output_path(path)
    row: dict[str, Any] = {
        "path": path,
        "parent": parent,
        "apiKey": api_key,
        "label": label,
        "description": description,
        "effect": effect,
        "businessMeaning": business_meaning,
        "interpretation": interpretation,
        "qualityCheck": quality_check,
        "abnormalSigns": abnormal_signs,
        "downstreamUse": downstream_use,
        "unit": unit,
        "range": range_text,
        "format": format_name,
        "vis": vis,
        "optional": optional,
        "conditional": conditional,
        "misuseWarning": misuse_warning,
    }
    if bands is not None:
        row["bands"] = bands
    if related_outputs is not None:
        row["relatedOutputs"] = related_outputs
    if quality_rule is not None:
        row["qualityRule"] = quality_rule
    return row


# 历史最小种子已全部迁入各层模块；保留空映射仅兼容公共聚合接口。
SEED_OUTPUT_KNOWLEDGE: dict[str, dict[str, Any]] = {}
