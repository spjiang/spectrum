"""Ross–Li 核驱动 BRDF（MODIS ATBD）归一到天底。"""
from __future__ import annotations

import math

import numpy as np


def _cos_safe(deg: float) -> float:
    return max(math.cos(math.radians(deg)), 1e-4)


def ross_thick(sza: float, vza: float, raa: float) -> float:
    """体积散射核 Kvol（Ross-Thick）。角度单位：度。"""
    ts, tv, phi = map(math.radians, (sza, vza, raa))
    cosxi = math.cos(ts) * math.cos(tv) + math.sin(ts) * math.sin(tv) * math.cos(phi)
    cosxi = min(1.0, max(-1.0, cosxi))
    xi = math.acos(cosxi)
    return ((math.pi / 2 - xi) * math.cos(xi) + math.sin(xi)) / (
        math.cos(ts) + math.cos(tv) + 1e-12
    ) - math.pi / 4


def li_sparse(sza: float, vza: float, raa: float, br: float = 1.0, hb: float = 2.0) -> float:
    """几何核 Kgeo（Li-Sparse）。br=b/r, hb=h/b。"""
    ts, tv, phi = map(math.radians, (sza, vza, raa))
    sects = 1.0 / max(math.cos(ts), 1e-4)
    sectv = 1.0 / max(math.cos(tv), 1e-4)
    cosxi = math.cos(ts) * math.cos(tv) + math.sin(ts) * math.sin(tv) * math.cos(phi)
    cosxi = min(1.0, max(-1.0, cosxi))
    d2 = (
        math.tan(ts) ** 2
        + math.tan(tv) ** 2
        - 2 * math.tan(ts) * math.tan(tv) * math.cos(phi)
    )
    d2 = max(d2, 0.0)
    cost = br * math.sqrt(d2 + (math.tan(ts) * math.tan(tv) * math.sin(phi)) ** 2)
    cost = min(1.0, cost)
    t = math.acos(min(1.0, max(-1.0, cost)))
    o = (1 / math.pi) * (t - math.sin(t) * cost) * (sects + sectv)
    return o - sects - sectv + 0.5 * (1 + cosxi) * sects * sectv


def nadir_normalize(
    rho: np.ndarray,
    *,
    solar_zenith: float,
    view_zenith: np.ndarray | float,
    relative_azimuth: float = 0.0,
    f_iso: float = 0.2,
    f_vol: float = 0.1,
    f_geo: float = 0.05,
) -> np.ndarray:
    """
    ρ_n = ρ * k_nadir / k(θs,θv,φ)
    k = f_iso + f_vol Kvol + f_geo Kgeo
    核权重默认为植被 MODIS 后备参数量级。
    view_zenith 可为逐列视场角数组。
    """
    k0 = f_iso + f_vol * ross_thick(solar_zenith, 0.0, 0.0) + f_geo * li_sparse(solar_zenith, 0.0, 0.0)
    vz = np.asarray(view_zenith, dtype=np.float64)
    if vz.ndim == 0:
        k = f_iso + f_vol * ross_thick(solar_zenith, float(vz), relative_azimuth) + f_geo * li_sparse(
            solar_zenith, float(vz), relative_azimuth
        )
        factor = k0 / max(k, 1e-6)
        return rho * factor
    factor = np.empty(vz.shape, dtype=np.float64)
    it = np.nditer(vz, flags=["multi_index"])
    for x in it:
        k = f_iso + f_vol * ross_thick(solar_zenith, float(x), relative_azimuth) + f_geo * li_sparse(
            solar_zenith, float(x), relative_azimuth
        )
        factor[it.multi_index] = k0 / max(k, 1e-6)
    while factor.ndim < rho.ndim:
        factor = factor[..., None]
    return rho * factor
