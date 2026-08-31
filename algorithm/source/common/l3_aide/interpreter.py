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
    if low < -1.0 or high > 1.0:
        return {
            "status": "warn",
            "label": "指数越出理论区间",
            "detail": f"本次范围 {low:.3f}～{high:.3f}，超出 [-1, 1]，需人工检查波段与定标。",
        }
    if algorithm_id == "27_ndvi" and role == "contrast":
        detail = "同景 NDVI 只作对照：封垄后绿度指数不够用，不能单独当补氮依据。"
        if mean >= 0.65:
            detail += "高值区接近饱和，空间反差可能偏弱。"
        return {
            "status": "pass",
            "label": "本场景不能当补氮主依据",
            "detail": detail,
        }
    if algorithm_id == "28_ndre" and role == "primary":
        return {
            "status": "pass",
            "label": "可作为分区关注的主图",
            "detail": "落在红边指数合理区间。低值斑块优先当「相对弱区」看，不能换算成公斤/亩。",
        }
    return {
        "status": "unknown",
        "label": "不可判定",
        "detail": "没有匹配的质量规则。",
    }
