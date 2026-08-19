"""2D/3D-CNN 空谱分类：HybridSN（Roy et al. 2020）。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile

from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

from .model import train_and_predict

ALGORITHM_ID = "37_cnn3d_classify"
TITLE = "2D/3D-CNN空谱分类"
IMPLEMENTED = True
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """
    file: 多波段 GeoTIFF（Cube）
    file2: 单波段标签 GeoTIFF（0 为背景/忽略）
    params: patch_size, pca_components, epochs, test_size, batch_size
    """
    if file2 is None:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message="3D-CNN 分类需要 file2 标签 GeoTIFF（单波段，0 表示忽略）",
        )
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    patch_size = int(params.get("patch_size", 5))
    if patch_size % 2 == 0 or patch_size < 3:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message="patch_size 须为 >=3 的奇数",
        )
    pca_components = int(params.get("pca_components", 8))
    epochs = int(params.get("epochs", 8))
    test_size = float(params.get("test_size", 0.3))
    batch_size = int(params.get("batch_size", 64))

    job = new_job_dir(ALGORITHM_ID)
    cube_path = await save_upload(file, job)
    gt_path = await save_upload(file2, job)
    cube_arr, profile = load_raster(cube_path)
    gt_arr, _ = load_raster(gt_path)
    cube = as_cube(cube_arr.astype(np.float64))
    gt = gt_arr if gt_arr.ndim == 2 else gt_arr[:, :, 0]
    if gt.shape != cube.shape[:2]:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message=f"标签尺寸需为 {cube.shape[:2]}，实际 {gt.shape}",
        )

    try:
        result = train_and_predict(
            cube,
            gt.astype(np.int32),
            patch_size=patch_size,
            pca_components=pca_components,
            epochs=epochs,
            batch_size=batch_size,
            test_size=test_size,
        )
    except Exception as e:  # noqa: BLE001 — 返回给调用方可读错误
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=f"训练/推理失败: {e}")

    pred_map = result.pop("pred_map")
    pred_path = job / "pred_map.tif"
    png_path = job / "pred_preview.png"
    save_geotiff(pred_map, pred_path, profile=profile)
    save_preview_png(pred_map.astype(float), png_path, title="3D-CNN Pred")

    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="HybridSN（Roy 2020）空谱分类完成；测试集给出 OA/AA/Kappa",
        data={
            "oa": result["oa"],
            "aa": result["aa"],
            "kappa": result["kappa"],
            "n_train": result["n_train"],
            "n_test": result["n_test"],
            "classes": result["classes"],
            "device": result["device"],
            "bands_after_pca": result["bands_after_pca"],
            "architecture": result.get("architecture", "HybridSN"),
            "patch_size": patch_size,
            "epochs": epochs,
            "format": "GeoTIFF",
            "backend": "PyTorch HybridSN",
        },
        files={"pred_map_tif": str(pred_path.resolve()), "preview_png": str(png_path.resolve())},
    )
