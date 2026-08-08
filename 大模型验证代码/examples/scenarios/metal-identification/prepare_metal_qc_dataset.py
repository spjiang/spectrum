#!/usr/bin/env python3
"""
金属质检示例数据 → 千问 SFT 训练集（JSONL）

用法:
    python examples/scenarios/metal-identification/prepare_metal_qc_dataset.py

    python examples/scenarios/metal-identification/prepare_metal_qc_dataset.py \
        --input examples/scenarios/metal-identification/data/metal_sample_spectrum.json \
        --output examples/scenarios/metal-identification/training/metal_sft_train.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SYSTEM_PROMPT = (
    "你是一名高光谱金属质检专家，请根据反射率特征判断样品是否合格，并说明依据和处置建议。"
)

QC_RESULT_CN = {
    "pass": "合格",
    "fail": "不合格",
    "recheck": "待复检",
}

DISPOSITION_CN = {
    "release": "放行",
    "reject": "剔除",
    "recheck": "转人工复检",
    "quarantine": "隔离",
}

DEFECT_CN = {
    "none": "无",
    "oxidation": "氧化",
    "material_mismatch": "材质不符",
    "contamination": "污染",
    "plating_risk": "镀层风险",
}


def load_standards(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)["standards"]


def standard_template_text(expected_material: str, standards: dict) -> str:
    rule = standards[expected_material]
    return (
        f"红蓝比 {rule['red_blue_ratio_min']}-{rule['red_blue_ratio_max']}，"
        f"近红外均值 > {rule['nir_mean_min']}"
    )


def build_user_text(sample: dict, standards: dict) -> str:
    features = sample["features"]
    label = sample["label"]
    metadata = sample["metadata"]
    expected = label["expected_material"]

    return (
        f"样本编号：{sample['sample_id']}。\n"
        f"标称材质：{label['expected_material_cn']}。\n"
        f"采集范围：400-1000nm。\n"
        f"450nm 蓝光反射率：{features['blue_450']}。\n"
        f"550nm 绿光反射率：{features['green_550']}。\n"
        f"650nm 红光反射率：{features['red_650']}。\n"
        f"850nm 近红外反射率：{features['nir_850']}。\n"
        f"450-650nm 上升斜率：{features['slope_450_650']}。\n"
        f"红蓝比：{features['red_blue_ratio']}。\n"
        f"800-1000nm 近红外均值：{features['nir_mean_800_1000']}。\n"
        f"表面状态：{metadata['surface_state']}。\n"
        f"标准模板：{standard_template_text(expected, standards)}。"
    )


def build_assistant_text(sample: dict) -> str:
    label = sample["label"]
    features = sample["features"]
    qc_result = QC_RESULT_CN[label["qc_result"]]
    defect = DEFECT_CN.get(label["defect"], label["defect"])
    disposition = DISPOSITION_CN.get(label["disposition"], label["disposition"])

    lines = [
        f"质检结论：{qc_result}。",
        f"合格等级：{label['grade']}。",
        f"标称材质：{label['expected_material_cn']}。",
        f"实测材质：{label['detected_material_cn']}。",
    ]

    if label["defect"] != "none":
        lines.append(f"异常项：{defect}。")

    lines.append("置信度：高。" if label["qc_result"] == "pass" else "置信度：中。")
    lines.append("判断依据：")

    if label["qc_result"] == "pass":
        lines.extend([
            f"1. 红蓝比 {features['red_blue_ratio']}，符合{label['expected_material_cn']}标准模板；",
            f"2. 近红外均值 {features['nir_mean_800_1000']}，高于合格阈值；",
            "3. 标称材质与实测光谱一致，表面状态正常。",
        ])
    elif label["qc_result"] == "recheck":
        lines.extend([
            "1. 标称材质与实测光谱不完全一致，存在替代材料风险；",
            f"2. 红蓝比 {features['red_blue_ratio']}，近红外均值 {features['nir_mean_800_1000']} 偏离典型合格样本；",
            "3. 当前结果不足以直接放行。",
        ])
    else:
        lines.extend([
            f"1. 各波段反射率整体偏离合格{label['expected_material_cn']}模板；",
            f"2. 近红外均值仅 {features['nir_mean_800_1000']}，明显低于合格阈值；",
            f"3. 表面状态异常，异常项为 {defect}。",
        ])

    lines.append(f"处置建议：{disposition}。")
    return "\n".join(lines)


def build_record(sample: dict, standards: dict) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_text(sample, standards)},
            {"role": "assistant", "content": build_assistant_text(sample)},
        ]
    }


def generate_dataset(input_path: Path, standards_path: Path, output_path: Path) -> int:
    with input_path.open(encoding="utf-8") as f:
        payload = json.load(f)

    standards = load_standards(standards_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with output_path.open("w", encoding="utf-8") as f:
        for sample in payload["samples"]:
            record = build_record(sample, standards)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="金属质检示例数据转千问训练 JSONL")
    parser.add_argument(
        "--input",
        type=Path,
        default=base / "data" / "metal_sample_spectrum.json",
    )
    parser.add_argument(
        "--standards",
        type=Path,
        default=base / "data" / "qc_standards.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "training" / "metal_sft_train.jsonl",
    )
    args = parser.parse_args()

    count = generate_dataset(args.input, args.standards, args.output)
    print(f"已生成 {count} 条金属质检训练样本 → {args.output}")


if __name__ == "__main__":
    main()
