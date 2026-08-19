"""INS/GNSS POS：速度估计、姿态解缠、位置互补滤波与 RTS 平滑。"""
from __future__ import annotations

import math

import numpy as np

from common.rs.photogrammetry import meters_per_deg


def unwrap_deg(angles: np.ndarray) -> np.ndarray:
    """角度解缠（度），避免 359→1 被当成大跳变。"""
    rad = np.deg2rad(angles.astype(np.float64))
    return np.rad2deg(np.unwrap(rad))


def estimate_velocity(time_s: np.ndarray, lat: np.ndarray, lon: np.ndarray, alt: np.ndarray) -> np.ndarray:
    """由 GNSS 位置差分估计 ENU 速度 (m/s)。"""
    n = len(time_s)
    vel = np.zeros((n, 3), dtype=np.float64)
    if n < 2:
        return vel
    lat0 = float(np.mean(lat))
    m_lon, m_lat = meters_per_deg(lat0)
    for i in range(1, n):
        dt = max(float(time_s[i] - time_s[i - 1]), 1e-6)
        vel[i, 0] = (lon[i] - lon[i - 1]) * m_lon / dt
        vel[i, 1] = (lat[i] - lat[i - 1]) * m_lat / dt
        vel[i, 2] = (alt[i] - alt[i - 1]) / dt
    vel[0] = vel[1]
    return vel


def reject_gnss_outliers(
    time_s: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
    alt: np.ndarray,
    z_thr: float = 4.0,
) -> np.ndarray:
    """按速度 3–4σ 剔除 GNSS 跳点，返回有效掩膜。"""
    vel = estimate_velocity(time_s, lat, lon, alt)
    speed = np.linalg.norm(vel, axis=1)
    mu, sd = float(np.median(speed)), float(np.median(np.abs(speed - np.median(speed))) * 1.4826 + 1e-9)
    return speed <= (mu + z_thr * sd)


