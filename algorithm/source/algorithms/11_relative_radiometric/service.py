"""相对辐射归一：直方图匹配（镶嵌/多架次生产常用）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile
from skimage.exposure import match_histograms

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "11_relative_radiometric"
TITLE = "相对辐射归一"
IMPLEMENTED = True
LEVEL = "L1"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """将 file 各波段直方图匹配到 file2。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="相对辐射归一需要 file2 参考景")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    _ = params
    job = new_job_dir(ALGORITHM_ID)
    arr, profile = load_raster(await save_upload(file, job))
    arr2, _ = load_raster(await save_upload(file2, job))
    cube = as_cube(arr.astype(np.float64))
    ref = as_cube(arr2.astype(np.float64))
    if ref.shape[2] != cube.shape[2]:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="两景波段数须一致")
    h = min(cube.shape[0], ref.shape[0])
    w = min(cube.shape[1], ref.shape[1])
    out = cube.copy()
    for bi in range(cube.shape[2]):
        out[:h, :w, bi] = match_histograms(cube[:h, :w, bi], ref[:h, :w, bi])
    tif = job / "radiometric_aligned.tif"
    save_geotiff(out.astype(np.float32), tif, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="直方图匹配相对辐射归一完成",
        data={"method": "histogram_matching", "shape": list(out.shape), "format": "GeoTIFF"},
        files={"cube_tif": str(tif.resolve())},
    )
