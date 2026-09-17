"""VARI可见大气阻力指数。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.response import err_response, ok_response
from common.single_index import SingleIndexSuccess, run_single_band_index

ALGORITHM_ID = "50_vari"
TITLE = "VARI可见大气阻力指数"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: blue_band, green_band, red_band。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    blue_i = int(params.get("blue_band", 0))
    green_i = int(params.get("green_band", 1))
    red_i = int(params.get("red_band", 2))

    def compute(named, extras):
        _ = extras
        green, red, blue = named["green_band"], named["red_band"], named["blue_band"]
        return (green - red) / (green + red - blue + 1e-12)

    result = await run_single_band_index(
        algorithm_id=ALGORITHM_ID,
        title=TITLE,
        file=file,
        bands={"blue_band": blue_i, "green_band": green_i, "red_band": red_i},
        extras=None,
        compute=compute,
        file_stem="vari",
        preview_title="VARI",
    )
    if not isinstance(result, SingleIndexSuccess):
        return result
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 VARI，输出单波段 GeoTIFF 与预览 PNG",
        data=result.data,
        files={
            "vari_tif": str(result.tif_path),
            "preview_png": str(result.png_path),
        },
    )
