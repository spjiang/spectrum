"""共享科学证据模型的完整性门禁。"""

import hashlib
import importlib.util
import json
import re
from datetime import datetime
from pathlib import Path

import pytest

from common.catalog import ALGORITHMS
from common import scientific_evidence
from common.scientific_evidence import (
    get_algorithm_evidence,
    load_scientific_evidence,
)


ALL_ALGORITHM_IDS = [item["id"] for item in ALGORITHMS]
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
REQUIRED_TARGETS = {
    "principle",
    "source-panel",
    "console-output",
    "ai-knowledge",
    "product-analysis",
    "docs-api-checklist",
    "docs-algorithm-inventory",
}
REVIEWED_IDS = {
    f"{index:02d}_{name}"
    for index, name in enumerate(
        (
            "flight_planning",
            "sync_timestamp",
            "pos_solution",
            "flight_qc",
            "cloud_shadow",
            "dark_current",
            "bad_pixel",
            "destriping",
            "smile_keystone",
            "radiance_calibration",
            "relative_radiometric",
        ),
        start=1,
    )
}
ALGORITHM_ROOT = Path(__file__).resolve().parents[2]


def test_all_45_algorithms_have_scientific_evidence():
    rows = load_scientific_evidence()
    assert len(rows) == 55
    assert {row["algorithmId"] for row in rows} == set(ALL_ALGORITHM_IDS)


def test_complete_schema_and_enums_are_required():
    for row in load_scientific_evidence():
        assert set(row) == TOP_LEVEL_KEYS
        assert all(
            isinstance(row[key], str) and row[key].strip()
            for key in ("algorithmId", "title", "implementation")
        )
        assert row["grade"] in {"A", "B", "C"}
        assert isinstance(row["claims"], list) and row["claims"]
        assert isinstance(row["references"], list) and row["references"]

        claim_ids = []
        for claim in row["claims"]:
            assert set(claim) == CLAIM_KEYS
            assert all(
                isinstance(claim[key], str) and claim[key].strip()
                for key in ("claimId", "text", "reviewNote")
            )
            assert claim["category"] in CLAIM_CATEGORIES
            assert claim["status"] in CLAIM_STATUSES
            assert all(
                isinstance(claim[key], list) and claim[key]
                for key in ("targets", "implementationRefs")
            )
            assert isinstance(claim["referenceIds"], list)
            assert all(
                isinstance(value, str) and value.strip()
                for key in ("targets", "referenceIds", "implementationRefs")
                for value in claim[key]
            )
            assert set(claim["targets"]) <= REQUIRED_TARGETS
            claim_ids.append(claim["claimId"])
        assert len(claim_ids) == len(set(claim_ids))

        reference_ids = []
        for ref in row["references"]:
            assert set(ref) == REFERENCE_KEYS
            assert all(
                isinstance(ref[key], str) and ref[key].strip()
                for key in (
                    "referenceId",
                    "authors",
                    "year",
                    "title",
                    "venue",
                    "url",
                    "sourceType",
                    "summary",
                )
            )
            assert ref["sourceType"] in SOURCE_TYPES
            assert ref["url"].startswith("https://")
            assert len(ref["summary"]) >= 20
            assert any("\u3400" <= char <= "\u9fff" for char in ref["summary"])
            assert isinstance(ref["supports"], list) and ref["supports"]
            assert all(
                isinstance(claim_id, str) and claim_id.strip()
                for claim_id in ref["supports"]
            )
            reference_ids.append(ref["referenceId"])
        assert len(reference_ids) == len(set(reference_ids))


def test_all_registered_citations_are_migrated():
    rows = load_scientific_evidence()
    assert sum(len(row["references"]) for row in rows) >= 74
    assert all(row["references"] for row in rows)


def test_core_claim_categories_are_present():
    for row in load_scientific_evidence():
        assert CLAIM_CATEGORIES <= {c["category"] for c in row["claims"]}


def test_each_algorithm_maps_all_required_review_targets():
    for row in load_scientific_evidence():
        targets = {target for claim in row["claims"] for target in claim["targets"]}
        assert targets == REQUIRED_TARGETS


