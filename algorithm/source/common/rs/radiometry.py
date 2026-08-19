"""辐射定标与大气校正：USGS TOA + Chavez DOS2 + 经验线法。"""
from __future__ import annotations

import math

import numpy as np


def earth_sun_distance(doy: int) -> float:
    """日地距离（天文单位）。USGS Landsat 公式。"""
    d = 1.0 - 0.01672 * math.cos(math.radians(0.9856 * (doy - 4)))
    return float(d)


def esun_thuillier(wavelength_nm: np.ndarray) -> np.ndarray:
    """
    太阳光谱辐照度 ESUN（W/m²/μm）。
    按 Thuillier 2003 曲线在可见-短波的分段插值（生产 TOA 常用）。
    """
    # (nm, W/m^2/um)
    lut = np.array(
        [
            [400, 1715],
            [450, 2067],
            [500, 1948],
            [550, 1874],
            [600, 1794],
            [650, 1545],
            [700, 1430],
            [750, 1278],
            [800, 1110],
            [850, 980],
            [900, 895],
            [1000, 747],
            [1200, 526],
            [1600, 245],
            [2100, 85],
            [2500, 35],
        ],
        dtype=np.float64,
    )
    return np.interp(wavelength_nm.astype(np.float64), lut[:, 0], lut[:, 1])


def default_wavelengths(n_bands: int, start_nm: float = 450.0, end_nm: float = 850.0) -> np.ndarray:
    """等间隔波长（无头文件时的传感器默认）。"""
    if n_bands <= 1:
        return np.array([0.5 * (start_nm + end_nm)], dtype=np.float64)
    return np.linspace(start_nm, end_nm, n_bands)


def dn_to_radiance(
    dn: np.ndarray,
    gain: np.ndarray | float,
    offset: np.ndarray | float,
) -> np.ndarray:
    """L = gain * DN + offset。gain/offset 可为标量或逐波段。"""
    g = np.asarray(gain, dtype=np.float64)
    o = np.asarray(offset, dtype=np.float64)
    if g.ndim == 1:
        g = g.reshape(1, 1, -1)
    if o.ndim == 1:
        o = o.reshape(1, 1, -1)
    return g * dn.astype(np.float64) + o


def toa_reflectance(
    radiance: np.ndarray,
    wavelength_nm: np.ndarray,
    solar_zenith_deg: float,
    doy: int = 180,
) -> np.ndarray:
    """
    表观反射率 ρ_TOA = π L d² / (ESUN cosθs)。
    radiance 单位须与 ESUN 一致：W/m²/sr/μm。
    """
    d = earth_sun_distance(doy)
    esun = esun_thuillier(wavelength_nm).reshape(1, 1, -1)
    mu = max(math.cos(math.radians(solar_zenith_deg)), 1e-3)
    return np.clip(math.pi * radiance * d * d / (esun * mu), 0.0, 1.5)


def dos2_surface_reflectance(
    radiance: np.ndarray,
    wavelength_nm: np.ndarray,
    solar_zenith_deg: float,
    doy: int = 180,
    dark_percentile: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Chavez (1996) DOS2：
    Lhaze = Lmin - 0.01 * ESUN * cosθs / (π d²)
    ρ = π (L-Lhaze) d² / (ESUN cosθs τ²)，τ 取 cosθs（DOS2）。
    返回 (反射率, 各波段路径辐射)。
    """
    d = earth_sun_distance(doy)
    esun = esun_thuillier(wavelength_nm).reshape(1, 1, -1)
    mu = max(math.cos(math.radians(solar_zenith_deg)), 1e-3)
    lmin = np.percentile(radiance, dark_percentile, axis=(0, 1), keepdims=True)
    l1pct = 0.01 * esun * mu / (math.pi * d * d)
    lhaze = np.maximum(lmin - l1pct, 0.0)
    tau = mu  # DOS2 用 cosθs 近似双向透过率
    rho = math.pi * (radiance - lhaze) * d * d / (esun * mu * tau * tau + 1e-12)
    return np.clip(rho, 0.0, 1.5).astype(np.float64), lhaze.reshape(-1)


def empirical_line(
    radiance: np.ndarray,
    panel_spectrum: np.ndarray,
    panel_reflectance: np.ndarray | float,
    dark_spectrum: np.ndarray | None = None,
) -> np.ndarray:
    """
    经验线法（无人机高光谱生产主路径）：
    ρ = ρ_panel * (L - L_dark) / (L_panel - L_dark)。
    panel_spectrum: (B,) 影像上参考板辐亮度。
    """
    lp = np.asarray(panel_spectrum, dtype=np.float64).reshape(1, 1, -1)
    rp = np.asarray(panel_reflectance, dtype=np.float64).reshape(1, 1, -1)
    if dark_spectrum is None:
        ld = np.zeros_like(lp)
    else:
        ld = np.asarray(dark_spectrum, dtype=np.float64).reshape(1, 1, -1)
    denom = lp - ld
    denom = np.where(np.abs(denom) < 1e-12, 1e-12, denom)
    return np.clip(rp * (radiance - ld) / denom, 0.0, 1.5)


def extract_panel_spectrum(cube: np.ndarray, roi: list[int] | None = None, bright_pct: float = 99.0) -> np.ndarray:
    """从 ROI 或最亮百分位提取参考板光谱。"""
    if roi is not None and len(roi) == 4:
        r0, r1, c0, c1 = [int(x) for x in roi]
        patch = cube[r0:r1, c0:c1]
        if patch.size:
            return patch.reshape(-1, cube.shape[2]).mean(axis=0)
    bright = cube.mean(axis=2)
    thr = np.percentile(bright, bright_pct)
    mask = bright >= thr
    if not mask.any():
        return cube.reshape(-1, cube.shape[2]).mean(axis=0)
    return cube[mask].mean(axis=0)


def extract_dark_spectrum(cube: np.ndarray, dark_pct: float = 1.0) -> np.ndarray:
    """最暗百分位光谱，作经验线暗点。"""
    dark = cube.mean(axis=2)
    thr = np.percentile(dark, dark_pct)
    mask = dark <= thr
    if not mask.any():
        return np.zeros(cube.shape[2], dtype=np.float64)
    return cube[mask].mean(axis=0)
