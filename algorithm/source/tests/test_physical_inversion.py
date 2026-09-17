"""#33 PROSAIL LUT：RMSE 代价、最优解集平均、边界命中。"""
from __future__ import annotations

import asyncio
import importlib
import json
import unittest

import numpy as np

from common.console_params import get_service_params
from common.scientific_evidence import get_algorithm_evidence
from tests.test_console_output_knowledge import geotiff_upload, remove_job_output


class LutMatchTests(unittest.TestCase):
    def test_rmse_single_best_stays_on_grid(self) -> None:
        from common.rs.prosail_inv import match_lut

        lut = np.array(
            [
                [0.10, 0.20, 0.30],
                [0.40, 0.50, 0.60],
                [0.70, 0.80, 0.90],
            ],
            dtype=np.float64,
        )
        lai_v = np.array([1.0, 2.0, 3.0])
        cab_v = np.array([10.0, 30.0, 50.0])
        spectra = lut[1:2]
        lai, cab, meta = match_lut(
            spectra,
            lut,
            lai_v,
            cab_v,
            cost_method="rmse",
            best_frac=0.01,
        )
        self.assertEqual(meta["best_n"], 1)
        self.assertEqual(meta["cost_method"], "rmse")
        np.testing.assert_allclose(lai, [2.0])
        np.testing.assert_allclose(cab, [30.0])

    def test_rmse_ensemble_averages_best_members_off_grid(self) -> None:
        from common.rs.prosail_inv import match_lut

        lut = np.array(
            [
                [0.00, 0.00, 0.00],
                [1.00, 1.00, 1.00],
                [2.00, 2.00, 2.00],
                [3.00, 3.00, 3.00],
            ],
            dtype=np.float64,
        )
        lai_v = np.array([1.0, 2.0, 3.0, 4.0])
        cab_v = np.array([10.0, 20.0, 30.0, 40.0])
        spectra = np.array([[1.50, 1.50, 1.50]], dtype=np.float64)
        lai, cab, meta = match_lut(
            spectra,
            lut,
            lai_v,
            cab_v,
            cost_method="rmse",
            best_frac=0.5,
        )
        self.assertEqual(meta["best_n"], 2)
        np.testing.assert_allclose(lai, [2.5])
        np.testing.assert_allclose(cab, [25.0])

    def test_sam_prefers_shape_when_rmse_prefers_magnitude(self) -> None:
        from common.rs.prosail_inv import match_lut

        lut = np.array(
            [
                [0.10, 0.20, 0.30],
                [0.18, 0.38, 0.55],
            ],
            dtype=np.float64,
        )
        lai_v = np.array([2.0, 5.0])
        cab_v = np.array([20.0, 60.0])
        spectra = np.array([[0.20, 0.40, 0.60]], dtype=np.float64)
        lai_rmse, _cab_rmse, _ = match_lut(
            spectra, lut, lai_v, cab_v, cost_method="rmse", best_frac=0.01
        )
        lai_sam, _cab_sam, _ = match_lut(
            spectra, lut, lai_v, cab_v, cost_method="sam", best_frac=0.01
        )
        np.testing.assert_allclose(lai_rmse, [5.0])
        np.testing.assert_allclose(lai_sam, [2.0])

    def test_boundary_hits_require_all_selected_on_edge(self) -> None:
        from common.rs.prosail_inv import match_lut

        lut = np.array(
            [
                [0.0, 0.0],
                [1.0, 1.0],
                [2.0, 2.0],
            ],
            dtype=np.float64,
        )
        lai_v = np.array([0.2, 3.1, 6.0])
        cab_v = np.array([10.0, 40.0, 70.0])
        spectra = np.array(
            [
                [-1.0, -1.0],
                [1.0, 1.0],
            ],
            dtype=np.float64,
        )
        _lai, _cab, meta = match_lut(
            spectra,
            lut,
            lai_v,
            cab_v,
            cost_method="rmse",
            best_frac=0.01,
        )
        self.assertEqual(meta["n_boundary_lai"], 1)
        self.assertEqual(meta["n_boundary_cab"], 1)


