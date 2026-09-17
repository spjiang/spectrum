"""46–55 植被指数：公式数值、单波段 GeoTIFF、越界失败。"""
from __future__ import annotations

import asyncio
import importlib
import json
import unittest

import numpy as np

from tests.test_console_output_knowledge import geotiff_upload, remove_job_output


def _cube() -> np.ndarray:
    """教学默认索引：蓝 0、绿 1、红 2、近红外 3、红边 4、短波红外 5。"""
    cube = np.zeros((2, 3, 6), dtype=np.float32)
    cube[..., 0] = 0.06
    cube[..., 1] = 0.10
    cube[..., 2] = 0.08
    cube[..., 3] = 0.40
    cube[..., 4] = 0.22
    cube[..., 5] = 0.14
    return cube


def _run(algorithm_id: str, params: dict) -> dict:
    service = importlib.import_module(f"algorithms.{algorithm_id}.service")
    return asyncio.run(
        service.run(
            file=geotiff_upload(_cube(), f"{algorithm_id}.tif"),
            file2=None,
            params_json=json.dumps(params),
        )
    )


class VegetationIndices4655Tests(unittest.TestCase):
    def _assert_index(self, algorithm_id: str, file_key: str, expected: float, params: dict) -> None:
        from common.io import load_raster
        from pathlib import Path

        response = _run(algorithm_id, params)
        try:
            self.assertTrue(response["success"], response.get("message"))
            self.assertEqual(set(response["files"]), {file_key, "preview_png"})
            path = Path(response["files"][file_key])
            self.assertEqual(path.name, f"{file_key.removesuffix('_tif')}.tif")
            arr, _profile = load_raster(path)
            self.assertEqual(arr.ndim, 2)
            np.testing.assert_allclose(arr, expected, rtol=1e-5, atol=1e-6)
            self.assertEqual(response["data"]["format"], "GeoTIFF")
            self.assertEqual(response["data"]["shape"], [2, 3])
        finally:
            remove_job_output(response)

    def test_reci_is_nir_over_red_edge_minus_one(self) -> None:
        nir, re = 0.40, 0.22
        self._assert_index(
            "46_reci",
            "reci_tif",
            nir / (re + 1e-12) - 1.0,
            {"re_band": 4, "nir_band": 3},
        )

    def test_gndvi_is_normalized_nir_green(self) -> None:
        nir, green = 0.40, 0.10
        self._assert_index(
            "47_gndvi",
            "gndvi_tif",
            (nir - green) / (nir + green + 1e-12),
            {"green_band": 1, "nir_band": 3},
        )

    def test_osavi_uses_fixed_soil_term(self) -> None:
        nir, red, soil_l = 0.40, 0.08, 0.16
        self._assert_index(
            "48_osavi",
            "osavi_tif",
            (nir - red) / (nir + red + soil_l),
            {"red_band": 2, "nir_band": 3, "L": 0.16},
        )

    def test_arvi_uses_blue_corrected_red(self) -> None:
        nir, red, blue, gamma = 0.40, 0.08, 0.06, 1.0
        rb = red - gamma * (blue - red)
        self._assert_index(
            "49_arvi",
            "arvi_tif",
            (nir - rb) / (nir + rb + 1e-12),
            {"blue_band": 0, "red_band": 2, "nir_band": 3, "gamma": 1.0},
        )

    def test_vari_is_visible_only(self) -> None:
        green, red, blue = 0.10, 0.08, 0.06
        self._assert_index(
            "50_vari",
            "vari_tif",
            (green - red) / (green + red - blue + 1e-12),
            {"blue_band": 0, "green_band": 1, "red_band": 2},
        )

    def test_lai_index_is_clipped_evi_linear_not_prosail(self) -> None:
        blue, red, nir = 0.06, 0.08, 0.40
        evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
        self._assert_index(
            "51_lai_index",
            "lai_index_tif",
            max(3.618 * evi - 0.118, 0.0),
            {"blue_band": 0, "red_band": 2, "nir_band": 3},
        )

    def test_nbr_matches_ndmi_form_on_same_swir(self) -> None:
        nir, swir = 0.40, 0.14
        self._assert_index(
            "52_nbr",
            "nbr_tif",
            (nir - swir) / (nir + swir + 1e-12),
            {"nir_band": 3, "swir_band": 5},
        )

    def test_sipi_is_pigment_ratio(self) -> None:
        nir, blue, red = 0.40, 0.06, 0.08
        self._assert_index(
            "53_sipi",
            "sipi_tif",
            (nir - blue) / (nir - red + 1e-12),
            {"blue_band": 0, "red_band": 2, "nir_band": 3},
        )

    def test_gci_is_nir_over_green_minus_one(self) -> None:
        nir, green = 0.40, 0.10
        self._assert_index(
            "54_gci",
            "gci_tif",
            nir / (green + 1e-12) - 1.0,
            {"green_band": 1, "nir_band": 3},
        )

    def test_ndsi_matches_mndwi_form_on_same_bands(self) -> None:
        green, swir = 0.10, 0.14
        self._assert_index(
            "55_ndsi",
            "ndsi_tif",
            (green - swir) / (green + swir + 1e-12),
            {"green_band": 1, "swir_band": 5},
        )

    def test_band_index_out_of_range_fails_closed(self) -> None:
        service = importlib.import_module("algorithms.46_reci.service")
        response = asyncio.run(
            service.run(
                file=geotiff_upload(_cube(), "reci-oob.tif"),
                file2=None,
                params_json='{"re_band": 9, "nir_band": 3}',
            )
        )
        self.assertFalse(response["success"])
        self.assertIn("越界", response["message"])
