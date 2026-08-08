#!/usr/bin/env python3
"""
高光谱数据 → 千问 SFT 训练集（JSONL）转换脚本

用法:
    python examples/common/prepare_dataset.py \
        --raw-dir dataset/raw \
        --labels dataset/labels.csv \
        --output dataset/train.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SYSTEM_PROMPT = (
    "你是一名高光谱农产品质检专家，请根据光谱特征判断样本状态，并给出简要依据。"
)

# 各类别的典型光谱特征（用于演示；实际项目请从真实数据计算）
DEMO_FEATURES: dict[str, dict[str, float]] = {
    "healthy": {
        "green_peak_550": 0.118,
        "absorption_680": 0.034,
        "red_edge_nm": 718.5,
        "nir_mean_800_900": 0.451,
    },
    "bruise": {
        "green_peak_550": 0.095,
        "absorption_680": 0.071,
        "red_edge_nm": 705.3,
        "nir_mean_800_900": 0.210,
    },
    "rot": {
        "green_peak_550": 0.062,
        "absorption_680": 0.088,
        "red_edge_nm": 698.1,
        "nir_mean_800_900": 0.152,
    },
}

DEMO_RESPONSES: dict[str, str] = {
    "healthy": (
        "判定结果：健康。\n置信度：高。\n依据：绿峰、红边、近红外指标均处于正常范围。\n建议：A 级放行。"
    ),
    "bruise": (
        "判定结果：碰伤。\n置信度：高。\n依据：\n"
        "1. 680nm 吸收谷变浅；\n"
        "2. 红边位置前移；\n"
        "3. 近红外反射率显著下降。\n"
        "建议：降级为 B 级，单独分拣。"
    ),
    "rot": (
        "判定结果：腐烂。\n置信度：高。\n依据：\n"
        "1. 各波段反射率整体偏低；\n"
        "2. 红边特征消失；\n"
        "3. 近红外反射率极低。\n"
        "建议：C 级剔除，不得流入下一工序。"
    ),
}


def snv(spectrum: np.ndarray) -> np.ndarray:
    return (spectrum - spectrum.mean()) / (spectrum.std() + 1e-8)


def extract_features(spectrum: np.ndarray, wavelengths: np.ndarray) -> dict[str, float]:
    idx_680 = int(np.argmin(np.abs(wavelengths - 680)))
    idx_550 = int(np.argmin(np.abs(wavelengths - 550)))
    idx_range = (wavelengths >= 700) & (wavelengths <= 750)
    derivative = np.gradient(spectrum[idx_range])
    red_edge_nm = float(wavelengths[idx_range][np.argmax(derivative)])
    idx_nir = (wavelengths >= 800) & (wavelengths <= 900)

    return {
        "green_peak_550": round(float(spectrum[idx_550]), 4),
        "absorption_680": round(float(spectrum[idx_680]), 4),
        "red_edge_nm": round(red_edge_nm, 1),
        "nir_mean_800_900": round(float(spectrum[idx_nir].mean()), 4),
    }


def features_to_user_text(sample_id: str, features: dict[str, float], object_type: str = "苹果") -> str:
    return (
        f"样本编号：{sample_id}。\n"
        f"波段范围：397-999nm，共224个波段。\n"
        f"550nm 绿峰反射率：{features['green_peak_550']}。\n"
        f"680nm 吸收谷反射率：{features['absorption_680']}。\n"
        f"红边位置：{features['red_edge_nm']} nm。\n"
        f"800-900nm 近红外均值：{features['nir_mean_800_900']}。\n"
        f"采集场景：产线质检。\n"
        f"样本类型：{object_type}。"
    )


def build_message(sample_id: str, label: str, features: dict[str, float], object_type: str = "苹果") -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": features_to_user_text(sample_id, features, object_type)},
            {"role": "assistant", "content": DEMO_RESPONSES[label]},
        ]
    }


def load_spectrum_from_envi(hdr_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """读取 ENVI 数据；需安装 spectral 库: pip install spectral"""
    try:
        from spectral import envi
    except ImportError as exc:
        raise ImportError("请先安装 spectral: pip install spectral") from exc

    img = envi.open(str(hdr_path))
    cube = np.asarray(img.load())
    wavelengths = np.asarray(img.bands.centers, dtype=np.float32)
    return cube, wavelengths


def process_sample(hdr_path: Path, roi: tuple[slice, slice] | None = None) -> dict[str, float]:
    cube, wavelengths = load_spectrum_from_envi(hdr_path)
    if roi:
        spectrum = cube[roi].mean(axis=(0, 1))
    else:
        h, w = cube.shape[0], cube.shape[1]
        spectrum = cube[h // 2, w // 2, :]
    spectrum = snv(spectrum.astype(np.float32))
    return extract_features(spectrum, wavelengths)


def generate_demo_dataset(labels_path: Path, output_path: Path) -> int:
    """无 ENVI 文件时，用 labels.csv + 预设特征生成演示训练集"""
    df = pd.read_csv(labels_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with output_path.open("w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            label = row["label"]
            features = DEMO_FEATURES.get(label, DEMO_FEATURES["healthy"])
            # 加入轻微随机扰动，避免所有样本完全相同
            noisy = {
                k: round(v + np.random.uniform(-0.005, 0.005), 4)
                for k, v in features.items()
            }
            record = build_message(row["sample_id"], label, noisy, row.get("notes", "苹果")[:2] if False else "苹果")
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def generate_from_envi(labels_path: Path, output_path: Path) -> int:
    """从真实 ENVI 文件提取特征并生成训练集"""
    df = pd.read_csv(labels_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with output_path.open("w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            hdr_path = Path(row["file_path"])
            if not hdr_path.exists():
                print(f"[跳过] 文件不存在: {hdr_path}")
                continue
            features = process_sample(hdr_path)
            record = build_message(row["sample_id"], row["label"], features)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="高光谱数据转千问训练 JSONL")
    parser.add_argument("--raw-dir", type=Path, default=Path("dataset/raw"))
    parser.add_argument("--labels", type=Path, default=Path("dataset/labels.csv"))
    parser.add_argument("--output", type=Path, default=Path("dataset/train.jsonl"))
    parser.add_argument("--demo", action="store_true", help="使用演示数据（无需真实 ENVI 文件）")
    args = parser.parse_args()

    if args.demo or not args.labels.exists():
        if not args.labels.exists():
            print(f"标签文件不存在，生成演示 labels.csv → {args.labels}")
            args.labels.parent.mkdir(parents=True, exist_ok=True)
            demo_labels = pd.DataFrame([
                {"sample_id": "APPLE-001", "file_path": "raw/apple_healthy/001.hdr", "label": "healthy", "label_cn": "健康"},
                {"sample_id": "APPLE-002", "file_path": "raw/apple_healthy/002.hdr", "label": "healthy", "label_cn": "健康"},
                {"sample_id": "APPLE-003", "file_path": "raw/apple_bruise/003.hdr", "label": "bruise", "label_cn": "碰伤"},
                {"sample_id": "APPLE-004", "file_path": "raw/apple_rot/004.hdr", "label": "rot", "label_cn": "腐烂"},
                {"sample_id": "APPLE-005", "file_path": "raw/apple_healthy/005.hdr", "label": "healthy", "label_cn": "健康"},
            ])
            demo_labels.to_csv(args.labels, index=False)

        count = generate_demo_dataset(args.labels, args.output)
        print(f"演示模式：已生成 {count} 条训练样本 → {args.output}")
    else:
        count = generate_from_envi(args.labels, args.output)
        print(f"已处理 {count} 条训练样本 → {args.output}")


if __name__ == "__main__":
    main()
