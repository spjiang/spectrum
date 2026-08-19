"""经验回归反演：PLS 把光谱映射为连续生化量。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from common.impl import as_label2d, parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response
from common.rs.preprocess import snv

ALGORITHM_ID = "32_regression_inversion"
TITLE = "经验回归反演"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=光谱 Cube，file2=真值图。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="回归反演需要 file2 真值 GeoTIFF")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    n_comp = int(params.get("n_components", 3))
    test_size = float(params.get("test_size", 0.3))
    job = new_job_dir(ALGORITHM_ID)
    p1 = await save_upload(file, job)
    p2 = await save_upload(file2, job)
    cube, profile = load_raster(p1)
    cube = as_cube(cube.astype(np.float64))
    ymap = as_label2d(load_raster(p2)[0]).astype(np.float64)
    if ymap.shape != cube.shape[:2]:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="真值图尺寸须与影像一致")
    x = cube.reshape(-1, cube.shape[2])
    if str(params.get("preprocess", "snv")).lower() == "snv":
        x = snv(cube).reshape(-1, cube.shape[2])
    y = ymap.ravel()
    n_comp = max(1, min(n_comp, cube.shape[2], x.shape[0] - 1))
    x_tr, x_te, y_tr, y_te = train_test_split(x, y, test_size=test_size, random_state=42)
    model = PLSRegression(n_components=n_comp)
    model.fit(x_tr, y_tr)
    pred_te = model.predict(x_te).ravel()
    r2 = float(r2_score(y_te, pred_te))
    rmse = float(np.sqrt(mean_squared_error(y_te, pred_te)))
    pred = model.predict(x).ravel().reshape(ymap.shape).astype(np.float32)
    tif = job / "inversion.tif"
    png = job / "inversion_preview.png"
    save_geotiff(pred, tif, profile=profile)
    save_preview_png(pred, png, title="PLS inversion")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="SNV + PLS 回归反演完成",
        data={"r2": r2, "rmse": rmse, "n_components": n_comp, "n_train": int(len(y_tr)), "n_test": int(len(y_te)), "preprocess": "snv", "format": "GeoTIFF"},
        files={"inversion_tif": str(tif.resolve()), "preview_png": str(png.resolve())},
    )
