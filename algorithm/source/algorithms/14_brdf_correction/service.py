"""BRDF：Ross-Thick / Li-Sparse 核驱动归一到天底（MODIS ATBD）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.brdf import nadir_normalize

ALGORITHM_ID = "14_brdf_correction"
TITLE = "BRDF/观测几何校正"
IMPLEMENTED = True
LEVEL = "L1→L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """按列视场角做 RTLS 天底归一。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    sza = float(params.get("solar_zenith", 30))
    vz_max = float(params.get("view_zenith", 10))
    raa = float(params.get("relative_azimuth", 0))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    h, w, _ = cube.shape
    vz = np.linspace(-vz_max, vz_max, w)[None, :].repeat(h, axis=0)
    out = nadir_normalize(
        cube,
        solar_zenith=sza,
        view_zenith=vz,
        relative_azimuth=raa,
        f_iso=float(params.get("f_iso", 0.2)),
        f_vol=float(params.get("f_vol", 0.1)),
        f_geo=float(params.get("f_geo", 0.05)),
    ).astype(np.float32)
    tif = job / "brdf_corrected.tif"
    save_geotiff(out, tif, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="Ross-Li BRDF 天底归一完成",
        data={
            "method": "ross_li_rtls",
            "solar_zenith": sza,
            "view_zenith_edge": vz_max,
            "relative_azimuth": raa,
            "shape": list(out.shape),
            "format": "GeoTIFF",
        },
        files={"cube_tif": str(tif.resolve())},
    )
