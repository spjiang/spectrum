"""用 28 testdata 立方体调用现有算法 service.run。"""

from __future__ import annotations

import importlib
import io
import json
from typing import Any

from fastapi import UploadFile
from starlette.datastructures import Headers

from common.console_paths import testdata_dir
from common.console_router import files_to_http


def _as_upload(path) -> UploadFile:
    """把磁盘文件包装成 UploadFile。"""
    data = path.read_bytes()
    return UploadFile(
        file=io.BytesIO(data),
        filename=path.name,
        headers=Headers({"content-type": "application/octet-stream"}),
    )


def cube_path():
    """同景立方体：两次指数都吃 28 的 testdata。"""
    return testdata_dir("28_ndre") / "input.tif"


async def run_algorithm(algorithm_id: str, params: dict[str, Any]) -> dict[str, Any]:
    """调用 algorithms.<id>.service.run，并补 files_http。"""
    service = importlib.import_module(f"algorithms.{algorithm_id}.service")
    file = _as_upload(cube_path())
    result = await service.run(file=file, file2=None, params_json=json.dumps(params))
    if not isinstance(result, dict):
        return {"success": False, "message": "算法返回非 JSON", "data": {}, "files": {}, "files_http": {}}
    files = result.get("files") or {}
    result["files_http"] = files_to_http(files) if files else {}
    return result