def test_claim_reference_links_are_closed():
    for row in load_scientific_evidence():
        refs = {r["referenceId"]: r for r in row["references"]}
        claims = {c["claimId"]: c for c in row["claims"]}
        for claim in row["claims"]:
            for rid in claim["referenceIds"]:
                assert rid in refs
                assert claim["claimId"] in refs[rid]["supports"]
        for ref in row["references"]:
            for claim_id in ref["supports"]:
                assert claim_id in claims
                assert ref["referenceId"] in claims[claim_id]["referenceIds"]


def test_formula_claim_has_primary_or_official_evidence():
    forbidden_only = {"secondary-index", "aggregator", "search-result"}
    for row in load_scientific_evidence():
        refs = {r["referenceId"]: r for r in row["references"]}
        for claim in row["claims"]:
            if claim["category"] != "formula" or claim["status"] == "implementation-only":
                continue
            assert any(
                refs[r]["sourceType"] not in forbidden_only
                for r in claim["referenceIds"]
            )


def test_algorithms_01_to_11_have_final_reviewed_claims_and_grades():
    expected_grades = {
        "01_flight_planning": "B",
        "02_sync_timestamp": "C",
        "03_pos_solution": "B",
        "04_flight_qc": "B",
        "05_cloud_shadow": "C",
        "06_dark_current": "B",
        "07_bad_pixel": "C",
        "08_destriping": "B",
        "09_smile_keystone": "B",
        "10_radiance_calibration": "A",
        "11_relative_radiometric": "B",
    }
    skeleton_phrases = (
        "以当前服务实现为准",
        "输入契约以服务参数和测试数据为准",
        "输出契约以服务响应为准",
        "尚未完成逐项科学证据审查",
        "等待后续任务补强",
    )
    reviewed = {
        row["algorithmId"]: row
        for row in load_scientific_evidence()
        if row["algorithmId"] in REVIEWED_IDS
    }
    assert {algorithm_id: row["grade"] for algorithm_id, row in reviewed.items()} == expected_grades
    for row in reviewed.values():
        claim_text = " ".join(
            f"{claim['text']} {claim['reviewNote']}" for claim in row["claims"]
        )
        assert not any(phrase in claim_text for phrase in skeleton_phrases)


def test_algorithms_12_to_26_have_final_reviewed_claims_and_grades():
    expected_grades = {
        "12_panel_reflectance": "B",
        "13_atmospheric_correction": "B",
        "14_brdf_correction": "B",
        "15_geo_locate": "C",
        "16_orthorectify": "C",
        "17_mosaic": "B",
        "18_color_balance": "B",
        "19_multi_source_register": "B",
        "20_bad_band_remove": "C",
        "21_savgol_smooth": "A",
        "22_normalize": "B",
        "23_pca": "B",
        "24_band_select": "B",
        "25_superpixel": "C",
        "26_patch_build": "C",
    }
    rows = {
        row["algorithmId"]: row
        for row in load_scientific_evidence()
        if 12 <= int(row["algorithmId"][:2]) <= 26
    }
    assert {algorithm_id: row["grade"] for algorithm_id, row in rows.items()} == expected_grades
    skeleton_phrases = (
        "计算规则以当前服务实现为准",
        "输入契约以服务参数和测试数据为准",
        "输出契约以服务响应为准",
        "尚未完成逐项科学证据审查",
        "等待后续任务补强",
    )
    for row in rows.values():
        text = " ".join(
            f"{item['text']} {item['reviewNote']}" for item in row["claims"]
        )
        assert not any(phrase in text for phrase in skeleton_phrases)


