"""局部 RX 异常检测（Reed–Xiaoli + 局部背景）。"""
from __future__ import annotations

import numpy as np


def global_rx(cube: np.ndarray) -> np.ndarray:
    """全局 RX：(x-μ)^T Σ^{-1} (x-μ)。"""
    h, w, b = cube.shape
    x = cube.reshape(-1, b).astype(np.float64)
    mu = x.mean(axis=0)
    xc = x - mu
    cov = np.cov(xc, rowvar=False)
    if cov.ndim == 0:
        cov = np.array([[float(cov)]])
    cov = cov + np.eye(cov.shape[0]) * 1e-6
    inv = np.linalg.pinv(cov)
    scores = np.einsum("ij,jk,ik->i", xc, inv, xc)
    return scores.reshape(h, w)


def local_rx(cube: np.ndarray, win: int = 7, inner: int = 3) -> np.ndarray:
    """
    双窗 LRX：外窗估背景，内窗排除目标污染。
    小图自动缩小窗口。
    """
    h, w, b = cube.shape
    if min(h, w) < 5:
        return global_rx(cube)
    win = min(win, h if h % 2 == 1 else h - 1, w if w % 2 == 1 else w - 1)
    if win < 5:
        return global_rx(cube)
    if inner % 2 == 0:
        inner += 1
    inner = min(inner, win - 2)
    pad = win // 2
    inner_r = inner // 2
    padded = np.pad(cube.astype(np.float64), ((pad, pad), (pad, pad), (0, 0)), mode="edge")
    scores = np.empty((h, w), dtype=np.float64)
    eye = np.eye(b) * 1e-6
    for r in range(h):
        for c in range(w):
            block = padded[r : r + win, c : c + win, :].reshape(-1, b)
            # 挖去中心 inner×inner
            yy, xx = np.mgrid[0:win, 0:win]
            guard = (np.abs(yy - pad) <= inner_r) & (np.abs(xx - pad) <= inner_r)
            bg = block[~guard.ravel()]
            if bg.shape[0] <= b + 2:
                bg = block
            mu = bg.mean(axis=0)
            xc = bg - mu
            cov = np.cov(bg, rowvar=False)
            if np.ndim(cov) == 0:
                cov = np.array([[float(cov)]])
            cov = np.nan_to_num(cov, nan=0.0, posinf=0.0, neginf=0.0) + eye
            try:
                inv = np.linalg.inv(cov)
            except np.linalg.LinAlgError:
                inv = np.linalg.pinv(cov)
            d = cube[r, c].astype(np.float64) - mu
            scores[r, c] = float(d @ inv @ d)
    return scores
