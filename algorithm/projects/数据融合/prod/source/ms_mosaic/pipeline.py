from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from ms_mosaic.catalog import scan_directory
from ms_mosaic.geo import filter_usable
from ms_mosaic.mosaic import mosaic_paths, write_georef
from ms_mosaic.report import write_report

MS_BANDS = ["450nm", "550nm", "650nm", "720nm", "750nm", "800nm", "850nm"]


def _assert_out_outside_input(input_dir: Path, out_dir: Path) -> tuple[Path, Path]:
    """输入目录只读。成果必须写到输入目录之外。"""
    inp = input_dir.expanduser().resolve()
    out = out_dir.expanduser().resolve()
    if out == inp or inp in out.parents:
        raise ValueError(f"禁止写入输入目录 {inp}，请把 --out 指到别处（例如 prod/runs/）")
    return inp, out


def run_mosaic(
    input_dir: Path,
    out_dir: Path,
    *,
    max_frames: int | None = None,
    max_index: int | None = None,
) -> dict[str, Any]:
    t0 = time.time()
    input_dir, out_dir = _assert_out_outside_input(Path(input_dir), Path(out_dir))
    process = out_dir / "process"
    mosaics = out_dir / "mosaics"
    process.mkdir(parents=True, exist_ok=True)
    mosaics.mkdir(parents=True, exist_ok=True)

    scanned = scan_directory(input_dir, max_index=max_index)
    usable = filter_usable(scanned)
    items = sorted(usable.items())
    if max_frames is not None:
        items = items[: int(max_frames)]
    shots = dict(items)
    if not shots:
        raise ValueError(f"目录 {input_dir} 没有可用作业帧（POS + 离地）")

    rgb_paths: list[Path] = []
    band_paths: dict[str, list[Path]] = {b: [] for b in MS_BANDS}
    for idx, shot in shots.items():
        if shot.pos is None:
            continue
        if shot.rgb is not None:
            dst = process / f"{idx:04d}_rgb.tif"
            write_georef(shot.rgb.path, dst, shot.pos)
            rgb_paths.append(dst)
        for band, rec in shot.ms.items():
            if rec.role != "D":
                continue
            pos = rec.pos or shot.pos
            dst = process / f"{idx:04d}_{band}.tif"
            write_georef(rec.path, dst, pos)
            band_paths.setdefault(band, []).append(dst)

    files: dict[str, Any] = {"bands": {}}
    rgb_meta: dict[str, Any] = {}
    if rgb_paths:
        rgb_meta = mosaic_paths(rgb_paths, mosaics / "rgb.tif")
        files["rgb"] = rgb_meta["path"]
    for band, paths in band_paths.items():
        if not paths:
            continue
        meta = mosaic_paths(paths, mosaics / f"ms_{band}.tif")
        files["bands"][band] = meta["path"]

    elapsed = round(time.time() - t0, 3)
    payload = {
        "input": str(input_dir.resolve()),
        "n_scanned": len(scanned),
        "n_shots": len(shots),
        "n_filtered": len(scanned) - len(usable),
        "shot_indices": [idx for idx, _ in items],
        "crs": rgb_meta.get("crs") or "EPSG:32647",
        "elapsed_s": elapsed,
        "method": "pos_direct_georef + merge",
        "files": files,
        "rgb_meta": rgb_meta,
    }
    paths = write_report(out_dir, payload)
    files["report_json"] = paths["report_json"]
    files["report_md"] = paths["report_md"]
    payload["files"] = files
    return payload