def test_algorithms_27_to_45_have_final_reviewed_claims_and_grades():
    expected_grades = {
        "27_ndvi": "A",
        "28_ndre": "C",
        "29_evi_savi": "A",
        "30_ndmi_ndwi": "A",
        "31_red_edge_params": "B",
        "32_regression_inversion": "A",
        "33_physical_inversion": "A",
        "34_svm_rf_classify": "A",
        "35_spectral_matching": "B",
        "36_cnn1d_classify": "B",
        "37_cnn3d_classify": "B",
        "38_transformer_classify": "B",
        "39_few_shot_classify": "C",
        "40_detect_segment": "C",
        "41_unmixing": "A",
        "42_anomaly_detect": "A",
        "43_change_detect": "B",
        "44_postprocess_smooth": "B",
        "45_parcel_zonal_stats": "B",
        "46_reci": "A",
        "47_gndvi": "A",
        "48_osavi": "A",
        "49_arvi": "A",
        "50_vari": "A",
        "51_lai_index": "C",
        "52_nbr": "A",
        "53_sipi": "B",
        "54_gci": "A",
        "55_ndsi": "A",
    }
    rows = {
        row["algorithmId"]: row
        for row in load_scientific_evidence()
        if 27 <= int(row["algorithmId"][:2]) <= 55
    }
    assert {algorithm_id: row["grade"] for algorithm_id, row in rows.items()} == expected_grades
    skeleton_phrases = (
        "计算规则以当前服务实现为准",
        "输入契约以服务参数和测试数据为准",
        "输出契约以服务响应为准",
        "尚未完成逐项科学证据审查",
        "等待后续任务补强",
    )
    for row in rows.values():
        text = " ".join(
            f"{item['text']} {item['reviewNote']}" for item in row["claims"]
        )
        assert not any(phrase in text for phrase in skeleton_phrases)


def test_algorithms_28_and_40_keep_unsupported_parts_qualified():
    rows = {row["algorithmId"]: row for row in load_scientific_evidence()}
    ndre_formula = next(
        claim for claim in rows["28_ndre"]["claims"] if claim["claimId"] == "formula"
    )
    assert ndre_formula["status"] == "qualified"
    assert "首创" not in ndre_formula["text"] + ndre_formula["reviewNote"]
    ace_seed = next(
        claim
        for claim in rows["40_detect_segment"]["claims"]
        if claim["claimId"] == "seed-strategy"
    )
    assert ace_seed["status"] == "implementation-only"
    assert ace_seed["referenceIds"] == []
    ace_formula = next(
        claim for claim in rows["40_detect_segment"]["claims"] if claim["claimId"] == "formula"
    )
    assert ace_formula["referenceIds"] == ["40_detect_segment-ref-01"]
    assert rows["40_detect_segment"]["references"][0]["url"].lower().endswith(
        "10.1109/acssc.1996.599116"
    )


def test_red_edge_params_has_domestic_existence_evidence():
    """国内题录只证明方法存在，不得挂到 Guyot 公式主张上。"""
    row = get_algorithm_evidence("31_red_edge_params")
    assert row is not None
    existence = next(claim for claim in row["claims"] if claim["claimId"] == "existence")
    formula = next(claim for claim in row["claims"] if claim["claimId"] == "formula")
    assert existence["status"] == "qualified"
    assert existence["category"] == "definition"
    assert "不是仓库自造" in existence["text"]
    expected = {
        "https://doi.org/10.3724/sp.j.1006.2009.01681",
        "https://doi.org/10.1080/01431160310001654365",
        "https://doi.org/10.1360/zf2011-41-suppl-213",
    }
    urls = {ref["url"] for ref in row["references"]}
    assert expected <= urls
    assert set(existence["referenceIds"]) == {
        "31_red_edge_params-ref-03",
        "31_red_edge_params-ref-04",
        "31_red_edge_params-ref-05",
    }
    for reference_id in existence["referenceIds"]:
        ref = next(item for item in row["references"] if item["referenceId"] == reference_id)
        assert ref["sourceType"] == "primary-paper"
        assert ref["supports"] == ["existence"]
        assert reference_id not in formula["referenceIds"]
        assert "formula" not in ref["supports"]
    guyot = next(item for item in row["references"] if item["referenceId"] == "31_red_edge_params-ref-01")
    assert "Guyot" in guyot["authors"]
    assert "formula" in guyot["supports"]


