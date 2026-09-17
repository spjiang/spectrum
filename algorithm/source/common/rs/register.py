"""相位相关配准：Kuglin–Hines + Foroosh 亚像元平移。"""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
from scipy.ndimage import map_coordinates, shift as nd_shift
from skimage.transform import resize

from common.rs.parallel import map_threads, worker_count


def _wrap_peak(idx: int, n: int) -> float:
    return float(idx if idx <= n // 2 else idx - n)


def foroosh_delta(c0: float, c1: float) -> float:
    """
    Foroosh et al. 2002：由主峰与旁瓣估计亚像元偏移。
    Δ = C1 / (C1 + sign(C1)*C0)
    """
    if abs(c0) < 1e-12 and abs(c1) < 1e-12:
        return 0.0
    s = 1.0 if c1 >= 0 else -1.0
    denom = c1 + s * c0
    if abs(denom) < 1e-12:
        return 0.0
    d = c1 / denom
    return float(np.clip(d, -1.0, 1.0))


def phase_correlation_subpixel(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    """
    返回 (dy, dx, peak_response)。
    a/b 为同尺寸 2D。
    """
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    a = a - a.mean()
    b = b - b.mean()
    win_y = np.hanning(a.shape[0])[:, None]
    win_x = np.hanning(a.shape[1])[None, :]
    fa = np.fft.fft2(a * win_y * win_x)
    fb = np.fft.fft2(b * win_y * win_x)
    r = fa * np.conj(fb)
    r /= np.abs(r) + 1e-12
    c = np.fft.ifft2(r).real
    peak = np.unravel_index(int(np.argmax(c)), c.shape)
    py, px = int(peak[0]), int(peak[1])
    h, w = c.shape
    c0 = float(c[py, px])
    c_yp = float(c[(py + 1) % h, px])
    c_yn = float(c[(py - 1) % h, px])
    c_xp = float(c[py, (px + 1) % w])
    c_xn = float(c[py, (px - 1) % w])
    dy = _wrap_peak(py, h) + foroosh_delta(c0, c_yp if abs(c_yp) >= abs(c_yn) else c_yn)
    dx = _wrap_peak(px, w) + foroosh_delta(c0, c_xp if abs(c_xp) >= abs(c_xn) else c_xn)
    if abs(c_yn) > abs(c_yp):
        dy = _wrap_peak(py, h) - foroosh_delta(c0, c_yn)
    if abs(c_xn) > abs(c_xp):
        dx = _wrap_peak(px, w) - foroosh_delta(c0, c_xn)
    return float(dy), float(dx), float(c0)


def _resize_cube(src_cube: np.ndarray, hw: tuple[int, int]) -> np.ndarray:
    """把立方体空间尺寸缩到参考网格。"""
    h, w = hw
    if src_cube.shape[:2] == (h, w):
        return src_cube.astype(np.float64, copy=False)
    out = np.empty((h, w, src_cube.shape[2]), dtype=np.float64)
    for bi in range(src_cube.shape[2]):
        out[:, :, bi] = resize(src_cube[:, :, bi], (h, w), preserve_range=True, anti_aliasing=True)
    return out


def _iter_tiles(h: int, w: int, tile_size: int):
    """有效边长至少 16 的分块。"""
    for r0 in range(0, h, tile_size):
        for c0 in range(0, w, tile_size):
            r1 = min(h, r0 + tile_size)
            c1 = min(w, c0 + tile_size)
            if r1 - r0 < 16 or c1 - c0 < 16:
                continue
            yield slice(r0, r1), slice(c0, c1)


def _global_shift(ref_g: np.ndarray, src_g: np.ndarray, *, max_side: int = 512) -> tuple[float, float, float]:
    """大图先缩到 max_side 再相位相关，位移按尺度还原。"""
    h, w = ref_g.shape
    longest = max(h, w)
    if longest <= max_side:
        return phase_correlation_subpixel(ref_g, src_g)
    nh = max(32, int(round(h * max_side / longest)))
    nw = max(32, int(round(w * max_side / longest)))
    a = resize(ref_g, (nh, nw), preserve_range=True, anti_aliasing=True)
    b = resize(src_g, (nh, nw), preserve_range=True, anti_aliasing=True)
    dy, dx, peak = phase_correlation_subpixel(a, b)
    return dy * (h / nh), dx * (w / nw), peak


def _refine_shift(
    ref_g: np.ndarray,
    src_g: np.ndarray,
    dy: float,
    dx: float,
    peak: float,
    tile_size: int,
    workers: int,
) -> tuple[float, float, float, int, str]:
    """分块相位相关校核全局平移。"""
    h, w = ref_g.shape
    ts = int(tile_size) if tile_size else 0
    n_tiles = 1
    method = "phase_correlation_foroosh"
    if not (ts >= 16 and max(h, w) > ts):
        return dy, dx, peak, n_tiles, method
    tiles = list(_iter_tiles(h, w, ts))
    n_workers = worker_count(workers) if len(tiles) > 1 else 1

    def _one(item):
        rs, cs = item
        return phase_correlation_subpixel(ref_g[rs, cs], src_g[rs, cs])

    records = map_threads(_one, tiles, n_workers)
    n_tiles = max(len(records), 1)
    method = "phase_correlation_foroosh_tiled"
    close = [
        item
        for item in records
        if abs(item[0] - dy) < 2.0 and abs(item[1] - dx) < 2.0
    ]
    if len(close) >= 2:
        dy = float(np.median([item[0] for item in close]))
        dx = float(np.median([item[1] for item in close]))
        peak = float(np.median([item[2] for item in close]))
    return dy, dx, peak, n_tiles, method


def register_to_reference(
    ref_cube: np.ndarray,
    src_cube: np.ndarray,
    *,
    tile_size: int = 0,
    workers: int = 0,
) -> tuple[np.ndarray, dict]:
    """将 src 配准到 ref 网格：先降采样到参考行列，再相位相关。大图缩略图估全局位移，分块只作校核。"""
    src_cube = _resize_cube(src_cube.astype(np.float64, copy=False), ref_cube.shape[:2])
    ref_g = ref_cube.mean(axis=2)
    src_g = src_cube.mean(axis=2)
    ts = int(tile_size) if tile_size else 0
    dy, dx, peak = _global_shift(ref_g, src_g)
    dy, dx, peak, n_tiles, method = _refine_shift(ref_g, src_g, dy, dx, peak, ts, workers)
    aligned = np.empty_like(src_cube, dtype=np.float64)
    for bi in range(src_cube.shape[2]):
        aligned[:, :, bi] = nd_shift(src_cube[:, :, bi], shift=(dy, dx), order=3, mode="nearest")
    meta = {
        "method": method,
        "dy": dy,
        "dx": dx,
        "peak_response": peak,
        "n_tiles": n_tiles,
        "tile_size": ts,
        "workers": worker_count(workers) if n_tiles > 1 else 1,
    }
    return aligned, meta


def _read_gray_overview(path: Path, height: int, width: int) -> np.ndarray:
    """把栅格读成指定行列的均波段灰度，用于缩略图相位相关。"""
    import rasterio

    with rasterio.open(path) as src:
        data = src.read(out_shape=(src.count, height, width)).astype(np.float64)
    return data.mean(axis=0)


def _read_gray_overview_window(
    path: Path,
    r0: int,
    c0: int,
    rh: int,
    cw: int,
    dst_h: int | None = None,
    dst_w: int | None = None,
) -> np.ndarray:
    """读一个窗口的均波段。src 若尺寸不同，按目标网格映射窗口。"""
    import rasterio
    from rasterio.windows import Window

    with rasterio.open(path) as src:
        if dst_h is None:
            win = Window(c0, r0, cw, rh)
            data = src.read(window=win).astype(np.float64)
        else:
            scale_r = src.height / float(dst_h)
            scale_c = src.width / float(dst_w or src.width)
            sr0 = int(np.floor(r0 * scale_r))
            sc0 = int(np.floor(c0 * scale_c))
            sr1 = int(np.ceil((r0 + rh) * scale_r))
            sc1 = int(np.ceil((c0 + cw) * scale_c))
            sr0 = max(0, sr0)
            sc0 = max(0, sc0)
            sr1 = min(src.height, max(sr1, sr0 + 1))
            sc1 = min(src.width, max(sc1, sc0 + 1))
            win = Window(sc0, sr0, sc1 - sc0, sr1 - sr0)
            data = src.read(window=win, out_shape=(src.count, rh, cw)).astype(np.float64)
    return data.mean(axis=0)


def _write_shifted_rgb(
    src_path: Path,
    dst_path: Path,
    *,
    height: int,
    width: int,
    profile: dict,
    dy: float,
    dx: float,
    tile_size: int,
    workers: int,
) -> None:
    """把 RGB 缩到参考网格并按 (dy,dx) 分块写出，不分配整幅对齐立方体。"""
    import rasterio
    from rasterio.windows import Window

    from common.io import default_profile

    with rasterio.open(src_path) as src:
        src_h, src_w, src_b = src.height, src.width, src.count
    bands = src_b
    step = max(16, int(tile_size) if tile_size else 512)
    n_workers = worker_count(workers)
    out_profile = default_profile(height, width, bands, "float32")
    for key in ("crs", "transform", "compress"):
        if key in profile and profile[key] is not None:
            out_profile[key] = profile[key]
    if width >= 256 and height >= 256:
        out_profile["tiled"] = True
        out_profile["blockxsize"] = 256
        out_profile["blockysize"] = 256
    scale_r = src_h / float(height)
    scale_c = src_w / float(width)
    pad = 3
    windows: list[tuple[int, int, int, int]] = []
    for r0 in range(0, height, step):
        rh = min(step, height - r0)
        for c0 in range(0, width, step):
            cw = min(step, width - c0)
            windows.append((r0, c0, rh, cw))

    def _one(item: tuple[int, int, int, int]) -> tuple[int, int, np.ndarray]:
        r0, c0, rh, cw = item
        rr = (np.arange(r0, r0 + rh) - dy) * scale_r
        cc = (np.arange(c0, c0 + cw) - dx) * scale_c
        rmin = int(np.floor(rr.min())) - pad
        rmax = int(np.ceil(rr.max())) + pad + 1
        cmin = int(np.floor(cc.min())) - pad
        cmax = int(np.ceil(cc.max())) + pad + 1
        rmin_c = max(0, rmin)
        cmin_c = max(0, cmin)
        rmax_c = min(src_h, rmax)
        cmax_c = min(src_w, cmax)
        block = np.empty((rh, cw, bands), dtype=np.float64)
        if rmax_c <= rmin_c or cmax_c <= cmin_c:
            block[:] = 0
            return r0, c0, block.astype(np.float32)
        win = Window(cmin_c, rmin_c, cmax_c - cmin_c, rmax_c - rmin_c)
        with rasterio.open(src_path) as src:
            data = src.read(window=win).astype(np.float64)
        coords_r = np.broadcast_to((rr - rmin_c)[:, None], (rh, cw))
        coords_c = np.broadcast_to((cc - cmin_c)[None, :], (rh, cw))
        for bi in range(bands):
            block[:, :, bi] = map_coordinates(
                data[bi],
                [coords_r, coords_c],
                order=3,
                mode="nearest",
            )
        return r0, c0, block.astype(np.float32)

    dst_path = Path(dst_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    batch = max(n_workers * 2, 1)
    with rasterio.open(dst_path, "w", **out_profile) as dst:
        for i in range(0, len(windows), batch):
            chunk = windows[i : i + batch]
            for r0, c0, block in map_threads(_one, chunk, n_workers):
                dst.write(
                    np.moveaxis(block, -1, 0),
                    window=Window(c0, r0, block.shape[1], block.shape[0]),
                )


def register_to_path(
    ref_path: Path,
    src_path: Path,
    hsi_out: Path,
    rgb_out: Path,
    *,
    tile_size: int = 512,
    workers: int = 0,
) -> dict:
    """磁盘流式配准：缩略图估平移，分块写出 RGB，HSI 原文件拷贝。"""
    import rasterio

    with rasterio.open(ref_path) as ref:
        height, width = int(ref.height), int(ref.width)
        profile = ref.profile.copy()
    longest = max(height, width)
    max_side = 512
    if longest <= max_side:
        nh, nw = height, width
    else:
        nh = max(32, int(round(height * max_side / longest)))
        nw = max(32, int(round(width * max_side / longest)))
    ref_g = _read_gray_overview(ref_path, nh, nw)
    src_g = _read_gray_overview(src_path, nh, nw)
    dy, dx, peak = phase_correlation_subpixel(ref_g, src_g)
    dy *= height / float(nh)
    dx *= width / float(nw)
    ts = int(tile_size) if tile_size else 0
    n_tiles = 1
    method = "phase_correlation_foroosh"
    if ts >= 16 and max(height, width) > ts:
        tiles = list(_iter_tiles(height, width, ts))
        n_workers = worker_count(workers) if len(tiles) > 1 else 1

        def _one(item):
            rs, cs = item
            rh = rs.stop - rs.start
            cw = cs.stop - cs.start
            a = _read_gray_overview_window(ref_path, rs.start, cs.start, rh, cw)
            b = _read_gray_overview_window(src_path, rs.start, cs.start, rh, cw, height, width)
            return phase_correlation_subpixel(a, b)

        records = map_threads(_one, tiles, n_workers)
        n_tiles = max(len(records), 1)
        method = "phase_correlation_foroosh_tiled"
        close = [
            item
            for item in records
            if abs(item[0] - dy) < 2.0 and abs(item[1] - dx) < 2.0
        ]
        if len(close) >= 2:
            dy = float(np.median([item[0] for item in close]))
            dx = float(np.median([item[1] for item in close]))
            peak = float(np.median([item[2] for item in close]))
    shutil.copy2(ref_path, hsi_out)
    _write_shifted_rgb(
        src_path,
        rgb_out,
        height=height,
        width=width,
        profile=profile,
        dy=dy,
        dx=dx,
        tile_size=ts or 512,
        workers=workers,
    )
    return {
        "method": method,
        "dy": dy,
        "dx": dx,
        "peak_response": peak,
        "n_tiles": n_tiles,
        "tile_size": ts,
        "workers": worker_count(workers),
    }
