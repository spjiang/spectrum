"""坏波段剔除：SNR + 大气吸收窗口，并入手动 drop_bands。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.badband import auto_drop_bands

ALGORITHM_ID = "20_bad_band_remove"
TITLE = "坏波段剔除与光谱去噪"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params.drop_bands 与自动检测取并集。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    extra = [int(x) for x in params.get("drop_bands", [])]
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr)
    wl = params.get("wavelengths_nm")
    drop, keep, meta = auto_drop_bands(
        cube,
        wavelength_nm=None if wl is None else wl,
        extra_drop=extra,
        snr_ratio=float(params.get("snr_ratio", 0.4)),
    )
    if not keep:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="剔除后无剩余波段")
    out_cube = cube[:, :, keep]
    out = job / "cube_clean.tif"
    save_geotiff(out_cube, out, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"已剔除 {len(drop)} 个波段（SNR/吸收/手动），剩余 {len(keep)}",
        data={
            "input_bands": cube.shape[2],
            "dropped": drop,
            "kept": keep,
            "shape": list(out_cube.shape),
            "format": "GeoTIFF",
            **meta,
        },
        files={"cube_tif": str(out.resolve())},
    )
