"""正射：共线方程 + DEM 直接地理定位（单片生产路径）。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.photogrammetry import orthorectify_collinearity

ALGORITHM_ID = "16_orthorectify"
TITLE = "正射校正"
IMPLEMENTED = True
LEVEL = "L1→L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=影像，file2=DEM。共线方程将地面格网点投影回像方重采样。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="正射需要 file2 DEM GeoTIFF")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(float))
    dem = load_raster(await save_upload(file2, job))[0]
    if dem.ndim == 3:
        dem = dem[:, :, 0]
    out, meta = orthorectify_collinearity(
        cube,
        dem,
        altitude_m=float(params.get("alt_m", 120)),
        roll_deg=float(params.get("roll", 0)),
        pitch_deg=float(params.get("pitch", 0)),
        yaw_deg=float(params.get("yaw", 0)),
        focal_mm=float(params.get("focal_mm", 8.0)),
        pixel_um=float(params.get("pixel_um", 5.5)),
    )
    tif = job / "ortho.tif"
    save_geotiff(out.astype("float32"), tif, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="共线方程+DEM 正射完成",
        data={**meta, "shape": list(out.shape), "format": "GeoTIFF"},
        files={"ortho_tif": str(tif.resolve())},
    )
