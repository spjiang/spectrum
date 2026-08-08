#!/usr/bin/env python3
"""生成教学用示例立方体与标签。"""
from __future__ import annotations

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "examples"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    rng = np.random.default_rng(42)
    h, w, b = 32, 32, 8
    # 模拟反射率立方体：左侧偏“植被”，右侧偏“裸土”
    cube = rng.uniform(0.05, 0.25, size=(h, w, b))
    # 近红外波段抬高左侧
    cube[:, : w // 2, 3] = rng.uniform(0.4, 0.7, size=(h, w // 2))
    cube[:, : w // 2, 2] = rng.uniform(0.05, 0.15, size=(h, w // 2))
    # 红边
    cube[:, : w // 2, 4] = rng.uniform(0.2, 0.35, size=(h, w // 2))

    gt = np.zeros((h, w), dtype=np.int32)
    gt[:, : w // 2] = 1  # 植被
    gt[:, w // 2 :] = 2  # 裸土

    # 伪 DN（乘 1000）供定标示意
    dn = (cube * 1000).astype(np.float64)

    np.save(OUT / "sample_cube.npy", cube)
    np.save(OUT / "sample_dn.npy", dn)
    np.save(OUT / "sample_gt.npy", gt)
    print("wrote", OUT / "sample_cube.npy")
    print("wrote", OUT / "sample_dn.npy")
    print("wrote", OUT / "sample_gt.npy")


if __name__ == "__main__":
    main()
