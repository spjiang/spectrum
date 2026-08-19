"""POS 解算：GNSS 粗差剔除 + 位置互补滤波 + RTS 平滑 + 杠杆臂。"""
from __future__ import annotations

import numpy as np
from fastapi import UploadFile

from common.impl import parse_params, write_json
from common.io import new_job_dir, save_upload
from common.response import err_response, ok_response
from common.rs.ins import solve_pos

ALGORITHM_ID = "03_pos_solution"
TITLE = "POS解算（GPS+IMU）"
IMPLEMENTED = True
LEVEL = "L0"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """输入 POS CSV（time,lat,lon,alt,roll,pitch,yaw）。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    try:
        arr = np.genfromtxt(path, delimiter=",", names=True, dtype=None, encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=f"无法解析 POS CSV: {exc}")
    if arr.size == 0:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="POS CSV 为空")
    names = arr.dtype.names or ()
    needed = ("time", "lat", "lon", "alt", "roll", "pitch", "yaw")
    if any(n not in names for n in needed):
        return err_response(
            algorithm_id=ALGORITHM_ID,
            algorithm=TITLE,
            message=f"CSV 需含列 {needed}，实际 {names}",
        )

    def col(name: str) -> np.ndarray:
        return np.atleast_1d(arr[name]).astype(np.float64)

    result = solve_pos(
        col("time"),
        col("lat"),
        col("lon"),
        col("alt"),
        col("roll"),
        col("pitch"),
        col("yaw"),
        alpha=float(params.get("alpha", 0.85)),
        lever_enu=(
            float(params.get("lever_e_m", 0.0)),
            float(params.get("lever_n_m", 0.0)),
            float(params.get("lever_u_m", 0.0)),
        ),
    )
    frames = result["frames"]
    out_json = job / "pos_frames.json"
    out_csv = job / "pos_frames.csv"
    write_json(out_json, result)
    header = "time,lat,lon,alt,roll,pitch,yaw,ve,vn,vu,gnss_ok\n"
    body = "".join(
        f"{f['time']},{f['lat']},{f['lon']},{f['alt']},{f['roll']},{f['pitch']},{f['yaw']},"
        f"{f['ve']},{f['vn']},{f['vu']},{int(f['gnss_ok'])}\n"
        for f in frames
    )
    out_csv.write_text(header + body, encoding="utf-8")
    summary = {k: v for k, v in result.items() if k != "frames"}
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"POS 后处理完成：{len(frames)} 条，剔除 GNSS 粗差 {result['n_outlier']}",
        data={**summary, "format": "JSON+CSV"},
        files={"pos_json": str(out_json.resolve()), "pos_csv": str(out_csv.resolve())},
    )
