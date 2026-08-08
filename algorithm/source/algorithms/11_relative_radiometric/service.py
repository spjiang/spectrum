"""骨架实现：相对辐射归一。"""
from __future__ import annotations

import json

from fastapi import UploadFile

from common.response import stub_response

ALGORITHM_ID = "11_relative_radiometric"
TITLE = "相对辐射归一"
IMPLEMENTED = False
LEVEL = "L1"


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
