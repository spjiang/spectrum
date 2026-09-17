"""PROSAIL LUT 反演 LAI / Cab（Jacquemoud / Verhoef；Weiss 多解平均；RMSE 默认）。"""
from __future__ import annotations

import numpy as np
import prosail

from common.rs.radiometry import default_wavelengths

LAI_MIN, LAI_MAX = 0.2, 6.0
CAB_MIN, CAB_MAX = 10.0, 70.0
DEFAULT_N_LAI = 25
DEFAULT_N_CAB = 16
DEFAULT_BEST_FRAC = 0.05
COST_METHODS = {"rmse", "sam"}


def _prosail_wl() -> np.ndarray:
    return np.arange(400, 2501, dtype=np.float64)


def build_lut(
    wavelengths_nm: np.ndarray,
    *,
    solar_zenith: float = 30.0,
    view_zenith: float = 0.0,
    relative_azimuth: float = 0.0,
    n_lai: int = DEFAULT_N_LAI,
    n_cab: int = DEFAULT_N_CAB,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    构建 (LAI, Cab) LUT。
    返回 spectra (M, B), lai (M,), cab (M,)。
    """
    wl_full = _prosail_wl()
    lai_grid = np.linspace(LAI_MIN, LAI_MAX, n_lai)
    cab_grid = np.linspace(CAB_MIN, CAB_MAX, n_cab)
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


def _lut_costs(spectra: np.ndarray, lut: np.ndarray, method: str) -> np.ndarray:
    """spectra (N, B), lut (M, B) → 代价 (N, M)，越小越像。"""
    if method == "rmse":
        n_pix, n_lut = spectra.shape[0], lut.shape[0]
        costs = np.empty((n_pix, n_lut), dtype=np.float64)
        for index in range(n_lut):
            diff = spectra - lut[index]
            costs[:, index] = np.sqrt(np.mean(diff * diff, axis=1))
        return costs
    spectra_n = spectra / (np.linalg.norm(spectra, axis=1, keepdims=True) + 1e-12)
    lut_n = lut / (np.linalg.norm(lut, axis=1, keepdims=True) + 1e-12)
    cosine = np.clip(spectra_n @ lut_n.T, -1.0, 1.0)
    return 1.0 - cosine


def match_lut(
    spectra: np.ndarray,
    lut: np.ndarray,
    lai_v: np.ndarray,
    cab_v: np.ndarray,
    *,
    cost_method: str = "rmse",
    best_frac: float = DEFAULT_BEST_FRAC,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """按代价取最优若干条，对 LAI/Cab 平均（Weiss 2000 多解平均）。"""
    method = str(cost_method).lower()
    if method not in COST_METHODS:
        raise ValueError("cost_method 仅支持 rmse 或 sam")
    if not (0.0 < float(best_frac) <= 1.0):
        raise ValueError("best_frac 须在 (0, 1] 内")
    costs = _lut_costs(np.asarray(spectra, dtype=np.float64), np.asarray(lut, dtype=np.float64), method)
    n_lut = lut.shape[0]
    best_n = max(1, min(n_lut, int(round(float(best_frac) * n_lut))))
    selected = np.argpartition(costs, kth=best_n - 1, axis=1)[:, :best_n]
    lai = np.asarray(lai_v, dtype=np.float64)[selected].mean(axis=1)
    cab = np.asarray(cab_v, dtype=np.float64)[selected].mean(axis=1)
    lai_min, lai_max = float(np.min(lai_v)), float(np.max(lai_v))
    cab_min, cab_max = float(np.min(cab_v)), float(np.max(cab_v))
    sel_lai = np.asarray(lai_v, dtype=np.float64)[selected]
    sel_cab = np.asarray(cab_v, dtype=np.float64)[selected]
    lai_edge = np.all(np.isclose(sel_lai, lai_min), axis=1) | np.all(np.isclose(sel_lai, lai_max), axis=1)
    cab_edge = np.all(np.isclose(sel_cab, cab_min), axis=1) | np.all(np.isclose(sel_cab, cab_max), axis=1)
    meta = {
        "cost_method": method,
        "best_n": int(best_n),
        "n_boundary_lai": int(lai_edge.sum()),
        "n_boundary_cab": int(cab_edge.sum()),
    }
    return lai.astype(np.float32), cab.astype(np.float32), meta


def invert_cube(
    cube: np.ndarray,
    wavelengths_nm: np.ndarray | None = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """PROSAIL LUT 反演：默认 RMSE，对最优若干条取平均。"""
    cost_method = str(kwargs.pop("cost_method", "rmse")).lower()
    best_frac = float(kwargs.pop("best_frac", DEFAULT_BEST_FRAC))
    n_lai = int(kwargs.get("n_lai", DEFAULT_N_LAI))
    n_cab = int(kwargs.get("n_cab", DEFAULT_N_CAB))
    height, width, bands = cube.shape
    wavelengths = np.asarray(wavelengths_nm) if wavelengths_nm is not None else default_wavelengths(bands)
    lut, lai_v, cab_v = build_lut(wavelengths, **kwargs)
    lai_flat, cab_flat, match_meta = match_lut(
        cube.reshape(-1, bands),
        lut,
        lai_v,
        cab_v,
        cost_method=cost_method,
        best_frac=best_frac,
    )
    meta = {
        "model": "PROSAIL-5 + 4SAIL",
        "lut_size": int(len(lai_v)),
        "n_lai": n_lai,
        "n_cab": n_cab,
        "wavelengths_nm": wavelengths.tolist(),
        "library": "prosail (PyPI)",
        **match_meta,
    }
    return (
        lai_flat.reshape(height, width).astype(np.float32),
        cab_flat.reshape(height, width).astype(np.float32),
        meta,
    )
