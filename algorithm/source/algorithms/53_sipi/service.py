"""SIPI结构不敏感色素指数。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.response import err_response, ok_response
from common.single_index import SingleIndexSuccess, run_single_band_index

ALGORITHM_ID = "53_sipi"
TITLE = "SIPI结构不敏感色素指数"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: blue_band, red_band, nir_band。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    blue_i = int(params.get("blue_band", 0))
    red_i = int(params.get("red_band", 2))
    nir_i = int(params.get("nir_band", 3))

    def compute(named, extras):
        _ = extras
        nir, blue, red = named["nir_band"], named["blue_band"], named["red_band"]
        return (nir - blue) / (nir - red + 1e-12)

    result = await run_single_band_index(
        algorithm_id=ALGORITHM_ID,
        title=TITLE,
        file=file,
        bands={"blue_band": blue_i, "red_band": red_i, "nir_band": nir_i},
        extras=None,
        compute=compute,
        file_stem="sipi",
        preview_title="SIPI",
    )
    if not isinstance(result, SingleIndexSuccess):
        return result
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 SIPI，输出单波段 GeoTIFF 与预览 PNG",
        data=result.data,
        files={
            "sipi_tif": str(result.tif_path),
            "preview_png": str(result.png_path),
        },
    )
