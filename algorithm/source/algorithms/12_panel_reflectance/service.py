"""白板/灰板反射率定标（示意）。输入 DN GeoTIFF，输出反射率 GeoTIFF。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile

from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "12_panel_reflectance"
TITLE = "白板/灰板反射率定标（示意）"
IMPLEMENTED = True
LEVEL = "L1→L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """将输入立方体按比例缩放到近似反射率。"""
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    scale = float(params.get("scale", 1.0 / 1000.0))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    refl = np.clip(cube * scale, 0.0, 1.0).astype(np.float32)
    out = job / "reflectance.tif"
    save_geotiff(refl, out, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已完成示意反射率定标，输出 GeoTIFF 反射率立方体",
        data={
            "shape": list(refl.shape),
            "scale": scale,
            "min": float(refl.min()),
            "max": float(refl.max()),
            "mean": float(refl.mean()),
            "format": "GeoTIFF",
        },
        files={"reflectance_tif": str(out.resolve())},
    )
