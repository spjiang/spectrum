"""正射：共线方程 + DEM 直接地理定位（单片或 zip 多片并行）。"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.mosaic import collect_geotiff_paths, mosaic_paths_to_path
from common.rs.parallel import map_threads, worker_count
from common.rs.photogrammetry import orthorectify_collinearity

ALGORITHM_ID = "16_orthorectify"
TITLE = "正射校正"
IMPLEMENTED = True
LEVEL = "L1→L2"


def _ortho_one(frame: Path, dem: object, kwargs: dict, out_dir: Path) -> Path:
    arr, profile = load_raster(frame)
    cube = as_cube(arr.astype(float))
    out, _meta = orthorectify_collinearity(cube, dem, **kwargs)
    dest = out_dir / f"{frame.stem}_ortho.tif"
    save_geotiff(out.astype("float32"), dest, profile=profile)
    return dest


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=影像或 zip 多片，file2=DEM。共线方程将地面格网点投影回像方重采样。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="正射需要 file2 DEM GeoTIFF")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    dem_arr = load_raster(await save_upload(file2, job))[0]
    if dem_arr.ndim == 3:
        dem_arr = dem_arr[:, :, 0]
    workers = int(params.get("workers", 0))
    tile_rows = int(params.get("tile_rows", 256))
    gsd_out = params.get("gsd_out")
    kwargs = dict(
        altitude_m=float(params.get("alt_m", 120)),
        roll_deg=float(params.get("roll", 0)),
        pitch_deg=float(params.get("pitch", 0)),
        yaw_deg=float(params.get("yaw", 0)),
        focal_mm=float(params.get("focal_mm", 8.0)),
        pixel_um=float(params.get("pixel_um", 5.5)),
        tile_rows=tile_rows,
        gsd_out=float(gsd_out) if gsd_out is not None else None,
        workers=1,
    )
    tif = job / "ortho.tif"

    def _compute():
        frames = collect_geotiff_paths(path, job / "frames_in")
        n = worker_count(workers)
        if len(frames) == 1:
            arr, profile = load_raster(frames[0])
            cube = as_cube(arr.astype(float))
            one_kwargs = dict(kwargs)
            one_kwargs["workers"] = n
            out, meta = orthorectify_collinearity(cube, dem_arr, **one_kwargs)
            save_geotiff(out.astype("float32"), tif, profile=profile)
            meta["shape"] = list(out.shape)
            return meta
        frame_dir = job / "frames"
        frame_dir.mkdir(parents=True, exist_ok=True)
        outs = map_threads(lambda frame: _ortho_one(frame, dem_arr, kwargs, frame_dir), frames, n)
        if len(outs) == 1:
            import shutil

            shutil.copy2(outs[0], tif)
            meta = {"n_frames": 1, "tile_rows": tile_rows, "workers": n}
        else:
            meta = mosaic_paths_to_path(outs, tif, tile_size=1024, workers=n)
            meta["n_frames"] = len(outs)
        return meta

    meta = await asyncio.to_thread(_compute)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="共线方程+DEM 正射完成",
        data={**meta, "format": "GeoTIFF"},
        files={"ortho_tif": str(tif.resolve())},
    )
