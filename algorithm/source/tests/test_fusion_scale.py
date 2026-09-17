"""大测区融合：分块配准、分块镶嵌、分行正射。"""
from __future__ import annotations

import asyncio
import io
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path

import numpy as np
from fastapi import UploadFile
from rasterio.crs import CRS
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from scipy.ndimage import shift as nd_shift

from common.io import load_raster
from common.rs.mosaic import mosaic_georeferenced
from common.rs.photogrammetry import orthorectify_collinearity
from common.rs.register import register_to_reference
from tests.test_console_output_knowledge import geotiff_upload, remove_job_output


def _pattern(h: int, w: int) -> np.ndarray:
    rng = np.random.default_rng(1)
    img = rng.random((h, w))
    yy, xx = np.mgrid[0:h, 0:w]
    img = img + 0.4 * np.exp(-((yy - h / 3) ** 2 + (xx - w / 2) ** 2) / 80.0)
    img = img + 0.3 * np.exp(-((yy - 2 * h / 3) ** 2 + (xx - w / 4) ** 2) / 40.0)
    return img.astype(np.float64)


def _profile(west: float, north: float, res: float = 1.0) -> dict:
    return {"crs": CRS.from_epsg(4326), "transform": from_origin(west, north, res, res)}


class RegisterTileTests(unittest.TestCase):
    def test_resizes_source_to_reference_grid(self) -> None:
        ref = np.stack([_pattern(20, 24)] * 3, axis=-1)
        src = np.stack([_pattern(40, 48)] * 3, axis=-1)
        aligned, meta = register_to_reference(ref, src, tile_size=16)
        self.assertEqual(aligned.shape[:2], (20, 24))
        self.assertEqual(aligned.shape[2], 3)
        self.assertIn("method", meta)

    def test_tiled_recovers_integer_shift(self) -> None:
        base = _pattern(64, 64)
        moved = nd_shift(base, shift=(4.0, -3.0), order=1, mode="nearest")
        ref = np.stack([base, base * 0.8], axis=-1)
        src = np.stack([moved, moved * 0.8], axis=-1)
        aligned, meta = register_to_reference(ref, src, tile_size=24)
        self.assertLess(abs(meta["dy"] - (-4.0)), 0.6)
        self.assertLess(abs(meta["dx"] - 3.0), 0.6)
        self.assertGreaterEqual(int(meta.get("n_tiles", 1)), 2)
        residual = np.abs(aligned[:, :, 0] - base)
        self.assertLess(float(np.median(residual[8:-8, 8:-8])), 0.15)


class MosaicTileTests(unittest.TestCase):
    def test_three_scenes_feather(self) -> None:
        a = np.ones((8, 8, 2), dtype=np.float32)
        b = np.full((8, 8, 2), 3.0, dtype=np.float32)
        c = np.full((8, 8, 2), 5.0, dtype=np.float32)
        out, profile, meta = mosaic_georeferenced(
            [a, b, c],
            [_profile(0, 10), _profile(4, 10), _profile(8, 10)],
        )
        self.assertEqual(meta["n_scenes"], 3)
        self.assertEqual(out.shape[0], 8)
        self.assertGreaterEqual(out.shape[1], 12)
        self.assertIsNotNone(profile.get("crs"))

    def test_tiled_write_matches_memory_mosaic(self) -> None:
        from common.rs.mosaic import mosaic_georeferenced_to_path

        a = np.ones((12, 12, 1), dtype=np.float32) * 2
        b = np.ones((12, 12, 1), dtype=np.float32) * 4
        profiles = [_profile(0, 20), _profile(6, 20)]
        mem, _, _ = mosaic_georeferenced([a, b], profiles)
        with tempfile.TemporaryDirectory() as tmp:
            out_tif = Path(tmp) / "mosaic.tif"
            mosaic_georeferenced_to_path([a, b], profiles, out_tif, tile_size=5)
            disk, _ = load_raster(out_tif)
        if disk.ndim == 2:
            disk = disk[:, :, None]
        np.testing.assert_allclose(disk, mem, rtol=1e-5, atol=1e-4)


class OrthoTileTests(unittest.TestCase):
    def test_row_tiles_match_full_frame(self) -> None:
        rng = np.random.default_rng(0)
        cube = rng.random((18, 16, 3))
        dem = np.linspace(10, 40, 18 * 16).reshape(18, 16)
        kwargs = dict(
            altitude_m=120.0,
            roll_deg=2.0,
            pitch_deg=-1.0,
            yaw_deg=0.0,
            focal_mm=8.0,
            pixel_um=5.5,
        )
        full, _ = orthorectify_collinearity(cube, dem, **kwargs)
        tiled, meta = orthorectify_collinearity(cube, dem, tile_rows=5, **kwargs)
        np.testing.assert_allclose(tiled, full, rtol=1e-6, atol=1e-6)
        self.assertEqual(meta.get("tile_rows"), 5)


def _geotiff_bytes(cube: np.ndarray, west: float) -> bytes:
    bands = np.moveaxis(cube, -1, 0).astype(np.float32)
    with MemoryFile() as memory_file:
        with memory_file.open(
            driver="GTiff",
            height=cube.shape[0],
            width=cube.shape[1],
            count=cube.shape[2],
            dtype="float32",
            crs=CRS.from_epsg(4326),
            transform=from_origin(west, 22.54, 0.00001, 0.00001),
        ) as dataset:
            dataset.write(bands)
        return memory_file.read()


