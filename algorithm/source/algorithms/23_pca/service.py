"""PCA / MNF 降维。默认 MNF（Green et al. 1988）。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response
from common.rs.mnf import mnf_transform, pca_transform

ALGORITHM_ID = "23_pca"
TITLE = "PCA/MNF降维"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params.method: mnf | pca；params.n_components 默认 3。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    n = int(params.get("n_components", 3))
    method = str(params.get("method", "mnf")).lower()
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(float))
    if method == "pca":
        z, meta = pca_transform(cube, n)
    else:
        z, meta = mnf_transform(cube, n)
        method = "mnf"
    out = job / f"{method}_cube.tif"
    save_geotiff(z, out, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"{method.upper()} 降维至 {z.shape[2]} 维",
        data={**meta, "shape": list(z.shape), "format": "GeoTIFF"},
        files={"pca_tif": str(out.resolve())},
    )
