"""文件读写与数组加载。"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

import numpy as np
from fastapi import UploadFile

from common.config import OUTPUT_DIR, UPLOAD_DIR


def new_job_dir(prefix: str) -> Path:
    """为一次请求创建输出目录。"""
    job = OUTPUT_DIR / f"{prefix}_{uuid.uuid4().hex[:10]}"
    job.mkdir(parents=True, exist_ok=True)
    return job


async def save_upload(file: UploadFile, dest_dir: Path | None = None) -> Path:
    """保存上传文件到 uploads 或指定目录。"""
    dest_dir = dest_dir or UPLOAD_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "input.bin").suffix or ".bin"
    path = dest_dir / f"{uuid.uuid4().hex[:12]}{suffix}"
    content = await file.read()
    path.write_bytes(content)
    return path


def load_array(path: Path) -> np.ndarray:
    """加载 .npy / .npz / .json(list) 为 numpy 数组。"""
    suffix = path.suffix.lower()
    if suffix == ".npy":
        return np.load(path)
    if suffix == ".npz":
        return np.loadtxt(path, delimiter=",")
    if suffix == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return np.asarray(raw)
    raise ValueError(f"暂不支持的文件类型: {suffix}，请使用 .npy / .npz / .json")


def save_npy(arr: np.ndarray, path: Path) -> str:
    """保存 npy 并返回字符串路径。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, arr)
    return str(path.resolve())


def save_preview_png(arr2d: np.ndarray, path: Path, title: str = "") -> str:
    """将二维数组保存为预览 PNG。"""
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
