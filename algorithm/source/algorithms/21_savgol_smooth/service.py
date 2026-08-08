"""Savitzky-Golay 光谱平滑。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile
from scipy.signal import savgol_filter

from common.io import as_cube, load_array, new_job_dir, save_npy, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "21_savgol_smooth"
TITLE = "Savitzky-Golay平滑"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """沿波段维做 SG 平滑。params: window_length, polyorder"""
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    window = int(params.get("window_length", 5))
    poly = int(params.get("polyorder", 2))
    if window % 2 == 0:
        window += 1
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    cube = as_cube(load_array(path).astype(np.float64))
    if cube.shape[2] < window:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message=f"波段数 {cube.shape[2]} 小于 window_length {window}",
        )
    # 沿光谱维平滑
    smooth = savgol_filter(cube, window_length=window, polyorder=poly, axis=2, mode="nearest")
    out = job / "cube_smooth.npy"
    save_npy(smooth, out)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已完成 Savitzky-Golay 光谱平滑",
        data={"shape": list(smooth.shape), "window_length": window, "polyorder": poly},
        files={"cube_npy": str(out.resolve())},
    )
