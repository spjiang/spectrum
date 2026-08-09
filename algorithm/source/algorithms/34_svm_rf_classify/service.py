"""SVM 像素分类。Cube/标签均为 GeoTIFF；分类图输出 GeoTIFF。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "34_svm_rf_classify"
TITLE = "SVM/随机森林分类"
IMPLEMENTED = True
LEVEL = "L3"


def _aa_from_cm(cm: np.ndarray) -> float:
    """由混淆矩阵计算 Average Accuracy。"""
    with np.errstate(divide="ignore", invalid="ignore"):
        per = np.diag(cm) / cm.sum(axis=1)
    per = per[~np.isnan(per)]
    return float(per.mean()) if len(per) else 0.0


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """
    file: 多波段 GeoTIFF（Cube）
    file2: 单波段标签 GeoTIFF（0 为背景/忽略）
    params: test_size, kernel
    """
    if file2 is None:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message="SVM 分类需要 file2 标签 GeoTIFF（单波段，0 表示忽略）",
        )
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    test_size = float(params.get("test_size", 0.3))
    kernel = str(params.get("kernel", "rbf"))
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

    mask = gt > 0
    if mask.sum() < 10:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="有效标注像素过少")

    x = cube[mask]
    y = gt[mask].astype(int)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
    )
    clf = SVC(kernel=kernel, gamma="scale")
    clf.fit(x_train, y_train)
    y_pred_test = clf.predict(x_test)
    oa = float(accuracy_score(y_test, y_pred_test))
    kappa = float(cohen_kappa_score(y_test, y_pred_test))
    cm = confusion_matrix(y_test, y_pred_test)
    aa = _aa_from_cm(cm)

    flat = cube.reshape(-1, cube.shape[2])
    pred_map = clf.predict(flat).reshape(cube.shape[:2]).astype(np.int32)

    pred_path = job / "pred_map.tif"
    png_path = job / "pred_preview.png"
    save_geotiff(pred_map, pred_path, profile=profile)
    save_preview_png(pred_map.astype(float), png_path, title="SVM Pred")

    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="SVM 分类完成；输出分类 GeoTIFF；测试集给出 OA/AA/Kappa",
        data={
            "oa": oa,
            "aa": aa,
            "kappa": kappa,
            "n_train": int(len(y_train)),
            "n_test": int(len(y_test)),
            "classes": [int(c) for c in np.unique(y)],
            "kernel": kernel,
            "format": "GeoTIFF",
        },
        files={"pred_map_tif": str(pred_path.resolve()), "preview_png": str(png_path.resolve())},
    )
