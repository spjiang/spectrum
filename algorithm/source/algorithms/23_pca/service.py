"""PCA 降维。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile
from sklearn.decomposition import PCA

from common.io import as_cube, load_array, new_job_dir, save_npy, save_upload
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
    cube = as_cube(load_array(path).astype(np.float64))
    h, w, b = cube.shape
    n = max(1, min(n, b, h * w))
    x = cube.reshape(-1, b)
    pca = PCA(n_components=n)
    z = pca.fit_transform(x).reshape(h, w, n)
    out = job / "pca_cube.npy"
    save_npy(z, out)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"PCA 降维至 {n} 维",
        data={
            "shape": list(z.shape),
            "explained_variance_ratio": [float(v) for v in pca.explained_variance_ratio_],
        },
        files={"pca_npy": str(out.resolve())},
    )
