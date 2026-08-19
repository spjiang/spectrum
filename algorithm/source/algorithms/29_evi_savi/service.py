"""EVI / SAVI / MSAVI 植被指数。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import check_bands, parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "29_evi_savi"
TITLE = "EVI/SAVI/MSAVI"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: blue_band, red_band, nir_band, L。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    blue_i = int(params.get("blue_band", 0))
    red_i = int(params.get("red_band", 2))
    nir_i = int(params.get("nir_band", 3))
    soil_l = float(params.get("L", 0.5))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    msg = check_bands(cube, blue=blue_i, red=red_i, nir=nir_i)
    if msg:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=msg)
    blue, red, nir = cube[:, :, blue_i], cube[:, :, red_i], cube[:, :, nir_i]
    evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
    savi = (1 + soil_l) * (nir - red) / (nir + red + soil_l)
    msavi = 0.5 * (2 * nir + 1 - np.sqrt((2 * nir + 1) ** 2 - 8 * (nir - red)))
    stack = np.stack([evi, savi, msavi], axis=-1).astype(np.float32)
    tif = job / "evi_savi_msavi.tif"
    png = job / "evi_preview.png"
    save_geotiff(stack, tif, profile=profile)
    save_preview_png(evi, png, title="EVI")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 EVI/SAVI/MSAVI（波段顺序：EVI,SAVI,MSAVI）",
        data={
            "blue_band": blue_i,
            "red_band": red_i,
            "nir_band": nir_i,
            "L": soil_l,
            "evi_mean": float(np.nanmean(evi)),
            "savi_mean": float(np.nanmean(savi)),
            "msavi_mean": float(np.nanmean(msavi)),
            "shape": list(stack.shape),
            "format": "GeoTIFF",
        },
        files={"indices_tif": str(tif.resolve()), "preview_png": str(png.resolve())},
    )
