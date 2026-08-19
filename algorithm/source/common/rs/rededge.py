"""红边位置：Guyot 线性内插（Guyot & Baret 1991）+ SG 一阶导数峰值。"""
from __future__ import annotations

import numpy as np
from scipy.signal import savgol_filter

from common.rs.radiometry import default_wavelengths


def _interp_wl(cube: np.ndarray, wl: np.ndarray, targets: np.ndarray) -> np.ndarray:
    """将立方体光谱内插到目标波长。"""
    h, w, b = cube.shape
    x = cube.reshape(-1, b)
    out = np.empty((x.shape[0], len(targets)), dtype=np.float64)
    for i in range(x.shape[0]):
        out[i] = np.interp(targets, wl, x[i])
    return out.reshape(h, w, len(targets))


def guyot_rep(cube: np.ndarray, wavelength_nm: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    REP = 700 + 40 * ((R670+R780)/2 - R700) / (R740 - R700)
    同时给出红边振幅 R780-R670。
    """
    h, w, b = cube.shape
    wl = np.asarray(wavelength_nm) if wavelength_nm is not None else default_wavelengths(b)
    targets = np.array([670.0, 700.0, 740.0, 780.0])
    spec = _interp_wl(cube.astype(np.float64), wl, targets)
    r670, r700, r740, r780 = spec[:, :, 0], spec[:, :, 1], spec[:, :, 2], spec[:, :, 3]
    denom = r740 - r700
    denom = np.where(np.abs(denom) < 1e-8, 1e-8, denom)
    rep = 700.0 + 40.0 * ((r670 + r780) / 2.0 - r700) / denom
    amp = r780 - r670
    meta = {"method": "Guyot_linear_interpolation", "anchors_nm": [670, 700, 740, 780]}
    return rep.astype(np.float32), amp.astype(np.float32), meta


def derivative_rep(cube: np.ndarray, wavelength_nm: np.ndarray | None = None) -> np.ndarray:
    """SG 一阶导数在 680–750 nm 的峰值波长。"""
    b = cube.shape[2]
    wl = np.asarray(wavelength_nm) if wavelength_nm is not None else default_wavelengths(b)
    win = min(b if b % 2 == 1 else b - 1, 5)
    win = max(3, win)
    d1 = savgol_filter(cube.astype(np.float64), window_length=win, polyorder=2, deriv=1, axis=2, mode="nearest")
    lo = np.searchsorted(wl, 680.0)
    hi = np.searchsorted(wl, 760.0)
    if hi <= lo + 1:
        lo, hi = 0, b
    sl = d1[:, :, lo:hi]
    peak = sl.argmax(axis=2) + lo
    return wl[np.clip(peak, 0, b - 1)].astype(np.float32)