def test_all_algorithms_keep_foreign_refs_and_add_domestic_existence():
    """国内文献只追加；国外公式出处必须保留。"""
    for row in load_scientific_evidence():
        existence = next((c for c in row["claims"] if c["claimId"] == "existence"), None)
        assert existence is not None, row["algorithmId"]
        assert existence["status"] == "qualified"
        assert existence["referenceIds"]
        formula = next(c for c in row["claims"] if c["claimId"] == "formula")
        for rid in existence["referenceIds"]:
            ref = next(item for item in row["references"] if item["referenceId"] == rid)
            if rid not in formula["referenceIds"]:
                assert "formula" not in ref["supports"], row["algorithmId"]
    first = get_algorithm_evidence("01_flight_planning")
    urls = {ref["url"] for ref in first["references"]}
    assert "https://doi.org/10.1016/j.isprsjprs.2014.02.013" in urls
    assert "https://doi.org/10.1109/tgrs.2013.2280134" in urls
    ndvi = get_algorithm_evidence("27_ndvi")
    assert any("Piao" in ref["authors"] for ref in ndvi["references"])
    assert any("Rouse" in ref["authors"] for ref in ndvi["references"])


def test_task4_source_panel_matches_qualified_evidence_boundaries():
    source_panel = (ALGORITHM_ROOT / "web/src/sources.ts").read_text(encoding="utf-8")
    assert "原文未直接复核" in source_panel
    assert "公式保持 qualified" in source_panel
    assert "公式与 Barnes 等 2000 及 Index Database 著录一致" not in source_panel
    assert "Scharf L. L., McWhorter L. T." in source_panel
    assert "10.1109/ACSSC.1996.599116" in source_panel
    assert "Adaptive matched subspace detectors and adaptive coherence estimators" in source_panel
    assert "低 NDVI 种子策略" in source_panel
    assert "implementation-only" in source_panel
    assert "代码注释写「Guyot & Baret 1991」" not in source_panel
    assert "Guyot & Baret 1988" in source_panel


def test_parcel_specific_behaviors_are_implementation_only():
    row = next(
        row
        for row in load_scientific_evidence()
        if row["algorithmId"] == "45_parcel_zonal_stats"
    )
    formula = next(c for c in row["claims"] if c["claimId"] == "formula")
    output = next(c for c in row["claims"] if c["claimId"] == "output")
    limitation = next(c for c in row["claims"] if c["claimId"] == "limitation")
    for claim in (formula, output, limitation):
        assert claim["status"] == "implementation-only"
        assert claim["referenceIds"] == []
    reference = row["references"][0]
    assert reference["year"] == "n.d."
    assert reference["supports"] == ["definition"]
    assert "方法背景" in reference["summary"]
    assert "NoData" not in reference["summary"]


def test_shared_isprs_mosaic_reference_has_verified_metadata():
    rows = {
        row["algorithmId"]: row for row in load_scientific_evidence()
    }
    expected = {
        "authors": "Kang Y., Pan L., Chen Q., Zhang T., Zhang S., Liu Z.",
        "title": "AUTOMATIC MOSAICKING OF SATELLITE IMAGERY CONSIDERING THE CLOUDS",
        "venue": (
            "ISPRS Annals of the Photogrammetry, Remote Sensing and "
            "Spatial Information Sciences, III-3, 415–421"
        ),
        "url": "https://isprs-annals.copernicus.org/articles/III-3/415/2016/",
    }
    for algorithm_id, reference_id in (
        ("17_mosaic", "17_mosaic-ref-02"),
        ("18_color_balance", "18_color_balance-ref-02"),
    ):
        ref = next(
            ref
            for ref in rows[algorithm_id]["references"]
            if ref["referenceId"] == reference_id
        )
        assert {key: ref[key] for key in expected} == expected


