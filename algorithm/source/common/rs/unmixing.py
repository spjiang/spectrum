"""FCLS 全约束最小二乘解混（Heinz & Chang, 2001）。"""
from __future__ import annotations

import numpy as np
from scipy.optimize import nnls


def fcls(endmembers: np.ndarray, mixed: np.ndarray, delta: float = 10.0) -> np.ndarray:
    """
    endmembers: (B, K)
    mixed: (N, B)
    约束 a>=0 且 1ᵀa=1。
    用增广 NNLS：min ||[A; δ1ᵀ] a - [x; δ]||, a>=0。
    """
    b, k = endmembers.shape
    n = mixed.shape[0]
    a_aug = np.vstack([endmembers, delta * np.ones((1, k))])
    out = np.zeros((n, k), dtype=np.float64)
    for i in range(n):
        b_aug = np.append(mixed[i], delta)
        a, _ = nnls(a_aug, b_aug)
        s = a.sum()
        out[i] = a / s if s > 1e-12 else a
    return out
