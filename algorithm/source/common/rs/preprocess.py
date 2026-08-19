"""光谱预处理：SNV / 矢量归一。"""
from __future__ import annotations

import numpy as np


def snv(cube: np.ndarray) -> np.ndarray:
    """Standard Normal Variate：逐像元光谱减均值除标准差。"""
    x = cube.astype(np.float64)
    mu = x.mean(axis=2, keepdims=True)
    sd = x.std(axis=2, keepdims=True) + 1e-12
    return (x - mu) / sd


def l2_normalize(cube: np.ndarray) -> np.ndarray:
    """逐像元 L2 归一（光谱角准备）。"""
    x = cube.astype(np.float64)
    nrm = np.linalg.norm(x, axis=2, keepdims=True) + 1e-12
    return x / nrm
