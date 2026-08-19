"""1D-CNN 光谱分类。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import as_label2d, parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

from .model import train_and_predict

ALGORITHM_ID = "36_cnn1d_classify"
TITLE = "1D-CNN/RNN光谱分类"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=Cube，file2=标签。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="1D-CNN 需要 file2 标签 GeoTIFF")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    epochs = int(params.get("epochs", 8))
    test_size = float(params.get("test_size", 0.3))
    job = new_job_dir(ALGORITHM_ID)
    p1 = await save_upload(file, job)
    p2 = await save_upload(file2, job)
    cube, profile = load_raster(p1)
    cube = as_cube(cube.astype(np.float64))
    gt = as_label2d(load_raster(p2)[0])
    if gt.shape != cube.shape[:2]:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="标签尺寸须与影像一致")
    try:
        result = train_and_predict(cube, gt.astype(np.int32), epochs=epochs, test_size=test_size)
    except Exception as exc:  # noqa: BLE001
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=f"训练/推理失败: {exc}")
    pred_map = result.pop("pred_map")
    tif = job / "pred_map.tif"
    png = job / "pred_preview.png"
    save_geotiff(pred_map, tif, profile=profile)
    save_preview_png(pred_map.astype(float), png, title="1D-CNN Pred")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="Hu et al. 2015 1-D CNN 光谱分类完成",
        data={**result, "epochs": epochs, "format": "GeoTIFF", "backend": "PyTorch Hu2015CNN"},
        files={"pred_map_tif": str(tif.resolve()), "preview_png": str(png.resolve())},
    )
