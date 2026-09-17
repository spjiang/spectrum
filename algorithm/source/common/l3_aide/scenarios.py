"""L3 输出对照演示；只解释已运行算法，不给场景或动作建议。"""

from __future__ import annotations

from typing import Any

SCENARIOS: dict[str, dict[str, Any]] = {
    "index_output_review": {
        "question": {
            "title": "如何解释两项指数算法的本次返回？",
            "sensor": "演示反射率立方体",
            "task": "接口输出边界检查",
            "hook": "只解释各算法已返回的统计与方法边界，不据此作处方或业务决策。",
        },
        "primary": {
            "algorithmId": "28_ndre",
            "title": "NDRE",
            "role": "primary",
            "reason": "单独核对 NDRE 返回字段、波段参数与指数值域。",
            "params": {"re_band": 4, "nir_band": 3},
        },
        "contrast": {
            "algorithmId": "27_ndvi",
            "title": "NDVI",
            "role": "contrast",
            "reason": "单独核对 NDVI 返回字段、波段参数与指数值域。",
            "params": {"red_band": 2, "nir_band": 3},
        },
        "skipped": [
            {
                "algorithmId": "29_evi_savi",
                "title": "EVI/SAVI/MSAVI",
                "reason": "本次没有运行，不作解释，也不推荐替换当前算法。",
            }
        ],
        "advice": {
            "headline": "仅解释已运行算法的返回",
            "bullets": [
                "分别核对本次指数范围、波段索引与质量状态。",
                "不把相对统计外推为原因、处方或业务决策。",
                "不得推荐其他算法；下一步只检查当前算法的输入、参数与返回字段。",
            ],
        },
    }
}
