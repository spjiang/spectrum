"""大气校正：Chavez DOS2（USGS 暗目标，生产常用无 6S 许可时的标准算法）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.radiometry import default_wavelengths, dn_to_radiance, dos2_surface_reflectance

ALGORITHM_ID = "13_atmospheric_correction"
TITLE = "大气校正"
IMPLEMENTED = True
LEVEL = "L1→L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """辐亮度→DOS2 地表反射率。DN 输入时先按 gain/offset 定标。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    if float(cube.max()) > 2.0:
        cube = dn_to_radiance(cube, params.get("gain", 0.01), params.get("offset", 0.0))
    wl = np.asarray(params.get("wavelengths_nm") or default_wavelengths(cube.shape[2]), dtype=np.float64)
    if wl.size != cube.shape[2]:
        wl = default_wavelengths(cube.shape[2])
    rho, haze = dos2_surface_reflectance(
        cube,
        wl,
        solar_zenith_deg=float(params.get("solar_zenith", 30)),
        doy=int(params.get("doy", 180)),
        dark_percentile=float(params.get("dark_percentile", 1.0)),
    )
    tif = job / "reflectance_dos.tif"
    save_geotiff(rho.astype(np.float32), tif, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="Chavez DOS2 大气校正完成",
        data={
            "method": "DOS2",
            "solar_zenith": float(params.get("solar_zenith", 30)),
            "doy": int(params.get("doy", 180)),
            "haze_radiance": [float(x) for x in haze],
            "wavelengths_nm": [float(x) for x in wl],
            "shape": list(rho.shape),
            "min": float(rho.min()),
            "max": float(rho.max()),
            "format": "GeoTIFF",
        },
        files={"reflectance_tif": str(tif.resolve())},
    )
