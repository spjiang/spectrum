"""地块汇总：GeoJSON 栅格化后逐多边形分区统计。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile

from common.io import load_raster, load_text_or_json, new_job_dir, save_upload
from common.response import err_response, ok_response
from common.rs.zonal import zonal_by_geojson

ALGORITHM_ID = "45_parcel_zonal_stats"
TITLE = "地块汇总与专题统计"
IMPLEMENTED = True
LEVEL = "L4"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """
    file: 单波段 GeoTIFF（指数或分类）
    file2: GeoJSON 地块（推荐）。无矢量时统计整幅。
    params.mode: continuous | categorical
    """
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    mode = str(params.get("mode", "continuous"))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    if arr.ndim == 3 and arr.shape[2] == 1:
        arr = arr[:, :, 0]
    if arr.ndim != 2:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message="地块汇总需要单波段 GeoTIFF（2D）",
        )

    files: dict[str, str] = {}
    parcels: list[dict] = []
    geo = None
    if file2 is not None:
        gpath = await save_upload(file2, job)
        if gpath.suffix.lower() in {".json", ".geojson"}:
            geo = load_text_or_json(gpath)
            files["parcel_geojson"] = str(gpath.resolve())
            if isinstance(geo, dict):
                parcels = zonal_by_geojson(arr, profile, geo, mode=mode)

    whole = arr.ravel()
    if mode == "categorical":
        vals, counts = np.unique(whole.astype(int), return_counts=True)
        total = int(counts.sum())
        scene = {
            "class_area_ratio": {str(int(v)): float(c / total) for v, c in zip(vals, counts)},
            "class_pixel_count": {str(int(v)): int(c) for v, c in zip(vals, counts)},
        }
    else:
        scene = {
            "mean": float(whole.mean()),
            "std": float(whole.std()),
            "min": float(whole.min()),
            "max": float(whole.max()),
        }

    data = {
        "mode": mode,
        "method": "rasterize_zonal",
        "n_parcels": len(parcels),
        "n_parcels_with_pixels": int(sum(1 for p in parcels if p.get("pixel_count", 0) > 0)),
        "scene": scene,
        "parcels": parcels,
        "input_format": "GeoTIFF",
        "has_geojson": geo is not None,
    }
    report = job / "zonal_report.json"
    report.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    files["report_json"] = str(report.resolve())
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"分区统计完成：{len(parcels)} 个多边形，{data['n_parcels_with_pixels']} 个有像元",
        data=data,
        files=files,
    )
