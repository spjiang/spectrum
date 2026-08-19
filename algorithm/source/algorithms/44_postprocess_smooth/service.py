"""分类后处理：众数滤波 + 小斑剔除。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile
from scipy import ndimage as ndi

from common.impl import as_label2d, parse_params
from common.io import load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "44_postprocess_smooth"
TITLE = "分类后处理平滑/小斑剔除"
IMPLEMENTED = True
LEVEL = "L3→L4"


def _majority(lab: np.ndarray, size: int = 3) -> np.ndarray:
    """窗口众数滤波。"""

    def mode_fun(values: np.ndarray) -> float:
        vals, cnts = np.unique(values.astype(int), return_counts=True)
        return float(vals[cnts.argmax()])

    return ndi.generic_filter(lab.astype(float), mode_fun, size=size, mode="nearest")


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """file=分类标签 GeoTIFF。params.min_pixels。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    min_pixels = int(params.get("min_pixels", 4))
    win = int(params.get("window", 3))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    lab = as_label2d(arr).astype(np.int32)
    smooth = _majority(lab, size=max(3, win)).astype(np.int32)
    out = smooth.copy()
    for cls in np.unique(smooth):
        mask = smooth == cls
        labeled, n = ndi.label(mask)
        for i in range(1, n + 1):
            blob = labeled == i
            if int(blob.sum()) < min_pixels:
                # 填为邻域众数
                dil = ndi.binary_dilation(blob)
                border = dil & (~blob)
                if border.any():
                    vals, cnts = np.unique(out[border], return_counts=True)
                    out[blob] = vals[cnts.argmax()]
    tif = job / "labels_smooth.tif"
    png = job / "labels_preview.png"
    save_geotiff(out, tif, profile=profile)
    save_preview_png(out.astype(float), png, title="Smoothed labels")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已完成众数滤波与小斑剔除",
        data={
            "min_pixels": min_pixels,
            "window": max(3, win),
            "n_changed": int((out != lab).sum()),
            "classes": [int(c) for c in np.unique(out)],
            "format": "GeoTIFF",
        },
        files={"labels_tif": str(tif.resolve()), "preview_png": str(png.resolve())},
    )