def test_algorithms_01_to_11_keep_repository_defaults_implementation_only():
    expected_implementation_claims = {
        "02_sync_timestamp": ("formula", "中位数钟差"),
        "03_pos_solution": ("formula", "互补滤波"),
        "04_flight_qc": ("formula", "本仓库工程默认"),
        "05_cloud_shadow": ("formula", "whiteness < 0.7"),
        "06_dark_current": ("formula", "逐波段最小值"),
        "07_bad_pixel": ("formula", "6σ/4σ"),
        "10_radiance_calibration": ("input", "默认 gain=0.01、offset=0"),
    }
    reviewed = {
        row["algorithmId"]: row for row in load_scientific_evidence()
    }
    for algorithm_id, (claim_id, expected_text) in expected_implementation_claims.items():
        claim = next(
            claim
            for claim in reviewed[algorithm_id]["claims"]
            if claim["claimId"] == claim_id
        )
        assert claim["status"] == "implementation-only"
        assert claim["referenceIds"] == []
        assert expected_text in claim["text"]


def test_relative_radiometric_repository_crop_behavior_has_no_external_reference():
    """防止官方直方图文档被用于背书仓库特有的左上角裁切边界。"""
    row = next(
        row
        for row in load_scientific_evidence()
        if row["algorithmId"] == "11_relative_radiometric"
    )
    formula = next(claim for claim in row["claims"] if claim["claimId"] == "formula")
    repository_phrases = (
        "左上角共同尺寸",
        "超出共同尺寸部分保持原值",
        "其余区域保持原值",
        "超出参考尺寸的部分不变",
    )

    assert formula["status"] == "verified"
    assert formula["referenceIds"] == ["11_relative_radiometric-ref-01"]
    assert not any(phrase in formula["text"] for phrase in repository_phrases)

    specialized_claims = [
        claim
        for claim in row["claims"]
        if any(phrase in claim["text"] for phrase in repository_phrases)
    ]
    assert specialized_claims
    for claim in specialized_claims:
        assert claim["status"] == "implementation-only"
        assert claim["referenceIds"] == []


def test_reviewed_titles_match_narrowed_catalog_scope():
    rows = {
        row["algorithmId"]: row for row in load_scientific_evidence()
    }
    assert rows["03_pos_solution"]["title"] == "POS轨迹平滑与杠杆臂校正"
    assert rows["04_flight_qc"]["title"] == "架次过曝与场景统计质检"
    assert rows["15_geo_locate"]["title"] == "POS中心点与GSD粗定位"
    assert rows["18_color_balance"]["title"] == "Wallis局部匀色"
    assert rows["19_multi_source_register"]["title"] == "HSI-RGB全局平移配准"


def test_source_panel_keeps_engineering_defaults_and_verified_metadata_distinct():
    source_panel = (ALGORITHM_ROOT / "web/src/sources.ts").read_text(encoding="utf-8")
    for expected in (
        "中位数钟差是本仓库工程默认",
        "6σ/4σ 与邻域均值填充是本仓库工程默认",
        "默认 gain=0.01、offset=0 是本仓库工程默认",
        "Gadallah F. L., Csillag F., Smith E. J. M.",
        "EMVA Standard 1288 — Release 4.0 General",
    ):
        assert expected in source_panel


def test_loader_and_lookup_return_deep_copies():
    rows = load_scientific_evidence()
    row = get_algorithm_evidence(rows[0]["algorithmId"])
    assert row is not None
    row["claims"][0]["text"] = "mutated"
    assert get_algorithm_evidence(rows[0]["algorithmId"])["claims"][0]["text"] != "mutated"


def test_unknown_algorithm_returns_none():
    assert get_algorithm_evidence("not_registered") is None


def test_every_algorithm_has_a_formula_takeaway():
    """原理页「一句话理解」须覆盖全部 55 项。"""
    text = (ALGORITHM_ROOT / "web/src/principles/formulaTakeaways.ts").read_text(
        encoding="utf-8"
    )
    missing = [aid for aid in ALL_ALGORITHM_IDS if f'"{aid}":' not in text]
    assert missing == []
    assert len(re.findall(r'^  "[0-9]{2}_[a-z0-9_]+":', text, re.M)) == 55


