"""线性解混：FCLS 全约束最小二乘（Heinz & Chang 2001）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import load_endmember_csv, parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response
from common.rs.unmixing import fcls

ALGORITHM_ID = "41_unmixing"
TITLE = "混合像元分解"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """非负且丰度和为 1。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="解混需要 file2 端元 CSV")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    cube, profile = load_raster(await save_upload(file, job))
    cube = as_cube(cube.astype(np.float64))
    em = load_endmember_csv(await save_upload(file2, job))
    h, w, b = cube.shape
    if em.shape[0] != b:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=f"端元波段 {em.shape[0]} 与影像 {b} 不一致")
    abund = fcls(em, cube.reshape(-1, b), delta=float(params.get("delta", 10)))
    abund = abund.reshape(h, w, em.shape[1]).astype(np.float32)
    tif = job / "abundance.tif"
    png = job / "abundance_preview.png"
    save_geotiff(abund, tif, profile=profile)
    save_preview_png(abund[:, :, 0], png, title="FCLS abundance e0")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"FCLS 解混完成，端元 {em.shape[1]} 类",
        data={
            "method": "FCLS",
            "n_endmembers": int(em.shape[1]),
            "abundance_mean": [float(abund[:, :, i].mean()) for i in range(em.shape[1])],
            "sum_to_one_mean": float(abund.sum(axis=2).mean()),
            "shape": list(abund.shape),
            "format": "GeoTIFF",
        },
        files={"abundance_tif": str(tif.resolve()), "preview_png": str(png.resolve())},
    )
