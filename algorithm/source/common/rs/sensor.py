"""传感器校正：暗电流+列 FPN、坏像元自动检测与双线性填充。"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi


def dark_current_correct(cube: np.ndarray, dark: np.ndarray | None = None) -> tuple[np.ndarray, dict]:
    """
    DN' = DN - dark - 列向固定模式噪声。
    无暗帧时：每波段最小值作暗电流，列均值残差作 FPN。
    """
    cube = cube.astype(np.float64)
    if dark is not None:
        dark = dark.astype(np.float64)
        method = "dark_frame"
    else:
        dark = cube.min(axis=(0, 1), keepdims=True)
        method = "per_band_min"
    out = cube - dark
    # 列 FPN：每列相对行均值的偏差
    col_mean = out.mean(axis=0, keepdims=True)
    global_mean = out.mean(axis=(0, 1), keepdims=True)
    fpn = col_mean - global_mean
    out = out - fpn
    out = np.clip(out, 0.0, None)
    meta = {
        "method": method + "+column_fpn",
        "fpn_abs_mean": float(np.abs(fpn).mean()),
        "dark_mean": float(np.mean(dark)),
    }
    return out, meta


def detect_bad_mask(cube: np.ndarray, z_thr: float = 6.0) -> tuple[np.ndarray, list[int]]:
    """
    空间中值残差 6σ 热/死像元 + 列统计坏线。
    返回 (H×W 掩膜, 坏列索引)。
    """
    h, w, b = cube.shape
    mask = np.zeros((h, w), dtype=bool)
    for bi in range(b):
        band = cube[:, :, bi]
        med = ndi.median_filter(band, size=3, mode="nearest")
        resid = band - med
        sigma = 1.4826 * np.median(np.abs(resid - np.median(resid))) + 1e-12
        mask |= np.abs(resid) > (z_thr * sigma)
    col_mean = cube.mean(axis=(0, 2))
    col_med = ndi.median_filter(col_mean, size=3, mode="nearest")
    col_res = col_mean - col_med
    col_s = 1.4826 * np.median(np.abs(col_res - np.median(col_res))) + 1e-12
    bad_cols = [int(i) for i in np.where(np.abs(col_res) > max(4.0 * col_s, 1e-6))[0]]
    for c in bad_cols:
        mask[:, c] = True
    return mask, bad_cols


def fill_bad_pixels(cube: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """坏位置用 3×3 忽略自身的邻域均值填充（逐波段）。"""
    out = cube.astype(np.float64).copy()
    if not mask.any():
        return out
    for bi in range(out.shape[2]):
        band = out[:, :, bi]
        tmp = band.copy()
        tmp[mask] = np.nan
        fill = ndi.generic_filter(tmp, np.nanmean, size=3, mode="nearest")
        # 若整窗都是 nan，退回全局中值
        still = mask & ~np.isfinite(fill)
        if still.any():
            fill[still] = np.nanmedian(tmp)
        band[mask] = fill[mask]
        out[:, :, bi] = band
    return out
