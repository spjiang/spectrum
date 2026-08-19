"""Fmask 光谱云/云影检测（Zhu & Woodcock，无热红外通道时的光谱规则）。"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi


def fmask_spectral(
    cube: np.ndarray,
    *,
    blue: int = 0,
    green: int = 1,
    red: int = 2,
    nir: int = 3,
    swir: int | None = 5,
) -> tuple[np.ndarray, np.ndarray]:
    """
    返回 (cloud_mask, shadow_mask)，uint8 0/1。
    规则对齐 Fmask 潜在云：高亮、低 NDVI、高白度；影为近红外低值且非水体。
    """
    b = cube.shape[2]

    def band(i: int) -> np.ndarray:
        i2 = min(max(i, 0), b - 1)
        return cube[:, :, i2].astype(np.float64)

    blue_r, green_r, red_r, nir_r = band(blue), band(green), band(red), band(nir)
    vis = (blue_r + green_r + red_r) / 3.0
    ndvi = (nir_r - red_r) / (nir_r + red_r + 1e-12)
    ndwi = (green_r - nir_r) / (green_r + nir_r + 1e-12)
    mean_vis = vis + 1e-12
    whiteness = (
        np.abs(blue_r - mean_vis) + np.abs(green_r - mean_vis) + np.abs(red_r - mean_vis)
    ) / mean_vis
    cloud = (vis > 0.25) & (ndvi < 0.7) & (whiteness < 0.7)
    if swir is not None and swir < b:
        swir_r = band(swir)
        ndsi = (green_r - swir_r) / (green_r + swir_r + 1e-12)
        cloud = cloud & (ndsi < 0.8) & (swir_r > 0.03)
    water = ndwi > 0.1
    # 云影：近红外显著偏低且非水、非云
    nir_thr = float(np.percentile(nir_r[~cloud], 15)) if (~cloud).any() else float(np.percentile(nir_r, 15))
    shadow = (~cloud) & (~water) & (nir_r < nir_thr)
    cloud_u = ndi.binary_opening(cloud, structure=np.ones((3, 3), dtype=bool)).astype(np.uint8)
    shadow_u = ndi.binary_opening(shadow, structure=np.ones((3, 3), dtype=bool)).astype(np.uint8)
    return cloud_u, shadow_u
