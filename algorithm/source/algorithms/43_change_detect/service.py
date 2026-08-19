"""多时相变化检测：IR-MAD（Nielsen 2007）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response
from common.rs.change import ir_mad

ALGORITHM_ID = "43_change_detect"
TITLE = "多时相变化检测"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=T1，file2=T2。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="变化检测需要 file2 第二时相 GeoTIFF")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    percentile = float(params.get("percentile", 90))
    job = new_job_dir(ALGORITHM_ID)
    p1 = await save_upload(file, job)
    p2 = await save_upload(file2, job)
    c1, profile = load_raster(p1)
    c2, _ = load_raster(p2)
    c1 = as_cube(c1.astype(np.float64))
    c2 = as_cube(c2.astype(np.float64))
    chi, mag, meta = ir_mad(c1, c2, max_iter=int(params.get("max_iter", 15)))
    thr = float(np.percentile(chi, percentile))
    mask = (chi >= thr).astype(np.uint8)
    mag_tif = job / "change_magnitude.tif"
    chi_tif = job / "change_chi2.tif"
    mask_tif = job / "change_mask.tif"
    png = job / "change_preview.png"
    save_geotiff(mag, mag_tif, profile=profile)
    save_geotiff(chi, chi_tif, profile=profile)
    save_geotiff(mask, mask_tif, profile=profile)
    save_preview_png(chi, png, title="IR-MAD chi2")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="IR-MAD 变化检测完成",
        data={
            **meta,
            "percentile": percentile,
            "threshold": thr,
            "n_change": int(mask.sum()),
            "format": "GeoTIFF",
        },
        files={
            "magnitude_tif": str(mag_tif.resolve()),
            "chi2_tif": str(chi_tif.resolve()),
            "mask_tif": str(mask_tif.resolve()),
            "preview_png": str(png.resolve()),
        },
    )
