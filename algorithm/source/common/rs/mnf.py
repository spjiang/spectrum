"""最小噪声分数 MNF（Green et al. 1988）。"""
from __future__ import annotations

import numpy as np


def _noise_shift(x: np.ndarray, h: int, w: int, b: int) -> np.ndarray:
    """空间移位差分估计噪声：N = X - shift(X, 1 col)。"""
    cube = x.reshape(h, w, b)
    noise = np.zeros_like(cube)
    noise[:, 1:, :] = cube[:, 1:, :] - cube[:, :-1, :]
    noise[:, 0, :] = noise[:, 1, :]
    return noise.reshape(-1, b)


def mnf_transform(cube: np.ndarray, n_components: int) -> tuple[np.ndarray, dict]:
    """
    1) 噪声协方差白化  2) 对白化数据做 PCA。
    返回 H×W×K 与特征值。
    """
    h, w, b = cube.shape
    x = cube.reshape(-1, b).astype(np.float64)
    x = x - x.mean(axis=0, keepdims=True)
    noise = _noise_shift(x, h, w, b)
    noise = noise - noise.mean(axis=0, keepdims=True)
    cn = np.cov(noise, rowvar=False)
    if cn.ndim == 0:
        cn = np.array([[float(cn)]], dtype=np.float64)
    cn = np.nan_to_num(0.5 * (cn + cn.T), nan=0.0, posinf=0.0, neginf=0.0)
    cn = cn + np.eye(b) * (1e-6 * (np.trace(cn) / b + 1.0))
    eigval_n, eigvec_n = np.linalg.eigh(cn)
    eigval_n = np.clip(eigval_n, 1e-8, None)
    w_n = eigvec_n @ (np.diag(1.0 / np.sqrt(eigval_n)) @ eigvec_n.T)
    xw = np.nan_to_num(x @ w_n, nan=0.0, posinf=0.0, neginf=0.0)
    cov = xw.T @ xw / max(len(xw) - 1, 1)
    eigval, eigvec = np.linalg.eigh(cov)
    order = np.argsort(eigval)[::-1]
    eigval = eigval[order]
    eigvec = eigvec[:, order]
    k = max(1, min(n_components, b, h * w))
    z = (xw @ eigvec[:, :k]).reshape(h, w, k)
    ev = eigval[:k]
    ev = np.clip(ev, 0, None)
    ratio = ev / (ev.sum() + 1e-12)
    meta = {
        "method": "MNF",
        "eigenvalues": [float(v) for v in ev],
        "explained_variance_ratio": [float(v) for v in ratio],
        "n_components": k,
    }
    return z.astype(np.float32), meta


def pca_transform(cube: np.ndarray, n_components: int) -> tuple[np.ndarray, dict]:
    """标准化后 PCA（对照路径）。"""
    h, w, b = cube.shape
    x = cube.reshape(-1, b).astype(np.float64)
    mu = x.mean(axis=0, keepdims=True)
    sd = x.std(axis=0, keepdims=True) + 1e-12
    x = (x - mu) / sd
    cov = x.T @ x / max(len(x) - 1, 1)
    eigval, eigvec = np.linalg.eigh(cov)
    order = np.argsort(eigval)[::-1]
    eigval = eigval[order]
    eigvec = eigvec[:, order]
    k = max(1, min(n_components, b, h * w))
    z = (x @ eigvec[:, :k]).reshape(h, w, k)
    ev = np.clip(eigval[:k], 0, None)
    ratio = ev / (ev.sum() + 1e-12)
    meta = {
        "method": "PCA",
        "eigenvalues": [float(v) for v in ev],
        "explained_variance_ratio": [float(v) for v in ratio],
        "n_components": k,
    }
    return z.astype(np.float32), meta
