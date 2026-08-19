"""白板/灰板经验线法反射率定标（无人机高光谱生产主路径）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.radiometry import empirical_line, extract_dark_spectrum, extract_panel_spectrum

ALGORITHM_ID = "12_panel_reflectance"
TITLE = "白板/灰板反射率定标"
IMPLEMENTED = True
LEVEL = "L1→L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """
    ρ = ρ_panel * (L - L_dark) / (L_panel - L_dark)。
    参考板：params.panel_roi 或影像最亮百分位；暗点取最暗百分位。
    """
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    panel_rho = params.get("panel_reflectance", 0.6)
    roi = params.get("panel_roi")
    lp = extract_panel_spectrum(cube, roi=roi, bright_pct=float(params.get("bright_percentile", 99)))
    ld = extract_dark_spectrum(cube, dark_pct=float(params.get("dark_percentile", 1)))
    refl = empirical_line(cube, lp, panel_rho, ld).astype(np.float32)
    out = job / "reflectance.tif"
    save_geotiff(refl, out, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="经验线法（白板+暗点）反射率定标完成",
        data={
            "method": "empirical_line",
            "panel_reflectance": panel_rho,
            "panel_radiance": [float(x) for x in lp],
            "dark_radiance": [float(x) for x in ld],
            "shape": list(refl.shape),
            "min": float(refl.min()),
            "max": float(refl.max()),
            "mean": float(refl.mean()),
            "format": "GeoTIFF",
        },
        files={"reflectance_tif": str(out.resolve())},
    )
