"""稀疏重建的编排层：扫描 → 像对 → 特征 → 匹配 → 构网 → 空三。

单独成模块是因为特征提取和匹配要跑多进程，工作函数必须能被 pickle，
不能是闭包或局部函数。脚本与正式管线都调这里，避免两份实现走偏。
"""

from __future__ import annotations

import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ms_mosaic.at import ATResult, run_at
from ms_mosaic.camera import Camera, Pose
from ms_mosaic.catalog import scan_directory
from ms_mosaic.features import extract_file
from ms_mosaic.matching import PairMatches, match_pair
from ms_mosaic.pairs import select_pairs
from ms_mosaic.scene import PRIMARY_BAND, Block, build_block, usable_shots
from ms_mosaic.tracks import Tracks, build_tracks

_SHARED: dict = {}


@dataclass
class SparseResult:
    block: Block
    at: ATResult
    tracks: Tracks
    image_paths: dict[int, Path]
    poses: dict[int, Pose]
    camera: Camera
    timings: dict[str, float] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    matches: list[PairMatches] = field(default_factory=list)
    keypoint_counts: dict[int, int] = field(default_factory=dict)

    @property
    def points(self) -> np.ndarray:
        return self.at.points


def _extract_worker(job):
    index, path, cache_dir, max_features = job
    extract_file(Path(path), cache_dir=Path(cache_dir), max_features=max_features)
    return index


def _match_init(cache_dir, indices, paths, cam):
    _SHARED["cam"] = cam
    _SHARED["feats"] = {
        i: extract_file(Path(p), cache_dir=Path(cache_dir)) for i, p in zip(indices, paths)
    }


def _match_worker(job):
    i, j = job
    cam = _SHARED["cam"]
    pm = match_pair(i, j, _SHARED["feats"][i], _SHARED["feats"][j], cam, cam)
    if pm is None:
        return None
    return (pm.i, pm.j, pm.indices, pm.model)


def run_sparse(
    input_dir: Path,
    cache_dir: Path,
    *,
    max_index: int | None = None,
    max_frames: int | None = None,
    max_features: int = 8192,
    workers: int = 10,
    log=lambda *_: None,
) -> SparseResult:
    """跑完主波段的稀疏重建。输入目录只读。"""
    timings: dict[str, float] = {}
    t0 = time.time()

    shots = scan_directory(input_dir, max_index=max_index)
    keep, reasons = usable_shots(shots)
    if max_frames is not None:
        keys = sorted(keep)[: int(max_frames)]
        keep = {k: keep[k] for k in keys}
    block = build_block(keep)
    primary = block.primary()
    cam = block.cameras[PRIMARY_BAND]
    log(f"曝光 {len(shots)} → 可用 {len(keep)}（过滤 {reasons}）")

    cameras = {im.index: cam for im in primary}
    poses = {im.index: block.poses[im.index] for im in primary}
    candidates = select_pairs(cameras, poses, block.ground_z)
    log(f"候选像对 {len(candidates)} 对（全组合 {len(primary) * (len(primary) - 1) // 2}）")

    cache_dir.mkdir(parents=True, exist_ok=True)
    indices = [im.index for im in primary]
    paths = [str(im.path) for im in primary]

    t = time.time()
    jobs = [(i, p, str(cache_dir), max_features) for i, p in zip(indices, paths)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        list(pool.map(_extract_worker, jobs))
    timings["features"] = time.time() - t
    log(f"特征提取 {timings['features']:.1f}s")

    t = time.time()
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_match_init,
        initargs=(str(cache_dir), indices, paths, cam),
    ) as pool:
        raw = list(pool.map(_match_worker, [(c.i, c.j) for c in candidates], chunksize=4))
    matches = [PairMatches(*r) for r in raw if r is not None]
    timings["matching"] = time.time() - t
    log(f"匹配 {len(matches)}/{len(candidates)} 对成功，{timings['matching']:.1f}s")

    tracks = build_tracks(matches)
    log(
        f"连接点 {len(tracks)} 条，观测 {tracks.total_observations()}，"
        f"平均轨迹长 {tracks.lengths.mean():.2f}"
    )

    feats = {i: extract_file(Path(p), cache_dir=cache_dir) for i, p in zip(indices, paths)}
    image_camera = {i: PRIMARY_BAND for i in indices}
    gps = {i: block.gps[i] for i in indices}
    att = {i: block.poses[i].rotation for i in indices}

    t = time.time()
    at = run_at({PRIMARY_BAND: cam}, poses, tracks, feats, image_camera, gps, att, log=log)
    timings["at"] = time.time() - t
    timings["total"] = time.time() - t0
    log(f"空三 {timings['at']:.1f}s，稀疏重建合计 {timings['total']:.1f}s")

    return SparseResult(
        block=block,
        at=at,
        tracks=tracks,
        image_paths={i: Path(p) for i, p in zip(indices, paths)},
        poses=at.poses,
        camera=at.cameras[PRIMARY_BAND],
        timings=timings,
        counts={
            "n_shots": len(shots),
            "n_usable": len(keep),
            "n_primary": len(primary),
            "n_candidates": len(candidates),
            "n_matched_pairs": len(matches),
            "n_tracks": len(tracks),
        },
        matches=matches,
        keypoint_counts={i: len(feats[i]) for i in feats},
    )
