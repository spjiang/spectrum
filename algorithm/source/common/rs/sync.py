"""多传感器时间同步：POS 内插到曝光时刻 + 离散相机最近邻。"""
from __future__ import annotations

import math

import numpy as np


def _as_records(items: list) -> tuple[np.ndarray, list[dict]]:
    recs = [dict(r) for r in items]
    ts = np.array([float(r.get("ts", 0.0)) for r in recs], dtype=np.float64)
    order = np.argsort(ts)
    return ts[order], [recs[i] for i in order]


def _interp_scalar(ts_src: np.ndarray, vals: np.ndarray, t: float) -> float:
    if len(ts_src) == 0:
        return float("nan")
    if len(ts_src) == 1:
        return float(vals[0])
    return float(np.interp(t, ts_src, vals))


def slerp_deg(a: float, b: float, w: float) -> float:
    """绕单轴的最短弧插值（度）。"""
    da = ((b - a + 180.0) % 360.0) - 180.0
    return a + w * da


def interpolate_pos(pos: list[dict], t: float) -> dict | None:
    """在曝光时刻线性内插位置，姿态走最短弧。"""
    if not pos:
        return None
    ts, recs = _as_records(pos)
    if t <= ts[0]:
        src = recs[0]
        w = 0.0
        i0, i1 = 0, 0
    elif t >= ts[-1]:
        src = recs[-1]
        w = 1.0
        i0, i1 = len(recs) - 1, len(recs) - 1
    else:
        i1 = int(np.searchsorted(ts, t, side="right"))
        i0 = i1 - 1
        dt = ts[i1] - ts[i0]
        w = 0.0 if dt < 1e-12 else (t - ts[i0]) / dt
        src = recs[i0]
    a, b = recs[i0], recs[i1]
    out = {
        "ts": t,
        "lat": _interp_scalar(ts, np.array([float(r.get("lat", 0.0)) for r in recs]), t),
        "lon": _interp_scalar(ts, np.array([float(r.get("lon", 0.0)) for r in recs]), t),
        "alt": _interp_scalar(ts, np.array([float(r.get("alt", 0.0)) for r in recs]), t) if "alt" in a or "alt" in b else None,
        "roll": slerp_deg(float(a.get("roll", 0.0)), float(b.get("roll", 0.0)), w) if "roll" in a or "roll" in b else None,
        "pitch": slerp_deg(float(a.get("pitch", 0.0)), float(b.get("pitch", 0.0)), w) if "pitch" in a or "pitch" in b else None,
        "yaw": slerp_deg(float(a.get("yaw", 0.0)), float(b.get("yaw", 0.0)), w) if "yaw" in a or "yaw" in b else None,
        "dt_span": float(abs(ts[i1] - ts[i0])),
    }
    return {k: v for k, v in out.items() if v is not None}


def nearest_record(records: list[dict], t: float, key: str = "ts") -> tuple[dict | None, float]:
    """离散帧（RGB/快门）最近邻，返回 (记录, |Δt|)。"""
    if not records:
        return None, float("nan")
    best = min(records, key=lambda r: abs(float(r.get(key, 0.0)) - t))
    return best, abs(float(best.get(key, 0.0)) - t)


def estimate_clock_offset(hsi: list[dict], other: list[dict]) -> float:
    """用中位 Δt 估计相机相对 HSI 的钟差（秒）。"""
    if not hsi or not other:
        return 0.0
    dts = []
    for fr in hsi:
        _, dt = nearest_record(other, float(fr.get("ts", 0.0)))
        if math.isfinite(dt):
            dts.append(dt if nearest_record(other, float(fr.get("ts", 0.0)))[0] is None else (
                float(nearest_record(other, float(fr.get("ts", 0.0)))[0].get("ts", 0.0)) - float(fr.get("ts", 0.0))
            ))
    return float(np.median(dts)) if dts else 0.0


def align_hsi(hsi: list[dict], rgb: list[dict], pos: list[dict]) -> dict:
    """HSI 曝光时刻：RGB 最近邻，POS 内插。"""
    clock_rgb = estimate_clock_offset(hsi, rgb)
    rows = []
    for fr in hsi:
        ts = float(fr.get("ts", 0.0))
        rgb_hit, dt_rgb = nearest_record(rgb, ts + clock_rgb)
        pos_hit = interpolate_pos(pos, ts)
        dt_pos = None if pos_hit is None else abs(float(pos_hit.get("ts", ts)) - ts)
        rows.append(
            {
                "hsi_id": fr.get("id"),
                "hsi_ts": ts,
                "rgb_id": None if rgb_hit is None else rgb_hit.get("id"),
                "rgb_ts": None if rgb_hit is None else rgb_hit.get("ts"),
                "dt_rgb": None if rgb_hit is None else dt_rgb,
                "pos": pos_hit,
                "dt_pos": dt_pos,
            }
        )
    dts = [r["dt_rgb"] for r in rows if r["dt_rgb"] is not None]
    return {
        "method": "pos_linear_interp + rgb_nearest + clock_offset",
        "clock_offset_rgb_s": clock_rgb,
        "n": len(rows),
        "dt_rgb_median": float(np.median(dts)) if dts else None,
        "rows": rows,
    }
