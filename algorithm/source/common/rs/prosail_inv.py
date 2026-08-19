"""PROSAIL LUT 反演 LAI / Cab（Jacquemoud / Verhoef；使用 PyPI `prosail`）。"""
from __future__ import annotations

import numpy as np
import prosail

from common.rs.radiometry import default_wavelengths


def _prosail_wl() -> np.ndarray:
    return np.arange(400, 2501, dtype=np.float64)


def build_lut(
    wavelengths_nm: np.ndarray,
    *,
    solar_zenith: float = 30.0,
    view_zenith: float = 0.0,
    relative_azimuth: float = 0.0,
    n_lai: int = 12,
    n_cab: int = 8,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    构建 (LAI, Cab) LUT。
    返回 spectra (M, B), lai (M,), cab (M,)。
    """
    wl_full = _prosail_wl()
    lai_grid = np.linspace(0.2, 6.0, n_lai)
    cab_grid = np.linspace(10.0, 70.0, n_cab)
    specs, lais, cabs = [], [], []
    for lai in lai_grid:
        for cab in cab_grid:
            rho = np.asarray(
                prosail.run_prosail(
                    1.5,
                    float(cab),
                    8.0,
                    0.0,
                    0.01,
                    0.009,
                    float(lai),
                    30.0,
                    0.01,
                    float(solar_zenith),
                    float(view_zenith),
                    float(relative_azimuth),
                    prospect_version="5",
                    typelidf=2,
                    factor="SDR",
                    rsoil=1.0,
                    psoil=0.5,
                ),
                dtype=np.float64,
            )
            specs.append(np.interp(wavelengths_nm, wl_full, rho))
            lais.append(lai)
            cabs.append(cab)
    return np.vstack(specs), np.asarray(lais), np.asarray(cabs)


def invert_cube(
    cube: np.ndarray,
    wavelengths_nm: np.ndarray | None = None,
    **lut_kw,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """逐像素光谱角/RMSE 最近邻 LUT 反演。"""
    h, w, b = cube.shape
    wl = np.asarray(wavelengths_nm) if wavelengths_nm is not None else default_wavelengths(b)
    lut, lai_v, cab_v = build_lut(wl, **lut_kw)
    lut_n = lut / (np.linalg.norm(lut, axis=1, keepdims=True) + 1e-12)
    x = cube.reshape(-1, b)
    x_n = x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-12)
    # 光谱角最小
    cos = np.clip(x_n @ lut_n.T, -1.0, 1.0)
    idx = cos.argmax(axis=1)
    lai = lai_v[idx].reshape(h, w).astype(np.float32)
    cab = cab_v[idx].reshape(h, w).astype(np.float32)
    meta = {
        "model": "PROSAIL-5 + 4SAIL",
        "lut_size": int(len(lai_v)),
        "wavelengths_nm": wl.tolist(),
        "library": "prosail (PyPI)",
    }
    return lai, cab, meta
