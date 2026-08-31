"""根据场景表生成算法计划；未知场景必须失败。"""

from __future__ import annotations

from typing import Any

from common.l3_aide.scenarios import SCENARIOS


class UnknownScenarioError(KeyError):
    """请求了未登记的 scenarioId。"""


def get_scenario(scenario_id: str) -> dict[str, Any]:
    """读取场景；不存在则抛 UnknownScenarioError。"""
    scene = SCENARIOS.get(scenario_id)
    if scene is None:
        raise UnknownScenarioError(scenario_id)
    if "primary" not in scene or "contrast" not in scene:
        raise ValueError("参谋配置不完整")
    return scene


def _plan_item(item: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    """拷贝计划字段，不把波段参数暴露给前端选型卡。"""
    return {key: item[key] for key in keys}


def build_plan(scenario_id: str) -> dict[str, Any]:
    """输出主跑 / 对照 / 跳过清单。"""
    scene = get_scenario(scenario_id)
    card = ("algorithmId", "title", "role", "reason")
    skip = ("algorithmId", "title", "reason")
    return {
        "primary": _plan_item(scene["primary"], card),
        "contrast": _plan_item(scene["contrast"], card),
        "skipped": [_plan_item(row, skip) for row in scene["skipped"]],
    }
