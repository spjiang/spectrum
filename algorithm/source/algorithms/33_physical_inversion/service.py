"""PROSAIL LUT 物理反演：不用化验图，一次给出叶面积和叶绿素两张图。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response
from common.rs.prosail_inv import COST_METHODS, invert_cube

ALGORITHM_ID = "33_physical_inversion"
TITLE = "辐射传输物理反演"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """不用化验图，一次给出叶面积和叶绿素图。PROSPECT-5 + 4SAIL 查找表，默认 RMSE，对最优若干条取平均。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    n_lai = int(params.get("n_lai", 25))
    n_cab = int(params.get("n_cab", 16))
    best_frac = float(params.get("best_frac", 0.05))
    cost_method = str(params.get("cost_method", "rmse")).lower()
    if cost_method not in COST_METHODS:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message="cost_method 仅支持 rmse 或 sam",
        )
    if n_lai < 2 or n_cab < 2:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message="n_lai 与 n_cab 均须 ≥ 2",
        )
    if not (0.0 < best_frac <= 1.0):
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message="best_frac 须在 (0, 1] 内",
        )
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(float))
    wavelengths = params.get("wavelengths_nm")
    try:
        lai, cab, meta = invert_cube(
            cube,
            None if wavelengths is None else wavelengths,
            solar_zenith=float(params.get("solar_zenith", 30)),
            view_zenith=float(params.get("view_zenith", 0)),
            relative_azimuth=float(params.get("relative_azimuth", 0)),
            n_lai=n_lai,
            n_cab=n_cab,
            best_frac=best_frac,
            cost_method=cost_method,
        )
    except Exception as exc:  # noqa: BLE001
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=f"PROSAIL 反演失败: {exc}")
    lai_tif = job / "lai.tif"
    cab_tif = job / "cab.tif"
    png = job / "lai_preview.png"
    save_geotiff(lai, lai_tif, profile=profile)
    save_geotiff(cab, cab_tif, profile=profile)
    save_preview_png(lai, png, title="PROSAIL LAI")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="PROSAIL LUT 反演完成（LAI、Cab）",
        data={
            **meta,
            "lai_mean": float(lai.mean()),
            "lai_max": float(lai.max()),
            "cab_mean": float(cab.mean()),
            "shape": list(lai.shape),
            "format": "GeoTIFF",
        },
        files={
            "lai_tif": str(lai_tif.resolve()),
            "cab_tif": str(cab_tif.resolve()),
            "preview_png": str(png.resolve()),
        },
    )
