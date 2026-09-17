"""受 Fmask 启发的简化云/暗区检测（无热红外与云影投影几何）。"""
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
    云候选规则：可见光亮、NDVI 低、可见光波段间相对差异较小（低白度指标）；
    暗区候选为近红外低值且非水体。
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
    # 候选暗区：近红外显著偏低且非水、非云
    nir_thr = float(np.percentile(nir_r[~cloud], 15)) if (~cloud).any() else float(np.percentile(nir_r, 15))
    shadow = (~cloud) & (~water) & (nir_r < nir_thr)
    cloud_u = ndi.binary_opening(cloud, structure=np.ones((3, 3), dtype=bool)).astype(np.uint8)
    shadow_u = ndi.binary_opening(shadow, structure=np.ones((3, 3), dtype=bool)).astype(np.uint8)
    return cloud_u, shadow_u
