"""红边位置：Guyot 线性内插 + SG 导数峰值。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response
from common.rs.radiometry import default_wavelengths
from common.rs.rededge import derivative_rep, guyot_rep

ALGORITHM_ID = "31_red_edge_params"
TITLE = "红边位置与光谱特征参数"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """输出波段：Guyot REP、红边振幅、导数 REP。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    w0 = float(params.get("wl_start_nm", 450.0))
    w1 = float(params.get("wl_end_nm", 850.0))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(float))
    if cube.shape[2] < 3:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="红边参数至少需要 3 个波段")
    wl = default_wavelengths(cube.shape[2], w0, w1)
    rep, amp, meta = guyot_rep(cube, wl)
    drep = derivative_rep(cube, wl)
    stack = np.stack([rep, amp, drep], axis=-1)
    tif = job / "red_edge_params.tif"
    png = job / "rep_preview.png"
    save_geotiff(stack.astype("float32"), tif, profile=profile)
    save_preview_png(rep, png, title="Guyot red-edge position (nm)")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="Guyot 红边位置 + 振幅 + SG 导数峰值",
        data={
            **meta,
            "wl_start_nm": w0,
            "wl_end_nm": w1,
            "rep_mean": float(rep.mean()),
            "amp_mean": float(amp.mean()),
            "deriv_rep_mean": float(drep.mean()),
            "shape": list(stack.shape),
            "format": "GeoTIFF",
            "bands": ["guyot_rep_nm", "red_edge_amplitude", "sg_derivative_rep_nm"],
        },
        files={"params_tif": str(tif.resolve()), "preview_png": str(png.resolve())},
    )
