"""影像镶嵌：按地理参考重投影，重叠区距离羽化。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.mosaic import mosaic_georeferenced

ALGORITHM_ID = "17_mosaic"
TITLE = "影像匹配与镶嵌"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file / file2 为已地理参考的航带 GeoTIFF。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="镶嵌需要 file2 第二条带 GeoTIFF")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    _ = params
    job = new_job_dir(ALGORITHM_ID)
    p1 = await save_upload(file, job)
    p2 = await save_upload(file2, job)
    a1, profile1 = load_raster(p1)
    a2, profile2 = load_raster(p2)
    c1 = as_cube(a1.astype(float))
    c2 = as_cube(a2.astype(float))
    if profile1 is None or profile2 is None or "transform" not in profile1 or "transform" not in profile2:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="两条带均须带 GeoTransform")
    mosaic, geo_profile, meta = mosaic_georeferenced([c1, c2], [profile1, profile2])
    out_profile = dict(profile1)
    out_profile.update(geo_profile)
    tif = job / "mosaic.tif"
    save_geotiff(mosaic, tif, profile=out_profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="地理镶嵌+羽化完成",
        data={**meta, "format": "GeoTIFF"},
        files={"mosaic_tif": str(tif.resolve())},
    )
