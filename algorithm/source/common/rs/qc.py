"""架次辐射质检：按位深饱和、欠曝、SNR。"""
from __future__ import annotations

import numpy as np


def infer_saturation(vmax: float, bit_depth: int | None = None) -> float:
    """推断饱和 DN。优先位深；否则按动态范围落在 8/12/16 bit。"""
    if bit_depth is not None:
        return float((1 << bit_depth) - 1)
    if vmax <= 1.5:
        return 1.0
    if vmax <= 255.5:
        return 255.0
    if vmax <= 4095.5:
        return 4095.0
    if vmax <= 16383.5:
        return 16383.0
    return 65535.0


def band_snr(cube: np.ndarray) -> np.ndarray:
    """
    逐波段 SNR ≈ μ/σ。
    均匀区近似：全图统计（推扫质检常用快速指标）。
    """
    mu = cube.mean(axis=(0, 1))
    sd = cube.std(axis=(0, 1)) + 1e-12
    return mu / sd


def flight_qc(
    cube: np.ndarray,
    *,
    bit_depth: int | None = None,
    max_saturated_ratio: float = 0.01,
    sat_frac: float = 0.98,
    dark_frac: float = 0.02,
) -> dict:
    """过曝/欠曝比例 + 波段 SNR。"""
    cube = cube.astype(np.float64)
    vmax = float(np.nanmax(cube))
    vmin = float(np.nanmin(cube))
    sat_level = infer_saturation(vmax, bit_depth)
    sat = cube >= (sat_level * sat_frac)
    dark = cube <= (sat_level * dark_frac)
    sat_ratio = float(sat.mean())
    dark_ratio = float(dark.mean())
    snr = band_snr(cube)
    passed = sat_ratio <= max_saturated_ratio
    return {
        "passed": passed,
        "suggest_refly": (not passed),
        "saturation_level": sat_level,
        "bit_depth_used": bit_depth,
        "saturated_ratio": sat_ratio,
        "underexposed_ratio": dark_ratio,
        "max_saturated_ratio": max_saturated_ratio,
        "snr_per_band": [float(x) for x in snr],
        "snr_min": float(snr.min()),
        "snr_median": float(np.median(snr)),
        "min": vmin,
        "max": vmax,
        "mean": float(cube.mean()),
        "shape": list(cube.shape),
        "method": "bit_depth_saturation + band_snr",
    }
