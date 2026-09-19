"""DSM 成果：粗差滤除、空洞填充、DTM 提取、GeoTIFF 输出。

输出规格对齐商业成品 `拼图结果/DSM.tif`：
float32、LZW 压缩、nodata = -3.4028235e+38、与正射同范围且 GSD 为正射的 2 倍。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ms_mosaic.dense import HeightField
from ms_mosaic.grid import Grid, inpaint_nearest, refine_coverage_mask

NODATA = np.float32(-3.4028234663852886e38)  # 与商业 DSM.tif 一致
SPIKE_MEDIAN_CELLS = 5
SPIKE_TOLERANCE_M = 2.5
SMOOTH_MEDIAN_CELLS = 3
MIN_CONFIDENCE = 0.02
DTM_OPENING_M = 12.0
# 航带边缘单视区：立体匹配经常解不出，但相片足迹还盖得到。商业正射把这块
# 铺上了；自研若只填封闭孔，缺口与测区外 nodata 连成一片就被 400k 上限跳过。
# 40 m ≈ 本测区缺失像元到有效 DSM 的 p99 距离，且小于右下角游离绿斑的间距。
MAX_FILL_GAP_M = 40.0


@dataclass
class Dsm:
    grid: Grid
    z: np.ndarray  # nan 表示无数据
    stats: dict

    @property
    def valid(self) -> np.ndarray:
        return np.isfinite(self.z)


def remove_spikes(
    z: np.ndarray,
    *,
    median_cells: int = SPIKE_MEDIAN_CELLS,
    tolerance_m: float = SPIKE_TOLERANCE_M,
) -> np.ndarray:
    """去孤立粗差：与邻域中值偏离过大的格网判为噪声。

    用中值而非均值，才不会被粗差本身带跑。判据取「固定容差」与「局部离散度」
    的较大者：固定容差管平坦区，局部离散度（由残差的 MAD 估计）管陡坎与
    植被区 —— 本批数据 161 m 的起伏下，单用 2.5 m 固定容差会把陡坡上
    两成的正常格网当成粗差删掉。
    """
    from scipy.ndimage import median_filter

    filled = np.where(np.isfinite(z), z, np.nan)
    if not np.isfinite(filled).any():
        return filled
    proxy = np.where(np.isfinite(filled), filled, np.nanmedian(filled))
    smooth = median_filter(proxy, size=median_cells, mode="nearest")
    residual = filled - smooth
    # 1.4826·MAD 是正态分布下标准差的稳健估计
    scale = 1.4826 * median_filter(
        np.where(np.isfinite(residual), np.abs(residual), 0.0), size=median_cells, mode="nearest"
    )
    limit = np.maximum(tolerance_m, 4.0 * scale)
    bad = np.isfinite(filled) & (np.abs(residual) > limit)
    return np.where(bad, np.nan, filled)


def median_smooth(
    z: np.ndarray,
    *,
    cells: int = SMOOTH_MEDIAN_CELLS,
) -> np.ndarray:
    """有效格网上的中值平滑（Kraus《Photogrammetry》DSM 去噪）。

    只改已有高程，不填空洞：空值用邻域中值作滤波垫，写回时仍保持 nan。
    窗口 3 格（本测区约 0.3 m）压匹配噪声，建筑块不会被抹平。
    """
    from scipy.ndimage import median_filter

    filled = np.asarray(z, np.float64)
    ok = np.isfinite(filled)
    size = int(cells) | 1
    if int(ok.sum()) < 4 or size < 3:
        return filled
    proxy = np.where(ok, filled, np.nanmedian(filled[ok]))
    smooth = median_filter(proxy, size=size, mode="nearest")
    return np.where(ok, smooth, np.nan)


OFFSETS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def _clip_z_outliers(z: np.ndarray, *, lo_pct: float = 0.2, hi_pct: float = 99.8) -> np.ndarray:
    """丢掉远离主体高程的格网。全量 DSM 曾出现 −1908 m 的飞点斑块。"""
    ok = np.isfinite(z)
    if int(ok.sum()) < 32:
        return z
    lo, hi = np.nanpercentile(z, [lo_pct, hi_pct])
    span = max(hi - lo, 1.0)
    return np.where((z < lo - 0.25 * span) | (z > hi + 0.25 * span), np.nan, z)


def fill_holes(
    z: np.ndarray,
    *,
    max_component_cells: int = 400_000,
    domain: np.ndarray | None = None,
) -> np.ndarray:
    """空洞填充：在空洞内求解拉普拉斯方程，边界取周围的有效高程。

    解 ∇²z = 0 得到的是调和插值面，它有两个我们要的性质：与空洞边界的高程和
    坡度自然衔接，且内部不会出现新的极值（最大值原理）—— 正射用它重采样时
    不会在空洞处冒出假的坎。

    一个自然的想法是「反复用有效邻域均值向内扩散」，但那样每个格网只取一次
    已定值邻域的均值就冻结，会把坡度逐层抹平：0.5 m/格 的坡面上误差可达 1 m。
    所以这里按连通域组装稀疏线性方程直接解，线性坡面能精确复原。

    domain 给出「应当有 DSM 的范围」（相片足迹 ∩ 距主体不太远）。没有 domain
    时，与测区外 nodata 连成一片的缺口会被当成超大空洞跳过；给了 domain 后
    只在域内补，大缺口改用最近邻（EDT），避免百万格 Laplace 撑爆内存。
    """
    from scipy.ndimage import find_objects, label
    from scipy.sparse import csr_matrix
    from scipy.sparse.linalg import spsolve

    out = np.array(z, dtype=np.float64, copy=True)
    hole = ~np.isfinite(out)
    if domain is not None:
        hole = hole & np.asarray(domain, bool)
    if not hole.any():
        return out
    if hole.all():
        return np.full_like(out, np.nan)

    height, width = out.shape
    # 必须按包围盒解：对每个连通域做 `components == id` 会扫整幅 DSM。
    # 全测区约 4000 万格、上万个小洞时，旧写法会卡死在补洞阶段。
    components, n_comp = label(hole)
    if n_comp == 0:
        return out
    slices = find_objects(components)
    for comp, slc in enumerate(slices, start=1):
        if slc is None:
            continue
        r0 = max(0, slc[0].start - 1)
        r1 = min(height, slc[0].stop + 1)
        c0 = max(0, slc[1].start - 1)
        c1 = min(width, slc[1].stop + 1)
        sub = components[r0:r1, c0:c1]
        mask = sub == comp
        n = int(mask.sum())
        if n == 0 or n > max_component_cells:
            # 超大空洞：无 domain 时是测区外，留 nodata；有 domain 时交给后面最近邻
            continue
        h, w = sub.shape
        idx = np.full((h, w), -1, np.int64)
        idx[mask] = np.arange(n)
        rows_i, cols_i = np.nonzero(mask)
        sub_z = out[r0:r1, c0:c1]

        diag = np.zeros(n)
        rhs = np.zeros(n)
        a_rows: list[np.ndarray] = []
        a_cols: list[np.ndarray] = []
        for dr, dc in OFFSETS:
            nr, nc = rows_i + dr, cols_i + dc
            inside = (nr >= 0) & (nr < h) & (nc >= 0) & (nc < w)
            sel = np.nonzero(inside)[0]
            if sel.size == 0:
                continue
            nb = idx[nr[sel], nc[sel]]
            is_hole = nb >= 0
            z_nb = sub_z[nr[sel], nc[sel]]
            is_known = (~is_hole) & np.isfinite(z_nb)
            use = is_hole | is_known
            diag[sel[use]] += 1
            a_rows.append(sel[is_hole])
            a_cols.append(nb[is_hole])
            np.add.at(rhs, sel[is_known], z_nb[is_known])

        if not np.any(diag > 0):
            continue
        r = np.concatenate([np.arange(n), *a_rows])
        c = np.concatenate([np.arange(n), *a_cols])
        v = np.concatenate([np.maximum(diag, 1.0), *[-np.ones(x.size) for x in a_rows]])
        # 完全被空洞包围的孤岛（rhs 全零且无已知邻居）无解，跳过留 nodata
        if not np.any(rhs != 0.0):
            continue
        sol = spsolve(csr_matrix((v, (r, c)), shape=(n, n)), rhs)
        out[rows_i + r0, cols_i + c0] = sol

    if domain is not None:
        take = np.asarray(domain, bool) | np.isfinite(out)
        still = take & ~np.isfinite(out)
        if still.any() and np.isfinite(out).any():
            out = inpaint_nearest(out, np.isfinite(out), take)
    return out


def _fill_domain(
    valid: np.ndarray,
    coverage: np.ndarray,
    gsd: float,
    max_fill_gap_m: float | None,
) -> np.ndarray:
    """应有 DSM 的范围：足迹/商业覆盖。max_fill_gap_m 为 None 时填满覆盖域。"""
    from scipy.ndimage import distance_transform_edt

    cov = np.asarray(coverage, bool)
    valid = np.asarray(valid, bool)
    if max_fill_gap_m is None:
        return valid | cov
    gap_cells = max(1, int(round(float(max_fill_gap_m) / max(float(gsd), 1e-9))))
    dist = distance_transform_edt(~valid)
    return valid | (cov & (dist <= gap_cells))


def build_dsm(
    field: HeightField,
    *,
    min_confidence: float = MIN_CONFIDENCE,
    tolerance_m: float = SPIKE_TOLERANCE_M,
    fill: bool = True,
    coverage: np.ndarray | None = None,
    max_fill_gap_m: float | None = MAX_FILL_GAP_M,
    clip_to_coverage: bool = False,
) -> Dsm:
    """由密集匹配的高程场生成 DSM。"""
    z = field.z.copy()
    low_conf = np.isfinite(field.confidence) & (field.confidence < min_confidence)
    z = np.where(low_conf, np.nan, z)
    raw_valid = int(np.isfinite(z).sum())

    z = remove_spikes(z, tolerance_m=tolerance_m)
    after_spikes = int(np.isfinite(z).sum())
    z = median_smooth(z)
    z = _clip_z_outliers(z)
    main = refine_coverage_mask(np.isfinite(z), max_hole_cells=0, merge_gap_cells=4)
    z = np.where(main, z, np.nan)
    if fill:
        domain = None
        if coverage is not None:
            domain = _fill_domain(main, coverage, field.grid.gsd, max_fill_gap_m)
        z = fill_holes(z, domain=domain)
        if clip_to_coverage and coverage is not None:
            z = np.where(np.asarray(coverage, bool), z, np.nan)

    valid = np.isfinite(z)
    stats = {
        "gsd": field.grid.gsd,
        "width": field.grid.width,
        "height": field.grid.height,
        "n_valid": int(valid.sum()),
        "fill_ratio": float(valid.mean()),
        "dropped_low_confidence": int(np.isfinite(field.z).sum() - raw_valid),
        "dropped_spikes": int(raw_valid - after_spikes),
        "z_min": float(np.nanmin(z)) if valid.any() else float("nan"),
        "z_median": float(np.nanmedian(z)) if valid.any() else float("nan"),
        "z_max": float(np.nanmax(z)) if valid.any() else float("nan"),
        "mean_point_spacing_m": field.grid.gsd,
    }
    return Dsm(field.grid, z.astype(np.float32), stats)


def complete_dsm_coverage(
    z: np.ndarray,
    grid: Grid,
    coverage: np.ndarray,
    *,
    max_fill_gap_m: float | None = MAX_FILL_GAP_M,
    clip_to_coverage: bool = False,
) -> np.ndarray:
    """已有 DSM 沿覆盖域补缺口。clip 时裁掉覆盖域外的突出。"""
    z = np.asarray(z, np.float64)
    main = np.isfinite(z)
    domain = _fill_domain(main, coverage, grid.gsd, max_fill_gap_m)
    out = fill_holes(z, domain=domain)
    if clip_to_coverage:
        out = np.where(np.asarray(coverage, bool), out, np.nan)
    return out


def to_dtm(dsm: Dsm, *, opening_m: float = DTM_OPENING_M) -> Dsm:
    """由 DSM morphological opening 得到 DTM（地面模型）。

    灰度形态学开运算按窗口取局部最低面，能压掉建筑与树冠；窗口需大于
    要滤除的地物平面尺寸，小于地形本身的起伏波长。
    """
    from scipy.ndimage import grey_opening, uniform_filter

    size = max(3, int(round(opening_m / dsm.grid.gsd)) | 1)
    filled = fill_holes(dsm.z.astype(np.float64))
    proxy = np.where(np.isfinite(filled), filled, np.nanmax(filled))
    ground = grey_opening(proxy, size=size, mode="nearest")
    ground = uniform_filter(ground, size // 2 | 1, mode="nearest")
    ground = np.where(np.isfinite(dsm.z), ground, np.nan)
    stats = dict(dsm.stats)
    stats["opening_m"] = opening_m
    stats["z_median"] = float(np.nanmedian(ground))
    return Dsm(dsm.grid, ground.astype(np.float32), stats)


def resample_height(
    z: np.ndarray,
    src: Grid,
    dst: Grid,
    window: tuple[int, int, int, int] | None = None,
) -> np.ndarray:
    """把 src 格网上的高程双线性重采样到 dst（或 dst 的一个窗口）。

    正射格网是 DSM 的 1:2 细化，真正射必须在正射分辨率上取高程。无效值
    （nan）不能当成 0 参与插值，否则空洞边缘会被拉出假斜坡。
    """
    from scipy.ndimage import map_coordinates

    xs, ys = dst.cell_centers(window)
    inv = ~src.transform
    cols, rows = inv * (xs, ys)
    # rasterio 的像素坐标把整数落在像元左上角，map_coordinates 把 0 当成第 0 个
    # 像元中心，差半个像元。不减 0.5 会把线性坡面整体平移 0.5 格。
    cols = np.asarray(cols, np.float64) - 0.5
    rows = np.asarray(rows, np.float64) - 0.5
    valid = np.isfinite(z).astype(np.float64)
    proxy = np.where(np.isfinite(z), z, 0.0).astype(np.float64)
    sampled = map_coordinates(proxy, [rows, cols], order=1, mode="nearest", prefilter=False)
    weight = map_coordinates(valid, [rows, cols], order=1, mode="nearest", prefilter=False)
    out = np.where(weight > 0.5, sampled, np.nan)
    return out.astype(np.float32)


def write_geotiff(dsm: Dsm, path: Path) -> Path:
    """写出与商业 DSM.tif 同规格的单波段 float32 GeoTIFF。"""
    import rasterio

    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.where(np.isfinite(dsm.z), dsm.z, NODATA).astype(np.float32)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=dsm.grid.width,
        height=dsm.grid.height,
        count=1,
        dtype="float32",
        crs=dsm.grid.crs,
        transform=dsm.grid.transform,
        nodata=float(NODATA),
        compress="lzw",
        tiled=False,
        blockxsize=dsm.grid.width,
        blockysize=1,
        interleave="band",
        BIGTIFF="IF_SAFER",
    ) as dst:
        dst.write(data, 1)
        dst.update_tags(AREA_OR_POINT="Area")
    return path
