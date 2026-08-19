"""几何粗校正：POS + GSD 直接地理定位写入仿射。"""
from __future__ import annotations

from fastapi import UploadFile
from rasterio.transform import from_origin

from common.impl import parse_params, write_json
from common.io import as_cube, load_raster, load_text_or_json, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.photogrammetry import gsd_m, meters_per_deg

ALGORITHM_ID = "15_geo_locate"
TITLE = "几何粗校正/地理定位"
IMPLEMENTED = True
LEVEL = "L1→L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """以像主点 POS 为中心，GSD=H·像元/焦距，写 EPSG:4326 GeoTIFF。"""
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr)
    pos = {}
    if file2 is not None:
        raw = load_text_or_json(await save_upload(file2, job))
        if isinstance(raw, dict):
            pos = raw.get("pos") if isinstance(raw.get("pos"), dict) else raw
    lon = float(pos.get("lon", params.get("lon", 114.06)))
    lat = float(pos.get("lat", params.get("lat", 22.54)))
    alt = float(pos.get("alt", params.get("alt_m", 120)))
    focal_mm = float(params.get("focal_mm", 8.0))
    pixel_um = float(params.get("pixel_um", 5.5))
    gsd = float(params.get("gsd_m", gsd_m(alt, pixel_um, focal_mm)))
    m_lon, m_lat = meters_per_deg(lat)
    res_x = gsd / m_lon
    res_y = gsd / m_lat
    h, w = cube.shape[:2]
    west = lon - (w / 2.0) * res_x
    north = lat + (h / 2.0) * res_y
    profile = dict(profile or {})
    profile["crs"] = "EPSG:4326"
    profile["transform"] = from_origin(west, north, res_x, res_y)
    tif = job / "geolocated.tif"
    save_geotiff(cube, tif, profile=profile)
    meta = {
        "method": "direct_georeferencing",
        "lon": lon,
        "lat": lat,
        "alt_m": alt,
        "gsd_m": gsd,
        "res_deg": [res_x, res_y],
        "yaw": pos.get("yaw"),
        "crs": "EPSG:4326",
    }
    meta_path = job / "geo_meta.json"
    write_json(meta_path, meta)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="直接地理定位完成（POS + GSD 仿射）",
        data={**meta, "shape": list(cube.shape), "format": "GeoTIFF"},
        files={"cube_tif": str(tif.resolve()), "meta_json": str(meta_path.resolve())},
    )