class MosaicZipServiceTests(unittest.TestCase):
    def test_zip_of_three_strips_runs(self) -> None:
        import importlib

        service = importlib.import_module("algorithms.17_mosaic.service")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for i, west in enumerate((114.06, 114.06004, 114.06008)):
                zf.writestr(f"strip{i}.tif", _geotiff_bytes(np.ones((6, 6, 2), dtype=np.float32) * (i + 1), west))
        upload = UploadFile(file=BytesIO(buf.getvalue()), filename="strips.zip")
        response = asyncio.run(service.run(file=upload, file2=None, params_json='{"tile_size": 4}'))
        try:
            self.assertTrue(response["success"], response.get("message"))
            self.assertGreaterEqual(response["data"]["n_scenes"], 3)
        finally:
            remove_job_output(response)


class StreamAndParallelTests(unittest.TestCase):
    def test_ortho_workers_match_serial(self) -> None:
        rng = np.random.default_rng(0)
        cube = rng.random((18, 16, 3))
        dem = np.linspace(10, 40, 18 * 16).reshape(18, 16)
        kwargs = dict(
            altitude_m=120.0,
            roll_deg=2.0,
            pitch_deg=-1.0,
            yaw_deg=0.0,
            focal_mm=8.0,
            pixel_um=5.5,
            tile_rows=5,
        )
        serial, _ = orthorectify_collinearity(cube, dem, workers=1, **kwargs)
        parallel, meta = orthorectify_collinearity(cube, dem, workers=4, **kwargs)
        np.testing.assert_allclose(parallel, serial, rtol=1e-6, atol=1e-6)
        self.assertGreaterEqual(int(meta["workers"]), 1)

    def test_mosaic_paths_match_memory(self) -> None:
        from common.rs.mosaic import mosaic_paths_to_path
        from common.io import save_geotiff

        a = np.ones((12, 12, 1), dtype=np.float32) * 2
        b = np.ones((12, 12, 1), dtype=np.float32) * 4
        profiles = [_profile(0, 20), _profile(6, 20)]
        mem, _, _ = mosaic_georeferenced([a, b], profiles)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p1 = root / "a.tif"
            p2 = root / "b.tif"
            out_tif = root / "mosaic.tif"
            save_geotiff(a, p1, profile=profiles[0])
            save_geotiff(b, p2, profile=profiles[1])
            mosaic_paths_to_path([p1, p2], out_tif, tile_size=5, workers=2)
            disk, _ = load_raster(out_tif)
        if disk.ndim == 2:
            disk = disk[:, :, None]
        np.testing.assert_allclose(disk, mem, rtol=1e-4, atol=1e-3)

    def test_register_to_path_recovers_shift(self) -> None:
        from common.io import save_geotiff
        from common.rs.register import register_to_path

        base = _pattern(64, 64)
        moved = nd_shift(base, shift=(4.0, -3.0), order=1, mode="nearest")
        ref = np.stack([base, base * 0.8], axis=-1)
        src = np.stack([moved, moved * 0.8], axis=-1)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ref_p = root / "hsi.tif"
            src_p = root / "rgb.tif"
            hsi_out = root / "hsi_ref.tif"
            rgb_out = root / "rgb_aligned.tif"
            save_geotiff(ref.astype(np.float32), ref_p)
            save_geotiff(src.astype(np.float32), src_p)
            meta = register_to_path(ref_p, src_p, hsi_out, rgb_out, tile_size=24, workers=2)
            aligned, _ = load_raster(rgb_out)
        self.assertLess(abs(meta["dy"] - (-4.0)), 0.8)
        self.assertLess(abs(meta["dx"] - 3.0), 0.8)
        if aligned.ndim == 2:
            aligned = aligned[:, :, None]
        residual = np.abs(aligned[:, :, 0] - base)
        self.assertLess(float(np.median(residual[8:-8, 8:-8])), 0.2)

    def test_fusion_budget_12km2_fits_25_min(self) -> None:
        from common.rs.fusion_budget import estimate_fusion_wall_s

        budget = estimate_fusion_wall_s(area_km2=12.0, gsd_m=0.3, workers=16)
        self.assertTrue(budget["within_25_min"], budget)
        self.assertLessEqual(budget["wall_s"], 25 * 60)

    def test_dark_current_stream_matches_memory(self) -> None:
        from common.io import save_geotiff
        from common.rs.sensor import dark_current_correct, dark_current_correct_to_path

        rng = np.random.default_rng(2)
        cube = rng.random((20, 24, 3)) * 100 + 5
        mem, _ = dark_current_correct(cube)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "dn.tif"
            dst = root / "out.tif"
            save_geotiff(cube.astype(np.float32), src)
            dark_current_correct_to_path(src, dst, tile_rows=7)
            disk, _ = load_raster(dst)
        if disk.ndim == 2:
            disk = disk[:, :, None]
        np.testing.assert_allclose(disk, mem.astype(np.float32), rtol=1e-4, atol=1e-3)
