"""架次质检：位深饱和、欠曝、波段 SNR。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params, write_json
from common.io import as_cube, load_raster, new_job_dir, save_upload
from common.response import err_response, ok_response
from common.rs.qc import flight_qc

ALGORITHM_ID = "04_flight_qc"
TITLE = "架次质检（丢帧/过曝）"
IMPLEMENTED = True
LEVEL = "L0"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params.bit_depth、max_saturated_ratio。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, _ = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    bit_depth = params.get("bit_depth")
    report = flight_qc(
        cube,
        bit_depth=int(bit_depth) if bit_depth is not None else None,
        max_saturated_ratio=float(params.get("max_saturated_ratio", 0.01)),
    )
    out = job / "qc_report.json"
    write_json(out, report)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="架次质检通过" if report["passed"] else "过曝比例超阈值，建议复飞",
        data=report,
        files={"report_json": str(out.resolve())},
    )
