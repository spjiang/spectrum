"""L3 参谋场景表：选型的唯一权威。"""

from __future__ import annotations

from typing import Any

SCENARIOS: dict[str, dict[str, Any]] = {
    "rice_dense_max_n": {
        "question": {
            "title": "密植水稻，MAX-S810 刚采完，要不要补氮？",
            "crop": "水稻",
            "canopy": "密植封垄",
            "sensor": "MAX-S810",
            "task": "氮素辅助判断",
            "hook": "对方机载已经会出 NDVI/NDRE。本页要证明的是：AI 团队决定「这场用哪个」，并挡住误用。",
        },
        "primary": {
            "algorithmId": "28_ndre",
            "title": "NDRE",
            "role": "primary",
            "reason": "密冠层红边对叶绿素更敏感，封垄后不易饱和。MAX 的 720/750 就是为这条准备的。",
            "params": {"re_band": 4, "nir_band": 3},
        },
        "contrast": {
            "algorithmId": "27_ndvi",
            "title": "NDVI",
            "role": "contrast",
            "reason": "用来当面指出：密冠层 NDVI 容易顶满，不能单独当补氮依据。",
            "params": {"red_band": 2, "nir_band": 3},
        },
        "skipped": [
            {
                "algorithmId": "29_evi_savi",
                "title": "EVI/SAVI/MSAVI",
                "reason": "土壤背景不重。苗期稀疏才上 SAVI；分类/水质换插件，不在本链。",
            }
        ],
        "advice": {
            "headline": "按 NDRE 低值区做分区巡田；本次不给施肥剂量",
            "bullets": [
                "主依据是 NDRE 相对空间格局，不是 NDVI，也不是机载实时绿度一条数。",
                "建议停留在「哪里先看、哪里可能更弱」。没有地面化验，不输出公斤/亩。",
                "要亩均报表和告警，下一层接 L4 地块汇总（45），本期演示只点到这里。",
            ],
        },
    }
}
