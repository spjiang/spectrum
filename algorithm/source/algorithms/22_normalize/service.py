"""标准化 / 归一化。输入/输出 GeoTIFF。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile

from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "22_normalize"
TITLE = "标准化/归一化"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params.method: zscore | minmax"""
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    method = str(params.get("method", "zscore")).lower()
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    if method == "minmax":
        mn = cube.min(axis=(0, 1), keepdims=True)
        mx = cube.max(axis=(0, 1), keepdims=True)
        out_arr = (cube - mn) / (mx - mn + 1e-12)
    else:
        mean = cube.mean(axis=(0, 1), keepdims=True)
        std = cube.std(axis=(0, 1), keepdims=True) + 1e-12
        out_arr = (cube - mean) / std
        method = "zscore"
    out = job / "cube_norm.tif"
    save_geotiff(out_arr.astype(np.float32), out, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"已完成 {method} 标准化，输出 GeoTIFF",
        data={
            "method": method,
            "shape": list(out_arr.shape),
            "mean": float(out_arr.mean()),
            "std": float(out_arr.std()),
            "format": "GeoTIFF",
        },
        files={"cube_tif": str(out.resolve())},
    )
