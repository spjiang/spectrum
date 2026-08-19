"""坏波段自动检测：SNR + 大气吸收窗口。"""
from __future__ import annotations

import numpy as np

from common.rs.qc import band_snr
from common.rs.radiometry import default_wavelengths

# 大气吸收（nm）：O2-A、水汽
ABSORPTION_WINDOWS = (
    (750.0, 775.0),
    (930.0, 970.0),
    (1100.0, 1160.0),
    (1350.0, 1480.0),
    (1800.0, 1960.0),
)


def absorption_indices(wavelength_nm: np.ndarray) -> list[int]:
    """落在吸收窗口内的波段索引。"""
    out = []
    for i, wl in enumerate(wavelength_nm):
        if any(lo <= wl <= hi for lo, hi in ABSORPTION_WINDOWS):
            out.append(int(i))
    return out


def auto_drop_bands(
    cube: np.ndarray,
    *,
    wavelength_nm: np.ndarray | None = None,
    extra_drop: list[int] | None = None,
    snr_ratio: float = 0.4,
) -> tuple[list[int], list[int], dict]:
    """
    剔除：手动指定 ∪ 低 SNR ∪ 吸收带。
    至少保留 2 个最高 SNR 波段。
    返回 (drop, keep, meta)。
    """
    b = cube.shape[2]
    snr = band_snr(cube.astype(np.float64))
    wl = np.asarray(wavelength_nm) if wavelength_nm is not None else default_wavelengths(b)
    drop = set(int(i) for i in (extra_drop or []) if 0 <= int(i) < b)
    drop.update(absorption_indices(wl))
    med = float(np.median(snr))
    drop.update(int(i) for i, s in enumerate(snr) if s < snr_ratio * max(med, 1e-6))
    keep = [i for i in range(b) if i not in drop]
    if len(keep) < 2:
        order = np.argsort(snr)[::-1]
        keep = [int(i) for i in order[: max(2, min(b, 2))]]
        drop = set(range(b)) - set(keep)
    meta = {
        "method": "snr+absorption",
        "snr_per_band": [float(x) for x in snr],
        "wavelength_nm": [float(x) for x in wl],
        "snr_ratio": snr_ratio,
    }
    return sorted(drop), keep, meta
