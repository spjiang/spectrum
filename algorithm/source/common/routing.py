"""统一算法路由工厂：每个算法目录只保留薄 router + 业务 service。"""
from __future__ import annotations

from types import ModuleType

from fastapi import APIRouter, File, Form, UploadFile


def build_router(service: ModuleType) -> APIRouter:
    """根据算法 service 模块生成标准 /health 与 /run。"""
    algorithm_id = getattr(service, "ALGORITHM_ID", "unknown")
    title = getattr(service, "TITLE", algorithm_id)
    implemented = bool(getattr(service, "IMPLEMENTED", False))
    level = getattr(service, "LEVEL", "")

    router = APIRouter()

    @router.get("/health", summary=f"{title} 健康检查")
    def health():
        """算法模块健康检查。"""
        return {
            "status": "ok",
            "algorithm_id": algorithm_id,
            "algorithm": title,
            "level": level,
            "implemented": implemented,
        }

    @router.post("/run", summary=f"运行 {title}")
    async def run_api(
        file: UploadFile = File(..., description="主输入文件（如 .npy）"),
        file2: UploadFile | None = File(None, description="可选第二文件（如标签图）"),
        params: str = Form("{}", description="JSON 字符串参数"),
    ):
        """文件输入，JSON 输出；产物路径在 files 字段。"""
        return await service.run(file=file, file2=file2, params_json=params)

    return router
