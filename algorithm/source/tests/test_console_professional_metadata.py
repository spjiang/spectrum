"""验证控制台专业字段元数据的完整性与关键语义。"""

from __future__ import annotations

from pathlib import Path
import unittest

from common import console_params, console_router
from common.console_catalog import get_console_algorithm, list_console_algorithms
from common.console_params import get_service_params


class ConsoleProfessionalMetadataTests(unittest.TestCase):
    REQUIRED_PARAMETER_DETAILS = {
        "label",
        "unit",
        "range",
        "defaultReason",
        "selectionGuide",
        "effect",
        "risk",
        "example",
    }

    def test_all_algorithms_expose_professional_field_metadata(self) -> None:
        items = list_console_algorithms()
        self.assertEqual(45, len(items))

        for item in items:
            with self.subTest(algorithm_id=item["id"]):
                self.assertTrue(item["fields"]["outputs"])
                for field in item["fields"]["inputs"]:
                    self.assertTrue(field.get("label"), field["name"])
                    self.assertTrue(field.get("description"), field["name"])
                    self.assertIn("selectionGuide", field)
                    self.assertTrue(field["selectionGuide"], field["name"])
                    self.assertIn("risk", field)
                    self.assertTrue(field["risk"], field["name"])

    def test_ndvi_band_fields_explain_zero_based_index(self) -> None:
        item = get_console_algorithm("27_ndvi")
        self.assertIsNotNone(item)
        assert item is not None

        red = next(
            row for row in item["fields"]["inputs"] if row["name"] == "params.red_band"
        )
        self.assertEqual("波段索引（从 0 开始）", red["unit"])
        self.assertIn("不是波长值", red["selectionGuide"])
        self.assertIn("620–680 nm", red["selectionGuide"])
        self.assertEqual(item["testdata"]["params"]["red_band"], red["default"])

    def test_same_parameter_can_have_algorithm_specific_guidance(self) -> None:
        detection = get_console_algorithm("40_detect_segment")
        anomaly = get_console_algorithm("42_anomaly_detect")
        self.assertIsNotNone(detection)
        self.assertIsNotNone(anomaly)
        assert detection is not None and anomaly is not None

        detection_percentile = next(
            row for row in detection["fields"]["inputs"] if row["name"] == "params.percentile"
        )
        anomaly_percentile = next(
            row for row in anomaly["fields"]["inputs"] if row["name"] == "params.percentile"
        )
        self.assertNotEqual(
            detection_percentile["selectionGuide"],
            anomaly_percentile["selectionGuide"],
        )

    def test_fields_follow_service_parameters_instead_of_testdata_ghosts(self) -> None:
        panel = get_console_algorithm("12_panel_reflectance")
        parcels = get_console_algorithm("45_parcel_zonal_stats")
        anomaly = get_console_algorithm("42_anomaly_detect")
        self.assertIsNotNone(panel)
        self.assertIsNotNone(parcels)
        self.assertIsNotNone(anomaly)
        assert panel is not None and parcels is not None and anomaly is not None

        panel_names = {row["name"] for row in panel["fields"]["inputs"]}
        parcel_names = {row["name"] for row in parcels["fields"]["inputs"]}
        anomaly_names = {row["name"] for row in anomaly["fields"]["inputs"]}
        self.assertIn("params.panel_reflectance", panel_names)
        self.assertNotIn("params.scale", panel_names)
        self.assertNotIn("params.roi", parcel_names)
        self.assertNotIn("scale", panel["testdata"]["params"])
        self.assertNotIn("roi", parcels["testdata"]["params"])
        self.assertTrue(
            {"params.method", "params.win", "params.inner"} <= anomaly_names
        )
        anomaly_rows = {row["name"]: row for row in anomaly["fields"]["inputs"]}
        self.assertEqual("lrx", anomaly_rows["params.method"]["default"])
        self.assertEqual(7, anomaly_rows["params.win"]["default"])
        self.assertEqual(3, anomaly_rows["params.inner"]["default"])

    def test_every_service_parameter_is_exposed_with_professional_detail(self) -> None:
        for item in list_console_algorithms():
            algorithm_id = item["id"]
            parameter_rows = {
                row["name"].removeprefix("params."): row
                for row in item["fields"]["inputs"]
                if row["name"].startswith("params.")
            }
            with self.subTest(algorithm_id=algorithm_id):
                self.assertEqual(set(get_service_params(algorithm_id)), set(parameter_rows))
                for key, row in parameter_rows.items():
                    self.assertTrue(
                        self.REQUIRED_PARAMETER_DETAILS <= row.keys(),
                        f"{algorithm_id}.{key}",
                    )
                    for detail_key in self.REQUIRED_PARAMETER_DETAILS:
                        self.assertNotEqual("", row[detail_key], f"{algorithm_id}.{key}.{detail_key}")
                    self.assertNotEqual(key, row["label"], f"{algorithm_id}.{key}.label")
                    self.assertNotEqual(
                        "依据当前算法说明、数据单位和业务目标选择，并记录实际取值。",
                        row["selectionGuide"],
                        f"{algorithm_id}.{key}.selectionGuide",
                    )

    def test_sample_run_keeps_submitted_overrides_and_filters_ghost_params(self) -> None:
        self.assertTrue(hasattr(console_router, "_merge_console_params"))
        merged = console_router._merge_console_params(
            "27_ndvi",
            {"red_band": 2, "nir_band": 3, "ghost": 99},
            {"red_band": 5, "ghost": 100},
        )
        self.assertEqual({"red_band": 5, "nir_band": 3}, merged)

    def test_file2_required_flag_follows_service_contract(self) -> None:
        required_ids = {
            "11_relative_radiometric",
            "16_orthorectify",
            "17_mosaic",
            "19_multi_source_register",
            "26_patch_build",
            "32_regression_inversion",
            "34_svm_rf_classify",
            "35_spectral_matching",
            "36_cnn1d_classify",
            "37_cnn3d_classify",
            "38_transformer_classify",
            "39_few_shot_classify",
            "41_unmixing",
            "43_change_detect",
        }
        for item in list_console_algorithms():
            algorithm_id = item["id"]
            file2 = next(
                (row for row in item["fields"]["inputs"] if row["name"] == "file2"),
                None,
            )
            with self.subTest(algorithm_id=algorithm_id):
                self.assertTrue(hasattr(console_params, "service_requires_file2"))
                self.assertEqual(
                    algorithm_id in required_ids,
                    console_params.service_requires_file2(algorithm_id),
                )
                if algorithm_id in required_ids:
                    self.assertIsNotNone(file2)
                    assert file2 is not None
                    self.assertTrue(file2["required"])

    def test_dynamic_default_parameters_keep_their_interface_types(self) -> None:
        expected = {
            ("01_flight_planning", "alt_m"): "float",
            ("04_flight_qc", "bit_depth"): "int",
            ("12_panel_reflectance", "panel_roi"): "list",
            ("13_atmospheric_correction", "wavelengths_nm"): "list",
            ("15_geo_locate", "gsd_m"): "float",
            ("20_bad_band_remove", "wavelengths_nm"): "list",
            ("33_physical_inversion", "wavelengths_nm"): "list",
        }
        for (algorithm_id, key), expected_type in expected.items():
            item = get_console_algorithm(algorithm_id)
            assert item is not None
            row = next(
                field
                for field in item["fields"]["inputs"]
                if field["name"] == f"params.{key}"
            )
            with self.subTest(algorithm_id=algorithm_id, key=key):
                self.assertEqual(expected_type, row["type"])

    def test_every_output_explains_interpretation_and_quality_check(self) -> None:
        for item in list_console_algorithms():
            for row in item["fields"]["outputs"]:
                with self.subTest(algorithm_id=item["id"], field=row["name"]):
                    self.assertTrue(row.get("selectionGuide"))
                    self.assertTrue(row.get("qualityCheck"))
                    self.assertTrue(row.get("downstreamUse"))

    def test_parameter_controls_have_accessible_names(self) -> None:
        component = (
            Path(__file__).parents[2] / "web" / "src" / "components" / "RunForm.vue"
        ).read_text(encoding="utf-8")
        self.assertEqual(5, component.count(':aria-label="fieldTitle(f)"'))

    def test_detect_segment_lists_conditional_annotation_output(self) -> None:
        item = get_console_algorithm("40_detect_segment")
        assert item is not None
        output_names = {row["name"] for row in item["fields"]["outputs"]}
        self.assertIn("files.annotation_geojson", output_names)

    def test_result_status_uses_keyboard_accessible_button(self) -> None:
        component = (
            Path(__file__).parents[2] / "web" / "src" / "views" / "AlgoView.vue"
        ).read_text(encoding="utf-8")
        self.assertIn(
            '<button\n        v-if="result"\n        class="status-line"',
            component,
        )


if __name__ == "__main__":
    unittest.main()
