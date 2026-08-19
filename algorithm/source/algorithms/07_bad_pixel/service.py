"""坏线/坏像元：6σ 热/死像元检测 + 邻域填充。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, load_text_or_json, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.sensor import detect_bad_mask, fill_bad_pixels

ALGORITHM_ID = "07_bad_pixel"
TITLE = "坏线/坏像元修复"
IMPLEMENTED = True
LEVEL = "L0→L1"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=DN；可选 file2/params 提供 bad_cols / bad_pixels，否则自动检测。"""
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    h, w, _b = cube.shape
    table = dict(params)
    if file2 is not None:
        tpath = await save_upload(file2, job)
        if tpath.suffix.lower() in {".json", ".geojson"}:
            raw = load_text_or_json(tpath)
            if isinstance(raw, dict):
                table.update(raw)
    auto_mask, auto_cols = detect_bad_mask(cube, z_thr=float(params.get("z_thr", 6.0)))
    mask = auto_mask.copy()
    bad_cols = [int(x) for x in table.get("bad_cols", [])] + auto_cols
    for c in bad_cols:
        if 0 <= c < w:
            mask[:, c] = True
    for r, c in table.get("bad_pixels", []):
        r, c = int(r), int(c)
        if 0 <= r < h and 0 <= c < w:
            mask[r, c] = True
    out = fill_bad_pixels(cube, mask)
    tif = job / "dn_repaired.tif"
    save_geotiff(out.astype(np.float32), tif, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"已修复 {int(mask.sum())} 个坏像元位置（含自动检测）",
        data={
            "method": "median_residual_6sigma + bilinear_fill",
            "n_bad_cols": len(set(bad_cols)),
            "n_auto_cols": len(auto_cols),
            "n_masked": int(mask.sum()),
            "shape": list(out.shape),
            "format": "GeoTIFF",
        },
        files={"cube_tif": str(tif.resolve())},
    )
