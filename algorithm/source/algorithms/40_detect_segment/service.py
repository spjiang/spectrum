"""语义分割/目标检测（教学实现）：基于 NDVI 低值斑块检测病斑/胁迫候选区。

输入多波段 GeoTIFF；可选 file2 GeoJSON（记录 AOI/标注，不强制）。
输出：得分图、二值掩膜 GeoTIFF、斑块 GeoJSON、预览 PNG。
"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile
from scipy import ndimage as ndi

from common.io import (
    as_cube,
    load_raster,
    load_text_or_json,
    new_job_dir,
    save_geotiff,
    save_preview_png,
    save_upload,
)
from common.response import err_response, ok_response

ALGORITHM_ID = "40_detect_segment"
TITLE = "语义分割/目标检测"
IMPLEMENTED = True
LEVEL = "L3"


def _mask_to_geojson(mask: np.ndarray, transform, crs) -> dict:
    """将二值掩膜转为 GeoJSON FeatureCollection（斑块多边形）。"""
    import rasterio.features
    from rasterio.crs import CRS

    feats = []
    # shapes 需要 int 标签；用连通域编号
    labeled, n = ndi.label(mask.astype(np.uint8))
    if n == 0:
        return {"type": "FeatureCollection", "features": []}

    crs_obj = CRS.from_user_input(crs) if crs is not None else None
    for geom, val in rasterio.features.shapes(
        labeled.astype(np.int32),
        mask=labeled > 0,
        transform=transform,
    ):
        vid = int(val)
        area_px = int((labeled == vid).sum())
        feats.append(
            {
                "type": "Feature",
                "properties": {
                    "object_id": vid,
                    "class": "stress_candidate",
                    "area_pixels": area_px,
                },
                "geometry": geom,
            }
        )
    fc = {"type": "FeatureCollection", "features": feats}
    if crs_obj is not None:
        fc["crs"] = {"type": "name", "properties": {"name": crs_obj.to_string()}}
    return fc


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """
    file: 多波段 GeoTIFF（反射率立方体）
    file2: 可选 GeoJSON（标注/AOI，写入结果元数据）
    params:
      - red_band / nir_band: NDVI 波段（0-based）
      - percentile: 低于该百分位的 NDVI 视为候选斑块（默认 20）
      - min_pixels: 小斑剔除阈值（默认 4）
    """
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    red_i = int(params.get("red_band", 2))
    nir_i = int(params.get("nir_band", 3))
    percentile = float(params.get("percentile", 20))
    min_pixels = int(params.get("min_pixels", 4))

    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    h, w, b = cube.shape
    if red_i >= b or nir_i >= b:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message=f"波段索引越界：red={red_i}, nir={nir_i}, bands={b}",
        )

    red = cube[:, :, red_i]
    nir = cube[:, :, nir_i]
    ndvi = (nir - red) / (nir + red + 1e-12)
    # 低 NDVI → 胁迫/病斑/裸土等候选；得分越高表示越异常偏低
    thr = float(np.percentile(ndvi, percentile))
    score = np.clip(thr - ndvi, 0, None)

    mask = ndvi <= thr
    # 小图跳过强开运算，避免样例数据斑块被抹掉
    if h >= 32 and w >= 32:
        mask = ndi.binary_opening(mask, structure=np.ones((3, 3), dtype=bool))
    else:
        mask = ndi.binary_opening(mask, structure=np.ones((2, 2), dtype=bool))
    labeled, n_raw = ndi.label(mask)
    keep = np.zeros_like(mask)
    for i in range(1, n_raw + 1):
        area = int((labeled == i).sum())
        if area >= min_pixels:
            keep[labeled == i] = True
    mask = keep
    labeled, n_obj = ndi.label(mask)

    transform = profile.get("transform") if profile else None
    crs = profile.get("crs") if profile else None
    if transform is None:
        from rasterio.transform import from_origin

        transform = from_origin(114.0600, 22.5400, 0.00001, 0.00001)

    geojson = _mask_to_geojson(mask, transform, crs)

    ann_meta = {"has_annotation_geojson": False, "annotation_features": 0}
    files: dict[str, str] = {}
    if file2 is not None:
        gpath = await save_upload(file2, job)
        if gpath.suffix.lower() in {".json", ".geojson"}:
            raw = load_text_or_json(gpath)
            ann_meta["has_annotation_geojson"] = True
            ann_meta["annotation_features"] = len(raw.get("features", [])) if isinstance(raw, dict) else 0
            files["annotation_geojson"] = str(gpath.resolve())

    score_tif = job / "detect_score.tif"
    mask_tif = job / "detect_mask.tif"
    geojson_path = job / "detect_polygons.geojson"
    png_path = job / "detect_preview.png"

    save_geotiff(score.astype(np.float32), score_tif, profile=profile)
    save_geotiff(mask.astype(np.uint8), mask_tif, profile=profile)
    geojson_path.write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")
    save_preview_png(score, png_path, title="Detect score (low-NDVI)")

    files.update(
        {
            "score_tif": str(score_tif.resolve()),
            "mask_tif": str(mask_tif.resolve()),
            "polygons_geojson": str(geojson_path.resolve()),
            "preview_png": str(png_path.resolve()),
        }
    )

    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已完成低 NDVI 斑块检测/分割（教学实现）；输出得分图、掩膜与斑块 GeoJSON",
        data={
            "method": "ndvi_low_blob",
            "red_band": red_i,
            "nir_band": nir_i,
            "percentile": percentile,
            "threshold_ndvi": thr,
            "min_pixels": min_pixels,
            "n_objects": int(n_obj),
            "n_positive_pixels": int(mask.sum()),
            "shape": [h, w],
            "format": "GeoTIFF+GeoJSON",
            **ann_meta,
        },
        files=files,
    )
