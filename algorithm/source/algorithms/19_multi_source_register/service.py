"""HSI-RGB 亚像元相位相关配准（Foroosh 2002）。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.register import register_to_reference

ALGORITHM_ID = "19_multi_source_register"
TITLE = "多源配准 HSI-RGB-矢量"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=HSI，file2=RGB。把 RGB 亚像元平移对齐到 HSI。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="配准需要 file2 RGB GeoTIFF")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    _ = params
    job = new_job_dir(ALGORITHM_ID)
    p1 = await save_upload(file, job)
    p2 = await save_upload(file2, job)
    hsi_arr, profile = load_raster(p1)
    rgb_arr, _ = load_raster(p2)
    hsi = as_cube(hsi_arr.astype(float))
    rgb = as_cube(rgb_arr.astype(float))
    aligned, meta = register_to_reference(hsi, rgb)
    hsi_tif = job / "hsi_ref.tif"
    rgb_tif = job / "rgb_aligned.tif"
    save_geotiff(hsi.astype("float32"), hsi_tif, profile=profile)
    save_geotiff(aligned.astype("float32"), rgb_tif, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"RGB 亚像元配准完成（dy={meta['dy']:.3f}, dx={meta['dx']:.3f}）",
        data={**meta, "hsi_shape": list(hsi.shape), "rgb_shape": list(aligned.shape), "format": "GeoTIFF"},
        files={"hsi_tif": str(hsi_tif.resolve()), "rgb_aligned_tif": str(rgb_tif.resolve())},
    )
