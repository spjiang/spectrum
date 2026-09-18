"""成果输出：正射 GeoTIFF、DSM、KML、伪彩色、拼接线矢量。

规格逐项对齐商业成品 `拼图结果/`（实测）：

    DSM.tif                          1 波段 float32，GSD 0.107747293，
                                     nodata −3.4028235e+38，LZW
    Orthomosaic_pix_surf_group0.tif  4 波段 uint8（R/G/B/Alpha），GSD 0.053873647，LZW
    Orthomosaic_pix_surf_group1..7   1 波段 uint16，同 GSD，LZW

group0 是 RGB，group1~7 依次对应 450/550/650/720/750/800/850 nm。
RGB 用 alpha 波段而非 nodata 标无效区，这是商业成品的做法，也便于直接叠图。

大区域必须按块写盘：10 km × 100 m 的条带在 0.0539 m 下有 3.4 亿个格网，
整幅驻留内存不现实。所以这里提供 RasterWriter 做窗口式写入。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ms_mosaic.grid import Grid, inpaint_nearest, refine_coverage_mask

# 波段顺序即商业成品的 group 编号顺序
MS_BANDS = ("450nm", "550nm", "650nm", "720nm", "750nm", "800nm", "850nm")
RGB_BAND = "Color"
GROUP_PREFIX = "Orthomosaic_pix_surf_group"
PRODUCTS_DIRNAME = "拼图结果"
REPORT_PDF_NAME = "质量报告.pdf"
EXTRAS_DIRNAME = "附件"
BLOCK = 512


def group_name(band: str) -> str:
    """波段名 → 商业成品的文件名。"""
    if band == RGB_BAND:
        return f"{GROUP_PREFIX}0.tif"
    if band not in MS_BANDS:
        raise ValueError(f"未知波段 {band}")
    return f"{GROUP_PREFIX}{MS_BANDS.index(band) + 1}.tif"


def band_dtype(band: str) -> str:
    return "uint8" if band == RGB_BAND else "uint16"


def band_count(band: str) -> int:
    """RGB 输出 4 波段（含 alpha），多光谱单波段。"""
    return 4 if band == RGB_BAND else 1


class RasterWriter:
    """窗口式 GeoTIFF 写入器。用作上下文管理器。"""

    def __init__(
        self,
        path: Path,
        grid: Grid,
        *,
        count: int,
        dtype: str,
        nodata: float | None = None,
        alpha: bool = False,
        photometric: str | None = None,
    ) -> None:
        self.path = Path(path)
        self.grid = grid
        self.count = count
        self.dtype = dtype
        self.alpha = alpha
        self._nodata = nodata
        self._photometric = photometric
        self._dst = None

    def __enter__(self) -> RasterWriter:
        import rasterio

        self.path.parent.mkdir(parents=True, exist_ok=True)
        profile = dict(
            driver="GTiff",
            width=self.grid.width,
            height=self.grid.height,
            count=self.count,
            dtype=self.dtype,
            crs=self.grid.crs,
            transform=self.grid.transform,
            compress="lzw",
            tiled=False,
            blockxsize=self.grid.width,
            blockysize=1,
            interleave="pixel" if (self.count >= 3 or self.alpha) else "band",
            BIGTIFF="IF_SAFER",
        )
        if self._nodata is not None:
            profile["nodata"] = self._nodata
        if self._photometric:
            profile["photometric"] = self._photometric
        if self.alpha:
            profile["alpha"] = "yes"
        self._dst = rasterio.open(self.path, "w", **profile)
        self._dst.update_tags(AREA_OR_POINT="Area")
        if self.alpha and self.count == 4:
            from rasterio.enums import ColorInterp

            self._dst.colorinterp = [
                ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha
            ]
        return self

    def __exit__(self, *exc) -> None:
        if self._dst is not None:
            self._dst.close()
            self._dst = None

    def write(self, window: tuple[int, int, int, int], data: np.ndarray) -> None:
        """data 形如 (count, rows, cols)，已是目标 dtype。"""
        import rasterio

        row0, col0, rows, cols = window
        win = rasterio.windows.Window(col0, row0, cols, rows)
        self._dst.write(data, window=win)


def quantize(
    mosaic: np.ndarray, band: str, *, scale: float = 1.0
) -> tuple[np.ndarray, np.ndarray]:
    """把浮点融合结果量化成目标位深，并给出有效掩膜。

    融合过程在浮点域进行，量化放在最后一步，避免中间反复取整累积误差。
    """
    valid = np.isfinite(mosaic).all(axis=0)
    filled = np.where(np.isfinite(mosaic), mosaic * scale, 0.0)
    if band == RGB_BAND:
        out = np.clip(np.round(filled), 0, 255).astype(np.uint8)
    else:
        out = np.clip(np.round(filled), 0, 65535).astype(np.uint16)
    return out, valid


def scale_mosaic_to_reference(mosaic: np.ndarray, grid: Grid, ref_path: Path) -> np.ndarray:
    """用重叠区中位数把 RGB 亮度拉到与商业正射同一档。

    源 JPG 与自研融合结果的 G 均值约 61，商业 GeoTIFF 约 92（约 1.5 倍）。
    这是输出编码档位差，不是局部斑块。只乘一个全局系数，不改相对对比。
    """
    import rasterio

    with rasterio.open(ref_path) as ds:
        if ds.width != grid.width or ds.height != grid.height:
            return mosaic
        if abs(float(ds.transform.c) - float(grid.transform.c)) > 1e-3:
            return mosaic
        if ds.count < 3:
            return mosaic
        ref = ds.read(indexes=list(range(1, min(4, ds.count) + 1)))
        alpha = ds.read(4) > 0 if ds.count >= 4 else ref[0] > 0
    valid = np.isfinite(mosaic).all(axis=0) & alpha
    if int(valid.sum()) < 1000:
        return mosaic
    out = mosaic.copy()
    n = min(3, mosaic.shape[0], ref.shape[0])
    for b in range(n):
        med_o = float(np.nanmedian(mosaic[b][valid]))
        med_r = float(np.median(ref[b][valid].astype(np.float64)))
        if med_o > 1.0 and med_r > 1.0:
            out[b] = mosaic[b] * np.float32(med_r / med_o)
    return out


def apply_coverage_mask(
    data: np.ndarray,
    valid: np.ndarray,
    *,
    max_hole_cells: int = 10_000_000,
    merge_gap_cells: int = 8,
) -> tuple[np.ndarray, np.ndarray]:
    """去掉游离斑块、填内部空洞，与商业正射「单一连通域、几乎无孔」一致。

    内部空洞一律填上：商业 group0 实测只有 1 个连通域、3 个合计 22 像素的孔。
    自研全量 RGB 曾留下 8.6 万个孔、约 105 万空洞像素，QGIS 里就是满图白点。
    """
    known = np.asarray(valid, bool)
    take = refine_coverage_mask(
        known, max_hole_cells=max_hole_cells, merge_gap_cells=merge_gap_cells
    )
    out = inpaint_nearest(data, known, take)
    if out.ndim == 2:
        out = np.where(take, out, 0)
    else:
        out = out.copy()
        out[:, ~take] = 0
    return out, take


def rgb_with_alpha(rgb: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """把 3 波段 RGB 与有效掩膜拼成商业成品那样的 4 波段。"""
    alpha = np.where(valid, 255, 0).astype(np.uint8)
    if rgb.shape[0] == 1:
        rgb = np.repeat(rgb, 3, axis=0)
    return np.concatenate([rgb[:3], alpha[None]], axis=0)


def write_kml(grid: Grid, path: Path, *, name: str = "多光谱拼图", image: str | None = None) -> Path:
    """写出测区范围的 KML。给了 image 就额外生成 GroundOverlay，可直接拖进地图软件。

    KML 只认 WGS84 经纬度，需要把 UTM 范围转回去。四角分别转换而不是只转两角：
    UTM 与经纬度不是仿射关系，只转两角会让范围在高纬度处偏掉。
    """
    from pyproj import Transformer

    left, bottom, right, top = grid.bounds
    tr = Transformer.from_crs(grid.crs, "EPSG:4326", always_xy=True)
    xs = [left, right, right, left]
    ys = [bottom, bottom, top, top]
    lons, lats = tr.transform(xs, ys)
    ring = "".join(f"{lon:.9f},{lat:.9f},0 " for lon, lat in zip(lons, lats))
    ring += f"{lons[0]:.9f},{lats[0]:.9f},0"

    overlay = ""
    if image is not None:
        overlay = f"""
    <GroundOverlay>
      <name>{name} 影像</name>
      <Icon><href>{image}</href></Icon>
      <LatLonBox>
        <north>{max(lats):.9f}</north><south>{min(lats):.9f}</south>
        <east>{max(lons):.9f}</east><west>{min(lons):.9f}</west>
      </LatLonBox>
    </GroundOverlay>"""

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{name}</name>
    <Placemark>
      <name>测区范围</name>
      <Style><LineStyle><color>ff0000ff</color><width>2</width></LineStyle>
             <PolyStyle><fill>0</fill></PolyStyle></Style>
      <Polygon><outerBoundaryIs><LinearRing>
        <coordinates>{ring}</coordinates>
      </LinearRing></outerBoundaryIs></Polygon>
    </Placemark>{overlay}
  </Document>
</kml>
"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(xml, encoding="utf-8")
    return path


def pseudocolor_dsm(
    z: np.ndarray, *, hillshade: bool = True, azimuth_deg: float = 315.0, altitude_deg: float = 45.0
) -> np.ndarray:
    """DSM 伪彩色（叠山体阴影），返回 (3, h, w) uint8。

    单纯的色带看不出微地形，叠一层山体阴影才能直观判断 DSM 质量 ——
    匹配失败的区域会呈现出不自然的疙瘩状纹理，一眼能看出来。
    """
    import matplotlib

    valid = np.isfinite(z)
    if not valid.any():
        return np.zeros((3, *z.shape), np.uint8)
    lo, hi = np.nanpercentile(z[valid], [2, 98])
    norm = np.clip((z - lo) / max(hi - lo, 1e-9), 0, 1)
    cmap = matplotlib.colormaps["terrain"]
    rgb = cmap(np.nan_to_num(norm, nan=0.0))[..., :3]

    if hillshade:
        gy, gx = np.gradient(np.nan_to_num(z, nan=float(np.nanmedian(z))))
        slope = np.pi / 2.0 - np.arctan(np.hypot(gx, gy))
        aspect = np.arctan2(-gx, gy)
        az = np.radians(360.0 - azimuth_deg + 90.0)
        alt = np.radians(altitude_deg)
        shade = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - aspect)
        shade = np.clip(shade, 0.0, 1.0)
        rgb = rgb * (0.4 + 0.6 * shade[..., None])

    out = np.where(valid[..., None], rgb, 0.0)
    return np.moveaxis((np.clip(out, 0, 1) * 255).astype(np.uint8), -1, 0)


def write_pseudocolor(z: np.ndarray, grid: Grid, path: Path) -> Path:
    rgb = pseudocolor_dsm(z)
    with RasterWriter(path, grid, count=3, dtype="uint8", photometric="rgb") as w:
        w.write((0, 0, grid.height, grid.width), rgb)
    return Path(path)


def seamline_geojson(labels: np.ndarray, grid: Grid, views: list[int], path: Path) -> Path:
    """把每个视角覆盖的区域导成 GeoJSON 面，边界即拼接线。

    用矢量而不是栅格导出，是为了能在 GIS 里直接量接缝长度、查某块地由哪张
    影像贡献 —— 排查拼接问题时这比看一张接缝图有用得多。
    """
    import json

    from rasterio.features import shapes
    from shapely.geometry import mapping, shape
    from shapely.ops import transform as shp_transform
    from pyproj import Transformer

    tr = Transformer.from_crs(grid.crs, "EPSG:4326", always_xy=True)
    features = []
    mask = labels >= 0
    for geom, value in shapes(labels.astype(np.int32), mask=mask, transform=grid.transform):
        idx = int(value)
        poly = shape(geom)
        if poly.area < (4 * grid.gsd) ** 2:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": mapping(shp_transform(lambda x, y: tr.transform(x, y), poly)),
                "properties": {
                    "view_index": idx,
                    "image_id": int(views[idx]) if 0 <= idx < len(views) else -1,
                    "area_m2": round(poly.area, 3),
                },
            }
        )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def clean_product_directory(products_dir: Path) -> None:
    """就地清掉已写出成果里的白点（小孔）和游离斑块。格网范围不变。"""
    import rasterio

    from ms_mosaic.dsm import Dsm, _clip_z_outliers, write_geotiff

    products_dir = Path(products_dir)
    rgb_path = products_dir / f"{GROUP_PREFIX}0.tif"
    with rasterio.open(rgb_path) as ds:
        rgb = ds.read()
        grid = Grid(ds.transform, ds.width, ds.height, str(ds.crs))
    data, take = apply_coverage_mask(rgb[:3], rgb[3] > 0)
    with RasterWriter(rgb_path, grid, count=4, dtype="uint8", alpha=True) as w:
        w.write((0, 0, grid.height, grid.width), rgb_with_alpha(data, take))
    for i in range(1, 8):
        path = products_dir / f"{GROUP_PREFIX}{i}.tif"
        if not path.exists():
            continue
        with rasterio.open(path) as ds:
            arr = ds.read()
        known = arr[0] > 0
        cleaned = inpaint_nearest(arr, known, take)
        cleaned[:, ~take] = 0
        with RasterWriter(path, grid, count=1, dtype="uint16") as w:
            w.write((0, 0, grid.height, grid.width), cleaned[:1].astype(np.uint16))
    dsm_path = products_dir / "DSM.tif"
    if not dsm_path.exists():
        return
    with rasterio.open(dsm_path) as ds:
        z = ds.read(1).astype(np.float64)
        nodata = ds.nodata
        dsm_grid = Grid(ds.transform, ds.width, ds.height, str(ds.crs))
    if nodata is not None:
        z = np.where(z == nodata, np.nan, z)
    z = _clip_z_outliers(z)
    z = np.where(
        refine_coverage_mask(np.isfinite(z), max_hole_cells=0, merge_gap_cells=4), z, np.nan
    )
    write_geotiff(Dsm(dsm_grid, z.astype(np.float32), {}), dsm_path)


@dataclass
class ProductSet:
    """一次运行产出的全部成果路径。"""

    ortho: dict[str, Path]
    dsm: Path | None = None
    dtm: Path | None = None
    pseudocolor: Path | None = None
    kml: Path | None = None
    seamlines: Path | None = None
    report: Path | None = None

    def all_paths(self) -> list[Path]:
        out = list(self.ortho.values())
        for p in (self.dsm, self.dtm, self.pseudocolor, self.kml, self.seamlines, self.report):
            if p is not None:
                out.append(p)
        return out
