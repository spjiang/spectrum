"""匀色：Wallis 局部自适应滤波（正射镶嵌匀光生产常用）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile
from scipy.ndimage import uniform_filter

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "18_color_balance"
TITLE = "匀色与接缝线优化"
IMPLEMENTED = True
LEVEL = "L2"


def _wallis(band: np.ndarray, win: int, contrast: float, brightness: float) -> np.ndarray:
    local_mean = uniform_filter(band, size=win, mode="reflect")
    local_sqr = uniform_filter(band * band, size=win, mode="reflect")
    local_std = np.sqrt(np.clip(local_sqr - local_mean**2, 0, None)) + 1e-6
    g_mean = float(band.mean())
    g_std = float(band.std()) + 1e-6
    return (band - local_mean) * (contrast * g_std) / (local_std + contrast * g_std) + brightness * g_mean + (
        1.0 - brightness
    ) * local_mean


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """逐波段 Wallis 匀光。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    win = int(params.get("window", 7))
    contrast = float(params.get("contrast", 0.8))
    brightness = float(params.get("brightness", 0.5))
    job = new_job_dir(ALGORITHM_ID)
    arr, profile = load_raster(await save_upload(file, job))
    cube = as_cube(arr.astype(np.float64))
    out = np.empty_like(cube)
    for bi in range(cube.shape[2]):
        out[:, :, bi] = _wallis(cube[:, :, bi], win, contrast, brightness)
    tif = job / "color_balanced.tif"
    png = job / "color_preview.png"
    save_geotiff(out.astype(np.float32), tif, profile=profile)
    save_preview_png(out.mean(axis=2), png, title="Wallis")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="Wallis 匀光完成",
        data={"method": "wallis", "window": win, "contrast": contrast, "brightness": brightness, "shape": list(out.shape), "format": "GeoTIFF"},
        files={"cube_tif": str(tif.resolve()), "preview_png": str(png.resolve())},
    )
