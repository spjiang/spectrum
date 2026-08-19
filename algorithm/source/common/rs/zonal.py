"""矢量地块分区统计（rasterize + zonal）。"""
from __future__ import annotations

from typing import Any

import numpy as np
import rasterio.features
from rasterio.crs import CRS
from rasterio.warp import transform_geom


def _as_crs(value: Any) -> CRS | None:
    if value is None:
        return None
    if isinstance(value, CRS):
        return value
    try:
        return CRS.from_user_input(value)
    except Exception:
        return None


def _iter_features(geo: dict) -> list[dict]:
    if geo.get("type") == "FeatureCollection":
        return list(geo.get("features") or [])
    if geo.get("type") == "Feature":
        return [geo]
    if geo.get("type") in {"Polygon", "MultiPolygon", "Point", "LineString"}:
        return [{"type": "Feature", "properties": {}, "geometry": geo}]
    return []


def zonal_by_geojson(
    arr: np.ndarray,
    profile: dict[str, Any] | None,
    geo: dict,
    *,
    mode: str = "continuous",
) -> list[dict]:
    """
    将每个多边形栅格化到影像网格，统计落入像元。
    矢量与栅格 CRS 不一致时重投影几何。
    """
    if arr.ndim != 2:
        raise ValueError("分区统计需要 2D 栅格")
    transform = None if profile is None else profile.get("transform")
    if transform is None:
        from rasterio.transform import from_origin

        transform = from_origin(114.0600, 22.5400, 0.00001, 0.00001)
    raster_crs = _as_crs(None if profile is None else profile.get("crs"))
    src_crs = _as_crs((geo.get("crs") or {}).get("properties", {}).get("name") if isinstance(geo.get("crs"), dict) else None)
    if src_crs is None:
        src_crs = CRS.from_epsg(4326)
    feats = _iter_features(geo)
    rows = []
    for i, feat in enumerate(feats):
        geom = feat.get("geometry")
        props = dict(feat.get("properties") or {})
        if geom is None:
            continue
        if raster_crs is not None and src_crs is not None and raster_crs != src_crs:
            try:
                geom = transform_geom(src_crs, raster_crs, geom)
            except Exception:
                pass
        mask = rasterio.features.geometry_mask(
            [geom],
            out_shape=arr.shape,
            transform=transform,
            invert=True,
            all_touched=True,
        )
        pix = arr[mask]
        rec: dict[str, Any] = {
            "id": props.get("id", i),
            "name": props.get("name"),
            "pixel_count": int(pix.size),
            "properties": props,
        }
        if pix.size == 0:
            rec["empty"] = True
            rows.append(rec)
            continue
        if mode == "categorical":
            vals, counts = np.unique(pix.astype(np.int64), return_counts=True)
            total = int(counts.sum())
            rec["class_pixel_count"] = {str(int(v)): int(c) for v, c in zip(vals, counts)}
            rec["class_area_ratio"] = {str(int(v)): float(c / total) for v, c in zip(vals, counts)}
        else:
            rec.update(
                {
                    "mean": float(np.mean(pix)),
                    "std": float(np.std(pix)),
                    "min": float(np.min(pix)),
                    "max": float(np.max(pix)),
                    "p25": float(np.percentile(pix, 25)),
                    "p50": float(np.percentile(pix, 50)),
                    "p75": float(np.percentile(pix, 75)),
                }
            )
        rows.append(rec)
    return rows
