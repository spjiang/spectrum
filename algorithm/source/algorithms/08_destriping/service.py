"""条带噪声：列向矩匹配（Gadallah / ENVI 推扫去条纹）。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.spectral_geo import moment_matching_destripe

ALGORITHM_ID = "08_destriping"
TITLE = "条带噪声去除"
IMPLEMENTED = True
LEVEL = "L0→L1"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """每列均值/标准差对齐到整幅。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    _ = params
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(float))
    out = moment_matching_destripe(cube).astype("float32")
    tif = job / "destripe.tif"
    save_geotiff(out, tif, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="列向矩匹配去条带完成",
        data={"method": "column_moment_matching", "shape": list(out.shape), "format": "GeoTIFF"},
        files={"cube_tif": str(tif.resolve())},
    )
