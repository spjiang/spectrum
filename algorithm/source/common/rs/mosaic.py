"""地理镶嵌：按 GeoTransform 重投影到统一网格，重叠区距离羽化。"""
from __future__ import annotations

from typing import Any

import numpy as np
from rasterio.transform import Affine, array_bounds, from_origin
from rasterio.warp import Resampling, reproject


def _edge_weight(h: int, w: int) -> np.ndarray:
    """到影像边缘的归一化距离，用作羽化权重。"""
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.minimum.reduce([yy + 1, xx + 1, h - yy, w - xx]).astype(np.float64)
    return d / (d.max() + 1e-12)


def mosaic_georeferenced(
    cubes: list[np.ndarray],
    profiles: list[dict[str, Any]],
) -> tuple[np.ndarray, dict[str, Any], dict]:
    """
    两景及以上 GeoTIFF 按地理范围镶嵌。
    重叠像元：距离边缘加权平均（feather）。
    """
    bounds = []
    resx, resy = None, None
    bands = min(c.shape[2] for c in cubes)
    for cube, prof in zip(cubes, profiles):
        h, w = cube.shape[:2]
        transform = Affine(*prof["transform"]) if not isinstance(prof["transform"], Affine) else prof["transform"]
        west, south, east, north = array_bounds(h, w, transform)
        crs = prof.get("crs")
        if crs is None:
            from rasterio.crs import CRS

            crs = CRS.from_epsg(4326)
            prof["crs"] = crs
        bounds.append((west, south, east, north))
        resx = abs(transform.a) if resx is None else min(resx, abs(transform.a))
        resy = abs(transform.e) if resy is None else min(resy, abs(transform.e))
    west = min(b[0] for b in bounds)
    south = min(b[1] for b in bounds)
    east = max(b[2] for b in bounds)
    north = max(b[3] for b in bounds)
    width = max(1, int(round((east - west) / resx)))
    height = max(1, int(round((north - south) / resy)))
    dst_transform = from_origin(west, north, resx, resy)
    acc = np.zeros((height, width, bands), dtype=np.float64)
    wsum = np.zeros((height, width), dtype=np.float64)
    for cube, prof in zip(cubes, profiles):
        src_t = Affine(*prof["transform"]) if not isinstance(prof["transform"], Affine) else prof["transform"]
        wt = _edge_weight(cube.shape[0], cube.shape[1])
        wt_dst = np.zeros((height, width), dtype=np.float64)
        reproject(
            source=wt.astype(np.float32),
            destination=wt_dst,
            src_transform=src_t,
            src_crs=prof.get("crs"),
            dst_transform=dst_transform,
            dst_crs=prof.get("crs"),
            resampling=Resampling.bilinear,
        )
        for bi in range(bands):
            dst = np.zeros((height, width), dtype=np.float64)
            reproject(
                source=cube[:, :, bi].astype(np.float32),
                destination=dst,
                src_transform=src_t,
                src_crs=prof.get("crs"),
                dst_transform=dst_transform,
                dst_crs=prof.get("crs"),
                resampling=Resampling.bilinear,
            )
            acc[:, :, bi] += dst * wt_dst
        wsum += wt_dst
    wsum = np.where(wsum < 1e-12, 1e-12, wsum)
    out = acc / wsum[:, :, None]
    profile = {
        "crs": profiles[0].get("crs"),
        "transform": dst_transform,
    }
    meta = {
        "method": "georeferenced_feather_mosaic",
        "n_scenes": len(cubes),
        "bounds": [west, south, east, north],
        "resolution": [resx, resy],
        "shape": list(out.shape),
    }
    return out.astype(np.float32), profile, meta
