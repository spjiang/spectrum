"""NDSI归一化差值雪指数。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import ndvi_like, parse_params
from common.response import err_response, ok_response
from common.single_index import SingleIndexSuccess, run_single_band_index

ALGORITHM_ID = "55_ndsi"
TITLE = "NDSI归一化差值雪指数"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: green_band, swir_band。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    green_i = int(params.get("green_band", 1))
    swir_i = int(params.get("swir_band", 5))

    def compute(named, extras):
        _ = extras
        return ndvi_like(named["swir_band"], named["green_band"])

    result = await run_single_band_index(
        algorithm_id=ALGORITHM_ID,
        title=TITLE,
        file=file,
        bands={"green_band": green_i, "swir_band": swir_i},
        extras=None,
        compute=compute,
        file_stem="ndsi",
        preview_title="NDSI",
    )
    if not isinstance(result, SingleIndexSuccess):
        return result
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 NDSI，输出单波段 GeoTIFF 与预览 PNG",
        data=result.data,
        files={
            "ndsi_tif": str(result.tif_path),
            "preview_png": str(result.png_path),
        },
    )
