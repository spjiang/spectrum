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


def _stretch(band: np.ndarray) -> np.ndarray:
    """2%–98% 线性拉伸到 0–1。"""
    finite = band[np.isfinite(band)]
    if finite.size == 0:
        return np.zeros_like(band, dtype=np.float64)
    lo, hi = np.percentile(finite, (2, 98))
    if hi - lo < 1e-12:
        return np.clip(band - lo, 0, 1)
    return np.clip((band - lo) / (hi - lo), 0.0, 1.0)


def _to_hwc(arr: np.ndarray) -> np.ndarray:
    cube = as_cube(arr.astype(np.float64))
    return cube


def guess_mode(name: str, bands: int, arr: np.ndarray) -> str:
    """按文件名与波段数推断预览模式。"""
    n = name.lower()
    if any(k in n for k in ("mask", "class", "pred", "label", "superpixel")):
        return "class"
    if any(k in n for k in ("ndvi", "ndre", "score", "lai", "cab", "inversion", "magnitude", "chi2", "abundance")):
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


def _index_rgb(plane: np.ndarray) -> np.ndarray:
    g = _stretch(plane)
    return cm.RdYlGn(g)[:, :, :3]


def _class_rgb(plane: np.ndarray) -> np.ndarray:
    vals, inv = np.unique(np.nan_to_num(plane, nan=0.0).astype(np.int32), return_inverse=True)
    n = max(int(vals.size), 1)
    colors = cm.tab20(np.linspace(0, 1, n, endpoint=False))[:, :3]
    return colors[inv].reshape(plane.shape + (3,))


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
    if use == "falsecolor":
        rgb = _rgb_image(cube, bands)
    elif use == "class":
        rgb = _class_rgb(cube[:, :, 0] if b >= 1 else cube.reshape(h, w))
    elif use in {"index", "gray"}:
        rgb = _index_rgb(cube[:, :, 0])
    else:
        rgb = _rgb_image(cube, bands)
        use = "falsecolor"
    # 限制最长边
    scale = min(1.0, MAX_SIDE / max(h, w))
    if scale < 0.999:
        from scipy.ndimage import zoom

        rgb = zoom(rgb, (scale, scale, 1), order=1)
    fig, ax = plt.subplots(figsize=(5.2, 4.4), dpi=110)
    ax.imshow(np.clip(rgb, 0, 1), origin="upper")
    ax.set_axis_off()
    fig.tight_layout(pad=0.15)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    buf.seek(0)
    meta = {"height": h, "width": w, "bands": b, "mode": use, "name": path.name}
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
    return {
        "height": h,
        "width": w,
        "bands": b,
        "dtype": str(arr.dtype),
        "name": path.name,
        "crs": str(profile.get("crs")) if profile else None,
    }