def test_every_algorithm_has_a_formula_process_diagram():
    """原理页「处理过程」须覆盖全部 55 项，避免只给个别算法画图。"""
    text = (ALGORITHM_ROOT / "web/src/principles/formulaProcesses.ts").read_text(
        encoding="utf-8"
    )
    missing = [aid for aid in ALL_ALGORITHM_IDS if f'"{aid}":' not in text]
    assert missing == []
    assert len(re.findall(r'^  "[0-9]{2}_[a-z0-9_]+": flow\(', text, re.M)) == 55
    assert 'kind: "process"' in text


def test_product_analysis_has_no_unsupported_marketing_or_absolute_copy():
    """产品适配只陈述工程条件，不把算法效果或商业价值写成结论。"""
    wayho_root = ALGORITHM_ROOT / "web/src/wayho"
    text = "\n".join(
        (wayho_root / name).read_text(encoding="utf-8")
        for name in ("l0.ts", "l2.ts", "l3.ts")
    )
    forbidden = (
        "最稳",
        "精确取",
        "独家",
        "高客单价",
        "竞争优势",
        "标准实现",
        "实验室定标完成",
        "最好卖",
        "技术壁垒",
        "商业价值",
        "高端包",
        "招牌指数",
    )
    assert not [phrase for phrase in forbidden if phrase in text]


def test_unverified_wayho_models_do_not_keep_concrete_numeric_specs():
    """未打开对应型号官方页时，不保留会被误读为已核验的具体规格。"""
    wayho_root = ALGORITHM_ROOT / "web/src/wayho"
    text = "\n".join(
        (wayho_root / name).read_text(encoding="utf-8")
        for name in ("l0.ts", "l2.ts", "l3.ts")
    )
    unsupported_specs = (
        "SHIS-V220 只到 750 nm",
        "SHIS-S260、VIX-S230 纯 SWIR",
        "SHIS-S260、VIX-S230",
        "VIX-N320/S230/W330",
        "SVC 有 720 nm",
        "SVC 更少",
        "5 个分立波段",
        "5 通道不能解混",
        "单点 720 nm",
        "MAX-S800",
        "视频长势，边缘已算",
        "边缘已有林木等模型",
        "漏油",
    )
    assert not [claim for claim in unsupported_specs if claim in text]


def test_max_s810_is_not_called_hyperspectral_in_product_or_ai_copy():
    """官方多光谱型号不得与「高光谱」写在同一句。"""
    files = [
        ALGORITHM_ROOT / "web/src/wayho/l0.ts",
        ALGORITHM_ROOT / "web/src/wayho/l2.ts",
        ALGORITHM_ROOT / "web/src/wayho/l3.ts",
        ALGORITHM_ROOT / "source/common/l3_aide/layers.py",
    ]
    leaked = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for sentence in re.split(r"[。！？\n]", text):
            if "MAX-S810" in sentence and "高光谱" in sentence:
                leaked.append(f"{path.name}: {sentence.strip()}")
    assert not leaked


def test_wayho_copy_drops_marketing_tone_and_fixed_agronomy():
    """产品分析去掉营销口吻，也不绑定固定农艺场景。"""
    wayho_root = ALGORITHM_ROOT / "web/src/wayho"
    l0 = (wayho_root / "l0.ts").read_text(encoding="utf-8")
    l3 = (wayho_root / "l3.ts").read_text(encoding="utf-8")
    assert "卖点" not in l0
    assert "MAX-S800" not in l0
    for phrase in ("更准", "方案升级话术", "差异化", "密植作物氮素"):
        assert phrase not in l3, phrase


def _parse_inventory_details(text: str) -> dict[int, dict[str, str]]:
    pattern = re.compile(
        r"####\s+(\d+)\.\s+(.+?)\n.*?"
        r"\|\s*\*\*作用\*\*\s*\|\s*(.+?)\s*\|\n"
        r"\|\s*\*\*使用场景\*\*\s*\|\s*(.+?)\s*\|\n"
        r"\|\s*\*\*数据输入\*\*\s*\|\s*(.+?)\s*\|\n"
        r"\|\s*\*\*数据输出\*\*\s*\|\s*(.+?)\s*\|\n"
        r"\|\s*\*\*方法边界\*\*\s*\|\s*(.+?)\s*\|",
        re.S,
    )
    return {
        int(match.group(1)): {
            "title": match.group(2).strip().replace("**", ""),
            "role": match.group(3).strip().replace("**", ""),
            "scene": match.group(4).strip().replace("**", ""),
            "input": match.group(5).strip().replace("**", ""),
            "output": match.group(6).strip().replace("**", ""),
            "boundary": match.group(7).strip().replace("**", ""),
        }
        for match in pattern.finditer(text)
    }


