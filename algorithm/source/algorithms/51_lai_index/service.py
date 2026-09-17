"""叶面积经验指数（EVI 线性式，不是 #33 PROSAIL）。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.response import err_response, ok_response
from common.single_index import SingleIndexSuccess, run_single_band_index

ALGORITHM_ID = "51_lai_index"
TITLE = "叶面积经验指数"
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
        blue, red, nir = named["blue_band"], named["red_band"], named["nir_band"]
        evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
        return (3.618 * evi - 0.118).clip(min=0)

    result = await run_single_band_index(
        algorithm_id=ALGORITHM_ID,
        title=TITLE,
        file=file,
        bands={"blue_band": blue_i, "red_band": red_i, "nir_band": nir_i},
        extras=None,
        compute=compute,
        file_stem="lai_index",
        preview_title="LAI index",
    )
    if not isinstance(result, SingleIndexSuccess):
        return result
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 EVI 线性经验 LAI，输出单波段 GeoTIFF 与预览 PNG；不是 #33 PROSAIL",
        data=result.data,
        files={
            "lai_index_tif": str(result.tif_path),
            "preview_png": str(result.png_path),
        },
    )
