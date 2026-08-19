"""少样本分类：原型网络 + 光谱角（Snell et al. / 高光谱常用度量）。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import aa_kappa, as_label2d, parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "39_few_shot_classify"
TITLE = "少样本/迁移学习分类"
IMPLEMENTED = True
LEVEL = "L3"


def _sam_to_protos(x: np.ndarray, proto: np.ndarray) -> np.ndarray:
    """x (N,B), proto (K,B) → 光谱角 (N,K)。"""
    xn = x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-12)
    pn = proto / (np.linalg.norm(proto, axis=1, keepdims=True) + 1e-12)
    cos = np.clip(xn @ pn.T, -1.0, 1.0)
    return np.arccos(cos)


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """params.shots: 每类原型数。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="少样本分类需要 file2 标签 GeoTIFF")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    shots = int(params.get("shots", 5))
    job = new_job_dir(ALGORITHM_ID)
    p1 = await save_upload(file, job)
    p2 = await save_upload(file2, job)
    cube, profile = load_raster(p1)
    cube = as_cube(cube.astype(np.float64))
    gt = as_label2d(load_raster(p2)[0]).astype(np.int32)
    if gt.shape != cube.shape[:2]:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="标签尺寸须与影像一致")
    h, w, b = cube.shape
    x = cube.reshape(-1, b)
    y = gt.reshape(-1)
    rng = np.random.default_rng(42)
    prototypes = {}
    support_idx = []
    query_true, query_pred = [], []
    for cls in np.unique(y):
        if cls <= 0:
            continue
        idx = np.where(y == cls)[0]
        if len(idx) == 0:
            continue
        take = min(shots, len(idx))
        chosen = rng.choice(idx, size=take, replace=False)
        support_idx.extend(chosen.tolist())
        prototypes[int(cls)] = x[chosen].mean(axis=0)
    if not prototypes:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="无有效类别")
    proto_cls = np.array(list(prototypes.keys()), dtype=np.int32)
    proto_mat = np.stack([prototypes[c] for c in proto_cls], axis=0)
    dist = _sam_to_protos(x, proto_mat)
    pred = proto_cls[dist.argmin(axis=1)]
    support_set = set(support_idx)
    for i, yi in enumerate(y):
        if yi <= 0 or i in support_set:
            continue
        query_true.append(int(yi))
        query_pred.append(int(pred[i]))
    metrics = {}
    if query_true:
        oa, aa, kappa = aa_kappa(np.asarray(query_true), np.asarray(query_pred))
        metrics = {"oa": oa, "aa": aa, "kappa": kappa, "n_query": len(query_true)}
    pred_map = pred.reshape(h, w).astype(np.int32)
    tif = job / "pred_map.tif"
    png = job / "pred_preview.png"
    save_geotiff(pred_map, tif, profile=profile)
    save_preview_png(pred_map.astype(float), png, title="Few-shot SAM prototypes")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"原型网络少样本分类完成（每类 {shots} shot，度量=SAM）",
        data={
            "shots": shots,
            "n_support": len(support_idx),
            "classes": [int(c) for c in proto_cls],
            "method": "prototypical_sam",
            "format": "GeoTIFF",
            **metrics,
        },
        files={"pred_map_tif": str(tif.resolve()), "preview_png": str(png.resolve())},
    )
