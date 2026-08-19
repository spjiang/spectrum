"""异常检测：Reed–Xiaoli / 局部 RX。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile
from scipy import ndimage as ndi

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response
from common.rs.rx import global_rx, local_rx

ALGORITHM_ID = "42_anomaly_detect"
TITLE = "异常检测"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params.method: lrx | rx；percentile；min_pixels。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    percentile = float(params.get("percentile", 95))
    min_pixels = int(params.get("min_pixels", 2))
    method = str(params.get("method", "lrx")).lower()
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    h, w, b = cube.shape
    if b < 2:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="RX 异常检测至少需要 2 个波段")
    if method == "rx":
        score = global_rx(cube)
        method = "reed_xiaoli"
    else:
        score = local_rx(cube, win=int(params.get("win", 7)), inner=int(params.get("inner", 3)))
        method = "local_rx"
    thr = float(np.percentile(score, percentile))
    mask = score >= thr
    if min_pixels > 1:
        labeled, n = ndi.label(mask)
        keep = np.zeros_like(mask)
        for i in range(1, n + 1):
            if int((labeled == i).sum()) >= min_pixels:
                keep[labeled == i] = True
        mask = keep
    score_tif = job / "anomaly_score.tif"
    mask_tif = job / "anomaly_mask.tif"
    png_path = job / "anomaly_preview.png"
    save_geotiff(score.astype(np.float32), score_tif, profile=profile)
    save_geotiff(mask.astype(np.uint8), mask_tif, profile=profile)
    save_preview_png(score, png_path, title=f"{method} score")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"已完成 {method} 光谱异常检测",
        data={
            "method": method,
            "bands": b,
            "percentile": percentile,
            "threshold": thr,
            "min_pixels": min_pixels,
            "n_anomaly_pixels": int(mask.sum()),
            "score_min": float(score.min()),
            "score_max": float(score.max()),
            "score_mean": float(score.mean()),
            "shape": [h, w],
            "format": "GeoTIFF",
        },
        files={
            "score_tif": str(score_tif.resolve()),
            "mask_tif": str(mask_tif.resolve()),
            "preview_png": str(png_path.resolve()),
        },
    )