def _parse_api_details(text: str) -> dict[int, dict[str, str]]:
    pattern = re.compile(
        r"###\s+(\d+)\.\s+(.+?)\n.*?"
        r"\| \*\*作用\*\* \| (.+?) \|\n"
        r"\| \*\*使用场景\*\* \| (.+?) \|\n"
        r"\| \*\*数据输入\*\* \| (.+?) \|\n"
        r"\| \*\*数据输出\*\* \| (.+?) \|\n"
        r"\| \*\*方法边界\*\* \| (.+?) \|",
        re.S,
    )
    return {
        int(match.group(1)): {
            "title": match.group(2).strip(),
            "role": match.group(3).strip(),
            "scene": match.group(4).strip(),
            "input": match.group(5).strip(),
            "output": match.group(6).strip(),
            "boundary": match.group(7).strip(),
        }
        for match in pattern.finditer(text)
    }


def test_both_checklists_match_catalog_evidence_and_each_other():
    docs = ALGORITHM_ROOT / "docs"
    inventory = _parse_inventory_details(
        (docs / "采集到算法-算法清单.md").read_text(encoding="utf-8")
    )
    api = _parse_api_details(
        (docs / "算法API测试清单.md").read_text(encoding="utf-8")
    )
    expected_titles = {
        int(row["algorithmId"][:2]): row["title"]
        for row in load_scientific_evidence()
    }
    catalog_titles = {int(row["id"][:2]): row["title"] for row in ALGORITHMS}
    assert len(inventory) == len(api) == 55
    assert expected_titles == catalog_titles
    assert {number: row["title"] for number, row in inventory.items()} == catalog_titles
    assert api == inventory


CHECKLIST_REVIEW_LEAKS = ("C 级", "保持 C", "证据等级")


