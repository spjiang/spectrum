"""光谱匹配：SAM + SID（Chang 2000）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import load_endmember_csv, parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "35_spectral_matching"
TITLE = "光谱匹配分类(SAM)"
IMPLEMENTED = True
LEVEL = "L3"


def _sam(x: np.ndarray, e: np.ndarray) -> np.ndarray:
    """x (N,B), e (B,K) → 角度 (N,K)。"""
    x_n = x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-12)
    e_n = e / (np.linalg.norm(e, axis=0, keepdims=True) + 1e-12)
    cos = np.clip(x_n @ e_n, -1, 1)
    return np.arccos(cos)


def _sid(x: np.ndarray, e: np.ndarray) -> np.ndarray:
    """光谱信息散度 SID。x (N,B), e (B,K)。"""
    p = np.clip(x, 1e-12, None)
    p = p / p.sum(axis=1, keepdims=True)
    q = np.clip(e, 1e-12, None)
    q = q / q.sum(axis=0, keepdims=True)
    n, _b = p.shape
    k = q.shape[1]
    out = np.empty((n, k), dtype=np.float64)
    for j in range(k):
        qj = q[:, j]
        out[:, j] = np.sum(p * np.log(p / qj), axis=1) + np.sum(qj * np.log(qj / p), axis=1)
    return out


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=Cube，file2=端元 CSV。params.method: sam | sid"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="SAM 需要 file2 端元光谱 CSV")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    method = str(params.get("method", "sam")).lower()
    job = new_job_dir(ALGORITHM_ID)
    p1 = await save_upload(file, job)
    p2 = await save_upload(file2, job)
    cube, profile = load_raster(p1)
    cube = as_cube(cube.astype(np.float64))
    h, w, b = cube.shape
    em = load_endmember_csv(p2)
    if em.shape[0] != b:
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message=f"端元波段数 {em.shape[0]} 与影像 {b} 不一致",
        )
    dist = _sid(cube.reshape(-1, b), em) if method == "sid" else _sam(cube.reshape(-1, b), em)
    if method != "sid":
        method = "sam"
    cls = dist.argmin(axis=1).reshape(h, w).astype(np.int32) + 1
    min_d = dist.min(axis=1).reshape(h, w).astype(np.float32)
    pred_tif = job / "sam_class.tif"
    ang_tif = job / "sam_angle.tif"
    png = job / "sam_preview.png"
    save_geotiff(cls, pred_tif, profile=profile)
    save_geotiff(min_d, ang_tif, profile=profile)
    save_preview_png(cls.astype(float), png, title=f"{method.upper()} class")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"{method.upper()} 完成，端元数 {em.shape[1]}",
        data={
            "method": method,
            "n_endmembers": int(em.shape[1]),
            "score_mean": float(min_d.mean()),
            "classes": [int(c) for c in np.unique(cls)],
            "format": "GeoTIFF",
        },
        files={"pred_map_tif": str(pred_tif.resolve()), "angle_tif": str(ang_tif.resolve()), "preview_png": str(png.resolve())},
    )
