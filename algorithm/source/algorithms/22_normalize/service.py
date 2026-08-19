"""标准化：Z-score / MinMax / SNV（光谱学生产预处理）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.preprocess import l2_normalize, snv

ALGORITHM_ID = "22_normalize"
TITLE = "标准化/归一化"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params.method: zscore | minmax | snv | l2"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    method = str(params.get("method", "snv")).lower()
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    if method == "minmax":
        mn = cube.min(axis=(0, 1), keepdims=True)
        mx = cube.max(axis=(0, 1), keepdims=True)
        out_arr = (cube - mn) / (mx - mn + 1e-12)
    elif method == "zscore":
        mean = cube.mean(axis=(0, 1), keepdims=True)
        std = cube.std(axis=(0, 1), keepdims=True) + 1e-12
        out_arr = (cube - mean) / std
    elif method == "l2":
        out_arr = l2_normalize(cube)
    else:
        out_arr = snv(cube)
        method = "snv"
    out = job / "cube_norm.tif"
    save_geotiff(out_arr.astype(np.float32), out, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"已完成 {method} 标准化",
        data={
            "method": method,
            "shape": list(out_arr.shape),
            "mean": float(out_arr.mean()),
            "std": float(out_arr.std()),
            "format": "GeoTIFF",
        },
        files={"cube_tif": str(out.resolve())},
    )
