"""算法实现共用帮助函数。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix


def parse_params(params_json: str) -> tuple[dict[str, Any] | None, str | None]:
    """解析 params JSON 字符串。失败时返回错误信息。"""
    try:
        obj = json.loads(params_json or "{}")
    except json.JSONDecodeError:
        return None, "params 不是合法 JSON"
    if not isinstance(obj, dict):
        return None, "params 必须是 JSON 对象"
    return obj, None


def write_json(path: Path, obj: Any) -> str:
    """写出 UTF-8 JSON 并返回绝对路径。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(path.resolve())


def as_label2d(arr: np.ndarray) -> np.ndarray:
    """标签图统一为 H×W。"""
    if arr.ndim == 3:
        return arr[:, :, 0]
    if arr.ndim == 2:
        return arr
    raise ValueError(f"标签期望 2D/3D，实际 ndim={arr.ndim}")


def aa_kappa(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float, float]:
    """返回 OA / AA / Kappa。"""
    oa = float(accuracy_score(y_true, y_pred))
    kappa = float(cohen_kappa_score(y_true, y_pred))
    cm = confusion_matrix(y_true, y_pred)
    with np.errstate(divide="ignore", invalid="ignore"):
        per = np.diag(cm) / cm.sum(axis=1)
    per = per[~np.isnan(per)]
    aa = float(per.mean()) if len(per) else 0.0
    return oa, aa, kappa


def load_endmember_csv(path: Path) -> np.ndarray:
    """读取端元 CSV：首列为 band，其后每列一个端元。返回 (B, K)。"""
    raw = np.genfromtxt(path, delimiter=",", names=True)
    if raw.dtype.names is None:
        arr = np.genfromtxt(path, delimiter=",", skip_header=1)
        return np.atleast_2d(arr)[:, 1:]
    cols = [n for n in raw.dtype.names if n.lower() != "band"]
    return np.column_stack([raw[c] for c in cols]).astype(np.float64)


def ndvi_like(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """通用归一化差值：(b-a)/(b+a)。"""
    return (b - a) / (b + a + 1e-12)


def check_bands(cube: np.ndarray, **named: int) -> str | None:
    """检查 0-based 波段索引是否越界。"""
    n = cube.shape[2]
    bad = [f"{k}={v}" for k, v in named.items() if v < 0 or v >= n]
    if bad:
        return f"波段索引越界：{', '.join(bad)}，bands={n}"
    return None
