"""坏波段剔除。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile

from common.io import as_cube, load_array, new_job_dir, save_npy, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "20_bad_band_remove"
TITLE = "坏波段剔除与光谱去噪"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """按索引删除指定波段。params: {\"drop_bands\": [0, 5, 10]}"""
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    drop = [int(x) for x in params.get("drop_bands", [])]
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    cube = as_cube(load_array(path))
    bands = cube.shape[2]
    keep = [i for i in range(bands) if i not in set(drop)]
    if not keep:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="剔除后无剩余波段")
    out_cube = cube[:, :, keep]
    out = job / "cube_clean.npy"
    save_npy(out_cube, out)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"已剔除 {len(drop)} 个波段，剩余 {len(keep)} 个",
        data={"input_bands": bands, "dropped": drop, "kept": keep, "shape": list(out_cube.shape)},
        files={"cube_npy": str(out.resolve())},
    )
