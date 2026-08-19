"""波段选择：有标签时用 ANOVA F 值，否则用方差。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile
from sklearn.feature_selection import f_classif

from common.impl import as_label2d, parse_params, write_json
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "24_band_select"
TITLE = "波段/特征选择"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """选出得分最高的 k 个波段。params.k 默认 3。"""
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    k = int(params.get("k", 3))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    h, w, b = cube.shape
    k = max(1, min(k, b))
    scores = cube.reshape(-1, b).var(axis=0)
    method = "variance"
    if file2 is not None:
        gp = await save_upload(file2, job)
        gt_arr, _ = load_raster(gp)
        gt = as_label2d(gt_arr)
        if gt.shape == (h, w):
            mask = gt > 0
            if mask.sum() >= 8 and len(np.unique(gt[mask])) > 1:
                fvals, _ = f_classif(cube[mask], gt[mask].astype(int))
                scores = np.nan_to_num(fvals, nan=0.0)
                method = "anova_f"
    order = np.argsort(scores)[::-1]
    keep = [int(i) for i in order[:k]]
    out = cube[:, :, keep].astype(np.float32)
    tif = job / "selected_bands.tif"
    ranking = job / "band_scores.json"
    save_geotiff(out, tif, profile=profile)
    write_json(
        ranking,
        {"method": method, "scores": [float(s) for s in scores], "selected": keep, "k": k},
    )
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"已按 {method} 选出 {k} 个波段",
        data={"method": method, "selected": keep, "scores": [float(scores[i]) for i in keep], "shape": list(out.shape)},
        files={"cube_tif": str(tif.resolve()), "ranking_json": str(ranking.resolve())},
    )
