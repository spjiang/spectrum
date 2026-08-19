"""推扫条纹、光谱微笑与关键畸变：业界在轨/机载常用估计与重采样。"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.ndimage import map_coordinates


def moment_matching_destripe(cube: np.ndarray) -> np.ndarray:
    """
    列向矩匹配去条带（Gadallah / ENVI 推扫常用）：
    每列均值、标准差对齐到整幅。
    """
    col_mean = cube.mean(axis=0, keepdims=True)
    col_std = cube.std(axis=0, keepdims=True) + 1e-12
    glob_mean = cube.mean(axis=(0, 1), keepdims=True)
    glob_std = cube.std(axis=(0, 1), keepdims=True) + 1e-12
    return (cube - col_mean) / col_std * glob_std + glob_mean


def _subpixel_shift(ref: np.ndarray, tgt: np.ndarray) -> float:
    """一维互相关抛物线亚像素峰值。"""
    ref = ref - ref.mean()
    tgt = tgt - tgt.mean()
    corr = np.correlate(tgt, ref, mode="full")
    k = int(np.argmax(corr))
    if 0 < k < len(corr) - 1:
        y0, y1, y2 = corr[k - 1 : k + 2]
        denom = 2 * (2 * y1 - y2 - y0) + 1e-12
        k = k + (y0 - y2) / denom
    return float(k - (len(ref) - 1))


def smile_keystone_correct(cube: np.ndarray) -> tuple[np.ndarray, dict]:
    """
    场景内估计：
    - Smile：各空间列平均光谱相对中心列的亚像素光谱偏移，三次样条重采样到参考波长栅格。
    - Keystone：各波段相对参考波段的列向空间偏移，双线性重采样。
    """
    h, w, b = cube.shape
    center = w // 2
    ref_spec = cube[:, center, :].mean(axis=0)
    smile = np.zeros(w, dtype=np.float64)
    for c in range(w):
        spec = cube[:, c, :].mean(axis=0)
        smile[c] = _subpixel_shift(ref_spec, spec)
    wave = np.arange(b, dtype=np.float64)
    out = np.empty_like(cube, dtype=np.float64)
    for c in range(w):
        src = wave + smile[c]
        for r in range(h):
            y = cube[r, c, :]
            spl = CubicSpline(wave, y, extrapolate=True)
            out[r, c, :] = spl(src)
    # Keystone：以中间波段为参考，估计每波段整幅列偏移
    ref_band = out[:, :, b // 2]
    keystone = np.zeros(b, dtype=np.float64)
    for bi in range(b):
        # 用行均值做 1D 相关
        keystone[bi] = _subpixel_shift(ref_band.mean(axis=0), out[:, :, bi].mean(axis=0))
    rr, cc = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    corrected = np.empty_like(out)
    for bi in range(b):
        corrected[:, :, bi] = map_coordinates(
            out[:, :, bi],
            [rr, cc - keystone[bi]],
            order=1,
            mode="nearest",
        )
    return corrected, {
        "smile_shift_bands": smile.tolist(),
        "keystone_shift_cols": keystone.tolist(),
        "method": "in_scene_xcorr_cubic",
    }
