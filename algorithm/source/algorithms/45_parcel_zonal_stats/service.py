"""地块级汇总示意。输入指数/分类 GeoTIFF；可选 GeoJSON 地块（file2）。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile

from common.io import load_raster, load_text_or_json, new_job_dir, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "45_parcel_zonal_stats"
TITLE = "地块汇总与专题统计"
IMPLEMENTED = True
LEVEL = "L4"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """
    file: 单波段 GeoTIFF（指数或分类）
    file2: 可选 GeoJSON 地块（本期记录路径；统计仍用 params.roi 像素窗）
    params.roi: [r0, r1, c0, c1]；params.mode: continuous | categorical
    """
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    mode = str(params.get("mode", "continuous"))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, _ = load_raster(path)
    if arr.ndim == 3 and arr.shape[2] == 1:
        arr = arr[:, :, 0]
    if arr.ndim != 2:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message="地块汇总需要单波段 GeoTIFF（2D）",
        )

    files: dict[str, str] = {}
    has_geojson = False
    if file2 is not None:
        gpath = await save_upload(file2, job)
        if gpath.suffix.lower() in {".json", ".geojson"}:
            _ = load_text_or_json(gpath)
            has_geojson = True
            files["parcel_geojson"] = str(gpath.resolve())

    roi = params.get("roi")
    if roi is None:
        sub = arr
        roi_used = [0, arr.shape[0], 0, arr.shape[1]]
    else:
        r0, r1, c0, c1 = [int(x) for x in roi]
        sub = arr[r0:r1, c0:c1]
        roi_used = [r0, r1, c0, c1]

    if sub.size == 0:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="ROI 为空")

    data: dict = {
        "roi": roi_used,
        "mode": mode,
        "pixel_count": int(sub.size),
        "input_format": "GeoTIFF",
        "has_geojson": has_geojson,
    }
    if mode == "categorical":
        vals, counts = np.unique(sub.astype(int), return_counts=True)
        total = counts.sum()
        data["class_area_ratio"] = {str(int(v)): float(c / total) for v, c in zip(vals, counts)}
        data["class_pixel_count"] = {str(int(v)): int(c) for v, c in zip(vals, counts)}
    else:
        data.update(
            {
                "mean": float(sub.mean()),
                "std": float(sub.std()),
                "min": float(sub.min()),
                "max": float(sub.max()),
            }
        )

    report = job / "zonal_report.json"
    report.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    files["report_json"] = str(report.resolve())

    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="地块/ROI 汇总完成（栅格 GeoTIFF；矢量可用 GeoJSON）",
        data=data,
        files=files,
    )
