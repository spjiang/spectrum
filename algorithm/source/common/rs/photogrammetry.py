"""摄影测量：GSD/航线、直接地理定位共线方程、DEM 正射。"""
from __future__ import annotations

import math

import numpy as np
from scipy.ndimage import map_coordinates

from common.rs.parallel import map_threads, worker_count


def meters_per_deg(lat_deg: float) -> tuple[float, float]:
    """返回 (米/度经度, 米/度纬度)。"""
    lat = math.radians(lat_deg)
    m_lat = 111_132.92 - 559.82 * math.cos(2 * lat) + 1.175 * math.cos(4 * lat)
    m_lon = 111_412.84 * math.cos(lat) - 93.5 * math.cos(3 * lat)
    return abs(m_lon), abs(m_lat)


def gsd_m(altitude_m: float, pixel_um: float, focal_mm: float) -> float:
    """GSD = H * 像元尺寸 / 焦距。"""
    return float(altitude_m) * (pixel_um * 1e-6) / (focal_mm * 1e-3)


def rpy_to_rotation(roll_deg: float, pitch_deg: float, yaw_deg: float) -> np.ndarray:
    """
    航空欧拉角 → 旋转矩阵（ZYX：偏航-俯仰-横滚）。
    将相机坐标系变换到当地东北天（ENU）。
    """
    r, p, y = np.deg2rad([roll_deg, pitch_deg, yaw_deg])
    cr, sr = math.cos(r), math.sin(r)
    cp, sp = math.cos(p), math.sin(p)
    cy, sy = math.cos(y), math.sin(y)
    rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]], dtype=np.float64)
    ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]], dtype=np.float64)
    rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]], dtype=np.float64)
    return rz @ ry @ rx


def plan_lawnmower(
    west: float,
    south: float,
    east: float,
    north: float,
    *,
    altitude_m: float,
    overlap: float,
    sidelap: float,
    focal_mm: float,
    pixel_um: float,
    n_cols: int,
    n_rows: int,
    cruise_speed_m_s: float,
) -> dict:
    """按摄影测量覆盖公式生成往返航线。"""
    gsd = gsd_m(altitude_m, pixel_um, focal_mm)
    swath = gsd * n_cols
    footprint_along = gsd * n_rows
    line_spacing = swath * (1.0 - sidelap)
    photo_spacing = footprint_along * (1.0 - overlap)
    lat0 = 0.5 * (south + north)
    m_lon, m_lat = meters_per_deg(lat0)
    waypoints = []
    y = south + 0.5 * (photo_spacing / m_lat)
    line_id = 0
    while y <= north + 1e-12:
        xs = np.arange(west, east + 0.5 * (photo_spacing / m_lon), photo_spacing / m_lon)
        if line_id % 2 == 1:
            xs = xs[::-1]
        for x in xs:
            waypoints.append({"line": line_id, "lon": float(x), "lat": float(y), "alt_m": float(altitude_m)})
        y += line_spacing / m_lat
        line_id += 1
    n = max(len(waypoints) - 1, 0)
    path_m = n * photo_spacing
    return {
        "gsd_m": gsd,
        "swath_m": swath,
        "footprint_along_m": footprint_along,
        "line_spacing_m": line_spacing,
        "photo_spacing_m": photo_spacing,
        "n_lines": line_id,
        "n_waypoints": len(waypoints),
        "est_path_m": path_m,
        "est_duration_s": path_m / max(cruise_speed_m_s, 1e-6),
        "waypoints": waypoints,
    }


def orthorectify_collinearity(
    cube: np.ndarray,
    dem: np.ndarray,
    *,
    altitude_m: float,
    roll_deg: float,
    pitch_deg: float,
    yaw_deg: float,
    focal_mm: float,
    pixel_um: float,
    gsd_out: float | None = None,
    tile_rows: int | None = None,
    workers: int = 0,
) -> tuple[np.ndarray, dict]:
    """
    单片直接地理定位正射：共线方程 + DEM 迭代交会。
    输出网格与输入同尺寸，地面采样用 GSD。行块可多线程。
    """
    h, w, b = cube.shape
    dem = dem.astype(np.float64)
    if dem.shape != (h, w):
        rr = np.linspace(0, dem.shape[0] - 1, h)
        cc = np.linspace(0, dem.shape[1] - 1, w)
        g0, g1 = np.meshgrid(rr, cc, indexing="ij")
        dem = map_coordinates(dem, [g0, g1], order=1, mode="nearest")
    gsd = gsd_out or gsd_m(altitude_m, pixel_um, focal_mm)
    f_px = (focal_mm * 1e-3) / (pixel_um * 1e-6)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    rot = rpy_to_rotation(roll_deg, pitch_deg, yaw_deg)
    xs = (np.arange(w) - cx) * gsd
    ys = (cy - np.arange(h)) * gsd
    z_cam = float(altitude_m)
    step = int(tile_rows) if tile_rows else h
    step = max(1, min(h, step))
    ranges = [(r0, min(h, r0 + step)) for r0 in range(0, h, step)]
    n_workers = worker_count(workers) if len(ranges) > 1 else 1

    def _one(pair: tuple[int, int]) -> tuple[int, int, np.ndarray]:
        r0, r1 = pair
        yy = ys[r0:r1, None]
        xx = xs[None, :]
        xxb, yyb = np.broadcast_arrays(xx, yy)
        vec = np.stack([xxb, yyb, dem[r0:r1] - z_cam], axis=-1).reshape(-1, 3)
        cam = vec @ rot
        block_h = r1 - r0
        cam_z = cam[:, 2].reshape(block_h, w)
        cam_z = np.where(np.abs(cam_z) < 1e-6, 1e-6, cam_z)
        denom = np.where(cam_z < 0, -cam_z, cam_z)
        samples_c = cx + f_px * cam[:, 0].reshape(block_h, w) / denom
        samples_r = cy + f_px * cam[:, 1].reshape(block_h, w) / denom
        block = np.empty((block_h, w, b), dtype=np.float64)
        for bi in range(b):
            block[:, :, bi] = map_coordinates(
                cube[:, :, bi],
                [samples_r, samples_c],
                order=1,
                mode="nearest",
            )
        return r0, r1, block

    out = np.empty_like(cube, dtype=np.float64)
    for r0, r1, block in map_threads(_one, ranges, n_workers):
        out[r0:r1] = block
    meta = {
        "method": "collinearity_direct_georeferencing",
        "gsd_m": gsd,
        "focal_px": f_px,
        "altitude_m": altitude_m,
        "roll_deg": roll_deg,
        "pitch_deg": pitch_deg,
        "yaw_deg": yaw_deg,
        "dem_min": float(dem.min()),
        "dem_max": float(dem.max()),
        "tile_rows": step,
        "workers": n_workers,
    }
    return out, meta