def _load_sync_module():
    path = ALGORITHM_ROOT / "docs" / "sync_api_test_checklist.py"
    spec = importlib.util.spec_from_file_location("sync_api_test_checklist", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checklists_do_not_leak_internal_review_grade_language():
    """对外清单只陈述方法边界，不带内部证据等级用语。"""
    docs = ALGORITHM_ROOT / "docs"
    for name in ("采集到算法-算法清单.md", "算法API测试清单.md"):
        text = (docs / name).read_text(encoding="utf-8")
        leaked = [phrase for phrase in CHECKLIST_REVIEW_LEAKS if phrase in text]
        assert not leaked, name


def test_limitation_copy_strips_review_grade_language():
    """拷贝 limitation 时必须去掉证据等级/内部评审用语。"""
    module = _load_sync_module()
    assert hasattr(module, "sanitize_limitation_for_docs")
    samples = (
        "当前实现没有空三/GCP、畸变模型、遮挡处理和真实地图格网，故保持 C 级。",
        "HITRAN 谱线库不能为固定宽窗口、场景 μ/σ 阈值或坏波段结论直接背书，故保持 C 级。",
        "方法可用，证据等级为合格。",
        "因此保持 C，不扩展范围。",
    )
    for sample in samples:
        cleaned = module.sanitize_limitation_for_docs(sample)
        leaked = [phrase for phrase in CHECKLIST_REVIEW_LEAKS if phrase in cleaned]
        assert not leaked, sample
        assert cleaned.strip()


def test_checklist_generation_is_clock_independent(tmp_path, monkeypatch):
    """连续两次生成哈希必须相同，且不得依赖同一分钟碰巧相同。"""
    module = _load_sync_module()
    assert hasattr(module, "generate_checklists")
    source = ALGORITHM_ROOT / "docs" / "采集到算法-算法清单.md"
    seed = source.read_text(encoding="utf-8")
    hashes = []
    for fake_now in (
        datetime(2024, 1, 1, 0, 1),
        datetime(2026, 9, 4, 18, 47),
    ):

        class FakeDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return fake_now

        monkeypatch.setattr(module, "datetime", FakeDateTime, raising=False)
        list_path = tmp_path / f"inventory-{fake_now.timestamp()}.md"
        out_path = tmp_path / f"api-{fake_now.timestamp()}.md"
        list_path.write_text(seed, encoding="utf-8")
        inventory, api = module.generate_checklists(
            list_path=list_path,
            out_path=out_path,
        )
        assert not re.search(r"同步生成于 \d{4}-\d{2}-\d{2} \d{2}:\d{2}", api)
        hashes.append(
            hashlib.sha256((inventory + "\n" + api).encode("utf-8")).hexdigest()
        )
    assert hashes[0] == hashes[1]
    assert hashes[0]


def test_sync_script_example_is_not_prescription():
    """示例说明不得写成处方或作业指令。"""
    text = (ALGORITHM_ROOT / "docs" / "sync_api_test_checklist.py").read_text(
        encoding="utf-8"
    )
    assert "精准喷药" not in text


CHECKLIST_UNIMPLEMENTED_DELIVERED = {
    3: re.compile(r"IMU\s*角速度|IMU\s*加速度|角速度/加速度|组合导航"),
    4: re.compile(r"坏帧列表|曝光增益日志|丢帧"),
    40: re.compile(r"检测框|语义分割|shp|框/掩膜"),
}
CHECKLIST_REQUIRED_DELIVERED = {
    3: (("input", "POS CSV"), ("role", "平滑"), ("role", "杠杆臂")),
    4: (("output", "过曝"), ("output", "欠曝"), ("output", "场景")),
    40: (("output", "ACE"), ("output", "候选掩膜"), ("output", "GeoJSON")),
}
_UNIMPLEMENTED_SENTENCE = re.compile(
    r"未实现|不读取|不搜索|不执行|不处理|不检测|不接受|不是|当前不|也不"
)


def _checklist_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[。；;！？\n]", text) if part.strip()]


def test_checklists_03_04_40_io_do_not_claim_unimplemented_capabilities():
    """两份清单 #03/#04/#40 的作用/输入/输出不得把未实现能力写成已交付。"""
    docs = ALGORITHM_ROOT / "docs"
    parsers = (
        ("采集到算法-算法清单.md", _parse_inventory_details),
        ("算法API测试清单.md", _parse_api_details),
    )
    for name, parser in parsers:
        details = parser((docs / name).read_text(encoding="utf-8"))
        for number, pattern in CHECKLIST_UNIMPLEMENTED_DELIVERED.items():
            row = details[number]
            delivered = {
                "role": row["role"],
                "input": row["input"],
                "output": row["output"],
            }
            for field, text in delivered.items():
                hits = pattern.findall(text)
                assert not hits, f"{name} #{number:02d} {field} 把未实现能力写成已交付: {hits} / {text}"
            for field, needle in CHECKLIST_REQUIRED_DELIVERED[number]:
                assert needle in delivered[field], (
                    f"{name} #{number:02d} {field} 缺少已实现口径 {needle!r}: {delivered[field]}"
                )
            for sentence in _checklist_sentences(row["boundary"]):
                if _UNIMPLEMENTED_SENTENCE.search(sentence):
                    continue
                hits = pattern.findall(sentence)
                assert not hits, (
                    f"{name} #{number:02d} 方法边界把未实现能力写成已交付: {hits} / {sentence}"
                )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: row["claims"][0].__setitem__("status", "typo"),
        lambda row: row["references"][0].pop("authors"),
        lambda row: row["references"][0].__setitem__("sourceType", "blog"),
    ],
)
def test_loader_fails_closed_for_invalid_schema(tmp_path, monkeypatch, mutation):
    rows = load_scientific_evidence()
    mutation(rows[0])
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(scientific_evidence, "EVIDENCE_PATH", invalid_path)

    with pytest.raises((TypeError, ValueError)):
        scientific_evidence.load_scientific_evidence()
