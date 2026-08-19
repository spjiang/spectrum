"""Patch 样本构建：切邻域立方体。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import as_label2d, parse_params, write_json
from common.io import as_cube, load_raster, new_job_dir, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "26_patch_build"
TITLE = "Patch/样本构建"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=Cube，file2=标签（0 忽略）。输出 npz 样本与清单。"""
    if file2 is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="构建样本需要 file2 标签 GeoTIFF")
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    patch = int(params.get("patch_size", 5))
    if patch < 1 or patch % 2 == 0:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="patch_size 须为正奇数")
    job = new_job_dir(ALGORITHM_ID)
    p1 = await save_upload(file, job)
    p2 = await save_upload(file2, job)
    cube = as_cube(load_raster(p1)[0].astype(np.float32))
    gt = as_label2d(load_raster(p2)[0])
    if gt.shape != cube.shape[:2]:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="标签尺寸须与影像一致")
    m = patch // 2
    h, w, b = cube.shape
    pad = np.pad(cube, ((m, m), (m, m), (0, 0)), mode="edge")
    xs, ys, coords = [], [], []
    for r in range(h):
        for c in range(w):
            lab = int(gt[r, c])
            if lab <= 0:
                continue
            xs.append(pad[r : r + patch, c : c + patch, :])
            ys.append(lab)
            coords.append([r, c])
    if not xs:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="无有效标注像素")
    patches = np.stack(xs, axis=0)
    labels = np.asarray(ys, dtype=np.int32)
    npz = job / "patches.npz"
    np.savez_compressed(npz, patches=patches, labels=labels, coords=np.asarray(coords, dtype=np.int32))
    manifest = {
        "n": int(len(labels)),
        "patch_size": patch,
        "bands": b,
        "shape": [int(patches.shape[0]), patch, patch, b],
        "classes": [int(c) for c in np.unique(labels)],
    }
    man_path = job / "manifest.json"
    write_json(man_path, manifest)
    png = job / "patch_mean_preview.png"
    save_preview_png(patches.mean(axis=(0, 3)), png, title="Mean patch")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"已构建 {len(labels)} 个 {patch}×{patch}×{b} patch",
        data=manifest,
        files={"patches_npz": str(npz.resolve()), "manifest_json": str(man_path.resolve()), "preview_png": str(png.resolve())},
    )
