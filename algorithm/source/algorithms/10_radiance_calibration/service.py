"""辐射定标：DN → 辐亮度（逐波段增益/偏置）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.radiometry import dn_to_radiance

ALGORITHM_ID = "10_radiance_calibration"
TITLE = "辐射定标 DN→辐亮度"
IMPLEMENTED = True
LEVEL = "L0→L1"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """L = gain_b * DN + offset_b。gain/offset 可为标量或长度=波段的列表。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    gain = params.get("gain", 0.01)
    offset = params.get("offset", 0.0)
    rad = dn_to_radiance(cube, gain, offset).astype(np.float32)
    tif = job / "radiance.tif"
    save_geotiff(rad, tif, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已完成实验室线性辐射定标 DN→辐亮度",
        data={
            "gain": gain if not isinstance(gain, list) else [float(x) for x in gain],
            "offset": offset if not isinstance(offset, list) else [float(x) for x in offset],
            "shape": list(rad.shape),
            "min": float(rad.min()),
            "max": float(rad.max()),
            "units": "W/m^2/sr/um（与增益单位一致）",
            "format": "GeoTIFF",
        },
        files={"radiance_tif": str(tif.resolve())},
    )
