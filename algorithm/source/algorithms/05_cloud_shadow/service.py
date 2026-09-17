"""云/暗区：受 Fmask 启发的简化光谱规则。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response
from common.rs.cloud import fmask_spectral

ALGORITHM_ID = "05_cloud_shadow"
TITLE = "云/云影检测"
IMPLEMENTED = True
LEVEL = "L0"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """受 Fmask 启发的简化光谱规则 + 近红外候选暗区。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(float))
    cloud, shadow = fmask_spectral(
        cube,
        blue=int(params.get("blue_band", 0)),
        green=int(params.get("green_band", 1)),
        red=int(params.get("red_band", 2)),
        nir=int(params.get("nir_band", 3)),
        swir=int(params.get("swir_band", 5)) if cube.shape[2] > 5 else None,
    )
    mask = shadow.astype("uint8")
    mask[cloud > 0] = 2
    cloud_tif = job / "cloud_mask.tif"
    shadow_tif = job / "shadow_mask.tif"
    combo_tif = job / "cloud_shadow_mask.tif"
    png = job / "cloud_shadow_preview.png"
    save_geotiff(cloud, cloud_tif, profile=profile)
    save_geotiff(shadow, shadow_tif, profile=profile)
    save_geotiff(mask, combo_tif, profile=profile)
    save_preview_png(mask.astype(float), png, title="cloud=2 candidate-shadow=1")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="简化光谱云与候选暗区检测完成",
        data={
            "method": "fmask_spectral",
            "n_cloud": int(cloud.sum()),
            "n_shadow": int(shadow.sum()),
            "legend": {"0": "clear", "1": "shadow", "2": "cloud"},
            "format": "GeoTIFF",
        },
        files={
            "cloud_mask_tif": str(cloud_tif.resolve()),
            "shadow_mask_tif": str(shadow_tif.resolve()),
            "combo_mask_tif": str(combo_tif.resolve()),
            "preview_png": str(png.resolve()),
        },
    )
