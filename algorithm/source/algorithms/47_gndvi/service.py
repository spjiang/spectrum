"""GNDVI绿色归一化植被指数。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import ndvi_like, parse_params
from common.response import err_response, ok_response
from common.single_index import SingleIndexSuccess, run_single_band_index

ALGORITHM_ID = "47_gndvi"
TITLE = "GNDVI绿色归一化植被指数"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: green_band, nir_band。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    green_i = int(params.get("green_band", 1))
    nir_i = int(params.get("nir_band", 3))

    def compute(named, extras):
        _ = extras
        return ndvi_like(named["green_band"], named["nir_band"])

    result = await run_single_band_index(
        algorithm_id=ALGORITHM_ID,
        title=TITLE,
        file=file,
        bands={"green_band": green_i, "nir_band": nir_i},
        extras=None,
        compute=compute,
        file_stem="gndvi",
        preview_title="GNDVI",
    )
    if not isinstance(result, SingleIndexSuccess):
        return result
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 GNDVI，输出单波段 GeoTIFF 与预览 PNG",
        data=result.data,
        files={
            "gndvi_tif": str(result.tif_path),
            "preview_png": str(result.png_path),
        },
    )
