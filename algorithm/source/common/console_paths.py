"""控制台文件白名单：仅 testdata / outputs / uploads。"""
from __future__ import annotations

from pathlib import Path

from common.config import OUTPUT_DIR, SOURCE_ROOT, UPLOAD_DIR

ALGORITHMS_DIR = SOURCE_ROOT / "algorithms"
PRIMARY_NAMES = ("input.tif", "input.geojson", "input.csv", "input.json")
SECONDARY_NAMES = ("file2.tif", "file2.geojson", "file2.csv", "file2.json")


def testdata_dir(algorithm_id: str) -> Path:
    """算法 testdata 目录。"""
    if "/" in algorithm_id or ".." in algorithm_id:
        raise ValueError("非法 algorithm_id")
    return ALGORITHMS_DIR / algorithm_id / "testdata"


def find_named(folder: Path, names: tuple[str, ...]) -> Path | None:
    """按约定文件名查找第一个存在的文件。"""
    for name in names:
        p = folder / name
        if p.is_file():
            return p
    return None


def resolve_testdata(algorithm_id: str, name: str) -> Path:
    """解析 testdata 下的文件（禁止路径穿越）。"""
    root = testdata_dir(algorithm_id).resolve()
    path = (root / name).resolve()
    if path != root and root not in path.parents:
        raise ValueError("路径越界")
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path


def resolve_output(job: str, name: str) -> Path:
    """解析 outputs/{job}/{name}。"""
    if "/" in job or ".." in job or "/" in name or ".." in name:
        raise ValueError("非法 job/name")
    root = OUTPUT_DIR.resolve()
    path = (root / job / name).resolve()
    if root not in path.parents:
        raise ValueError("路径越界")
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path


def resolve_upload(name: str) -> Path:
    """解析 uploads 下文件。"""
    if "/" in name or ".." in name:
        raise ValueError("非法文件名")
    path = (UPLOAD_DIR.resolve() / name).resolve()
    if UPLOAD_DIR.resolve() not in path.parents and path.parent != UPLOAD_DIR.resolve():
        raise ValueError("路径越界")
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path
