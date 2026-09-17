"""白板/灰板经验线法反射率定标（无人机高光谱生产主路径）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.radiometry import empirical_line, extract_dark_spectrum, extract_panel_spectrum
from common.rs.stream import map_geotiff_windows, read_overview_cube, should_stream

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
    panel_rho = params.get("panel_reflectance", 0.6)
    roi = params.get("panel_roi")
    out = job / "reflectance.tif"
    use_stream = should_stream(path) and not roi
    if use_stream:
        cube_stats = read_overview_cube(path)
        lp = extract_panel_spectrum(cube_stats, roi=None, bright_pct=float(params.get("bright_percentile", 99)))
        ld = extract_dark_spectrum(cube_stats, dark_pct=float(params.get("dark_percentile", 1)))

        def _fn(cube: np.ndarray) -> np.ndarray:
            return empirical_line(cube, lp, panel_rho, ld)

        h, w, b = map_geotiff_windows(path, out, _fn)
        preview = read_overview_cube(out)
        vmin, vmax, mean = float(preview.min()), float(preview.max()), float(preview.mean())
        shape = [h, w, b]
    else:
        arr, profile = load_raster(path)
        cube = as_cube(arr.astype(np.float64))
        lp = extract_panel_spectrum(cube, roi=roi, bright_pct=float(params.get("bright_percentile", 99)))
        ld = extract_dark_spectrum(cube, dark_pct=float(params.get("dark_percentile", 1)))
        refl = empirical_line(cube, lp, panel_rho, ld).astype(np.float32)
        save_geotiff(refl, out, profile=profile)
        vmin, vmax, mean = float(refl.min()), float(refl.max()), float(refl.mean())
        shape = list(refl.shape)
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
            "shape": shape,
            "min": vmin,
            "max": vmax,
            "mean": mean,
            "format": "GeoTIFF",
        },
        files={"reflectance_tif": str(out.resolve())},
    )
