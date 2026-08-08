"""骨架实现：异常检测。"""
from __future__ import annotations

import json

from fastapi import UploadFile

from common.response import stub_response

ALGORITHM_ID = "42_anomaly_detect"
TITLE = "异常检测"
IMPLEMENTED = False
LEVEL = "L3"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """骨架：接收文件但不做真实计算。"""
    _ = await file.read()
    if file2 is not None:
        _ = await file2.read()
    try:
        json.loads(params_json or "{}")
    except json.JSONDecodeError:
        pass
    return stub_response(algorithm_id=ALGORITHM_ID, title=TITLE, level=LEVEL)
