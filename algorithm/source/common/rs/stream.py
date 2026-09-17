"""大栅格按窗读写，避免整景立方体一次进内存。"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import numpy as np

from common.io import as_cube, default_profile

# 超过该像元数则走抽样/分块；演示数据远小于此值，行为不变。
STREAM_PIXELS = 2_000_000


def raster_hwc(path: Path) -> tuple[int, int, int]:
    import rasterio

    with rasterio.open(path) as src:
        return int(src.height), int(src.width), int(src.count)


def should_stream(path: Path) -> bool:
    suffix = path.suffix.lower()
    if suffix not in {".tif", ".tiff", ".geotiff"}:
        return False
    h, w, b = raster_hwc(path)
    return h * w * max(b, 1) > STREAM_PIXELS


def iter_windows(height: int, width: int, tile_size: int):
    step = max(1, int(tile_size))
    for r0 in range(0, height, step):
        rh = min(step, height - r0)
        for c0 in range(0, width, step):
            cw = min(step, width - c0)
            yield r0, c0, rh, cw


def read_overview_cube(path: Path, max_pixels: int = STREAM_PIXELS) -> np.ndarray:
    """抽稀到约 max_pixels 的立方体，用于质检/白板统计。"""
    import rasterio

    with rasterio.open(path) as src:
        h, w, b = src.height, src.width, src.count
        n = h * w
        if n <= max_pixels:
            data = src.read()
        else:
            scale = (max_pixels / float(n)) ** 0.5
            nh = max(16, int(round(h * scale)))
            nw = max(16, int(round(w * scale)))
            data = src.read(out_shape=(b, nh, nw))
    return as_cube(np.moveaxis(data, 0, -1).astype(np.float64))


def map_geotiff_windows(
    in_path: Path,
    out_path: Path,
    fn: Callable[[np.ndarray], np.ndarray],
    *,
    tile_size: int = 1024,
    profile: dict | None = None,
) -> tuple[int, int, int]:
    """逐窗读取、变换、写出。fn 输入/输出均为 HxWxB。"""
    import rasterio
    from rasterio.windows import Window

    with rasterio.open(in_path) as src:
        height, width, bands = int(src.height), int(src.width), int(src.count)
        src_profile = src.profile.copy()
        out_profile = default_profile(height, width, bands, "float32")
        for key in ("crs", "transform", "compress"):
            if profile and key in profile and profile[key] is not None:
                out_profile[key] = profile[key]
            elif key in src_profile and src_profile[key] is not None:
                out_profile[key] = src_profile[key]
        if width >= 256 and height >= 256:
            out_profile["tiled"] = True
            out_profile["blockxsize"] = 256
            out_profile["blockysize"] = 256
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(out_path, "w", **out_profile) as dst:
            for r0, c0, rh, cw in iter_windows(height, width, tile_size):
                win = Window(c0, r0, cw, rh)
                data = src.read(window=win)
                cube = as_cube(np.moveaxis(data, 0, -1).astype(np.float64))
                out = fn(cube).astype(np.float32)
                dst.write(np.moveaxis(out, -1, 0), window=win)
    return height, width, bands
