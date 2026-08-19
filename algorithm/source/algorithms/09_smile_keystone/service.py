"""光谱微笑 / 关键畸变：场景内互相关估计 + 三次样条/双线性重采样。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.spectral_geo import smile_keystone_correct

ALGORITHM_ID = "09_smile_keystone"
TITLE = "光谱微笑/关键畸变校正"
IMPLEMENTED = True
LEVEL = "L0→L1"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """无实验室文件时用中心列/中心波段作参考，估计 smile 与 keystone。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    _ = params
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(float))
    out, meta = smile_keystone_correct(cube)
    tif = job / "smile_corrected.tif"
    save_geotiff(out.astype("float32"), tif, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已完成场景内 smile/keystone 校正",
        data={**meta, "shape": list(out.shape), "format": "GeoTIFF"},
        files={"cube_tif": str(tif.resolve())},
    )
