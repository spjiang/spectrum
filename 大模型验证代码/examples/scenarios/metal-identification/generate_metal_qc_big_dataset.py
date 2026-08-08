#!/usr/bin/env python3
"""
金属质检大规模合成数据生成器 → 千问 SFT 训练集（JSONL）

基于 qc_standards.json 中的合格阈值，按物理规律合成黄金/白银光谱特征，
自动生成合格、待复检、不合格三类样本，并输出 LLaMA-Factory 可直接使用的 JSONL。

用法:
    python examples/scenarios/metal-identification/generate_metal_qc_big_dataset.py

    python examples/scenarios/metal-identification/generate_metal_qc_big_dataset.py \
        --num-samples 1000 \
        --seed 42
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

# 复用已有 JSONL 构建逻辑
from prepare_metal_qc_dataset import (
    build_record,
    load_standards,
)

# 13 个关键波段（与 metal_sample_spectrum.json 一致）
WAVELENGTHS_NM = [400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]

# 各材质典型反射率曲线模板（归一化形状，后续加噪声）
MATERIAL_PROFILES: dict[str, list[float]] = {
    "gold": [0.38, 0.42, 0.55, 0.72, 0.83, 0.88, 0.91, 0.92, 0.93, 0.93, 0.94, 0.94, 0.94],
    "silver": [0.88, 0.90, 0.91, 0.92, 0.93, 0.93, 0.94, 0.94, 0.94, 0.94, 0.95, 0.95, 0.95],
    "copper_like": [0.32, 0.36, 0.48, 0.61, 0.72, 0.80, 0.85, 0.87, 0.88, 0.89, 0.90, 0.90, 0.90],
    "aluminum_like": [0.75, 0.78, 0.80, 0.82, 0.84, 0.85, 0.86, 0.87, 0.88, 0.88, 0.89, 0.89, 0.90],
    "oxidized_metal": [0.22, 0.24, 0.28, 0.31, 0.33, 0.35, 0.36, 0.37, 0.38, 0.39, 0.40, 0.41, 0.42],
    "contaminated_metal": [0.45, 0.48, 0.52, 0.55, 0.58, 0.60, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68],
    "plating_risk": [0.55, 0.58, 0.65, 0.72, 0.78, 0.82, 0.85, 0.86, 0.87, 0.88, 0.89, 0.89, 0.90],
}

SURFACE_STATES = {
    "polished": "polished",
    "brushed": "brushed",
    "oxidized": "oxidized",
    "contaminated": "contaminated",
    "tarnished": "tarnished",
}

DETECTED_MATERIAL_CN = {
    "gold": "黄金",
    "silver": "白银",
    "copper_like": "疑似铜色金属",
    "aluminum_like": "疑似铝色金属",
    "silver_abnormal": "白银表面异常",
    "gold_abnormal": "黄金表面异常",
    "plating_suspect": "疑似镀层",
}


def add_noise(profile: list[float], scale: float, rng: random.Random) -> list[float]:
    """在曲线模板上叠加高斯噪声，并裁剪到 [0.05, 0.99]。"""
    noisy = []
    for v in profile:
        delta = rng.gauss(0, scale)
        noisy.append(round(max(0.05, min(0.99, v + delta)), 4))
    return noisy


def scale_profile(profile: list[float], factor: float) -> list[float]:
    """整体缩放反射率，模拟亮度/氧化程度差异。"""
    return [round(max(0.05, min(0.99, v * factor)), 4) for v in profile]


def extract_features(reflectance: list[float]) -> dict[str, float]:
    """从 13 波段反射率提取质检特征。"""
    blue_450 = reflectance[1]
    green_550 = reflectance[3]
    red_650 = reflectance[5]
    nir_850 = reflectance[9]
    slope = (red_650 - blue_450) / 200  # 450-650nm 跨度 200nm
    red_blue_ratio = round(red_650 / max(blue_450, 0.01), 2)
    nir_mean = round(sum(reflectance[8:13]) / 5, 4)  # 800-1000nm 共 5 点
    return {
        "blue_450": blue_450,
        "green_550": green_550,
        "red_650": red_650,
        "nir_850": nir_850,
        "slope_450_650": round(slope, 6),
        "red_blue_ratio": red_blue_ratio,
        "nir_mean_800_1000": nir_mean,
    }


def in_ratio_range(ratio: float, material: str, standards: dict) -> bool:
    rule = standards[material]
    return rule["red_blue_ratio_min"] <= ratio <= rule["red_blue_ratio_max"]


def nir_passes(nir_mean: float, material: str, standards: dict) -> bool:
    return nir_mean >= standards[material]["nir_mean_min"]


def assign_grade(qc_result: str, features: dict, material: str, standards: dict) -> str:
    """根据偏离标准程度分配 A/B/C 等级。"""
    if qc_result != "pass":
        return "C"
    rule = standards[material]
    ratio_mid = (rule["red_blue_ratio_min"] + rule["red_blue_ratio_max"]) / 2
    ratio_span = rule["red_blue_ratio_max"] - rule["red_blue_ratio_min"]
    ratio_dev = abs(features["red_blue_ratio"] - ratio_mid) / max(ratio_span, 0.01)
    nir_margin = features["nir_mean_800_1000"] - rule["nir_mean_min"]
    if ratio_dev < 0.15 and nir_margin > 0.02:
        return "A"
    return "B"


def build_pass_gold(idx: int, standards: dict, rng: random.Random) -> dict:
    """合格黄金样本。"""
    reflectance = add_noise(MATERIAL_PROFILES["gold"], 0.015, rng)
    features = extract_features(reflectance)
    # 确保落在合格区间
    if not in_ratio_range(features["red_blue_ratio"], "gold", standards):
        reflectance[5] = round(reflectance[1] * rng.uniform(2.0, 2.2), 4)
        features = extract_features(reflectance)
    surface = rng.choice(["polished", "brushed"])
    grade = assign_grade("pass", features, "gold", standards)
    return _make_sample(
        sample_id=f"qc_gold_pass_{idx:04d}",
        material_hint="标称黄金饰品，产线质检 ROI",
        reflectance=reflectance,
        features=features,
        expected="gold",
        detected="gold",
        qc_result="pass",
        grade=grade,
        defect="none",
        disposition="release",
        surface_state=surface,
    )


def build_pass_silver(idx: int, standards: dict, rng: random.Random) -> dict:
    """合格白银样本。"""
    reflectance = add_noise(MATERIAL_PROFILES["silver"], 0.012, rng)
    features = extract_features(reflectance)
    surface = rng.choice(["polished", "brushed"])
    grade = assign_grade("pass", features, "silver", standards)
    return _make_sample(
        sample_id=f"qc_silver_pass_{idx:04d}",
        material_hint="标称白银饰品，产线质检 ROI",
        reflectance=reflectance,
        features=features,
        expected="silver",
        detected="silver",
        qc_result="pass",
        grade=grade,
        defect="none",
        disposition="release",
        surface_state=surface,
    )


def build_recheck_gold_copper(idx: int, rng: random.Random) -> dict:
    """标称黄金但光谱疑似铜色替代 → 待复检。"""
    reflectance = add_noise(MATERIAL_PROFILES["copper_like"], 0.02, rng)
    features = extract_features(reflectance)
    return _make_sample(
        sample_id=f"qc_gold_recheck_copper_{idx:04d}",
        material_hint="标称黄金，光谱疑似铜色替代",
        reflectance=reflectance,
        features=features,
        expected="gold",
        detected="copper_like",
        qc_result="recheck",
        grade="C",
        defect="material_mismatch",
        disposition="recheck",
        surface_state="polished",
    )


def build_recheck_gold_borderline(idx: int, standards: dict, rng: random.Random) -> dict:
    """标称黄金，近红外略低于阈值 → 待复检。"""
    reflectance = add_noise(MATERIAL_PROFILES["gold"], 0.02, rng)
    reflectance = scale_profile(reflectance, rng.uniform(0.94, 0.98))
    features = extract_features(reflectance)
    # 强制近红外落在边界
    if features["nir_mean_800_1000"] >= standards["gold"]["nir_mean_min"]:
        reflectance[8:] = [round(v * 0.96, 4) for v in reflectance[8:]]
        features = extract_features(reflectance)
    return _make_sample(
        sample_id=f"qc_gold_recheck_nir_{idx:04d}",
        material_hint="标称黄金，近红外反射略低，边界样本",
        reflectance=reflectance,
        features=features,
        expected="gold",
        detected="gold",
        qc_result="recheck",
        grade="C",
        defect="none",
        disposition="recheck",
        surface_state=rng.choice(["polished", "brushed"]),
    )


def build_recheck_silver_borderline(idx: int, standards: dict, rng: random.Random) -> dict:
    """标称白银，红蓝比或近红外边界 → 待复检。"""
    reflectance = add_noise(MATERIAL_PROFILES["silver"], 0.025, rng)
    reflectance = scale_profile(reflectance, rng.uniform(0.96, 0.99))
    features = extract_features(reflectance)
    if features["nir_mean_800_1000"] >= standards["silver"]["nir_mean_min"]:
        reflectance[8:] = [round(v * 0.97, 4) for v in reflectance[8:]]
        features = extract_features(reflectance)
    return _make_sample(
        sample_id=f"qc_silver_recheck_{idx:04d}",
        material_hint="标称白银，光谱指标边界偏离",
        reflectance=reflectance,
        features=features,
        expected="silver",
        detected="silver",
        qc_result="recheck",
        grade="C",
        defect="none",
        disposition="recheck",
        surface_state="polished",
    )


def build_fail_silver_oxidized(idx: int, rng: random.Random) -> dict:
    """标称白银，表面氧化 → 不合格。"""
    reflectance = add_noise(MATERIAL_PROFILES["oxidized_metal"], 0.02, rng)
    features = extract_features(reflectance)
    return _make_sample(
        sample_id=f"qc_silver_fail_ox_{idx:04d}",
        material_hint="标称白银，表面氧化严重",
        reflectance=reflectance,
        features=features,
        expected="silver",
        detected="silver_abnormal",
        qc_result="fail",
        grade="C",
        defect="oxidation",
        disposition="reject",
        surface_state="oxidized",
    )


def build_fail_gold_oxidized(idx: int, rng: random.Random) -> dict:
    """标称黄金，氧化发黑 → 不合格。"""
    reflectance = add_noise(MATERIAL_PROFILES["oxidized_metal"], 0.025, rng)
    reflectance = scale_profile(reflectance, rng.uniform(0.85, 1.05))
    features = extract_features(reflectance)
    return _make_sample(
        sample_id=f"qc_gold_fail_ox_{idx:04d}",
        material_hint="标称黄金，表面氧化发黑",
        reflectance=reflectance,
        features=features,
        expected="gold",
        detected="gold_abnormal",
        qc_result="fail",
        grade="C",
        defect="oxidation",
        disposition="reject",
        surface_state="oxidized",
    )


def build_fail_contamination(idx: int, expected: str, rng: random.Random) -> dict:
    """标称贵金属，表面污染 → 不合格。"""
    reflectance = add_noise(MATERIAL_PROFILES["contaminated_metal"], 0.02, rng)
    features = extract_features(reflectance)
    detected = "gold_abnormal" if expected == "gold" else "silver_abnormal"
    return _make_sample(
        sample_id=f"qc_{expected}_fail_contam_{idx:04d}",
        material_hint=f"标称{'黄金' if expected == 'gold' else '白银'}，表面污染",
        reflectance=reflectance,
        features=features,
        expected=expected,
        detected=detected,
        qc_result="fail",
        grade="C",
        defect="contamination",
        disposition="quarantine",
        surface_state="contaminated",
    )


def build_fail_plating_risk(idx: int, expected: str, rng: random.Random) -> dict:
    """标称贵金属，疑似镀层 → 不合格/隔离。"""
    reflectance = add_noise(MATERIAL_PROFILES["plating_risk"], 0.02, rng)
    features = extract_features(reflectance)
    return _make_sample(
        sample_id=f"qc_{expected}_fail_plating_{idx:04d}",
        material_hint=f"标称{'黄金' if expected == 'gold' else '白银'}，疑似镀金/镀银",
        reflectance=reflectance,
        features=features,
        expected=expected,
        detected="plating_suspect",
        qc_result="fail",
        grade="C",
        defect="plating_risk",
        disposition="quarantine",
        surface_state="tarnished",
    )


def build_fail_material_mismatch(idx: int, expected: str, rng: random.Random) -> dict:
    """标称贵金属，实测为其他金属 → 不合格。"""
    actual_profile = rng.choice(["aluminum_like", "copper_like"])
    reflectance = add_noise(MATERIAL_PROFILES[actual_profile], 0.02, rng)
    features = extract_features(reflectance)
    return _make_sample(
        sample_id=f"qc_{expected}_fail_mismatch_{idx:04d}",
        material_hint=f"标称{'黄金' if expected == 'gold' else '白银'}，材质严重不符",
        reflectance=reflectance,
        features=features,
        expected=expected,
        detected=actual_profile,
        qc_result="fail",
        grade="C",
        defect="material_mismatch",
        disposition="reject",
        surface_state="polished",
    )


def _make_sample(
    *,
    sample_id: str,
    material_hint: str,
    reflectance: list[float],
    features: dict,
    expected: str,
    detected: str,
    qc_result: str,
    grade: str,
    defect: str,
    disposition: str,
    surface_state: str,
) -> dict:
    expected_cn = "黄金" if expected == "gold" else "白银"
    detected_cn = DETECTED_MATERIAL_CN.get(detected, detected)
    return {
        "sample_id": sample_id,
        "material_hint": material_hint,
        "reflectance": reflectance,
        "features": features,
        "metadata": {
            "camera": "VIS-NIR hyperspectral camera",
            "calibration": "white_reference_corrected",
            "illumination": "D65 simulated light source",
            "roi": "center_20x20_pixels",
            "surface_state": surface_state,
        },
        "label": {
            "expected_material": expected,
            "expected_material_cn": expected_cn,
            "detected_material": detected,
            "detected_material_cn": detected_cn,
            "qc_result": qc_result,
            "grade": grade,
            "defect": defect,
            "disposition": disposition,
            "label_source": "synthetic_rule_based",
        },
    }


# 各场景生成器及默认配比（合计 1.0）
SCENARIO_BUILDERS = [
    ("pass_gold", 0.22, lambda i, std, rng: build_pass_gold(i, std, rng)),
    ("pass_silver", 0.22, lambda i, std, rng: build_pass_silver(i, std, rng)),
    ("recheck_gold_copper", 0.08, lambda i, std, rng: build_recheck_gold_copper(i, rng)),
    ("recheck_gold_borderline", 0.06, lambda i, std, rng: build_recheck_gold_borderline(i, std, rng)),
    ("recheck_silver_borderline", 0.06, lambda i, std, rng: build_recheck_silver_borderline(i, std, rng)),
    ("fail_silver_oxidized", 0.08, lambda i, std, rng: build_fail_silver_oxidized(i, rng)),
    ("fail_gold_oxidized", 0.06, lambda i, std, rng: build_fail_gold_oxidized(i, rng)),
    ("fail_contamination", 0.08, lambda i, std, rng: build_fail_contamination(i, rng.choice(["gold", "silver"]), rng)),
    ("fail_plating_risk", 0.07, lambda i, std, rng: build_fail_plating_risk(i, rng.choice(["gold", "silver"]), rng)),
    ("fail_material_mismatch", 0.07, lambda i, std, rng: build_fail_material_mismatch(i, rng.choice(["gold", "silver"]), rng)),
]


def allocate_counts(num_samples: int) -> list[tuple[str, int]]:
    """按配比分配各场景样本数，余数补给合格样本。"""
    counts: list[tuple[str, int]] = []
    assigned = 0
    for name, ratio, _ in SCENARIO_BUILDERS[:-1]:
        n = int(num_samples * ratio)
        counts.append((name, n))
        assigned += n
    last_name = SCENARIO_BUILDERS[-1][0]
    counts.append((last_name, num_samples - assigned))
    return counts


def generate_samples(num_samples: int, standards: dict, seed: int) -> list[dict]:
    """生成指定数量的合成样本。"""
    rng = random.Random(seed)
    builder_map = {name: builder for name, _, builder in SCENARIO_BUILDERS}
    counters: dict[str, int] = {name: 0 for name, _, _ in SCENARIO_BUILDERS}
    samples: list[dict] = []

    for name, count in allocate_counts(num_samples):
        builder = builder_map[name]
        for _ in range(count):
            counters[name] += 1
            samples.append(builder(counters[name], standards, rng))

    rng.shuffle(samples)
    return samples


def write_spectrum_json(samples: list[dict], output_path: Path) -> None:
    payload = {
        "description": (
            f"金属高光谱质检合成数据集，共 {len(samples)} 条。"
            "覆盖合格、待复检、不合格及氧化/污染/镀层/材质不符等场景。"
        ),
        "wavelengths_nm": WAVELENGTHS_NM,
        "samples": samples,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_labels_csv(samples: list[dict], output_path: Path) -> None:
    fieldnames = [
        "sample_id", "expected_material", "expected_material_cn",
        "qc_result", "grade", "defect", "disposition",
        "surface_state", "red_blue_ratio", "nir_mean_800_1000", "notes",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in samples:
            label = s["label"]
            writer.writerow({
                "sample_id": s["sample_id"],
                "expected_material": label["expected_material"],
                "expected_material_cn": label["expected_material_cn"],
                "qc_result": label["qc_result"],
                "grade": label["grade"],
                "defect": label["defect"],
                "disposition": label["disposition"],
                "surface_state": s["metadata"]["surface_state"],
                "red_blue_ratio": s["features"]["red_blue_ratio"],
                "nir_mean_800_1000": s["features"]["nir_mean_800_1000"],
                "notes": s["material_hint"],
            })


def write_jsonl(samples: list[dict], standards: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for sample in samples:
            record = build_record(sample, standards)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def print_stats(samples: list[dict]) -> None:
    """打印数据集统计信息。"""
    from collections import Counter

    qc_counter = Counter(s["label"]["qc_result"] for s in samples)
    material_counter = Counter(s["label"]["expected_material"] for s in samples)
    defect_counter = Counter(s["label"]["defect"] for s in samples)

    print(f"总样本数：{len(samples)}")
    print(f"质检结论分布：{dict(qc_counter)}")
    print(f"标称材质分布：{dict(material_counter)}")
    print(f"缺陷类型分布：{dict(defect_counter)}")


def main() -> None:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="生成金属质检大规模千问 SFT 训练数据")
    parser.add_argument("--num-samples", type=int, default=800, help="合成样本总数（默认 800）")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument(
        "--standards",
        type=Path,
        default=base / "data" / "qc_standards.json",
    )
    parser.add_argument(
        "--spectrum-output",
        type=Path,
        default=base / "data" / "metal_sample_spectrum_full.json",
    )
    parser.add_argument(
        "--labels-output",
        type=Path,
        default=base / "data" / "labels_full.csv",
    )
    parser.add_argument(
        "--jsonl-output",
        type=Path,
        default=base / "training" / "metal_sft_train_full.jsonl",
    )
    args = parser.parse_args()

    standards = load_standards(args.standards)
    samples = generate_samples(args.num_samples, standards, args.seed)

    write_spectrum_json(samples, args.spectrum_output)
    write_labels_csv(samples, args.labels_output)
    write_jsonl(samples, standards, args.jsonl_output)

    print_stats(samples)
    print(f"\n已写入光谱数据 → {args.spectrum_output}")
    print(f"已写入标签表   → {args.labels_output}")
    print(f"已写入训练 JSONL → {args.jsonl_output}")


if __name__ == "__main__":
    main()
