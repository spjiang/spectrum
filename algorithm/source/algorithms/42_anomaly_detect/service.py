"""异常检测（教学实现）：Reed–Xiaoli (RX) 光谱异常得分图。

输入多波段 GeoTIFF；输出异常得分 GeoTIFF、可选二值告警掩膜与预览 PNG。
"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile
from scipy import ndimage as ndi

from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "42_anomaly_detect"
TITLE = "异常检测"
IMPLEMENTED = True
LEVEL = "L3"


def _rx_scores(cube: np.ndarray) -> np.ndarray:
    """计算 RX 异常得分： (x-μ)^T Σ^{-1} (x-μ)。"""
    h, w, b = cube.shape
    x = cube.reshape(-1, b)
    mu = x.mean(axis=0)
    xc = x - mu
    # 协方差 + 对角正则，避免奇异
    cov = np.cov(xc, rowvar=False)
    if cov.ndim == 0:
        cov = np.array([[float(cov)]])
    cov = cov + np.eye(cov.shape[0]) * 1e-6
    inv = np.linalg.pinv(cov)
    # 逐像素马氏距离平方
    scores = np.einsum("ij,jk,ik->i", xc, inv, xc)
    return scores.reshape(h, w)


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """
    file: 多波段 GeoTIFF（Cube）
    file2: 忽略（保留接口）
    params:
      - percentile: 得分高于该百分位判为告警（默认 95）
      - min_pixels: 告警小斑剔除（默认 2）
    """
    _ = file2
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    percentile = float(params.get("percentile", 95))
    min_pixels = int(params.get("min_pixels", 2))

    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(np.float64))
    h, w, b = cube.shape
    if b < 2:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message="RX 异常检测至少需要 2 个波段",
        )

    score = _rx_scores(cube)
    thr = float(np.percentile(score, percentile))
    mask = score >= thr
    if min_pixels > 1:
        labeled, n = ndi.label(mask)
        keep = np.zeros_like(mask)
        for i in range(1, n + 1):
            if int((labeled == i).sum()) >= min_pixels:
                keep[labeled == i] = True
        mask = keep

    score_tif = job / "anomaly_score.tif"
    mask_tif = job / "anomaly_mask.tif"
    png_path = job / "anomaly_preview.png"
    save_geotiff(score.astype(np.float32), score_tif, profile=profile)
    save_geotiff(mask.astype(np.uint8), mask_tif, profile=profile)
    save_preview_png(score, png_path, title="RX anomaly score")

    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已完成 RX 光谱异常检测；输出得分图与告警掩膜 GeoTIFF",
        data={
            "method": "reed_xiaoli",
            "bands": b,
            "percentile": percentile,
            "threshold": thr,
            "min_pixels": min_pixels,
            "n_anomaly_pixels": int(mask.sum()),
            "score_min": float(score.min()),
            "score_max": float(score.max()),
            "score_mean": float(score.mean()),
            "shape": [h, w],
            "format": "GeoTIFF",
        },
        files={
            "score_tif": str(score_tif.resolve()),
            "mask_tif": str(mask_tif.resolve()),
            "preview_png": str(png_path.resolve()),
        },
    )
