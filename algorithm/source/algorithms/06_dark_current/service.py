"""暗电流校正：暗帧相减 + 列向固定模式噪声。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.sensor import dark_current_correct

ALGORITHM_ID = "06_dark_current"
TITLE = "暗电流校正"
IMPLEMENTED = True
LEVEL = "L0→L1"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=DN，file2=暗电流参考。"""
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    _ = params
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    dark = None
    if file2 is not None:
        dpath = await save_upload(file2, job)
        dark_arr, _ = load_raster(dpath)
        dark = as_cube(dark_arr.astype(np.float64))
        if dark.shape != cube.shape:
            return err_response(
                algorithm_id=ALGORITHM_ID,
                algorithm=TITLE,
                message=f"暗帧尺寸须为 {cube.shape}，实际 {dark.shape}",
            )
    out_cube, meta = dark_current_correct(cube, dark)
    out = job / "dn_dark_corrected.tif"
    save_geotiff(out_cube.astype(np.float32), out, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="暗电流+列 FPN 校正完成",
        data={**meta, "shape": list(out_cube.shape), "mean": float(out_cube.mean()), "format": "GeoTIFF"},
        files={"cube_tif": str(out.resolve())},
    )
