"""NDRE = (NIR - RE) / (NIR + RE)。输入/输出 GeoTIFF。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile

from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "28_ndre"
TITLE = "NDRE红边植被指数"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: re_band, nir_band。"""
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    re_i = int(params.get("re_band", 4))
    nir_i = int(params.get("nir_band", 3))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    b = cube.shape[2]
    if re_i >= b or nir_i >= b:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message=f"波段索引越界：re={re_i}, nir={nir_i}, bands={b}",
        )
    re = cube[:, :, re_i]
    nir = cube[:, :, nir_i]
    ndre = (nir - re) / (nir + re + 1e-12)
    tif_path = job / "ndre.tif"
    png_path = job / "ndre_preview.png"
    save_geotiff(ndre.astype(np.float32), tif_path, profile=profile)
    save_preview_png(ndre, png_path, title="NDRE")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 NDRE，输出 GeoTIFF 专题图与预览 PNG",
        data={
            "re_band": re_i,
            "nir_band": nir_i,
            "min": float(ndre.min()),
            "max": float(ndre.max()),
            "mean": float(ndre.mean()),
            "shape": list(ndre.shape),
            "format": "GeoTIFF",
        },
        files={"ndre_tif": str(tif_path.resolve()), "preview_png": str(png_path.resolve())},
    )
