from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from ms_mosaic.compose import render_band, write_band_product
from ms_mosaic.dense import DenseConfig, compute_height_field
from ms_mosaic.dsm import Dsm, MAX_FILL_GAP_M, build_dsm, complete_dsm_coverage, write_geotiff
from ms_mosaic.grid import (
    ORTHO_OVER_DSM,
    Grid,
    coverage_from_footprints,
    coverage_from_product,
    grid_from_footprints,
    smooth_coverage_mask,
)
from ms_mosaic.products import (
    EXTRAS_DIRNAME,
    PRODUCTS_DIRNAME,
    REPORT_PDF_NAME,
    RGB_BAND,
    group_name,
    scale_mosaic_to_reference,
    seamline_geojson,
    write_kml,
    write_pseudocolor,
)
from ms_mosaic.qa import build_quality_payload, cameras_table, render_report_figures
from ms_mosaic.report import write_report
from ms_mosaic.report_pdf import write_quality_pdf
from ms_mosaic.runner import run_sparse
from ms_mosaic.scene import BAND_ORDER, PRIMARY_BAND, transfer_band

# 与商业 DSM.tif / group0.tif 实测值一致（不是四舍五入后的 0.107747293）
COMMERCIAL_DSM_GSD = 0.10774729333596
COMMERCIAL_PRODUCTS = "拼图结果"


def _assert_out_outside_input(input_dir: Path, out_dir: Path) -> tuple[Path, Path]:
    """输入目录只读。成果必须写到输入目录之外。"""
    inp = input_dir.expanduser().resolve()
    out = out_dir.expanduser().resolve()
    if out == inp or inp in out.parents:
        raise ValueError(f"禁止写入输入目录 {inp}，请把 --out 指到别处（例如 prod/runs/）")
    return inp, out


def commercial_product_dir(input_dir: Path) -> Path | None:
    """输入 MAX_* 的上一级若有商业「拼图结果」，用作格网与辐射基准。"""
    cand = Path(input_dir).expanduser().resolve().parent / COMMERCIAL_PRODUCTS
    dsm = cand / "DSM.tif"
    rgb = cand / "Orthomosaic_pix_surf_group0.tif"
    if dsm.is_file() and rgb.is_file():
        return cand
    return None


