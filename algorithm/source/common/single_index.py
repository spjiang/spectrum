"""单波段植被指数：反射率立方体 → 一个 GeoTIFF。"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from fastapi import UploadFile

from common.impl import check_bands
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response

ComputeFn = Callable[[dict[str, np.ndarray], dict[str, float]], np.ndarray]


@dataclass(frozen=True)
class SingleIndexSuccess:
    """写出指数图后的路径与统计；由各 service 用字面量 files 键封装 ok_response。"""

    data: dict
    tif_path: Path
    png_path: Path


async def run_single_band_index(
    *,
    algorithm_id: str,
    title: str,
    file: UploadFile,
    bands: dict[str, int],
    extras: dict[str, float] | None = None,
    compute: ComputeFn,
    file_stem: str,
    preview_title: str,
):
    """按已解析的波段索引取反射率，写出单波段指数图与预览 PNG。"""
    extras = extras or {}
    job = new_job_dir(algorithm_id)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    msg = check_bands(cube, **bands)
    if msg:
        return err_response(algorithm_id=algorithm_id, algorithm=title, message=msg)
    named = {name: cube[:, :, idx] for name, idx in bands.items()}
    index = np.asarray(compute(named, extras), dtype=np.float64)
    tif_path = job / f"{file_stem}.tif"
    png_path = job / f"{file_stem}_preview.png"
    save_geotiff(index.astype(np.float32), tif_path, profile=profile)
    save_preview_png(index, png_path, title=preview_title)
    data = {
        **bands,
        **extras,
        "min": float(np.nanmin(index)),
        "max": float(np.nanmax(index)),
        "mean": float(np.nanmean(index)),
        "shape": list(index.shape),
        "format": "GeoTIFF",
    }
    return SingleIndexSuccess(
        data=data,
        tif_path=tif_path.resolve(),
        png_path=png_path.resolve(),
    )
