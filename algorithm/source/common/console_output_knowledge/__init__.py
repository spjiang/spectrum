"""控制台输出知识库：公共接口、数据校验与分组聚合。"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .common import SEED_OUTPUT_KNOWLEDGE, make_output

__all__ = [
    "get_algorithm_output_knowledge",
    "list_known_output_paths",
    "make_output",
]


def _empty_knowledge() -> dict[str, Any]:
    """未知算法返回空结构，不伪造专业说明。"""
    return {"summary": {}, "outputs": {}}


def _collect_layer_knowledge() -> dict[str, dict[str, Any]]:
    """合并 L0/L2/L3 层输出知识；层模块尚未创建时仅使用种子数据。"""
    merged: dict[str, dict[str, Any]] = {}
    for module_name, attr in (
        ("l0", "L0_OUTPUT_KNOWLEDGE"),
        ("l2", "L2_OUTPUT_KNOWLEDGE"),
        ("l3", "L3_OUTPUT_KNOWLEDGE"),
    ):
        full_name = f"{__name__}.{module_name}"
        try:
            module = __import__(full_name, fromlist=[attr])
        except ModuleNotFoundError as exc:
            # 仅忽略目标层模块自身不存在；内部依赖缺失必须向上抛出。
            if exc.name == full_name:
                continue
            raise
        layer = getattr(module, attr, None)
        if isinstance(layer, dict):
            merged.update(layer)
    merged.update(SEED_OUTPUT_KNOWLEDGE)
    return merged


_LAYER_KNOWLEDGE = _collect_layer_knowledge()


def get_algorithm_output_knowledge(algorithm_id: str) -> dict[str, Any]:
    """按算法 ID 返回输出知识；不存在时返回空 summary 与 outputs。"""
    raw = _LAYER_KNOWLEDGE.get(algorithm_id)
    if not raw:
        return _empty_knowledge()
    return deepcopy(raw)


def list_known_output_paths(algorithm_id: str) -> set[str]:
    """返回算法已登记的全部输出路径集合。"""
    return set(get_algorithm_output_knowledge(algorithm_id).get("outputs", {}).keys())
