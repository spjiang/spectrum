"""地理镶嵌：按 GeoTransform 重投影到统一网格，重叠区距离羽化。"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from rasterio.transform import Affine, array_bounds, from_origin
from rasterio.warp import Resampling, reproject
from rasterio.windows import Window, from_bounds, transform as window_transform

from common.rs.parallel import map_threads, worker_count


def _edge_weight(h: int, w: int) -> np.ndarray:
    """到影像边缘的归一化距离，用作羽化权重。"""
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.minimum.reduce([yy + 1, xx + 1, h - yy, w - xx]).astype(np.float64)
    return d / (d.max() + 1e-12)


def _as_affine(transform: Any) -> Affine:
    return transform if isinstance(transform, Affine) else Affine(*transform)


def _intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    """a/b 为 west, south, east, north。"""
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


def _edge_weight_window(h: int, w: int, r0: int, c0: int, rh: int, cw: int) -> np.ndarray:
    """窗口内到整幅边缘的距离，归一化与整幅 _edge_weight 一致。"""
    yy, xx = np.mgrid[r0 : r0 + rh, c0 : c0 + cw]
    d = np.minimum.reduce([yy + 1, xx + 1, h - yy, w - xx]).astype(np.float64)
    return d / (min(h, w) / 2.0 + 1e-12)


def raster_mosaic_profile(path: Path) -> dict[str, Any]:
    """只读地理元数据，不载入像元。"""
    import rasterio

    with rasterio.open(path) as src:
        return {
            "crs": src.crs,
            "transform": src.transform,
            "height": int(src.height),
            "width": int(src.width),
            "count": int(src.count),
        }


def mosaic_grid_from_profiles(
    profiles: list[dict[str, Any]],
) -> tuple[int, int, int, Affine, list[float], list[float]]:
    """由各景 height/width/count/transform 计算镶嵌网格，不分配像元。"""
    return mosaic_grid(None, profiles)


def mosaic_grid(
    cubes: list[np.ndarray] | None,
    profiles: list[dict[str, Any]],
) -> tuple[int, int, int, Affine, list[float], list[float]]:
    """计算镶嵌输出网格。返回 height, width, bands, transform, bounds, resolution。"""
    crs_values = [profile.get("crs") for profile in profiles]
    if any(crs is None for crs in crs_values):
        raise ValueError("所有输入影像必须具有 CRS")
    if any(crs != crs_values[0] for crs in crs_values[1:]):
        raise ValueError("输入影像 CRS 不一致，拒绝镶嵌")
    bounds = []
    resx, resy = None, None
    if cubes is not None:
        sizes = [(c.shape[0], c.shape[1], c.shape[2]) for c in cubes]
    else:
        sizes = [(int(p["height"]), int(p["width"]), int(p["count"])) for p in profiles]
    bands = min(item[2] for item in sizes)
    for (h, w, _b), prof in zip(sizes, profiles):
        transform = _as_affine(prof["transform"])
        west, south, east, north = array_bounds(h, w, transform)
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
    return height, width, bands, dst_transform, [west, south, east, north], [resx, resy]


def _feather_window(
    cubes: list[np.ndarray],
    profiles: list[dict[str, Any]],
    *,
    dst_transform: Affine,
    height: int,
    width: int,
    bands: int,
) -> np.ndarray:
    """把各景重投影到指定输出窗口并羽化。"""
    acc = np.zeros((height, width, bands), dtype=np.float64)
    wsum = np.zeros((height, width), dtype=np.float64)
    for cube, prof in zip(cubes, profiles):
        src_t = _as_affine(prof["transform"])
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
    return (acc / wsum[:, :, None]).astype(np.float32)


def collect_mosaic_paths(primary: Path, secondary: Path | None, extract_dir: Path) -> list[Path]:
    """file 为 zip 时解出全部 GeoTIFF；否则需要两条带。"""
    if primary.suffix.lower() == ".zip":
        extract_dir.mkdir(parents=True, exist_ok=True)
        import zipfile

        with zipfile.ZipFile(primary) as archive:
            archive.extractall(extract_dir)
        tifs = sorted({*extract_dir.rglob("*.tif"), *extract_dir.rglob("*.tiff")})
        if len(tifs) < 2:
            raise ValueError("zip 内至少需要两景 GeoTIFF")
        return tifs
    if secondary is None:
        raise ValueError("镶嵌需要 file2 第二条带 GeoTIFF")
    return [primary, secondary]


def collect_geotiff_paths(primary: Path, extract_dir: Path) -> list[Path]:
    """zip 解出全部 GeoTIFF；单文件则返回自身。至少一景。"""
    if primary.suffix.lower() != ".zip":
        return [primary]
    extract_dir.mkdir(parents=True, exist_ok=True)
    import zipfile

    with zipfile.ZipFile(primary) as archive:
        archive.extractall(extract_dir)
    tifs = sorted({*extract_dir.rglob("*.tif"), *extract_dir.rglob("*.tiff")})
    if not tifs:
        raise ValueError("zip 内没有 GeoTIFF")
    return tifs


def _feather_window_from_paths(
    paths: list[Path],
    profiles: list[dict[str, Any]],
    *,
    dst_transform: Affine,
    height: int,
    width: int,
    bands: int,
) -> np.ndarray:
    """按窗口从磁盘读取相交景并羽化，不载入整景。"""
    import rasterio

    acc = np.zeros((height, width, bands), dtype=np.float64)
    wsum = np.zeros((height, width), dtype=np.float64)
    dst_bounds = array_bounds(height, width, dst_transform)
    pad = 2
    for path, prof in zip(paths, profiles):
        src_h = int(prof["height"])
        src_w = int(prof["width"])
        src_t = _as_affine(prof["transform"])
        src_bounds = array_bounds(src_h, src_w, src_t)
        if not _intersects(dst_bounds, src_bounds):
            continue
        raw = from_bounds(*dst_bounds, transform=src_t)
        r0 = max(0, int(np.floor(raw.row_off)) - pad)
        c0 = max(0, int(np.floor(raw.col_off)) - pad)
        r1 = min(src_h, int(np.ceil(raw.row_off + raw.height)) + pad)
        c1 = min(src_w, int(np.ceil(raw.col_off + raw.width)) + pad)
        if r1 <= r0 or c1 <= c0:
            continue
        win = Window(c0, r0, c1 - c0, r1 - r0)
        win_t = window_transform(win, src_t)
        wt = _edge_weight_window(src_h, src_w, r0, c0, r1 - r0, c1 - c0)
        wt_dst = np.zeros((height, width), dtype=np.float64)
        reproject(
            source=wt.astype(np.float32),
            destination=wt_dst,
            src_transform=win_t,
            src_crs=prof.get("crs"),
            dst_transform=dst_transform,
            dst_crs=prof.get("crs"),
            resampling=Resampling.bilinear,
        )
        with rasterio.open(path) as src:
            for bi in range(bands):
                data = src.read(bi + 1, window=win)
                dst = np.zeros((height, width), dtype=np.float64)
                reproject(
                    source=data.astype(np.float32),
                    destination=dst,
                    src_transform=win_t,
                    src_crs=prof.get("crs"),
                    dst_transform=dst_transform,
                    dst_crs=prof.get("crs"),
                    resampling=Resampling.bilinear,
                )
                acc[:, :, bi] += dst * wt_dst
        wsum += wt_dst
    wsum = np.where(wsum < 1e-12, 1e-12, wsum)
    return (acc / wsum[:, :, None]).astype(np.float32)


def mosaic_georeferenced(
    cubes: list[np.ndarray],
    profiles: list[dict[str, Any]],
) -> tuple[np.ndarray, dict[str, Any], dict]:
    """
    两景及以上 GeoTIFF 按地理范围镶嵌。
    重叠像元：距离边缘加权平均（feather）。
    """
    height, width, bands, dst_transform, bounds, resolution = mosaic_grid(cubes, profiles)
    out = _feather_window(
        cubes,
        profiles,
        dst_transform=dst_transform,
        height=height,
        width=width,
        bands=bands,
    )
    profile = {
        "crs": profiles[0].get("crs"),
        "transform": dst_transform,
    }
    meta = {
        "method": "georeferenced_feather_mosaic",
        "n_scenes": len(cubes),
        "bounds": bounds,
        "resolution": resolution,
        "shape": list(out.shape),
    }
    return out, profile, meta


def _write_mosaic_tiles(
    *,
    height: int,
    width: int,
    bands: int,
    dst_transform: Affine,
    bounds: list[float],
    resolution: list[float],
    profiles: list[dict[str, Any]],
    n_scenes: int,
    out_path: Path,
    tile_size: int,
    workers: int,
    block_fn,
) -> dict:
    """按窗并行算块、串行写入。"""
    import rasterio

    from common.io import default_profile

    step = max(1, int(tile_size))
    n_workers = worker_count(workers)
    out_profile = default_profile(height, width, bands, "float32")
    out_profile["crs"] = profiles[0].get("crs")
    out_profile["transform"] = dst_transform
    if width >= 256 and height >= 256:
        out_profile["tiled"] = True
        out_profile["blockxsize"] = 256
        out_profile["blockysize"] = 256
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    windows = []
    for r0 in range(0, height, step):
        rh = min(step, height - r0)
        for c0 in range(0, width, step):
            cw = min(step, width - c0)
            windows.append((r0, c0, rh, cw))

    def _one(item: tuple[int, int, int, int]) -> tuple[int, int, int, int, np.ndarray]:
        r0, c0, rh, cw = item
        win = Window(c0, r0, cw, rh)
        win_t = window_transform(win, dst_transform)
        block = block_fn(win_t, rh, cw)
        return r0, c0, rh, cw, block

    batch = max(n_workers * 2, 1)
    with rasterio.open(out_path, "w", **out_profile) as dst:
        for i in range(0, len(windows), batch):
            chunk = windows[i : i + batch]
            for r0, c0, rh, cw, block in map_threads(_one, chunk, n_workers):
                dst.write(np.moveaxis(block, -1, 0), window=Window(c0, r0, cw, rh))
    return {
        "method": "georeferenced_feather_mosaic_tiled",
        "n_scenes": n_scenes,
        "bounds": bounds,
        "resolution": resolution,
        "shape": [height, width, bands],
        "tile_size": step,
        "workers": n_workers,
        "crs": profiles[0].get("crs"),
        "transform": dst_transform,
    }


def mosaic_georeferenced_to_path(
    cubes: list[np.ndarray],
    profiles: list[dict[str, Any]],
    out_path: Path,
    *,
    tile_size: int = 1024,
    workers: int = 0,
) -> dict:
    """分块写出镶嵌 GeoTIFF，避免整幅累加数组。"""
    height, width, bands, dst_transform, bounds, resolution = mosaic_grid(cubes, profiles)

    def block_fn(win_t, rh, cw):
        return _feather_window(
            cubes,
            profiles,
            dst_transform=win_t,
            height=rh,
            width=cw,
            bands=bands,
        )

    return _write_mosaic_tiles(
        height=height,
        width=width,
        bands=bands,
        dst_transform=dst_transform,
        bounds=bounds,
        resolution=resolution,
        profiles=profiles,
        n_scenes=len(cubes),
        out_path=out_path,
        tile_size=tile_size,
        workers=workers,
        block_fn=block_fn,
    )


def mosaic_paths_to_path(
    paths: list[Path],
    out_path: Path,
    *,
    tile_size: int = 1024,
    workers: int = 0,
) -> dict:
    """从磁盘分块镶嵌，峰值内存约为一个输出窗加相交源窗。"""
    profiles = [raster_mosaic_profile(path) for path in paths]
    height, width, bands, dst_transform, bounds, resolution = mosaic_grid_from_profiles(profiles)

    def block_fn(win_t, rh, cw):
        return _feather_window_from_paths(
            paths,
            profiles,
            dst_transform=win_t,
            height=rh,
            width=cw,
            bands=bands,
        )

    meta = _write_mosaic_tiles(
        height=height,
        width=width,
        bands=bands,
        dst_transform=dst_transform,
        bounds=bounds,
        resolution=resolution,
        profiles=profiles,
        n_scenes=len(paths),
        out_path=out_path,
        tile_size=tile_size,
        workers=workers,
        block_fn=block_fn,
    )
    meta["method"] = "georeferenced_feather_mosaic_stream"
    return meta