class PhysicalInversionServiceTests(unittest.TestCase):
    def test_service_exposes_industry_lut_params(self) -> None:
        params = get_service_params("33_physical_inversion")
        self.assertEqual(params["n_lai"], 25)
        self.assertEqual(params["n_cab"], 16)
        self.assertEqual(params["best_frac"], 0.05)
        self.assertEqual(params["cost_method"], "rmse")
        self.assertIn("wavelengths_nm", params)
        self.assertEqual(params["solar_zenith"], 30)
        self.assertEqual(params["view_zenith"], 0)
        self.assertEqual(params["relative_azimuth"], 0)

    def test_unknown_cost_method_fails_closed(self) -> None:
        service = importlib.import_module("algorithms.33_physical_inversion.service")
        cube = np.full((2, 2, 4), 0.2, dtype=np.float32)
        response = asyncio.run(
            service.run(
                file=geotiff_upload(cube, "bad-cost.tif"),
                file2=None,
                params_json='{"cost_method": "sid", "n_lai": 2, "n_cab": 2}',
            )
        )
        self.assertFalse(response["success"])
        self.assertIn("rmse", response["message"])
        self.assertIn("sam", response["message"])
        self.assertFalse(response.get("files"))

    def test_invert_recovers_lut_member_when_best_n_is_one(self) -> None:
        from common.rs.prosail_inv import build_lut, invert_cube

        wl = np.array([450.0, 550.0, 670.0, 800.0])
        lut, lai_v, cab_v = build_lut(wl, n_lai=3, n_cab=2)
        cube = lut[2].reshape(1, 1, -1)
        lai, cab, meta = invert_cube(
            cube,
            wl,
            n_lai=3,
            n_cab=2,
            best_frac=0.01,
            cost_method="rmse",
        )
        self.assertEqual(meta["lut_size"], 6)
        self.assertEqual(meta["best_n"], 1)
        self.assertEqual(meta["cost_method"], "rmse")
        np.testing.assert_allclose(lai, [[lai_v[2]]])
        np.testing.assert_allclose(cab, [[cab_v[2]]])

    def test_service_returns_ensemble_and_boundary_metadata(self) -> None:
        service = importlib.import_module("algorithms.33_physical_inversion.service")
        cube = np.full((2, 3, 4), 0.25, dtype=np.float32)
        response = asyncio.run(
            service.run(
                file=geotiff_upload(cube, "prosail.tif"),
                file2=None,
                params_json=json.dumps(
                    {
                        "n_lai": 3,
                        "n_cab": 2,
                        "best_frac": 0.5,
                        "cost_method": "rmse",
                        "wavelengths_nm": [450, 550, 670, 800],
                    }
                ),
            )
        )
        try:
            self.assertTrue(response["success"], response.get("message"))
            self.assertEqual(
                set(response["files"]),
                {"lai_tif", "cab_tif", "preview_png"},
            )
            data = response["data"]
            self.assertEqual(data["lut_size"], 6)
            self.assertEqual(data["best_n"], 3)
            self.assertEqual(data["cost_method"], "rmse")
            self.assertEqual(data["n_lai"], 3)
            self.assertEqual(data["n_cab"], 2)
            self.assertIn("n_boundary_lai", data)
            self.assertIn("n_boundary_cab", data)
            self.assertGreaterEqual(data["n_boundary_lai"], 0)
            self.assertGreaterEqual(data["n_boundary_cab"], 0)
        finally:
            remove_job_output(response)


class PhysicalInversionEvidenceTests(unittest.TestCase):
    def test_formula_cites_weiss_rmse_ensemble_and_combal_limitation(self) -> None:
        row = get_algorithm_evidence("33_physical_inversion")
        assert row is not None
        claims = {claim["claimId"]: claim for claim in row["claims"]}
        refs = {ref["referenceId"]: ref for ref in row["references"]}
        formula = claims["formula"]["text"]
        limitation = claims["limitation"]["text"]
        self.assertIn("RMSE", formula)
        self.assertIn("平均", formula)
        self.assertNotIn("12×8", formula)
        self.assertIn("先验", limitation)
        authors = " ".join(item["authors"] for item in row["references"])
        self.assertIn("Weiss", authors)
        self.assertIn("Darvishzadeh", authors)
        self.assertIn("Combal", authors)
        weiss = next(item for item in row["references"] if "Weiss" in item["authors"])
        darvish = next(
            item for item in row["references"] if "Darvishzadeh" in item["authors"]
        )
        combal = next(item for item in row["references"] if "Combal" in item["authors"])
        self.assertIn("formula", weiss["supports"])
        self.assertIn("formula", darvish["supports"])
        self.assertEqual(combal["supports"], ["limitation"])
        self.assertIn(weiss["referenceId"], claims["formula"]["referenceIds"])
        self.assertIn(darvish["referenceId"], claims["formula"]["referenceIds"])
        self.assertIn(combal["referenceId"], claims["limitation"]["referenceIds"])
        self.assertNotIn(combal["referenceId"], claims["formula"]["referenceIds"])
        self.assertTrue(all(item["url"].startswith("https://") for item in (weiss, darvish, combal)))
        _ = refs


class PhysicalInversionConsoleCopyTests(unittest.TestCase):
    def test_input_and_output_fields_explain_lut_roles(self) -> None:
        from common.console_catalog import get_console_algorithm

        item = get_console_algorithm("33_physical_inversion")
        assert item is not None
        inputs = {row["name"]: row for row in item["fields"]["inputs"]}
        outputs = {row["name"]: row for row in item["fields"]["outputs"]}

        solar = inputs["params.solar_zenith"]
        self.assertEqual(solar["label"], "太阳天顶角")
        self.assertIn("查找表", solar["effect"])
        self.assertNotIn("核值", solar["effect"])
        self.assertIn("BRDF", solar["risk"])

        n_lai = inputs["params.n_lai"]
        self.assertEqual(n_lai["label"], "叶面积表有几档")
        self.assertEqual(n_lai["default"], 25)
        self.assertIn("档数", n_lai["effect"])

        best_frac = inputs["params.best_frac"]
        self.assertEqual(best_frac["label"], "平均最好的那部分表行")
        self.assertEqual(best_frac["default"], 0.05)

        cost = inputs["params.cost_method"]
        self.assertEqual(cost["label"], "比像不像的尺子")
        self.assertEqual(cost["default"], "rmse")

        self.assertIn("密不密", outputs["files.lai_tif"]["label"])
        self.assertIn("绿不绿", outputs["files.cab_tif"]["label"])
        self.assertIn("只渲 LAI", outputs["files.preview_png"]["label"])
        self.assertEqual(outputs["data.lut_size"]["label"], "查找表有多少条")
        self.assertEqual(outputs["data.best_n"]["label"], "实际平均了几条")
        self.assertIn("贴边", outputs["data.n_boundary_lai"]["label"])
