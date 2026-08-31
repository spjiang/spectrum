"""验证控制台输出知识库的契约结构与质量规则。"""

from __future__ import annotations

import builtins
import unittest
from unittest.mock import patch

from common.console_catalog import get_console_algorithm, list_console_algorithms
from common.console_output_knowledge import _collect_layer_knowledge, get_algorithm_output_knowledge

REQUIRED_OUTPUT_DETAILS = {
    "label",
    "description",
    "effect",
    "businessMeaning",
    "interpretation",
    "qualityCheck",
    "abnormalSigns",
    "downstreamUse",
}

L0_EXPECTED = {
    "01_flight_planning": {
        "files": {"mission_json", "waypoints_geojson"},
        "data": {
            "gsd_m",
            "swath_m",
            "footprint_along_m",
            "line_spacing_m",
            "photo_spacing_m",
            "n_lines",
            "n_waypoints",
            "est_path_m",
            "est_duration_s",
        },
    },
    "02_sync_timestamp": {
        "files": {"aligned_json"},
        "data": {"n_hsi", "n_rgb", "n_pos", "n_aligned", "clock_offset_rgb_s"},
    },
    "03_pos_solution": {
        "files": {"pos_json", "pos_csv"},
        "data": {"method", "n", "n_outlier", "alpha", "lever_enu_m"},
    },
    "04_flight_qc": {
        "files": {"report_json"},
        "data": {
            "passed",
            "suggest_refly",
            "saturation_level",
            "saturated_ratio",
            "underexposed_ratio",
            "max_saturated_ratio",
            "snr_per_band",
            "snr_min",
            "snr_median",
            "min",
            "max",
            "mean",
        },
    },
    "05_cloud_shadow": {
        "files": {
            "cloud_mask_tif",
            "shadow_mask_tif",
            "combo_mask_tif",
            "preview_png",
        },
        "data": {"n_cloud", "n_shadow", "legend"},
    },
    "06_dark_current": {
        "files": {"cube_tif"},
        "data": {"method", "fpn_abs_mean", "dark_mean", "mean"},
    },
    "07_bad_pixel": {
        "files": {"cube_tif"},
        "data": {"n_bad_cols", "n_auto_cols", "n_masked"},
    },
    "08_destriping": {"files": {"cube_tif"}, "data": set()},
    "09_smile_keystone": {
        "files": {"cube_tif"},
        "data": {"smile_shift_bands", "keystone_shift_cols"},
    },
    "10_radiance_calibration": {
        "files": {"radiance_tif"},
        "data": {"gain", "offset", "min", "max", "units"},
    },
    "11_relative_radiometric": {"files": {"cube_tif"}, "data": set()},
}

L2_EXPECTED = {
    "12_panel_reflectance": {
        "files": {"reflectance_tif"},
        "data": {"panel_reflectance", "panel_radiance", "dark_radiance", "min", "max", "mean"},
    },
    "13_atmospheric_correction": {
        "files": {"reflectance_tif"},
        "data": {"solar_zenith", "doy", "haze_radiance", "wavelengths_nm", "min", "max"},
    },
    "14_brdf_correction": {
        "files": {"cube_tif"},
        "data": {"solar_zenith", "view_zenith_edge", "relative_azimuth"},
    },
    "15_geo_locate": {
        "files": {"cube_tif", "meta_json"},
        "data": {"lon", "lat", "alt_m", "gsd_m", "res_deg", "yaw", "crs"},
    },
    "16_orthorectify": {
        "files": {"ortho_tif"},
        "data": {
            "gsd_m",
            "focal_px",
            "altitude_m",
            "roll_deg",
            "pitch_deg",
            "yaw_deg",
            "dem_min",
            "dem_max",
        },
    },
    "17_mosaic": {
        "files": {"mosaic_tif"},
        "data": {"n_scenes", "bounds", "resolution"},
    },
    "18_color_balance": {
        "files": {"cube_tif", "preview_png"},
        "data": {"window", "contrast", "brightness"},
    },
    "19_multi_source_register": {
        "files": {"hsi_tif", "rgb_aligned_tif"},
        "data": {"dy", "dx", "peak_response"},
    },
    "20_bad_band_remove": {
        "files": {"cube_tif"},
        "data": {"input_bands", "dropped", "kept", "snr_per_band", "wavelength_nm", "snr_ratio"},
    },
    "21_savgol_smooth": {
        "files": {"cube_tif"},
        "data": {"window_length", "polyorder"},
    },
    "22_normalize": {
        "files": {"cube_tif"},
        "data": {"method", "mean", "std"},
    },
    "23_pca": {
        "files": {"pca_tif"},
        "data": {"method", "eigenvalues", "explained_variance_ratio", "n_components"},
    },
    "24_band_select": {
        "files": {"cube_tif", "ranking_json"},
        "data": {"method", "selected", "scores"},
    },
    "25_superpixel": {
        "files": {"labels_tif", "preview_png"},
        "data": {"n_segments", "compactness", "n_unique"},
    },
    "26_patch_build": {
        "files": {"patches_npz", "manifest_json", "preview_png"},
        "data": {"n", "patch_size", "bands", "classes"},
    },
}

