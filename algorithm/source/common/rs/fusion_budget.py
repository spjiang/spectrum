"""融合墙钟预算：8 通道 GSD、两路正射并行、分块流式。"""
from __future__ import annotations

from common.rs.parallel import worker_count


def estimate_fusion_wall_s(
    *,
    area_km2: float = 12.0,
    gsd_m: float = 0.3,
    n_hsi_bands: int = 8,
    n_rgb_bands: int = 3,
    workers: int = 0,
    voxel_per_s_per_worker: float = 8.0e4,
) -> dict:
    """
    按像元量估算套合墙钟（秒）。
    两路正射+镶嵌并行，墙钟取较重的 8 通道一侧；配准按 RGB 对齐到 8 通道网格。
    voxel_per_s_per_worker 对应建议硬件上的保守吞吐。
    """
    n_workers = worker_count(workers)
    area_m2 = float(area_km2) * 1e6
    pixels = area_m2 / (float(gsd_m) ** 2)
    hsi_voxels = pixels * int(n_hsi_bands)
    rgb_voxels = pixels * int(n_rgb_bands)
    rate = float(voxel_per_s_per_worker) * n_workers
    qc_s = min(120.0, pixels / max(rate, 1.0) * 0.15)
    l1_s = hsi_voxels / max(rate, 1.0) * 0.25
    ortho_hsi_s = hsi_voxels / max(rate, 1.0)
    ortho_rgb_s = rgb_voxels / max(rate, 1.0)
    parallel_ortho_s = max(ortho_hsi_s, ortho_rgb_s)
    register_s = rgb_voxels / max(rate, 1.0) * 0.35
    write_s = (hsi_voxels + rgb_voxels) / max(rate, 1.0) * 0.08
    wall_s = qc_s + l1_s + parallel_ortho_s + register_s + write_s
    return {
        "area_km2": area_km2,
        "gsd_m": gsd_m,
        "pixels": pixels,
        "workers": n_workers,
        "qc_s": qc_s,
        "l1_s": l1_s,
        "parallel_ortho_mosaic_s": parallel_ortho_s,
        "register_s": register_s,
        "write_s": write_s,
        "wall_s": wall_s,
        "within_25_min": wall_s <= 25 * 60,
    }