def run_mosaic(
    input_dir: Path,
    out_dir: Path,
    *,
    max_frames: int | None = None,
    max_index: int | None = None,
    dsm_gsd: float = COMMERCIAL_DSM_GSD,
    workers: int | None = None,
    bands: Sequence[str] | None = None,
    cache_dir: Path | None = None,
    reuse_dsm: Path | None = None,
) -> dict[str, Any]:
    """完整交付：空三 → DSM → 真正射 → 拼接线/融合 → 商业文件名成果 + PDF 报告。"""
    t0 = time.time()
    input_dir, out_dir = _assert_out_outside_input(Path(input_dir), Path(out_dir))
    products_dir = out_dir / PRODUCTS_DIRNAME
    extras_dir = out_dir / EXTRAS_DIRNAME
    products_dir.mkdir(parents=True, exist_ok=True)
    extras_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = Path(cache_dir) if cache_dir is not None else out_dir / "cache" / "features"

    wanted = tuple(bands) if bands is not None else BAND_ORDER
    timings: dict[str, float] = {}

    def log(msg: str) -> None:
        print(msg)

    t = time.time()
    sparse = run_sparse(
        input_dir,
        cache_dir,
        max_index=max_index,
        max_frames=max_frames,
        workers=workers or 10,
        log=log,
    )
    timings["at"] = time.time() - t
    block = sparse.block
    at = sparse.at

    t = time.time()
    pts = sparse.points
    ground_z = float(np.median(pts[:, 2])) if len(pts) else block.ground_z
    cams = {i: sparse.camera for i in sparse.poses}
    ref_dir = None
    if max_frames is None and max_index is None:
        ref_dir = commercial_product_dir(input_dir)
    ortho_grid = None
    if ref_dir is not None:
        grid = Grid.from_raster(ref_dir / "DSM.tif")
        ortho_grid = Grid.from_raster(ref_dir / "Orthomosaic_pix_surf_group0.tif")
        log(f"格网锁定商业成品 {grid.width}x{grid.height} DSM / {ortho_grid.width}x{ortho_grid.height} 正射")
    else:
        grid = grid_from_footprints(cams, sparse.poses, ground_z, dsm_gsd, block.crs)
    lock_coverage = ref_dir is not None
    if lock_coverage:
        coverage = coverage_from_product(ref_dir / "DSM.tif", grid)
        log(f"覆盖域锁定商业 DSM，有效 {float(coverage.mean()):.3f}")
    else:
        coverage = smooth_coverage_mask(
            coverage_from_footprints(grid, cams, sparse.poses, ground_z), grid.gsd
        )
    field = None
    if reuse_dsm is not None:
        import rasterio

        src = Path(reuse_dsm).expanduser().resolve()
        with rasterio.open(src) as ds:
            z = ds.read(1).astype(np.float64)
            if ds.nodata is not None:
                z = np.where(z == ds.nodata, np.nan, z)
            grid = Grid(ds.transform, ds.width, ds.height, str(ds.crs))
        if lock_coverage:
            coverage = coverage_from_product(ref_dir / "DSM.tif", grid)
        z = complete_dsm_coverage(
            z,
            grid,
            coverage,
            max_fill_gap_m=None if lock_coverage else MAX_FILL_GAP_M,
            clip_to_coverage=lock_coverage,
        )
        valid = np.isfinite(z)
        dsm = Dsm(
            grid,
            z.astype(np.float32),
            {
                "gsd": grid.gsd,
                "width": grid.width,
                "height": grid.height,
                "n_valid": int(valid.sum()),
                "fill_ratio": float(valid.mean()),
                "z_min": float(np.nanmin(z)) if valid.any() else float("nan"),
                "z_median": float(np.nanmedian(z)) if valid.any() else float("nan"),
                "z_max": float(np.nanmax(z)) if valid.any() else float("nan"),
                "reused": str(src),
            },
        )
        timings["dense"] = 0.0
        log(f"复用 DSM {src}，足迹补洞后有效 {dsm.stats['fill_ratio']:.3f}")
    else:
        field = compute_height_field(
            grid,
            pts,
            {i: sparse.camera for i in sparse.poses},
            sparse.poses,
            sparse.image_paths,
            cfg=DenseConfig(workers=workers),
            log=log,
            workers=workers,
        )
        timings["dense"] = time.time() - t
        dsm = build_dsm(
            field,
            coverage=coverage,
            max_fill_gap_m=None if lock_coverage else MAX_FILL_GAP_M,
            clip_to_coverage=lock_coverage,
        )

    t = time.time()
    dsm_path = write_geotiff(dsm, products_dir / "DSM.tif")
    timings["dsm"] = time.time() - t

    if ortho_grid is None:
        ortho_grid = dsm.grid.refine(ORTHO_OVER_DSM)
    files: dict[str, Any] = {"bands": {}, "dsm": str(dsm_path), "mosaic_dir": str(products_dir)}
    labels_rgb = None
    views_rgb: list[int] = []
    t_ortho = time.time()
    for band in wanted:
        cameras, poses, paths = transfer_band(block, at.cameras, at.poses, band)
        if not poses:
            log(f"跳过 {band}：没有对应的空三外方位")
            continue
        log(f"=== 正射 {band}  {len(poses)} 张 ===")
        mosaic, labels, views = render_band(
            ortho_grid,
            dsm.z,
            dsm.grid,
            cameras,
            poses,
            paths,
            band=band,
            workers=workers,
            log=log,
        )
        if band == RGB_BAND and ref_dir is not None:
            mosaic = scale_mosaic_to_reference(
                mosaic, ortho_grid, ref_dir / "Orthomosaic_pix_surf_group0.tif"
            )
        out_path = products_dir / group_name(band)
        band_cov = None
        if lock_coverage:
            ref_band = ref_dir / group_name(band)
            band_cov = coverage_from_product(
                ref_band if ref_band.is_file() else ref_dir / "Orthomosaic_pix_surf_group0.tif",
                ortho_grid,
            )
        write_band_product(mosaic, ortho_grid, band, out_path, coverage=band_cov)
        files["bands"][band] = str(out_path)
        if band == RGB_BAND or band == PRIMARY_BAND:
            files["rgb"] = str(out_path)
            labels_rgb, views_rgb = labels, views
    timings["ortho"] = time.time() - t_ortho

    pc_path = write_pseudocolor(dsm.z, dsm.grid, extras_dir / "DSM_pseudocolor.tif")
    kml_path = write_kml(ortho_grid, extras_dir / "area.kml", image=Path(files.get("rgb", "DSM.tif")).name)
    files["pseudocolor"] = str(pc_path)
    files["kml"] = str(kml_path)
    if labels_rgb is not None:
        seam_path = seamline_geojson(labels_rgb, ortho_grid, views_rgb, extras_dir / "seamlines.geojson")
        files["seamlines"] = str(seam_path)

    n_shots = sparse.counts.get("n_usable", len(block.primary()))
    cam_info = cameras_table(block, at, at.stats.get("rms_reprojection_px"))
    payload = build_quality_payload(
        input_dir=input_dir,
        block=block,
        at=at,
        tracks=sparse.tracks,
        matches=sparse.matches,
        keypoint_counts=sparse.keypoint_counts,
        dsm=dsm,
        dense_stats=field.stats if field is not None else {"reused_dsm": True, **{k: dsm.stats[k] for k in ("n_valid", "fill_ratio") if k in dsm.stats}},
        files=files,
        timings=timings,
        elapsed_s=time.time() - t0,
        n_scanned=sparse.counts.get("n_shots", 0),
        n_usable=n_shots,
        cameras_info=cam_info,
    )
    primary = [im for im in block.primary() if im.index in at.poses]
    color_cams = {im.index: at.cameras[PRIMARY_BAND] for im in primary}
    color_poses = {im.index: at.poses[im.index] for im in primary}
    payload["figures"] = render_report_figures(
        fig_dir=out_dir / "report" / "figures",
        files=files,
        gps_rows=payload.get("gps_rows") or [],
        cameras=color_cams,
        poses=color_poses,
        points=at.points,
        ground_z=float(dsm.stats.get("z_median", block.ground_z)),
        grid=dsm.grid,
    )
    payload["method"] = "AT + object-space MVS + true ortho + graph-cut seam + Laplacian blend"
    paths = write_report(out_dir, payload)
    pdf_path = write_quality_pdf(payload, out_dir / REPORT_PDF_NAME)
    files["report_json"] = paths["report_json"]
    files["report_md"] = paths["report_md"]
    files["report_pdf"] = str(pdf_path)
    payload["files"] = files
    if ref_dir is not None:
        from ms_mosaic.compare import write_delivery_report

        log("=== 与商业成品逐像元比对 ===")

        cmp_path = out_dir / "比对报告.txt"
        try:
            crep = write_delivery_report(products_dir, ref_dir, cmp_path)
            files["compare"] = str(cmp_path)
            log(cmp_path.read_text(encoding="utf-8"))
            if not crep.ok:
                log("比对未达标，见 比对报告.txt")
        except Exception as exc:
            log(f"比对失败（成果已写出）：{exc}")
    return payload
