"""IR-MAD 多时相变化检测（Nielsen 2007）。"""
from __future__ import annotations

import numpy as np
from scipy.stats import chi2


def _weighted_moments(x: np.ndarray, y: np.ndarray, w: np.ndarray):
    sw = float(w.sum()) + 1e-12
    mx = (w[:, None] * x).sum(axis=0) / sw
    my = (w[:, None] * y).sum(axis=0) / sw
    xc = x - mx
    yc = y - my
    sxx = (w[:, None, None] * xc[:, :, None] * xc[:, None, :]).sum(axis=0) / sw
    syy = (w[:, None, None] * yc[:, :, None] * yc[:, None, :]).sum(axis=0) / sw
    sxy = (w[:, None, None] * xc[:, :, None] * yc[:, None, :]).sum(axis=0) / sw
    ridge = 1e-6 * (float(np.trace(sxx)) / max(sxx.shape[0], 1) + 1.0)
    sxx = np.nan_to_num(sxx, nan=0.0, posinf=0.0, neginf=0.0) + np.eye(sxx.shape[0]) * ridge
    syy = np.nan_to_num(syy, nan=0.0, posinf=0.0, neginf=0.0) + np.eye(syy.shape[0]) * ridge
    sxy = np.nan_to_num(sxy, nan=0.0, posinf=0.0, neginf=0.0)
    return mx, my, sxx, syy, sxy


def ir_mad(
    cube1: np.ndarray,
    cube2: np.ndarray,
    *,
    max_iter: int = 15,
    tol: float = 1e-4,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    迭代重加权多元变化检测。
    返回 (chi2 图, 变化掩膜用的 chi2, 元数据)。
    """
    h = min(cube1.shape[0], cube2.shape[0])
    w = min(cube1.shape[1], cube2.shape[1])
    b = min(cube1.shape[2], cube2.shape[2])
    x = cube1[:h, :w, :b].reshape(-1, b).astype(np.float64)
    y = cube2[:h, :w, :b].reshape(-1, b).astype(np.float64)
    # 标准化
    x = (x - x.mean(0)) / (x.std(0) + 1e-12)
    y = (y - y.mean(0)) / (y.std(0) + 1e-12)
    n = x.shape[0]
    n_bands = b
    weights = np.ones(n, dtype=np.float64)
    canon_corr = np.zeros(n_bands)
    mad = x - y
    chi = np.sum(mad ** 2, axis=1)
    for _ in range(max_iter):
        _, _, sxx, syy, sxy = _weighted_moments(x, y, weights)
        try:
            syy_inv = np.linalg.inv(syy)
            m = np.linalg.solve(sxx, sxy @ syy_inv @ sxy.T)
            eigval, eigvec = np.linalg.eig(m)
        except np.linalg.LinAlgError:
            break
        eigval = np.clip(np.real(eigval), 0.0, 1.0)
        eigvec = np.real(eigvec)
        order = np.argsort(eigval)[::-1]
        eigval = eigval[order]
        a = eigvec[:, order]
        bvec = syy_inv @ sxy.T @ a
        na = np.sqrt(np.clip(np.diag(a.T @ sxx @ a), 1e-12, None))
        nb = np.sqrt(np.clip(np.diag(bvec.T @ syy @ bvec), 1e-12, None))
        a = a / na
        bvec = bvec / nb
        mad = (x @ a) - (y @ bvec)
        var = np.var(mad, axis=0, ddof=1) + 1e-12
        chi = np.sum((mad ** 2) / var, axis=1)
        new_w = np.clip(1.0 - chi2.cdf(chi, df=n_bands), 1e-6, 1.0)
        delta = float(np.mean(np.abs(new_w - weights)))
        weights = new_w
        canon_corr = np.sqrt(eigval)
        if delta < tol:
            break
    chi_map = chi.reshape(h, w).astype(np.float32)
    mad_norm = np.sqrt(np.sum((mad ** 2) / (np.var(mad, axis=0, ddof=1) + 1e-12), axis=1))
    mag = mad_norm.reshape(h, w).astype(np.float32)
    meta = {
        "method": "IR-MAD",
        "canonical_correlations": [float(c) for c in canon_corr],
        "chi2_mean": float(chi_map.mean()),
        "chi2_df": b,
        "shape": [h, w],
    }
    return chi_map, mag, meta
