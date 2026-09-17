"""栅格预览：假彩色 / 指数色带 / 分类色块，以及点选光谱。"""
from __future__ import annotations

import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

from common.io import as_cube, load_raster
from common.rs.radiometry import default_wavelengths

MAX_SIDE = 768
INDEX_FILE_KEYS = (
    "ndvi",
    "ndre",
    "evi",
    "savi",
    "msavi",
    "ndmi",
    "ndwi",
    "mndwi",
    "score",
    "lai",
    "cab",
    "inversion",
    "magnitude",
    "chi2",
    "abundance",
    "index",
    "reci",
    "gndvi",
    "osavi",
    "arvi",
    "vari",
    "lai_index",
    "nbr",
    "sipi",
    "gci",
    "ndsi",
)
CLASS_FILE_KEYS = ("mask", "class", "pred", "label", "superpixel")


def _percentile_limits(band: np.ndarray) -> tuple[float, float]:
    """取有效像元的 2% 与 98% 分位，作为色带两端读数。"""
    finite = band[np.isfinite(band)]
    if finite.size == 0:
        return 0.0, 1.0
    lo, hi = np.percentile(finite, (2, 98))
    if hi - lo < 1e-12:
        return float(lo), float(lo + 1.0)
    return float(lo), float(hi)


def _stretch(band: np.ndarray) -> np.ndarray:
    """2%–98% 线性拉伸到 0–1。"""
    lo, hi = _percentile_limits(band)
    return np.clip((band - lo) / (hi - lo), 0.0, 1.0)


def _to_hwc(arr: np.ndarray) -> np.ndarray:
    cube = as_cube(arr.astype(np.float64))
    return cube


def guess_mode(name: str, bands: int, arr: np.ndarray) -> str:
    """按文件名与波段数推断预览模式。"""
    n = name.lower()
    if any(k in n for k in CLASS_FILE_KEYS):
        return "class"
    if any(k in n for k in INDEX_FILE_KEYS):
        return "index"
    if bands >= 3:
        return "falsecolor"
    # 单波段：类别很少则当分类
    if arr.ndim == 2 or (arr.ndim == 3 and arr.shape[2] == 1):
        plane = arr if arr.ndim == 2 else arr[:, :, 0]
        uniq = np.unique(plane[np.isfinite(plane)])
        if 1 < uniq.size <= 24 and np.allclose(uniq, np.round(uniq)):
            return "class"
        return "index"
    return "gray"


def _rgb_image(cube: np.ndarray, bands: tuple[int, int, int] | None) -> np.ndarray:
    h, w, b = cube.shape
    if b == 1:
        g = _stretch(cube[:, :, 0])
        return np.stack([g, g, g], axis=-1)
    if b == 2:
        r, g = _stretch(cube[:, :, 1]), _stretch(cube[:, :, 0])
        return np.stack([r, g, np.zeros_like(r)], axis=-1)
    if bands is None:
        # 优先 NIR-R-G：默认 3,2,1；不足则取末三波段
        if b >= 4:
            idx = (min(3, b - 1), 2, 1)
        else:
            idx = (b - 1, b - 2, max(b - 3, 0))
    else:
        idx = tuple(int(np.clip(i, 0, b - 1)) for i in bands)
    return np.stack([_stretch(cube[:, :, i]) for i in idx], axis=-1)


def _class_rgb(plane: np.ndarray) -> np.ndarray:
    vals, inv = np.unique(np.nan_to_num(plane, nan=0.0).astype(np.int32), return_inverse=True)
    n = max(int(vals.size), 1)
    colors = cm.tab20(np.linspace(0, 1, n, endpoint=False))[:, :3]
    return colors[inv].reshape(plane.shape + (3,))


def _color_scale(plane: np.ndarray) -> dict:
    lo, hi = _percentile_limits(plane)
    return {
        "colorLow": lo,
        "colorHigh": hi,
        "colorMid": float((lo + hi) / 2.0),
        "colorMap": "RdYlGn",
    }


def raster_png_bytes(
    path: Path,
    *,
    mode: str = "auto",
    bands: tuple[int, int, int] | None = None,
) -> tuple[bytes, dict]:
    """把 GeoTIFF 渲染为 PNG 字节。"""
    arr, _profile = load_raster(path)
    cube = _to_hwc(arr)
    h, w, b = cube.shape
    use = guess_mode(path.name, b, arr) if mode in {"auto", "", None} else mode
    color_meta: dict = {}
    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=110)
    scale = min(1.0, MAX_SIDE / max(h, w))

    if use in {"index", "gray"}:
        plane = cube[:, :, 0]
        color_meta = _color_scale(plane)
        display = plane
        if scale < 0.999:
            from scipy.ndimage import zoom

            display = zoom(plane, scale, order=1)
        im = ax.imshow(
            display,
            cmap="RdYlGn",
            vmin=color_meta["colorLow"],
            vmax=color_meta["colorHigh"],
            origin="upper",
        )
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(labelsize=8)
    elif use == "class":
        plane = cube[:, :, 0] if b >= 1 else cube.reshape(h, w)
        rgb = _class_rgb(plane)
        if scale < 0.999:
            from scipy.ndimage import zoom

            rgb = zoom(rgb, (scale, scale, 1), order=0)
        ax.imshow(np.clip(rgb, 0, 1), origin="upper")
    else:
        rgb = _rgb_image(cube, bands)
        if use != "falsecolor":
            use = "falsecolor"
        if scale < 0.999:
            from scipy.ndimage import zoom

            rgb = zoom(rgb, (scale, scale, 1), order=1)
        ax.imshow(np.clip(rgb, 0, 1), origin="upper")

    ax.set_axis_off()
    fig.tight_layout(pad=0.15)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    buf.seek(0)
    meta = {"height": h, "width": w, "bands": b, "mode": use, "name": path.name, **color_meta}
    return buf.getvalue(), meta


def spectrum_at(path: Path, row: int, col: int) -> dict:
    """读取指定像元光谱。"""
    arr, _ = load_raster(path)
    cube = _to_hwc(arr)
    h, w, b = cube.shape
    r = int(np.clip(row, 0, h - 1))
    c = int(np.clip(col, 0, w - 1))
    values = cube[r, c, :].astype(float).tolist()
    wl = default_wavelengths(b).tolist()
    return {
        "row": r,
        "col": c,
        "bands": b,
        "wavelengths_nm": wl,
        "values": values,
    }


def raster_meta(path: Path) -> dict:
    """栅格尺寸元数据。"""
    arr, profile = load_raster(path)
    cube = _to_hwc(arr)
    h, w, b = cube.shape
    meta = {
        "height": h,
        "width": w,
        "bands": b,
        "dtype": str(arr.dtype),
        "name": path.name,
        "crs": str(profile.get("crs")) if profile else None,
        "mode": guess_mode(path.name, b, arr),
    }
    if meta["mode"] in {"index", "gray"}:
        meta.update(_color_scale(cube[:, :, 0]))
    return meta
