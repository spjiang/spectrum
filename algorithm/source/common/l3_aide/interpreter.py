"""根据统计与角色给出质量状态；不依据 PNG 颜色。"""

from __future__ import annotations

from typing import Any


def interpret_result(
    algorithm_id: str,
    stats: dict[str, Any] | None,
    role: str,
) -> dict[str, str]:
    """返回 status / label / detail。缺统计则为不可判定。"""
    if not stats or any(key not in stats for key in ("min", "max", "mean")):
        return {
            "status": "unknown",
            "label": "不可判定",
            "detail": "缺少 min/max/mean，不能根据本次运行下结论。",
        }
    low = float(stats["min"])
    high = float(stats["max"])
    mean = float(stats["mean"])
    index_ids = {"27_ndvi", "28_ndre", "29_evi_savi", "30_ndmi_ndwi"}
    if algorithm_id in index_ids and (low < -1.0 or high > 1.0):
        return {
            "status": "warn",
            "label": "指数越出理论区间",
            "detail": f"本次范围 {low:.3f}～{high:.3f}，超出 [-1, 1]，需人工检查波段与定标。",
        }
    if algorithm_id == "27_ndvi" and role == "contrast":
        detail = "本次 NDVI 仅作同景对照，不能据此作业务决策。"
        if mean >= 0.65:
            detail += "高值区接近饱和，空间反差可能偏弱。"
        return {
            "status": "pass",
            "label": "仅作同景对照",
            "detail": detail,
        }
    if algorithm_id == "28_ndre" and role == "primary":
        return {
            "status": "pass",
            "label": "统计落在指数常见区间",
            "detail": "仅说明本次返回的相对空间格局，不是处方，也不能直接决策。",
        }
    if role == "solo" and algorithm_id in {"27_ndvi", "28_ndre", "29_evi_savi", "30_ndmi_ndwi"}:
        return {
            "status": "pass",
            "label": "统计落在指数常见区间",
            "detail": f"本次范围 {low:.3f}～{high:.3f}。仅演示数据，不能当农情结论。",
        }
    return {
        "status": "unknown",
        "label": "不可判定",
        "detail": "没有匹配的质量规则，仅展示本次统计（若有）。",
    }