L3_EXPECTED = {
    "27_ndvi": {"files": {"ndvi_tif", "preview_png"}, "data": {"min", "max", "mean"}},
    "28_ndre": {"files": {"ndre_tif", "preview_png"}, "data": {"min", "max", "mean"}},
    "29_evi_savi": {
        "files": {"indices_tif", "preview_png"},
        "data": {"L", "evi_mean", "savi_mean", "msavi_mean"},
    },
    "30_ndmi_ndwi": {
        "files": {"indices_tif", "preview_png"},
        "data": {"ndmi_mean", "ndwi_mean", "mndwi_mean"},
    },
    "31_red_edge_params": {
        "files": {"params_tif", "preview_png"},
        "data": {
            "anchors_nm",
            "rep_mean",
            "amp_mean",
            "deriv_rep_mean",
            "wl_start_nm",
            "wl_end_nm",
        },
    },
    "32_regression_inversion": {
        "files": {"inversion_tif", "preview_png"},
        "data": {"r2", "rmse", "n_components", "n_train", "n_test", "preprocess"},
    },
    "33_physical_inversion": {
        "files": {"lai_tif", "cab_tif", "preview_png"},
        "data": {"model", "lut_size", "lai_mean", "lai_max", "cab_mean", "wavelengths_nm"},
    },
    "34_svm_rf_classify": {
        "files": {"pred_map_tif", "preview_png"},
        "data": {"oa", "aa", "kappa", "n_train", "n_test", "classes", "model"},
    },
    "35_spectral_matching": {
        "files": {"pred_map_tif", "angle_tif", "preview_png"},
        "data": {"method", "n_endmembers", "score_mean", "classes"},
    },
    "36_cnn1d_classify": {
        "files": {"pred_map_tif", "preview_png"},
        "data": {
            "oa",
            "aa",
            "kappa",
            "n_train",
            "n_test",
            "classes",
            "device",
            "architecture",
            "epochs",
        },
    },
    "37_cnn3d_classify": {
        "files": {"pred_map_tif", "preview_png"},
        "data": {
            "oa",
            "aa",
            "kappa",
            "n_train",
            "n_test",
            "classes",
            "device",
            "bands_after_pca",
            "architecture",
            "patch_size",
            "epochs",
        },
    },
    "38_transformer_classify": {
        "files": {"pred_map_tif", "preview_png"},
        "data": {
            "oa",
            "aa",
            "kappa",
            "n_train",
            "n_test",
            "classes",
            "device",
            "architecture",
            "epochs",
        },
    },
    "39_few_shot_classify": {
        "files": {"pred_map_tif", "preview_png"},
        "data": {"shots", "n_support", "classes", "oa", "aa", "kappa", "n_query"},
    },
    "40_detect_segment": {
        "files": {
            "score_tif",
            "mask_tif",
            "polygons_geojson",
            "annotation_geojson",
            "preview_png",
        },
        "data": {
            "threshold_ndvi",
            "ace_percentile",
            "n_objects",
            "n_positive_pixels",
            "has_annotation_geojson",
            "annotation_features",
        },
    },
    "41_unmixing": {
        "files": {"abundance_tif", "preview_png"},
        "data": {"n_endmembers", "abundance_mean", "sum_to_one_mean"},
    },
    "42_anomaly_detect": {
        "files": {"score_tif", "mask_tif", "preview_png"},
        "data": {
            "method",
            "percentile",
            "threshold",
            "n_anomaly_pixels",
            "score_min",
            "score_max",
            "score_mean",
        },
    },
    "43_change_detect": {
        "files": {"magnitude_tif", "chi2_tif", "mask_tif", "preview_png"},
        "data": {
            "canonical_correlations",
            "chi2_mean",
            "chi2_df",
            "percentile",
            "threshold",
            "n_change",
        },
    },
    "44_postprocess_smooth": {
        "files": {"labels_tif", "preview_png"},
        "data": {"min_pixels", "window", "n_changed", "classes"},
    },
    "45_parcel_zonal_stats": {
        "files": {"report_json", "parcel_geojson"},
        "data": {"mode", "n_parcels", "n_parcels_with_pixels", "scene", "parcels"},
    },
}

ALL_EXPECTED = {**L0_EXPECTED, **L2_EXPECTED, **L3_EXPECTED}


