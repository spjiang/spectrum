"""统一 API JSON 响应。"""
from __future__ import annotations

from typing import Any


def ok_response(
    *,
    algorithm_id: str,
    algorithm: str,
    implemented: bool,
    message: str,
    data: dict[str, Any] | None = None,
    files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """构造成功响应。"""
    return {
        "success": True,
        "algorithm_id": algorithm_id,
        "algorithm": algorithm,
        "implemented": implemented,
        "message": message,
        "data": data or {},
        "files": files or {},
    }


def err_response(
    *,
    algorithm_id: str,
    algorithm: str,
    message: str,
    implemented: bool = True,
) -> dict[str, Any]:
    """构造失败响应。"""
    return {
        "success": False,
        "algorithm_id": algorithm_id,
        "algorithm": algorithm,
        "implemented": implemented,
        "message": message,
        "data": {},
        "files": {},
    }


def stub_response(*, algorithm_id: str, title: str, level: str) -> dict[str, Any]:
    """未实现算法的标准骨架响应。"""
    return ok_response(
        algorithm_id=algorithm_id,
        algorithm=title,
        implemented=False,
        message=(
            f"算法「{title}」当前为骨架服务（层级 {level}）。"
            "接口已预留：请上传 file，后续可在本目录 service.py 补齐真实逻辑。"
            "详见本目录 README.md。"
        ),
        data={"level": level, "hint": "skeleton"},
        files={},
    )
