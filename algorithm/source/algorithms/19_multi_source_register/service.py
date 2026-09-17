"""HSI-RGB 亚像元相位相关配准（Foroosh 2002）。"""
from __future__ import annotations

import asyncio

from fastapi import UploadFile

from common.impl import parse_params
from common.io import new_job_dir, save_upload
from common.response import err_response, ok_response
from common.rs.register import register_to_path

ALGORITHM_ID = "19_multi_source_register"
TITLE = "HSI-RGB全局平移配准"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=HSI，file2=RGB。把 RGB 亚像元平移对齐到 HSI。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="配准需要 file2 RGB GeoTIFF")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    tile_size = int(params.get("tile_size", 512))
    workers = int(params.get("workers", 0))
    job = new_job_dir(ALGORITHM_ID)
    p1 = await save_upload(file, job)
    p2 = await save_upload(file2, job)
    hsi_tif = job / "hsi_ref.tif"
    rgb_tif = job / "rgb_aligned.tif"

    def _compute():
        return register_to_path(
            p1,
            p2,
            hsi_tif,
            rgb_tif,
            tile_size=tile_size,
            workers=workers,
        )

    meta = await asyncio.to_thread(_compute)
    import rasterio

    with rasterio.open(hsi_tif) as hsi, rasterio.open(rgb_tif) as rgb:
        hsi_shape = [int(hsi.height), int(hsi.width), int(hsi.count)]
        rgb_shape = [int(rgb.height), int(rgb.width), int(rgb.count)]
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"RGB 亚像元配准完成（dy={meta['dy']:.3f}, dx={meta['dx']:.3f}）",
        data={**meta, "hsi_shape": hsi_shape, "rgb_shape": rgb_shape, "format": "GeoTIFF"},
        files={"hsi_tif": str(hsi_tif.resolve()), "rgb_aligned_tif": str(rgb_tif.resolve())},
    )
