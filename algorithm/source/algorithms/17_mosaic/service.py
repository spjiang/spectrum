"""影像镶嵌：按地理参考重投影，重叠区距离羽化。"""
from __future__ import annotations

import asyncio

from fastapi import UploadFile

from common.impl import parse_params
from common.io import new_job_dir, save_upload
from common.response import err_response, ok_response
from common.rs.mosaic import collect_mosaic_paths, mosaic_paths_to_path

ALGORITHM_ID = "17_mosaic"
TITLE = "影像匹配与镶嵌"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file / file2 为已地理参考的航带；file 也可为含多景 GeoTIFF 的 zip。"""
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    tile_size = int(params.get("tile_size", 1024))
    workers = int(params.get("workers", 0))
    job = new_job_dir(ALGORITHM_ID)
    p1 = await save_upload(file, job)
    if p1.suffix.lower() != ".zip" and file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="镶嵌需要 file2 第二条带 GeoTIFF")
    p2 = await save_upload(file2, job) if file2 is not None else None
    try:
        paths = collect_mosaic_paths(p1, p2, job / "strips")
    except ValueError as exc:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=str(exc))
    tif = job / "mosaic.tif"

    def _compute():
        return mosaic_paths_to_path(paths, tif, tile_size=tile_size, workers=workers)

    try:
        meta = await asyncio.to_thread(_compute)
    except ValueError as exc:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=str(exc))
    meta.pop("transform", None)
    if meta.get("crs") is not None:
        meta["crs"] = str(meta["crs"])
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"地理镶嵌+羽化完成，共 {meta['n_scenes']} 景",
        data={**meta, "format": "GeoTIFF"},
        files={"mosaic_tif": str(tif.resolve())},
    )
