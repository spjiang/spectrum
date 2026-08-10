#!/usr/bin/env python3
"""用共享 Indian Pines 对 Tiny3DCNN 做本地冒烟（不经 HTTP）。"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import scipy.io as sio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from algorithms import cnn3d_classify_shim as shim  # noqa: E402


def main() -> None:
    data_root = Path(
        "/Users/jiangshengping/wwwroot/shenzhen/spectrum/wwwroot/hyper-spectral-small-modes/datasets"
    )
    cube_path = data_root / "IndianPines" / "Indian_pines_corrected.mat"
    gt_path = data_root / "IndianPines" / "Indian_pines_gt.mat"
    if not cube_path.exists():
        raise SystemExit(f"缺少数据: {cube_path}")

    cube = sio.loadmat(cube_path)["indian_pines_corrected"]
    gt = sio.loadmat(gt_path)["indian_pines_gt"]
    print(f"IP cube={cube.shape} gt={gt.shape}")

    t0 = time.time()
    # 冒烟：少 epoch / 强 PCA，控制本机时长
    result = shim.train_and_predict(
        cube.astype("float64"),
        gt.astype("int32"),
        patch_size=5,
        pca_components=15,
        epochs=3,
        batch_size=128,
        test_size=0.7,
    )
    result.pop("pred_map", None)
    print("SMOKE_OK")
    for k, v in result.items():
        print(f"  {k}: {v}")
    print(f"  elapsed_sec: {time.time() - t0:.1f}")


if __name__ == "__main__":
    main()
