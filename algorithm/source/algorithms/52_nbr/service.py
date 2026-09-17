"""NBR标准化燃烧率。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import ndvi_like, parse_params
from common.response import err_response, ok_response
from common.single_index import SingleIndexSuccess, run_single_band_index

ALGORITHM_ID = "52_nbr"
TITLE = "NBR标准化燃烧率"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: nir_band, swir_band。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    nir_i = int(params.get("nir_band", 3))
    swir_i = int(params.get("swir_band", 5))

    def compute(named, extras):
        _ = extras
        return ndvi_like(named["swir_band"], named["nir_band"])

    result = await run_single_band_index(
        algorithm_id=ALGORITHM_ID,
        title=TITLE,
        file=file,
        bands={"nir_band": nir_i, "swir_band": swir_i},
        extras=None,
        compute=compute,
        file_stem="nbr",
        preview_title="NBR",
    )
    if not isinstance(result, SingleIndexSuccess):
        return result
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 NBR，输出单波段 GeoTIFF 与预览 PNG",
        data=result.data,
        files={
            "nbr_tif": str(result.tif_path),
            "preview_png": str(result.png_path),
        },
    )