def complementary_position(
    time_s: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
    alt: np.ndarray,
    *,
    alpha: float = 0.85,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    位置互补滤波：预测（匀速）与 GNSS 观测融合。
    对应松组合中位置通道的一阶互补形式。
    """
    n = len(time_s)
    lat_f = lat.astype(np.float64).copy()
    lon_f = lon.astype(np.float64).copy()
    alt_f = alt.astype(np.float64).copy()
    if n < 2:
        return lat_f, lon_f, alt_f
    lat0 = float(np.mean(lat))
    m_lon, m_lat = meters_per_deg(lat0)
    ve = ve_n = vu = 0.0
    for i in range(1, n):
        dt = max(float(time_s[i] - time_s[i - 1]), 1e-6)
        lat_p = lat_f[i - 1] + (ve_n * dt) / m_lat
        lon_p = lon_f[i - 1] + (ve * dt) / m_lon
        alt_p = alt_f[i - 1] + vu * dt
        lat_f[i] = alpha * lat_p + (1.0 - alpha) * lat[i]
        lon_f[i] = alpha * lon_p + (1.0 - alpha) * lon[i]
        alt_f[i] = alpha * alt_p + (1.0 - alpha) * alt[i]
        ve = (lon_f[i] - lon_f[i - 1]) * m_lon / dt
        ve_n = (lat_f[i] - lat_f[i - 1]) * m_lat / dt
        vu = (alt_f[i] - alt_f[i - 1]) / dt
    return lat_f, lon_f, alt_f


def rts_smooth_1d(z: np.ndarray, q: float = 1e-4, r: float = 1e-2) -> np.ndarray:
    """
    标量 Kalman + Rauch–Tung–Striebel 平滑（位置/姿态各通道）。
    过程噪声 q、量测噪声 r。
    """
    n = len(z)
    x_f = np.zeros(n)
    p_f = np.zeros(n)
    x_pred = np.zeros(n)
    p_pred = np.zeros(n)
    x_f[0] = z[0]
    p_f[0] = r
    for i in range(1, n):
        x_pred[i] = x_f[i - 1]
        p_pred[i] = p_f[i - 1] + q
        k = p_pred[i] / (p_pred[i] + r)
        x_f[i] = x_pred[i] + k * (z[i] - x_pred[i])
        p_f[i] = (1.0 - k) * p_pred[i]
    x_s = x_f.copy()
    for i in range(n - 2, -1, -1):
        if p_pred[i + 1] < 1e-18:
            continue
        a = p_f[i] / p_pred[i + 1]
        x_s[i] = x_f[i] + a * (x_s[i + 1] - x_pred[i + 1])
    return x_s


def apply_lever_arm(
    lat: np.ndarray,
    lon: np.ndarray,
    alt: np.ndarray,
    roll: np.ndarray,
    pitch: np.ndarray,
    yaw: np.ndarray,
    lever_e_m: float,
    lever_n_m: float,
    lever_u_m: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """将 GNSS 天线位置归算到相机投影中心（杠杆臂，东北天，米）。"""
    from common.rs.photogrammetry import rpy_to_rotation

    lat_o = lat.astype(np.float64).copy()
    lon_o = lon.astype(np.float64).copy()
    alt_o = alt.astype(np.float64).copy()
    arm = np.array([lever_e_m, lever_n_m, lever_u_m], dtype=np.float64)
    if np.allclose(arm, 0):
        return lat_o, lon_o, alt_o
    for i in range(len(lat)):
        rot = rpy_to_rotation(float(roll[i]), float(pitch[i]), float(yaw[i]))
        d_enu = rot @ arm
        m_lon, m_lat = meters_per_deg(float(lat[i]))
        lon_o[i] += d_enu[0] / max(m_lon, 1e-9)
        lat_o[i] += d_enu[1] / max(m_lat, 1e-9)
        alt_o[i] += d_enu[2]
    return lat_o, lon_o, alt_o


def solve_pos(
    time_s: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
    alt: np.ndarray,
    roll: np.ndarray,
    pitch: np.ndarray,
    yaw: np.ndarray,
    *,
    alpha: float = 0.85,
    lever_enu: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> dict:
    """生产 POS 后处理：粗差剔除 → 位置互补+RTS → 姿态解缠+RTS → 杠杆臂。"""
    n = len(time_s)
    keep = reject_gnss_outliers(time_s, lat, lon, alt)
    if keep.sum() < 1:
        keep = np.ones(n, dtype=bool)
    # 被剔除点用线性插值回填后再滤波
    idx = np.arange(n)
    good = idx[keep]
    lat_i = np.interp(idx, good, lat[keep])
    lon_i = np.interp(idx, good, lon[keep])
    alt_i = np.interp(idx, good, alt[keep])
    lat_c, lon_c, alt_c = complementary_position(time_s, lat_i, lon_i, alt_i, alpha=alpha)
    lat_s = rts_smooth_1d(lat_c, q=1e-12, r=1e-10)
    lon_s = rts_smooth_1d(lon_c, q=1e-12, r=1e-10)
    alt_s = rts_smooth_1d(alt_c, q=1e-3, r=2e-2)
    roll_u = unwrap_deg(roll)
    pitch_u = unwrap_deg(pitch)
    yaw_u = unwrap_deg(yaw)
    roll_s = rts_smooth_1d(roll_u, q=1e-2, r=5e-2)
    pitch_s = rts_smooth_1d(pitch_u, q=1e-2, r=5e-2)
    yaw_s = rts_smooth_1d(yaw_u, q=1e-2, r=5e-2)
    lat_s, lon_s, alt_s = apply_lever_arm(
        lat_s, lon_s, alt_s, roll_s, pitch_s, yaw_s, *lever_enu
    )
    vel = estimate_velocity(time_s, lat_s, lon_s, alt_s)
    frames = []
    for i in range(n):
        frames.append(
            {
                "time": float(time_s[i]),
                "lat": float(lat_s[i]),
                "lon": float(lon_s[i]),
                "alt": float(alt_s[i]),
                "roll": float(roll_s[i]),
                "pitch": float(pitch_s[i]),
                "yaw": float(math.fmod(yaw_s[i] + 360.0, 360.0)),
                "ve": float(vel[i, 0]),
                "vn": float(vel[i, 1]),
                "vu": float(vel[i, 2]),
                "gnss_ok": bool(keep[i]),
            }
        )
    return {
        "method": "complementary+RTS+lever_arm",
        "n": n,
        "n_outlier": int((~keep).sum()),
        "alpha": alpha,
        "lever_enu_m": list(lever_enu),
        "frames": frames,
    }
