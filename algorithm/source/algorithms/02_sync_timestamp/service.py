"""多传感器时间戳：POS 内插到曝光时刻，RGB 最近邻。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params, write_json
from common.io import load_text_or_json, new_job_dir, save_upload
from common.response import err_response, ok_response
from common.rs.sync import align_hsi

ALGORITHM_ID = "02_sync_timestamp"
TITLE = "同步曝光与时间戳对齐"
IMPLEMENTED = True
LEVEL = "L0"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """HSI 曝光时刻：POS 线性/最短弧内插，RGB 离散帧最近邻并估钟差。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    _ = params
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    raw = load_text_or_json(path)
    if not isinstance(raw, dict):
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="需要 JSON：hsi_frames / rgb_frames / pos")
    hsi = list(raw.get("hsi_frames") or [])
    rgb = list(raw.get("rgb_frames") or [])
    pos = list(raw.get("pos") or [])
    if not hsi:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="缺少 hsi_frames")
    aligned = align_hsi(hsi, rgb, pos)
    out = job / "aligned_frames.json"
    write_json(out, aligned)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"已按曝光时刻内插 POS、对齐 {aligned['n']} 帧 HSI",
        data={
            "n_hsi": len(hsi),
            "n_rgb": len(rgb),
            "n_pos": len(pos),
            "n_aligned": aligned["n"],
            "method": aligned["method"],
            "clock_offset_rgb_s": aligned["clock_offset_rgb_s"],
        },
        files={"aligned_json": str(out.resolve())},
    )
