"""PCA 降维。输入/输出 GeoTIFF。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile
from sklearn.decomposition import PCA

from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "23_pca"
TITLE = "PCA/MNF降维"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params.n_components: 主成分数，默认 3。"""
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    n = int(params.get("n_components", 3))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    h, w, b = cube.shape
    n = max(1, min(n, b, h * w))
    x = cube.reshape(-1, b)
    pca = PCA(n_components=n)
    z = pca.fit_transform(x).reshape(h, w, n).astype(np.float32)
    out = job / "pca_cube.tif"
    save_geotiff(z, out, profile=profile)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"PCA 降维至 {n} 维，输出 GeoTIFF",
        data={
            "shape": list(z.shape),
            "explained_variance_ratio": [float(v) for v in pca.explained_variance_ratio_],
            "format": "GeoTIFF",
        },
        files={"pca_tif": str(out.resolve())},
    )
