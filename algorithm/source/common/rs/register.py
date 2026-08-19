"""相位相关配准：Kuglin–Hines + Foroosh 亚像元平移。"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import shift as nd_shift
from skimage.transform import resize


def _wrap_peak(idx: int, n: int) -> float:
    return float(idx if idx <= n // 2 else idx - n)


def foroosh_delta(c0: float, c1: float) -> float:
    """
    Foroosh et al. 2002：由主峰与旁瓣估计亚像元偏移。
    Δ = C1 / (C1 + sign(C1)*C0)
    """
    if abs(c0) < 1e-12 and abs(c1) < 1e-12:
        return 0.0
    s = 1.0 if c1 >= 0 else -1.0
    denom = c1 + s * c0
    if abs(denom) < 1e-12:
        return 0.0
    d = c1 / denom
    return float(np.clip(d, -1.0, 1.0))


def phase_correlation_subpixel(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    """
    返回 (dy, dx, peak_response)。
    a/b 为同尺寸 2D。
    """
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    a = a - a.mean()
    b = b - b.mean()
    win_y = np.hanning(a.shape[0])[:, None]
    win_x = np.hanning(a.shape[1])[None, :]
    fa = np.fft.fft2(a * win_y * win_x)
    fb = np.fft.fft2(b * win_y * win_x)
    r = fa * np.conj(fb)
    r /= np.abs(r) + 1e-12
    c = np.fft.ifft2(r).real
    peak = np.unravel_index(int(np.argmax(c)), c.shape)
    py, px = int(peak[0]), int(peak[1])
    h, w = c.shape
    c0 = float(c[py, px])
    c_yp = float(c[(py + 1) % h, px])
    c_yn = float(c[(py - 1) % h, px])
    c_xp = float(c[py, (px + 1) % w])
    c_xn = float(c[py, (px - 1) % w])
    dy = _wrap_peak(py, h) + foroosh_delta(c0, c_yp if abs(c_yp) >= abs(c_yn) else c_yn)
    dx = _wrap_peak(px, w) + foroosh_delta(c0, c_xp if abs(c_xp) >= abs(c_xn) else c_xn)
    if abs(c_yn) > abs(c_yp):
        dy = _wrap_peak(py, h) - foroosh_delta(c0, c_yn)
    if abs(c_xn) > abs(c_xp):
        dx = _wrap_peak(px, w) - foroosh_delta(c0, c_xn)
    return float(dy), float(dx), float(c0)


def register_to_reference(
    ref_cube: np.ndarray,
    src_cube: np.ndarray,
) -> tuple[np.ndarray, dict]:
    """将 src 亮度配准到 ref，亚像元平移重采样全部波段。"""
    ref_g = ref_cube.mean(axis=2)
    src_g = src_cube.mean(axis=2)
    if src_g.shape != ref_g.shape:
        src_g = resize(src_g, ref_g.shape, preserve_range=True, anti_aliasing=True)
        resized = np.empty(ref_cube.shape[:2] + (src_cube.shape[2],), dtype=np.float64)
        for bi in range(src_cube.shape[2]):
            resized[:, :, bi] = resize(
                src_cube[:, :, bi], ref_g.shape, preserve_range=True, anti_aliasing=True
            )
        src_cube = resized
    dy, dx, peak = phase_correlation_subpixel(ref_g, src_g)
    aligned = np.empty_like(src_cube, dtype=np.float64)
    for bi in range(src_cube.shape[2]):
        aligned[:, :, bi] = nd_shift(src_cube[:, :, bi], shift=(dy, dx), order=3, mode="nearest")
    meta = {
        "method": "phase_correlation_foroosh",
        "dy": dy,
        "dx": dx,
        "peak_response": peak,
    }
    return aligned, meta
