"""OSAVI优化土壤调节植被指数。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.response import err_response, ok_response
from common.single_index import SingleIndexSuccess, run_single_band_index

ALGORITHM_ID = "48_osavi"
TITLE = "OSAVI优化土壤调节植被指数"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: red_band, nir_band, L。文献默认 L=0.16。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    red_i = int(params.get("red_band", 2))
    nir_i = int(params.get("nir_band", 3))
    soil_l = float(params.get("L", 0.16))

    def compute(named, extras):
        soil = extras["L"]
        nir, red = named["nir_band"], named["red_band"]
        return (nir - red) / (nir + red + soil)

    result = await run_single_band_index(
        algorithm_id=ALGORITHM_ID,
        title=TITLE,
        file=file,
        bands={"red_band": red_i, "nir_band": nir_i},
        extras={"L": soil_l},
        compute=compute,
        file_stem="osavi",
        preview_title="OSAVI",
    )
    if not isinstance(result, SingleIndexSuccess):
        return result
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 OSAVI，输出单波段 GeoTIFF 与预览 PNG",
        data=result.data,
        files={
            "osavi_tif": str(result.tif_path),
            "preview_png": str(result.png_path),
        },
    )
