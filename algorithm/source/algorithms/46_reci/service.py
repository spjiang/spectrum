"""RECI红边叶绿素指数。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.response import err_response, ok_response
from common.single_index import SingleIndexSuccess, run_single_band_index

ALGORITHM_ID = "46_reci"
TITLE = "RECI红边叶绿素指数"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params: re_band, nir_band。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    re_i = int(params.get("re_band", 4))
    nir_i = int(params.get("nir_band", 3))

    def compute(named, extras):
        _ = extras
        return named["nir_band"] / (named["re_band"] + 1e-12) - 1.0

    result = await run_single_band_index(
        algorithm_id=ALGORITHM_ID,
        title=TITLE,
        file=file,
        bands={"re_band": re_i, "nir_band": nir_i},
        extras=None,
        compute=compute,
        file_stem="reci",
        preview_title="RECI",
    )
    if not isinstance(result, SingleIndexSuccess):
        return result
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已计算 RECI，输出单波段 GeoTIFF 与预览 PNG",
        data=result.data,
        files={
            "reci_tif": str(result.tif_path),
            "preview_png": str(result.png_path),
        },
    )
