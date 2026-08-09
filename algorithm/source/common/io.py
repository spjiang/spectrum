"""业界栅格/矢量读写：GeoTIFF 为主，兼容 ENVI；教学用 npy 仅作回退。"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import UploadFile
from rasterio.crs import CRS
from rasterio.transform import from_origin

from common.config import OUTPUT_DIR, UPLOAD_DIR

# 教学样例默认地理参考（深圳附近，约 1m 分辨率示意）
DEFAULT_CRS = "EPSG:4326"
DEFAULT_ORIGIN = (114.0600, 22.5400)  # lon, lat（左上）
DEFAULT_RES = (0.00001, 0.00001)  # 约 1m 量级示意


def new_job_dir(prefix: str) -> Path:
    """为一次请求创建输出目录。"""
    job = OUTPUT_DIR / f"{prefix}_{uuid.uuid4().hex[:10]}"
    job.mkdir(parents=True, exist_ok=True)
    return job


async def save_upload(file: UploadFile, dest_dir: Path | None = None) -> Path:
    """保存上传文件到 uploads 或指定目录。"""
    dest_dir = dest_dir or UPLOAD_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "input.bin").suffix.lower() or ".bin"
    path = dest_dir / f"{uuid.uuid4().hex[:12]}{suffix}"
    path.write_bytes(await file.read())
    return path


def default_profile(height: int, width: int, count: int, dtype: str) -> dict[str, Any]:
    """构造带地理参考的 GeoTIFF profile。"""
    west, north = DEFAULT_ORIGIN
    xres, yres = DEFAULT_RES
    return {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": count,
        "dtype": dtype,
        "crs": CRS.from_string(DEFAULT_CRS),
        "transform": from_origin(west, north, xres, yres),
        "compress": "lzw",
    }


def _read_geotiff_or_envi(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    """读取 GeoTIFF / ENVI 等 GDAL 栅格，返回 (HxW 或 HxWxB, profile)。"""
    import rasterio

    with rasterio.open(path) as src:
        data = src.read()  # (bands, H, W)
        profile = src.profile.copy()
    if data.shape[0] == 1:
        return data[0], profile
    return np.moveaxis(data, 0, -1), profile


def load_raster(path: Path) -> tuple[np.ndarray, dict[str, Any] | None]:
    """
    加载栅格为主输入。

    支持：
    - .tif / .tiff / .geotiff → GeoTIFF（业界主推）
    - .dat / .img + 同名 .hdr → ENVI（GDAL 打开）
    - .hdr → 尝试打开配对数据文件
    - .npy → 仅兼容旧教学数据（无地理参考）
    """
    suffix = path.suffix.lower()
    if suffix in {".tif", ".tiff", ".geotiff", ".img", ".dat"}:
        return _read_geotiff_or_envi(path)
    if suffix == ".hdr":
        # ENVI：优先同目录无后缀或 .dat/.img
        for cand in (path.with_suffix(""), path.with_suffix(".dat"), path.with_suffix(".img")):
            if cand.exists() and cand != path:
                return _read_geotiff_or_envi(cand)
        return _read_geotiff_or_envi(path)
    if suffix == ".npy":
        arr = np.load(path)
        return arr, None
    raise ValueError(
        f"不支持的栅格类型: {suffix}。"
        "业界请使用 GeoTIFF（.tif）或 ENVI（.hdr+.dat）；"
        ".npy 仅兼容教学旧数据。"
    )


def load_array(path: Path) -> np.ndarray:
    """加载为 numpy 数组（栅格 / csv / json）。"""
    suffix = path.suffix.lower()
    if suffix in {".tif", ".tiff", ".geotiff", ".img", ".dat", ".hdr", ".npy"}:
        arr, _ = load_raster(path)
        return arr
    if suffix == ".csv":
        return np.loadtxt(path, delimiter=",", skiprows=1)
    if suffix in {".json", ".geojson"}:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return np.asarray(raw)
    raise ValueError(
        f"暂不支持的文件类型: {suffix}。"
        "栅格请用 .tif；矢量/参数可用 .geojson/.json；轨迹可用 .csv。"
    )


def save_geotiff(
    arr: np.ndarray,
    path: Path,
    *,
    profile: dict[str, Any] | None = None,
) -> str:
    """
    保存为 GeoTIFF。
    - 2D → 单波段
    - 3D HxWxB → 多波段
    """
    import rasterio

    path = path.with_suffix(".tif") if path.suffix.lower() not in {".tif", ".tiff"} else path
    path.parent.mkdir(parents=True, exist_ok=True)

    if arr.ndim == 2:
        bands = arr[np.newaxis, ...]
    elif arr.ndim == 3:
        bands = np.moveaxis(arr, -1, 0)
    else:
        raise ValueError(f"GeoTIFF 仅支持 2D/3D，实际 ndim={arr.ndim}")

    count, height, width = bands.shape
    dtype = np.dtype(bands.dtype).name
    # rasterio 对部分整数类型名敏感，统一 float32/float64/int32 等
    if dtype == "float64":
        bands = bands.astype("float32")
        dtype = "float32"
    elif dtype == "int64":
        bands = bands.astype("int32")
        dtype = "int32"

    out_profile = default_profile(height, width, count, dtype)
    if profile:
        for key in ("crs", "transform", "compress"):
            if key in profile and profile[key] is not None:
                out_profile[key] = profile[key]

    with rasterio.open(path, "w", **out_profile) as dst:
        dst.write(bands)
    return str(path.resolve())


# 兼容旧名：内部改为写 GeoTIFF
def save_npy(arr: np.ndarray, path: Path) -> str:
    """已废弃别名：请改用 save_geotiff。仍写出 .tif（忽略原 .npy 后缀）。"""
    return save_geotiff(arr, path.with_suffix(".tif"))


def save_preview_png(arr2d: np.ndarray, path: Path, title: str = "") -> str:
    """将二维数组保存为预览 PNG（给人看，非正式遥感产品）。"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(arr2d, cmap="RdYlGn")
    fig.colorbar(im, ax=ax, fraction=0.046)
    ax.set_title(title or path.stem)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return str(path.resolve())


def as_cube(arr: np.ndarray) -> np.ndarray:
    """保证输出为 H×W×B；若为 H×W 则扩一维。"""
    if arr.ndim == 2:
        return arr[:, :, None]
    if arr.ndim == 3:
        return arr
    raise ValueError(f"期望 2D/3D 数组，实际 ndim={arr.ndim}")


def load_text_or_json(path: Path) -> Any:
    """加载 JSON / GeoJSON / 纯文本（如 POS CSV 原文）。"""
    suffix = path.suffix.lower()
    if suffix in {".json", ".geojson"}:
        return json.loads(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8")
