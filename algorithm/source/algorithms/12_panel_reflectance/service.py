"""白板/灰板反射率定标（教学示意）：反射率 ≈ 辐亮度 * scale。"""
from __future__ import annotations

import json

import numpy as np
from fastapi import UploadFile

from common.io import as_cube, load_array, new_job_dir, save_npy, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "12_panel_reflectance"
TITLE = "白板/灰板反射率定标（示意）"
IMPLEMENTED = True
LEVEL = "L1→L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """将输入立方体按比例缩放到近似反射率。"""
    try:
        params = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="params 不是合法 JSON")

    # 白板法示意：统一乘以 scale；也可按波段传入 scales
    scale = float(params.get("scale", 1.0 / 1000.0))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    cube = as_cube(load_array(path).astype(np.float64))
    refl = np.clip(cube * scale, 0.0, 1.0)
    out = job / "reflectance.npy"
    save_npy(refl, out)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message="已完成示意反射率定标（乘以 scale 并裁剪到 0~1）",
        data={
            "shape": list(refl.shape),
            "scale": scale,
            "min": float(refl.min()),
            "max": float(refl.max()),
            "mean": float(refl.mean()),
        },
        files={"reflectance_npy": str(out.resolve())},
    )