class ConsoleOutputKnowledgeTests(unittest.TestCase):
    def test_catalog_exposes_output_summary_and_core_metrics(self) -> None:
        """防止控制台遗漏算法摘要、真实文件或核心指标独立行。"""
        item = get_console_algorithm("27_ndvi")
        assert item is not None
        self.assertTrue(item["output_summary"]["what"])
        rows = {row["name"]: row for row in item["fields"]["outputs"]}
        self.assertTrue(
            {
                "files.ndvi_tif",
                "files.preview_png",
                "data.min",
                "data.max",
                "data.mean",
            }
            <= rows.keys()
        )
        self.assertTrue(rows["files.ndvi_tif"]["effect"])
        self.assertTrue(rows["data.mean"]["businessMeaning"])

    def test_catalog_real_file_outputs_use_algorithm_knowledge(self) -> None:
        """防止真实文件输出静默退回格式级泛化说明。"""
        for item in list_console_algorithms():
            for row in item["fields"]["outputs"]:
                if row["name"].startswith("files."):
                    with self.subTest(algorithm_id=item["id"], path=row["name"]):
                        self.assertEqual("algorithm", row["knowledgeSource"])

    def test_catalog_paths_match_all_algorithm_knowledge(self) -> None:
        """防止 45 个算法的真实文件键、核心指标路径缺失、重复或混入 data 聚合行。"""
        items = {item["id"]: item for item in list_console_algorithms()}
        self.assertEqual(set(ALL_EXPECTED), set(items))
        for algorithm_id, expected in ALL_EXPECTED.items():
            expected_paths = {
                f"{parent}.{api_key}"
                for parent, api_keys in expected.items()
                for api_key in api_keys
            }
            rows = items[algorithm_id]["fields"]["outputs"]
            paths = [row["name"] for row in rows]
            catalog_rows = {row["name"]: row for row in rows}
            knowledge_rows = get_algorithm_output_knowledge(algorithm_id)["outputs"]
            with self.subTest(algorithm_id=algorithm_id):
                self.assertEqual(expected_paths, set(paths))
                self.assertEqual(len(paths), len(set(paths)))
                self.assertNotIn("data", paths)
                for path in expected_paths:
                    self.assertEqual("algorithm", catalog_rows[path]["knowledgeSource"])
                    for field in ("optional", "conditional"):
                        self.assertEqual(
                            knowledge_rows[path][field],
                            catalog_rows[path][field],
                            f"{path}.{field}",
                        )
                    if "bands" in knowledge_rows[path]:
                        self.assertEqual(
                            knowledge_rows[path]["bands"],
                            catalog_rows[path]["bands"],
                            f"{path}.bands",
                        )

    def test_catalog_preserves_specialized_knowledge_fields(self) -> None:
        """防止旧输出泛化逻辑覆盖算法专属知识与可视化配置。"""
        item = get_console_algorithm("27_ndvi")
        assert item is not None
        catalog_row = {
            row["name"]: row for row in item["fields"]["outputs"]
        }["files.ndvi_tif"]
        knowledge_row = get_algorithm_output_knowledge("27_ndvi")["outputs"][
            "files.ndvi_tif"
        ]
        for field in (
            "label",
            "description",
            "effect",
            "businessMeaning",
            "interpretation",
            "qualityCheck",
            "downstreamUse",
            "vis",
        ):
            with self.subTest(field=field):
                self.assertEqual(knowledge_row[field], catalog_row[field])

        bad_band = get_console_algorithm("20_bad_band_remove")
        assert bad_band is not None
        self.assertIn(
            "data.wavelength_nm",
            {row["name"] for row in bad_band["fields"]["outputs"]},
        )
        self.assertNotIn(
            "data.wavelengths_nm",
            {row["name"] for row in bad_band["fields"]["outputs"]},
        )

    def test_output_knowledge_contract_is_structured(self) -> None:
        item = get_algorithm_output_knowledge("27_ndvi")
        self.assertEqual(set(item["summary"]), {"what", "value", "caution"})
        ndvi = item["outputs"]["files.ndvi_tif"]
        self.assertTrue(REQUIRED_OUTPUT_DETAILS <= ndvi.keys())
        self.assertEqual(ndvi["parent"], "files")
        self.assertEqual(ndvi["apiKey"], "ndvi_tif")

    def test_quality_rule_is_machine_readable(self) -> None:
        row = get_algorithm_output_knowledge("27_ndvi")["outputs"]["data.min"]
        self.assertEqual(
            row["qualityRule"],
            {
                "kind": "between",
                "min": -1.0,
                "max": 1.0,
                "passWhenInside": True,
                "basis": "NDVI 理论定义域",
            },
        )

    def test_layer_internal_module_not_found_is_not_swallowed(self) -> None:
        """层模块存在但内部依赖缺失时，不得被 _collect_layer_knowledge 静默吞掉。"""
        real_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "common.console_output_knowledge.l0":
                raise ModuleNotFoundError(
                    "No module named 'missing_internal_dep'",
                    name="missing_internal_dep",
                )
            return real_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=fake_import):
            with self.assertRaises(ModuleNotFoundError) as ctx:
                _collect_layer_knowledge()
        self.assertEqual("missing_internal_dep", ctx.exception.name)

    def test_l0_output_paths_are_exact_and_content_is_actionable(self) -> None:
        """防止 01–11 缺项、多登记伪输出，或退化成不可执行的泛化说明。"""
        for algorithm_id, expected in L0_EXPECTED.items():
            with self.subTest(algorithm_id=algorithm_id):
                item = get_algorithm_output_knowledge(algorithm_id)
                self.assertEqual(set(item["summary"]), {"what", "value", "caution"})
                expected_paths = {
                    f"{parent}.{api_key}"
                    for parent, api_keys in expected.items()
                    for api_key in api_keys
                }
                self.assertEqual(set(item["outputs"]), expected_paths)
                for path, row in item["outputs"].items():
                    self.assertTrue(REQUIRED_OUTPUT_DETAILS <= row.keys(), path)
                    self.assertTrue(all(row[field].strip() for field in REQUIRED_OUTPUT_DETAILS - {"abnormalSigns"}), path)
                    self.assertTrue(row["abnormalSigns"], path)
                    self.assertTrue(row["misuseWarning"].strip(), path)

    def test_l0_specialized_semantics_are_preserved(self) -> None:
        """防止掩膜编码、暗电流方法效果及动态数组索引关系被写错。"""
        combo = get_algorithm_output_knowledge("05_cloud_shadow")["outputs"][
            "files.combo_mask_tif"
        ]
        combo_encoding = " ".join(
            f"{band.get('name', '')} {band.get('description', '')}"
            for band in combo["bands"]
        )
        self.assertIn("0=clear, 1=shadow, 2=cloud", combo_encoding)

        dark_cube = get_algorithm_output_knowledge("06_dark_current")["outputs"][
            "files.cube_tif"
        ]
        dark_explanation = " ".join(
            str(dark_cube[field])
            for field in ("description", "effect", "interpretation")
        )
        self.assertIn("dark_frame", dark_explanation)
        self.assertIn("per_band_min", dark_explanation)

        geometry = get_algorithm_output_knowledge("09_smile_keystone")["outputs"]
        smile = " ".join(
            str(geometry["data.smile_shift_bands"].get(field, ""))
            for field in ("description", "interpretation", "range")
        )
        keystone = " ".join(
            str(geometry["data.keystone_shift_cols"].get(field, ""))
            for field in ("description", "interpretation", "range")
        )
        self.assertIn("每列", smile)
        self.assertIn("波段", smile)
        self.assertIn("每波段", keystone)
        self.assertIn("列", keystone)

    def test_l0_flight_qc_gate_only_uses_saturation_ratio(self) -> None:
        """防止把欠曝率或快速相对 SNR 误写成通过与重飞建议的门控条件。"""
        outputs = get_algorithm_output_knowledge("04_flight_qc")["outputs"]
        for path in ("data.passed", "data.suggest_refly"):
            with self.subTest(path=path):
                explanation = " ".join(
                    str(outputs[path][field])
                    for field in ("description", "interpretation", "qualityCheck")
                )
                self.assertIn("saturated_ratio <= max_saturated_ratio", explanation)
                self.assertIn("欠曝", explanation)
                self.assertIn("SNR", explanation)
                self.assertIn("不参与", explanation)

    def test_l0_flight_qc_snr_is_scene_relative_quick_metric(self) -> None:
        """防止把全景 mean/std 快速指标误当实验室传感器 SNR 或状态诊断。"""
        snr = get_algorithm_output_knowledge("04_flight_qc")["outputs"]["data.snr_per_band"]
        explanation = " ".join(
            str(snr[field])
            for field in (
                "description",
                "businessMeaning",
                "interpretation",
                "qualityCheck",
                "misuseWarning",
            )
        )
        self.assertIn("全景", explanation)
        self.assertIn("mean/std", explanation)
        self.assertIn("场景纹理和地物组成", explanation)
        self.assertIn("快速相对指标", explanation)
        self.assertIn("实验室传感器 SNR", explanation)
        self.assertIn("不能", explanation)
        self.assertIn("坏波段", explanation)
        self.assertIn("传感器状态", explanation)

    def test_l0_shadow_is_nir_quantile_heuristic_without_projection_geometry(self) -> None:
        """防止把暗区启发式阴影掩膜描述成具有云影投影几何的结果。"""
        shadow = get_algorithm_output_knowledge("05_cloud_shadow")["outputs"][
            "files.shadow_mask_tif"
        ]
        explanation = " ".join(
            str(shadow[field])
            for field in ("description", "effect", "interpretation", "misuseWarning")
        )
        for expected in ("非云", "非水", "NIR", "15%", "分位数", "暗区启发式"):
            self.assertIn(expected, explanation)
        for absent_geometry in ("太阳方位", "云高", "投影几何"):
            self.assertIn(absent_geometry, explanation)
        self.assertIn("不使用", explanation)

    def test_l0_dark_current_methods_have_distinct_real_effects(self) -> None:
        """防止 dark_frame 与 per_band_min 的处理效果被交换。"""
        dark_cube = get_algorithm_output_knowledge("06_dark_current")["outputs"][
            "files.cube_tif"
        ]
        explanation = " ".join(
            str(dark_cube[field])
            for field in ("description", "effect", "interpretation")
        )
        self.assertIn("dark_frame 使用实测暗帧逐像元扣除", explanation)
        self.assertIn(
            "per_band_min 使用每个波段的全景空间最小值作为基线扣除",
            explanation,
        )
        self.assertIn("原始立方体逐波段全景最小值作为暗谱估计", explanation)
        self.assertIn("后续列 FPN 扣除与非负截断会改变最终分布", explanation)
        self.assertNotIn("令各波段至少一个输入最小值落到零", explanation)
        self.assertIn("列 FPN", explanation)

    def test_l0_dark_current_checks_zero_clipping_not_negative_ratio(self) -> None:
        """防止对已截到非负的输出继续建议检查负值比例。"""
        dark_cube = get_algorithm_output_knowledge("06_dark_current")["outputs"][
            "files.cube_tif"
        ]
        explanation = " ".join(
            str(dark_cube[field])
            for field in ("effect", "interpretation", "qualityCheck", "abnormalSigns")
        )
        self.assertIn("截到非负", explanation)
        self.assertIn("零值堆积", explanation)
        self.assertIn("截零比例", explanation)
        self.assertIn("过扣可能被截零隐藏", explanation)
        self.assertNotIn("负值比例", explanation)

    def test_l0_dark_current_all_outputs_avoid_impossible_negative_checks(self) -> None:
        """防止已截到非负的暗电流输出记录残留不可能的负值检查。"""
        outputs = get_algorithm_output_knowledge("06_dark_current")["outputs"]
        for path, row in outputs.items():
            with self.subTest(path=path):
                explanation = " ".join(
                    str(row.get(field, ""))
                    for field in (
                        "description",
                        "effect",
                        "businessMeaning",
                        "interpretation",
                        "qualityCheck",
                        "abnormalSigns",
                        "downstreamUse",
                        "misuseWarning",
                    )
                )
                for impossible_check in ("负值比例", "大幅为负", "整体负移"):
                    self.assertNotIn(impossible_check, explanation)

        mean = outputs["data.mean"]
        mean_explanation = " ".join(
            str(mean[field])
            for field in ("businessMeaning", "interpretation", "qualityCheck", "abnormalSigns")
        )
        self.assertIn("零值堆积", mean_explanation)
        self.assertIn("均值异常降低", mean_explanation)
        self.assertIn("过扣可能被截零隐藏", mean_explanation)

    def test_l0_relative_radiometric_documents_common_top_left_extent(self) -> None:
        """防止把局部左上角匹配误写成整景归一。"""
        cube = get_algorithm_output_knowledge("11_relative_radiometric")["outputs"][
            "files.cube_tif"
        ]
        explanation = " ".join(
            str(cube[field])
            for field in (
                "description",
                "effect",
                "interpretation",
                "qualityCheck",
                "abnormalSigns",
                "misuseWarning",
            )
        )
        self.assertIn("左上角共同尺寸区域", explanation)
        self.assertIn("主景超出参考尺寸部分保持原值", explanation)
        self.assertIn("边界接缝", explanation)

    def test_l0_est_path_is_spacing_formula_not_coordinate_length(self) -> None:
        """防止把简化规划估算误写成航点坐标累计的精确航程。"""
        est_path = get_algorithm_output_knowledge("01_flight_planning")["outputs"][
            "data.est_path_m"
        ]
        explanation = " ".join(
            str(est_path[field])
            for field in (
                "description",
                "effect",
                "interpretation",
                "qualityCheck",
                "misuseWarning",
            )
        )
        self.assertIn("(n_waypoints-1)*photo_spacing_m", explanation)
        self.assertIn("规划估算", explanation)
        self.assertIn("不是坐标累计", explanation)
        self.assertIn("不精确包含转弯衔接", explanation)

    def test_l0_previews_reference_quantitative_outputs(self) -> None:
        """防止把仅供目视的 PNG 预览误当作定量输出使用。"""
        for algorithm_id in L0_EXPECTED:
            outputs = get_algorithm_output_knowledge(algorithm_id)["outputs"]
            for path, row in outputs.items():
                if path.endswith(".preview_png"):
                    related = row.get("relatedOutputs", [])
                    self.assertTrue(related, path)
                    self.assertTrue(
                        any(
                            target in outputs
                            and not target.endswith(".preview_png")
                            and outputs[target]["format"] != "PNG"
                            for target in related
                        ),
                        path,
                    )

    def test_l2_output_paths_are_exact_and_content_is_actionable(self) -> None:
        """防止 12–26 缺项、多登记伪输出，或退化成不可执行的泛化说明。"""
        for algorithm_id, expected in L2_EXPECTED.items():
            with self.subTest(algorithm_id=algorithm_id):
                item = get_algorithm_output_knowledge(algorithm_id)
                self.assertEqual(set(item["summary"]), {"what", "value", "caution"})
                expected_paths = {
                    f"{parent}.{api_key}"
                    for parent, api_keys in expected.items()
                    for api_key in api_keys
                }
                self.assertEqual(set(item["outputs"]), expected_paths)
                for path, row in item["outputs"].items():
                    self.assertTrue(REQUIRED_OUTPUT_DETAILS <= row.keys(), path)
                    self.assertTrue(
                        all(
                            row[field].strip()
                            for field in REQUIRED_OUTPUT_DETAILS - {"abnormalSigns"}
                        ),
                        path,
                    )
                    self.assertTrue(row["abnormalSigns"], path)
                    self.assertTrue(row["misuseWarning"].strip(), path)

    def test_l2_dynamic_band_mappings_are_explicit(self) -> None:
        """防止动态波段数组被固化长度，或输出波段与原始索引关系丢失。"""
        outputs20 = get_algorithm_output_knowledge("20_bad_band_remove")["outputs"]
        clean_cube = " ".join(
            str(outputs20["files.cube_tif"].get(field, ""))
            for field in ("description", "interpretation", "qualityCheck", "misuseWarning")
        )
        self.assertIn("输出波段 k", clean_cube)
        self.assertIn("kept[k]", clean_cube)
        for path in ("data.dropped", "data.kept", "data.snr_per_band", "data.wavelength_nm"):
            explanation = " ".join(
                str(outputs20[path].get(field, ""))
                for field in ("description", "interpretation", "range", "misuseWarning")
            )
            self.assertIn("动态", explanation, path)

        outputs24 = get_algorithm_output_knowledge("24_band_select")["outputs"]
        selected_cube = " ".join(
            str(outputs24["files.cube_tif"].get(field, ""))
            for field in ("description", "interpretation", "qualityCheck", "misuseWarning")
        )
        self.assertIn("输出波段 j", selected_cube)
        self.assertIn("selected[j]", selected_cube)

    def test_l2_bad_band_wavelength_output_key_is_distinct_from_input_param(self) -> None:
        """防止混淆输入参数 wavelengths_nm 与响应字段 wavelength_nm。"""
        wavelength = get_algorithm_output_knowledge("20_bad_band_remove")["outputs"][
            "data.wavelength_nm"
        ]
        explanation = " ".join(
            str(wavelength.get(field, ""))
            for field in ("description", "interpretation", "qualityCheck", "misuseWarning")
        )
        self.assertIn("输入参数 wavelengths_nm", explanation)
        self.assertIn("输出 data 键 wavelength_nm", explanation)

    def test_l2_orthorectify_gsd_is_internal_scale_not_output_resolution(self) -> None:
        """防止把内部反投影计算尺度误称为输出 GeoTIFF 的实际 GSD。"""
        outputs = get_algorithm_output_knowledge("16_orthorectify")["outputs"]
        gsd = outputs["data.gsd_m"]
        explanation = " ".join(
            str(gsd.get(field, ""))
            for field in (
                "label",
                "description",
                "businessMeaning",
                "interpretation",
                "qualityCheck",
                "misuseWarning",
            )
        )
        self.assertNotEqual(gsd["label"], "输出 GSD")
        self.assertIn("内部反投影格网", explanation)
        self.assertIn("沿用输入 profile", explanation)
        self.assertIn("GeoTIFF transform", explanation)
        self.assertIn("不是输出像元分辨率", explanation)

    def test_l2_mosaic_requires_matching_crs_for_all_spatial_outputs(self) -> None:
        """防止把当前镶嵌实现描述成支持跨 CRS 统一重投影。"""
        item = get_algorithm_output_knowledge("17_mosaic")
        caution = item["summary"]["caution"]
        for expected in ("两景必须同 CRS", "不同 CRS", "结果无效"):
            self.assertIn(expected, caution)

        for path in ("files.mosaic_tif", "data.bounds", "data.resolution"):
            with self.subTest(path=path):
                row = item["outputs"][path]
                explanation = " ".join(
                    str(row.get(field, ""))
                    for field in (
                        "description",
                        "interpretation",
                        "qualityCheck",
                        "misuseWarning",
                    )
                )
                self.assertIn("两景必须同 CRS", explanation)
                self.assertIn("不同 CRS", explanation)
                self.assertTrue(
                    "结果无效" in explanation or "不可直接使用" in explanation,
                    path,
                )
                self.assertNotIn("跨 CRS 统一重投影", explanation)

    def test_l2_bad_band_wavelength_length_is_input_precondition(self) -> None:
        """防止把用户波长数组长度误写成服务已验证的输出保证。"""
        wavelength = get_algorithm_output_knowledge("20_bad_band_remove")["outputs"][
            "data.wavelength_nm"
        ]
        explanation = " ".join(
            str(wavelength.get(field, ""))
            for field in (
                "description",
                "interpretation",
                "qualityCheck",
                "abnormalSigns",
                "misuseWarning",
            )
        )
        self.assertIn("有效输入前提", explanation)
        self.assertIn("服务不校验", explanation)
        self.assertIn("错配", explanation)
        self.assertIn("越界 dropped", explanation)
        self.assertNotIn("服务保证长度等于 input_bands", explanation)

    def test_l2_pca_components_follow_descending_eigenvalues(self) -> None:
        """防止 PCA/MNF 输出波段顺序被误写成原始波段或任意顺序。"""
        product = get_algorithm_output_knowledge("23_pca")["outputs"]["files.pca_tif"]
        explanation = " ".join(
            str(product.get(field, ""))
            for field in ("description", "interpretation", "qualityCheck", "misuseWarning")
        )
        self.assertIn("特征值降序", explanation)
        self.assertIn("第 1..K 主成分", explanation)

    def test_l2_superpixel_labels_and_preview_are_not_ordinal_classes(self) -> None:
        """防止把超像素编号或预览颜色解释为有大小关系的类别。"""
        outputs = get_algorithm_output_knowledge("25_superpixel")["outputs"]
        labels = " ".join(
            str(outputs["files.labels_tif"].get(field, ""))
            for field in ("description", "interpretation", "misuseWarning")
        )
        preview = " ".join(
            str(outputs["files.preview_png"].get(field, ""))
            for field in ("description", "interpretation", "misuseWarning")
        )
        self.assertIn("从 1 开始", labels)
        self.assertIn("对象编号", labels)
        self.assertIn("颜色不代表类别大小", preview)

    def test_l2_patch_npz_layout_and_band_order_are_explicit(self) -> None:
        """防止 NPZ 成员、坐标语义或末维输入波段顺序说明缺失。"""
        npz = get_algorithm_output_knowledge("26_patch_build")["outputs"]["files.patches_npz"]
        explanation = " ".join(
            str(npz.get(field, ""))
            for field in ("description", "interpretation", "qualityCheck", "misuseWarning")
        )
        for member in ("patches", "labels", "coords"):
            self.assertIn(member, explanation)
        self.assertIn("末维", explanation)
        self.assertIn("输入波段顺序", explanation)

    def test_l2_required_secondary_files_are_declared(self) -> None:
        """防止把必须依赖 file2 的算法描述成可单文件产生有效输出。"""
        expected = {
            "16_orthorectify": "DEM",
            "17_mosaic": "第二条带",
            "19_multi_source_register": "RGB",
            "26_patch_build": "标签",
        }
        for algorithm_id, role in expected.items():
            outputs = get_algorithm_output_knowledge(algorithm_id)["outputs"]
            for path, row in outputs.items():
                if not path.startswith("files."):
                    continue
                with self.subTest(algorithm_id=algorithm_id, path=path):
                    explanation = " ".join(
                        str(row.get(field, ""))
                        for field in ("description", "qualityCheck", "misuseWarning")
                    )
                    self.assertIn("file2", explanation)
                    self.assertIn(role, explanation)
                    self.assertIn("不会产生有效输出", explanation)

    def test_l3_output_paths_are_exact_and_content_is_actionable(self) -> None:
        """防止 27–45 缺项、多登记伪输出，或退化成不可执行的泛化说明。"""
        for algorithm_id, expected in L3_EXPECTED.items():
            with self.subTest(algorithm_id=algorithm_id):
                item = get_algorithm_output_knowledge(algorithm_id)
                self.assertEqual(set(item["summary"]), {"what", "value", "caution"})
                expected_paths = {
                    f"{parent}.{api_key}"
                    for parent, api_keys in expected.items()
                    for api_key in api_keys
                }
                self.assertEqual(set(item["outputs"]), expected_paths)
                for path, row in item["outputs"].items():
                    self.assertTrue(REQUIRED_OUTPUT_DETAILS <= row.keys(), path)
                    self.assertTrue(
                        all(
                            row[field].strip()
                            for field in REQUIRED_OUTPUT_DETAILS - {"abnormalSigns"}
                        ),
                        path,
                    )
                    self.assertTrue(row["abnormalSigns"], path)
                    self.assertTrue(row["misuseWarning"].strip(), path)

    def test_l3_fixed_multiband_products_preserve_band_order(self) -> None:
        """防止固定多波段产品的波段名称或顺序与真实写出顺序不一致。"""
        expected = {
            ("29_evi_savi", "files.indices_tif"): ["EVI", "SAVI", "MSAVI"],
            ("30_ndmi_ndwi", "files.indices_tif"): ["NDMI", "NDWI", "MNDWI"],
            ("31_red_edge_params", "files.params_tif"): [
                "guyot_rep_nm",
                "red_edge_amplitude",
                "sg_derivative_rep_nm",
            ],
        }
        for (algorithm_id, path), band_names in expected.items():
            with self.subTest(algorithm_id=algorithm_id):
                row = get_algorithm_output_knowledge(algorithm_id)["outputs"][path]
                self.assertEqual([band["name"] for band in row["bands"]], band_names)

    def test_l3_few_shot_query_metrics_are_conditional(self) -> None:
        """防止无查询样本时仍把 few-shot 指标描述成必然存在。"""
        outputs = get_algorithm_output_knowledge("39_few_shot_classify")["outputs"]
        for path in ("data.oa", "data.aa", "data.kappa", "data.n_query"):
            with self.subTest(path=path):
                self.assertTrue(outputs[path]["optional"])
                self.assertIn("查询样本", outputs[path]["conditional"])

    def test_l3_optional_outputs_declare_real_generation_conditions(self) -> None:
        """防止条件文件被误写成每次运行都会生成。"""
        annotation = get_algorithm_output_knowledge("40_detect_segment")["outputs"][
            "files.annotation_geojson"
        ]
        self.assertTrue(annotation["optional"])
        self.assertIn("GeoJSON", annotation["conditional"])
        self.assertIn("标注", annotation["conditional"])

        parcel = get_algorithm_output_knowledge("45_parcel_zonal_stats")["outputs"][
            "files.parcel_geojson"
        ]
        self.assertTrue(parcel["optional"])
        self.assertTrue(parcel["conditional"].strip())

    def test_l3_dynamic_abundance_and_parcel_structures_are_not_fixed(self) -> None:
        """防止把动态端元波段或地块数组固化为固定长度。"""
        abundance = get_algorithm_output_knowledge("41_unmixing")["outputs"][
            "files.abundance_tif"
        ]
        abundance_text = " ".join(
            str(abundance.get(field, ""))
            for field in ("description", "interpretation", "qualityCheck", "misuseWarning")
        )
        self.assertIn("端元 CSV 列顺序", abundance_text)
        self.assertIn("动态", abundance_text)
        self.assertNotIn("固定端元数量", abundance_text)

        outputs = get_algorithm_output_knowledge("45_parcel_zonal_stats")["outputs"]
        for path in ("data.scene", "data.parcels"):
            with self.subTest(path=path):
                row = outputs[path]
                self.assertIn("短结构", row["format"])
                self.assertNotIn("固定长度", row["description"])

    def test_l3_classification_metrics_have_no_business_thresholds(self) -> None:
        """防止无验收依据的分类指标被擅自设置通过阈值。"""
        for algorithm_id in (
            "34_svm_rf_classify",
            "36_cnn1d_classify",
            "37_cnn3d_classify",
            "38_transformer_classify",
            "39_few_shot_classify",
        ):
            outputs = get_algorithm_output_knowledge(algorithm_id)["outputs"]
            for key in ("oa", "aa", "kappa"):
                with self.subTest(algorithm_id=algorithm_id, key=key):
                    row = outputs[f"data.{key}"]
                    self.assertNotIn("qualityRule", row)
                    self.assertIn("不可判定", row["qualityCheck"])

    def test_l3_index_domains_and_detection_score_directions_are_explicit(self) -> None:
        """防止指数定义域或检测分数方向被误解。"""
        for algorithm_id, formula in (
            ("27_ndvi", "(NIR-RED)/(NIR+RED)"),
            ("28_ndre", "(NIR-RE)/(NIR+RE)"),
        ):
            row = get_algorithm_output_knowledge(algorithm_id)["outputs"][
                f"files.{algorithm_id.split('_', 1)[1]}_tif"
            ]
            explanation = " ".join(
                str(row.get(field, ""))
                for field in ("description", "interpretation", "qualityCheck", "range")
            )
            self.assertIn(formula, explanation)
            self.assertIn("[-1, 1]", explanation)

        direction_cases = {
            ("35_spectral_matching", "files.angle_tif"): ("越小", "匹配"),
            ("40_detect_segment", "files.score_tif"): ("越高", "目标"),
            ("42_anomaly_detect", "files.score_tif"): ("越高", "异常"),
            ("43_change_detect", "files.chi2_tif"): ("越高", "变化"),
        }
        for (algorithm_id, path), terms in direction_cases.items():
            with self.subTest(algorithm_id=algorithm_id):
                row = get_algorithm_output_knowledge(algorithm_id)["outputs"][path]
                explanation = " ".join(
                    str(row.get(field, ""))
                    for field in ("description", "interpretation", "misuseWarning")
                )
                for term in terms:
                    self.assertIn(term, explanation)

    def test_l3_classification_preview_colors_only_map_class_ids(self) -> None:
        """防止把分类预览色彩解释为类别大小、置信度或业务等级。"""
        for algorithm_id in (
            "34_svm_rf_classify",
            "35_spectral_matching",
            "36_cnn1d_classify",
            "37_cnn3d_classify",
            "38_transformer_classify",
            "39_few_shot_classify",
            "44_postprocess_smooth",
        ):
            preview = get_algorithm_output_knowledge(algorithm_id)["outputs"][
                "files.preview_png"
            ]
            explanation = " ".join(
                str(preview.get(field, ""))
                for field in ("description", "interpretation", "misuseWarning")
            )
            self.assertIn("颜色仅映射类别 ID", explanation, algorithm_id)

    def test_l3_spectral_matching_class_map_uses_endmember_column_semantics(self) -> None:
        """防止算法 35 复用训练标签和混淆矩阵语义。"""
        row = get_algorithm_output_knowledge("35_spectral_matching")["outputs"][
            "files.pred_map_tif"
        ]
        explanation = " ".join(
            str(row.get(field, ""))
            for field in (
                "description",
                "effect",
                "interpretation",
                "qualityCheck",
                "misuseWarning",
            )
        )
        self.assertIn("端元 CSV 第 k 列", explanation)
        self.assertIn("类别 ID=k+1", explanation)
        self.assertNotIn("训练标签", explanation)
        self.assertNotIn("混淆矩阵", explanation)

    def test_l3_regression_preprocess_echo_cannot_prove_snv_execution(self) -> None:
        """防止把固定 preprocess 回显误当实际执行 SNV 的证据。"""
        row = get_algorithm_output_knowledge("32_regression_inversion")["outputs"][
            "data.preprocess"
        ]
        explanation = " ".join(
            str(row.get(field, ""))
            for field in (
                "description",
                "interpretation",
                "qualityCheck",
                "misuseWarning",
            )
        )
        for expected in (
            "仅当请求参数 preprocess",
            "固定回显",
            "可能与实际执行不一致",
            "不能据此确认",
            "请求参数和处理记录",
        ):
            self.assertIn(expected, explanation)

    def test_l3_detect_threshold_documents_seed_fallback_and_stale_echo(self) -> None:
        """防止把算法 40 原始 NDVI 阈值回显称为始终实际使用的种子阈值。"""
        row = get_algorithm_output_knowledge("40_detect_segment")["outputs"][
            "data.threshold_ndvi"
        ]
        explanation = " ".join(
            str(row.get(field, ""))
            for field in (
                "description",
                "interpretation",
                "qualityCheck",
                "misuseWarning",
            )
        )
        for expected in ("原始", "少于 3", "更高分位", "回退", "仍返回"):
            self.assertIn(expected, explanation)
        self.assertIn("不一定是实际种子阈值", explanation)

    def test_l3_detect_polygon_properties_schema_is_exact(self) -> None:
        """防止把 class 的值 stress_candidate 误写成属性名。"""
        row = get_algorithm_output_knowledge("40_detect_segment")["outputs"][
            "files.polygons_geojson"
        ]
        explanation = " ".join(
            str(row.get(field, ""))
            for field in ("description", "interpretation", "qualityCheck")
        )
        self.assertIn("object_id", explanation)
        self.assertIn("class='stress_candidate'", explanation)
        self.assertIn("area_pixels", explanation)
        self.assertNotIn("属性含 object_id、stress_candidate", explanation)


if __name__ == "__main__":
    unittest.main()
