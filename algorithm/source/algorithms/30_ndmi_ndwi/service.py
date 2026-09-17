"""NDMI / NDWI / MNDWI 水分与水体指数。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import check_bands, ndvi_like, parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "30_ndmi_ndwi"
TITLE = "NDMI/NDWI/MNDWI"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: green_band, nir_band, swir_band。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    g_i = int(params.get("green_band", 1))
    n_i = int(params.get("nir_band", 3))
    s_i = int(params.get("swir_band", 5))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    msg = check_bands(cube, green=g_i, nir=n_i, swir=s_i)
    if msg:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=msg)
    green, nir, swir = cube[:, :, g_i], cube[:, :, n_i], cube[:, :, s_i]
    ndmi = ndvi_like(swir, nir)
    ndwi = ndvi_like(nir, green)
    mndwi = ndvi_like(swir, green)
    ndmi_tif = job / "ndmi.tif"
    ndwi_tif = job / "ndwi.tif"
    mndwi_tif = job / "mndwi.tif"
    png = job / "ndwi_preview.png"
    save_geotiff(ndmi.astype(np.float32), ndmi_tif, profile=profile)
    save_geotiff(ndwi.astype(np.float32), ndwi_tif, profile=profile)
    save_geotiff(mndwi.astype(np.float32), mndwi_tif, profile=profile)
    save_preview_png(ndwi, png, title="NDWI")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 NDMI、NDWI、MNDWI，分别写出单波段 GeoTIFF",
        data={
            "green_band": g_i,
            "nir_band": n_i,
            "swir_band": s_i,
            "ndmi_mean": float(np.nanmean(ndmi)),
            "ndwi_mean": float(np.nanmean(ndwi)),
            "mndwi_mean": float(np.nanmean(mndwi)),
            "shape": list(ndmi.shape),
            "format": "GeoTIFF",
        },
        files={
            "ndmi_tif": str(ndmi_tif.resolve()),
            "ndwi_tif": str(ndwi_tif.resolve()),
            "mndwi_tif": str(mndwi_tif.resolve()),
            "preview_png": str(png.resolve()),
        },
    )
