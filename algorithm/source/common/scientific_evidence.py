"""读取 Python 与前端共用的科学证据登记表。"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


EVIDENCE_PATH = (
    Path(__file__).resolve().parents[2] / "shared" / "scientific_evidence.json"
)
TOP_LEVEL_KEYS = {
    "algorithmId",
    "title",
    "grade",
    "implementation",
    "claims",
    "references",
}
CLAIM_KEYS = {
    "claimId",
    "category",
    "text",
    "status",
    "targets",
    "referenceIds",
    "implementationRefs",
    "reviewNote",
}
REFERENCE_KEYS = {
    "referenceId",
    "authors",
    "year",
    "title",
    "venue",
    "url",
    "sourceType",
    "summary",
    "supports",
}
CLAIM_CATEGORIES = {"definition", "formula", "input", "output", "limitation"}
CLAIM_STATUSES = {"verified", "qualified", "implementation-only"}
SOURCE_TYPES = {
    "primary-paper",
    "official-documentation",
    "academic-material",
    "secondary-index",
}
REVIEW_TARGETS = {
    "principle",
    "source-panel",
    "console-output",
    "ai-knowledge",
    "product-analysis",
    "docs-api-checklist",
    "docs-algorithm-inventory",
}


def _require_nonempty_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} 必须是非空字符串")


def _require_string_list(
    value: Any,
    field: str,
    *,
    allow_empty: bool = False,
) -> None:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ValueError(f"{field} 必须是非空数组")
    for item in value:
        _require_nonempty_string(item, field)


def validate_scientific_evidence(data: Any) -> list[dict[str, Any]]:
    """严格验证共享证据；未知、缺失或空必需字段一律拒绝。"""
    if not isinstance(data, list) or not data:
        raise TypeError("scientific_evidence.json 顶层必须是非空数组")

    algorithm_ids: set[str] = set()
    for row_index, row in enumerate(data):
        prefix = f"rows[{row_index}]"
        if not isinstance(row, dict) or set(row) != TOP_LEVEL_KEYS:
            raise ValueError(f"{prefix} 顶层字段不完整")
        for field in ("algorithmId", "title", "implementation"):
            _require_nonempty_string(row[field], f"{prefix}.{field}")
        if row["algorithmId"] in algorithm_ids:
            raise ValueError(f"{prefix}.algorithmId 重复")
        algorithm_ids.add(row["algorithmId"])
        if row["grade"] not in {"A", "B", "C"}:
            raise ValueError(f"{prefix}.grade 非法")
        if not isinstance(row["claims"], list) or not row["claims"]:
            raise ValueError(f"{prefix}.claims 必须是非空数组")
        if not isinstance(row["references"], list) or not row["references"]:
            raise ValueError(f"{prefix}.references 必须是非空数组")

        claims: dict[str, dict[str, Any]] = {}
        for claim_index, claim in enumerate(row["claims"]):
            claim_prefix = f"{prefix}.claims[{claim_index}]"
            if not isinstance(claim, dict) or set(claim) != CLAIM_KEYS:
                raise ValueError(f"{claim_prefix} claim 字段不完整")
            for field in ("claimId", "text", "reviewNote"):
                _require_nonempty_string(claim[field], f"{claim_prefix}.{field}")
            if claim["claimId"] in claims:
                raise ValueError(f"{claim_prefix}.claimId 重复")
            if claim["category"] not in CLAIM_CATEGORIES:
                raise ValueError(f"{claim_prefix}.category 非法")
            if claim["status"] not in CLAIM_STATUSES:
                raise ValueError(f"{claim_prefix}.status 非法")
            _require_string_list(claim["targets"], f"{claim_prefix}.targets")
            if not set(claim["targets"]) <= REVIEW_TARGETS:
                raise ValueError(f"{claim_prefix}.targets 非法")
            _require_string_list(
                claim["referenceIds"],
                f"{claim_prefix}.referenceIds",
                allow_empty=True,
            )
            _require_string_list(
                claim["implementationRefs"],
                f"{claim_prefix}.implementationRefs",
            )
            claims[claim["claimId"]] = claim

        covered_targets = {
            target for claim in row["claims"] for target in claim["targets"]
        }
        if covered_targets != REVIEW_TARGETS:
            raise ValueError(f"{prefix}.claims 审查 targets 不完整")

        references: dict[str, dict[str, Any]] = {}
        for ref_index, ref in enumerate(row["references"]):
            ref_prefix = f"{prefix}.references[{ref_index}]"
            if not isinstance(ref, dict) or set(ref) != REFERENCE_KEYS:
                raise ValueError(f"{ref_prefix} reference 字段不完整")
            for field in (
                "referenceId",
                "authors",
                "year",
                "title",
                "venue",
                "url",
                "sourceType",
                "summary",
            ):
                _require_nonempty_string(ref[field], f"{ref_prefix}.{field}")
            if ref["referenceId"] in references:
                raise ValueError(f"{ref_prefix}.referenceId 重复")
            if ref["sourceType"] not in SOURCE_TYPES:
                raise ValueError(f"{ref_prefix}.sourceType 非法")
            if not ref["url"].startswith("https://"):
                raise ValueError(f"{ref_prefix}.url 必须使用 HTTPS")
            if len(ref["summary"]) < 20 or not any(
                "\u3400" <= char <= "\u9fff" for char in ref["summary"]
            ):
                raise ValueError(f"{ref_prefix}.summary 必须是至少 20 字的中文提要")
            _require_string_list(ref["supports"], f"{ref_prefix}.supports")
            references[ref["referenceId"]] = ref

        for claim in row["claims"]:
            for reference_id in claim["referenceIds"]:
                if reference_id not in references:
                    raise ValueError(f"{prefix} claim 引用了不存在的 reference")
                if claim["claimId"] not in references[reference_id]["supports"]:
                    raise ValueError(f"{prefix} claim/reference 未双向闭合")
        for reference in row["references"]:
            for claim_id in reference["supports"]:
                if claim_id not in claims:
                    raise ValueError(f"{prefix} reference 支持不存在的 claim")
                if reference["referenceId"] not in claims[claim_id]["referenceIds"]:
                    raise ValueError(f"{prefix} reference/claim 未双向闭合")
    return data


def load_scientific_evidence() -> list[dict[str, Any]]:
    """加载证据登记表；保持缺失字段可见，不做静默补全。"""
    with EVIDENCE_PATH.open(encoding="utf-8") as handle:
        rows = json.load(handle)
    return deepcopy(validate_scientific_evidence(rows))


def get_algorithm_evidence(algorithm_id: str) -> dict[str, Any] | None:
    """按算法 ID 返回独立副本；未登记时返回 None。"""
    for row in load_scientific_evidence():
        if row["algorithmId"] == algorithm_id:
            return deepcopy(row)
    return None
