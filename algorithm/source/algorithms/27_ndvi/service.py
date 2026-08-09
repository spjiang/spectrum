"""NDVI = (NIR - RED) / (NIR + RED)。输入/输出业界 GeoTIFF。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile

from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "27_ndvi"
TITLE = "NDVI植被指数"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: red_band, nir_band（0-based 波段索引）。"""
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    red_i = int(params.get("red_band", 2))
    nir_i = int(params.get("nir_band", 3))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    b = cube.shape[2]
    if red_i >= b or nir_i >= b:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message=f"波段索引越界：red={red_i}, nir={nir_i}, bands={b}",
        )
    red = cube[:, :, red_i]
    nir = cube[:, :, nir_i]
    ndvi = (nir - red) / (nir + red + 1e-12)
    tif_path = job / "ndvi.tif"
    png_path = job / "ndvi_preview.png"
    save_geotiff(ndvi.astype(np.float32), tif_path, profile=profile)
    save_preview_png(ndvi, png_path, title="NDVI")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 NDVI，输出 GeoTIFF 专题图与预览 PNG",
        data={
            "red_band": red_i,
            "nir_band": nir_i,
            "min": float(ndvi.min()),
            "max": float(ndvi.max()),
            "mean": float(ndvi.mean()),
            "shape": list(ndvi.shape),
            "format": "GeoTIFF",
        },
        files={"ndvi_tif": str(tif_path.resolve()), "preview_png": str(png_path.resolve())},
    )
