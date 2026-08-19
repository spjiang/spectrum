"""ACE 自适应余弦估计：高光谱目标探测业界标准（Kay, 1990s / HSI 处理软件常用）。"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi


def ace_score(cube: np.ndarray, target: np.ndarray) -> np.ndarray:
    """(x-μ)ᵀ Σ⁻¹ d / sqrt((x-μ)ᵀΣ⁻¹(x-μ) · dᵀΣ⁻¹d)。"""
    h, w, b = cube.shape
    x = cube.reshape(-1, b)
    mu = x.mean(axis=0)
    xc = x - mu
    d = np.asarray(target, dtype=np.float64) - mu
    cov = np.cov(xc, rowvar=False)
    if cov.ndim == 0:
        cov = np.array([[float(cov)]])
    cov = cov + np.eye(cov.shape[0]) * 1e-6
    inv = np.linalg.pinv(cov)
    wd = inv @ d
    num = xc @ wd
    den_x = np.einsum("ij,ji->i", xc @ inv, xc.T)
    den_d = float(d @ wd)
    den = np.sqrt(np.clip(den_x * den_d, 0, None)) + 1e-12
    return (num / den).reshape(h, w)


def detect_mask(score: np.ndarray, percentile: float = 95.0, min_pixels: int = 4) -> np.ndarray:
    """高分阈值 + 形态学去碎斑。"""
    thr = float(np.percentile(score, percentile))
    mask = score >= thr
    if score.shape[0] >= 8:
        mask = ndi.binary_opening(mask, structure=np.ones((3, 3), dtype=bool))
    labeled, n = ndi.label(mask)
    keep = np.zeros_like(mask)
    for i in range(1, n + 1):
        if int((labeled == i).sum()) >= min_pixels:
            keep[labeled == i] = True
    return keep
