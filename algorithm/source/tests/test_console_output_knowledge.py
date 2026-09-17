"""验证控制台输出知识库的契约结构与质量规则。"""

from __future__ import annotations

import asyncio
import builtins
import importlib
import json
import shutil
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import numpy as np
from fastapi import UploadFile
from rasterio.crs import CRS
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

from common.console_catalog import get_console_algorithm, list_console_algorithms
from common.console_output_knowledge import _collect_layer_knowledge, get_algorithm_output_knowledge
from common.io import load_raster
from common.rs.cloud import fmask_spectral
from common.rs.mosaic import mosaic_georeferenced
from common.rs.qc import band_snr
from common.rs.sensor import fill_bad_pixels


ALGORITHM_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEST_CRS = object()


def read_algorithm_file(relative_path: str) -> str:
    return (ALGORITHM_ROOT / relative_path).read_text(encoding="utf-8")


def geotiff_upload(
    cube: np.ndarray,
    filename: str = "input.tif",
    *,
    crs: CRS | None | object = DEFAULT_TEST_CRS,
    nodata: float | None = None,
) -> UploadFile:
    """把手工可核验的小立方体编码为真实 GeoTIFF 上传对象。"""
    bands = np.moveaxis(cube, -1, 0).astype(np.float32)
    with MemoryFile() as memory_file:
        with memory_file.open(
            driver="GTiff",
            height=cube.shape[0],
            width=cube.shape[1],
            count=cube.shape[2],
            dtype="float32",
            crs=CRS.from_epsg(4326) if crs is DEFAULT_TEST_CRS else crs,
            transform=from_origin(114.06, 22.54, 0.00001, 0.00001),
            nodata=nodata,
        ) as dataset:
            dataset.write(bands)
        payload = memory_file.read()
    return UploadFile(file=BytesIO(payload), filename=filename)


def json_upload(payload: dict, filename: str = "input.geojson") -> UploadFile:
    """把字典编码为真实 JSON/GeoJSON 上传对象。"""
    return UploadFile(
        file=BytesIO(json.dumps(payload, ensure_ascii=False).encode("utf-8")),
        filename=filename,
    )


def remove_job_output(response: dict) -> None:
    """清理真实 service 运行产生的单次作业目录。"""
    if response.get("files"):
        first_path = Path(next(iter(response["files"].values())))
        shutil.rmtree(first_path.parent, ignore_errors=True)

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
    "27_ndvi": {
        "files": {"ndvi_tif", "preview_png"},
        "data": {"min", "max", "mean", "red_band", "nir_band", "shape", "format"},
    },
    "28_ndre": {
        "files": {"ndre_tif", "preview_png"},
        "data": {"min", "max", "mean", "re_band", "nir_band", "shape", "format"},
    },
    "29_evi_savi": {
        "files": {"evi_tif", "savi_tif", "msavi_tif", "preview_png"},
        "data": {"L", "evi_mean", "savi_mean", "msavi_mean"},
    },
    "30_ndmi_ndwi": {
        "files": {"ndmi_tif", "ndwi_tif", "mndwi_tif", "preview_png"},
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
        "data": {
            "model",
            "lut_size",
            "n_lai",
            "n_cab",
            "best_n",
            "cost_method",
            "n_boundary_lai",
            "n_boundary_cab",
            "lai_mean",
            "lai_max",
            "cab_mean",
            "wavelengths_nm",
        },
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
    "46_reci": {
        "files": {"reci_tif", "preview_png"},
        "data": {"min", "max", "mean", "re_band", "nir_band", "shape", "format"},
    },
    "47_gndvi": {
        "files": {"gndvi_tif", "preview_png"},
        "data": {"min", "max", "mean", "green_band", "nir_band", "shape", "format"},
    },
    "48_osavi": {
        "files": {"osavi_tif", "preview_png"},
        "data": {"min", "max", "mean", "red_band", "nir_band", "L", "shape", "format"},
    },
    "49_arvi": {
        "files": {"arvi_tif", "preview_png"},
        "data": {"min", "max", "mean", "blue_band", "red_band", "nir_band", "gamma", "shape", "format"},
    },
    "50_vari": {
        "files": {"vari_tif", "preview_png"},
        "data": {"min", "max", "mean", "blue_band", "green_band", "red_band", "shape", "format"},
    },
    "51_lai_index": {
        "files": {"lai_index_tif", "preview_png"},
        "data": {"min", "max", "mean", "blue_band", "red_band", "nir_band", "shape", "format"},
    },
    "52_nbr": {
        "files": {"nbr_tif", "preview_png"},
        "data": {"min", "max", "mean", "nir_band", "swir_band", "shape", "format"},
    },
    "53_sipi": {
        "files": {"sipi_tif", "preview_png"},
        "data": {"min", "max", "mean", "blue_band", "red_band", "nir_band", "shape", "format"},
    },
    "54_gci": {
        "files": {"gci_tif", "preview_png"},
        "data": {"min", "max", "mean", "green_band", "nir_band", "shape", "format"},
    },
    "55_ndsi": {
        "files": {"ndsi_tif", "preview_png"},
        "data": {"min", "max", "mean", "green_band", "swir_band", "shape", "format"},
    },
}

ALL_EXPECTED = {**L0_EXPECTED, **L2_EXPECTED, **L3_EXPECTED}


class ConsoleOutputKnowledgeTests(unittest.TestCase):
    def test_regression_rejects_unknown_preprocess_without_outputs(self) -> None:
        """#32 非 snv/none 参数必须 fail closed。"""
        rng = np.random.default_rng(7)
        cube = rng.uniform(0.1, 0.9, size=(4, 5, 5)).astype(np.float32)
        truth = cube[:, :, :1]
        service = importlib.import_module("algorithms.32_regression_inversion.service")
        response = asyncio.run(
            service.run(
                file=geotiff_upload(cube, "invalid-preprocess.tif"),
                file2=geotiff_upload(truth, "truth.tif"),
                params_json='{"preprocess": "autoscale"}',
            )
        )
        self.assertFalse(response["success"])
        self.assertIn("snv", response["message"])
        self.assertIn("none", response["message"])
        self.assertFalse(response.get("files"))

    def test_parcel_stats_rejects_unknown_mode_without_outputs(self) -> None:
        """#45 非 continuous/categorical 模式必须 fail closed。"""
        service = importlib.import_module("algorithms.45_parcel_zonal_stats.service")
        values = np.arange(4, dtype=np.float32).reshape(2, 2, 1)
        response = asyncio.run(
            service.run(
                file=geotiff_upload(values, "invalid-mode.tif"),
                file2=None,
                params_json='{"mode": "classes"}',
            )
        )
        self.assertFalse(response["success"])
        self.assertIn("continuous", response["message"])
        self.assertIn("categorical", response["message"])
        self.assertFalse(response.get("files"))

    def test_parcel_geojson_categorical_excludes_invalid_and_marks_empty(self) -> None:
        """#45 真实多边形统计须统一有效像元分母并序列化空地块。"""
        service = importlib.import_module("algorithms.45_parcel_zonal_stats.service")
        values = np.array(
            [
                [1, 1, np.nan, -9999],
                [1, 2, np.nan, -9999],
                [2, 2, np.nan, -9999],
                [2, 1, np.nan, -9999],
            ],
            dtype=np.float32,
        )
        full = [
            [114.0600001, 22.5399601],
            [114.0600399, 22.5399601],
            [114.0600399, 22.5399999],
            [114.0600001, 22.5399999],
            [114.0600001, 22.5399601],
        ]
        empty_cell = [
            [114.0600301, 22.5399901],
            [114.0600399, 22.5399901],
            [114.0600399, 22.5399999],
            [114.0600301, 22.5399999],
            [114.0600301, 22.5399901],
        ]
        geo = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"id": "all"},
                    "geometry": {"type": "Polygon", "coordinates": [full]},
                },
                {
                    "type": "Feature",
                    "properties": {"id": "empty"},
                    "geometry": {"type": "Polygon", "coordinates": [empty_cell]},
                },
            ],
        }
        response = asyncio.run(
            service.run(
                file=geotiff_upload(
                    values[:, :, None], "parcel-categorical.tif", nodata=-9999
                ),
                file2=json_upload(geo, "parcels.geojson"),
                params_json='{"mode": "categorical"}',
            )
        )
        self.addCleanup(remove_job_output, response)
        self.assertTrue(response["success"])
        parcels = {row["id"]: row for row in response["data"]["parcels"]}
        self.assertEqual(8, parcels["all"]["pixel_count"])
        self.assertEqual({"1": 4, "2": 4}, parcels["all"]["class_pixel_count"])
        self.assertEqual({"1": 0.5, "2": 0.5}, parcels["all"]["class_area_ratio"])
        self.assertEqual(0, parcels["empty"]["pixel_count"])
        self.assertIs(parcels["empty"]["empty"], True)
        self.assertEqual("empty", parcels["empty"]["status"])
        self.assertNotIn("class_pixel_count", parcels["empty"])
        json.dumps(response["data"], ensure_ascii=False, allow_nan=False)

    def test_regression_preprocess_echo_matches_both_executed_branches(self) -> None:
        """#32 必须真实执行并准确回显 snv/none 两条分支。"""
        rng = np.random.default_rng(42)
        cube = rng.uniform(0.05, 0.8, size=(4, 5, 5)).astype(np.float32)
        truth = (
            0.7 * cube[:, :, 0] - 0.2 * cube[:, :, 2] + 0.1 * cube[:, :, 4]
        )[:, :, None]
        service = importlib.import_module("algorithms.32_regression_inversion.service")
        for preprocess in ("snv", "none"):
            with self.subTest(preprocess=preprocess):
                response = asyncio.run(
                    service.run(
                        file=geotiff_upload(cube, f"cube-{preprocess}.tif"),
                        file2=geotiff_upload(truth, f"truth-{preprocess}.tif"),
                        params_json=f'{{"preprocess": "{preprocess}"}}',
                    )
                )
                self.addCleanup(remove_job_output, response)
                self.assertTrue(response["success"])
                self.assertEqual(preprocess, response["data"]["preprocess"])
                self.assertIn(preprocess, response["message"].lower())

    def test_svm_fits_training_scaler_once_and_reuses_it_for_all_predictions(self) -> None:
        """#34 SVM scaler 只 fit 训练集，并复用于测试集与整图。"""
        from sklearn.preprocessing import StandardScaler

        cube = np.arange(6 * 5 * 3, dtype=np.float32).reshape(6, 5, 3) + 1
        labels = np.tile(np.array([1, 2, 1, 2, 1], dtype=np.float32), (6, 1))
        service = importlib.import_module("algorithms.34_svm_rf_classify.service")
        original_fit = StandardScaler.fit
        original_transform = StandardScaler.transform
        fit_rows: list[int] = []
        transform_calls: list[tuple[int, int]] = []

        def tracked_fit(scaler, values, *args, **kwargs):
            fit_rows.append(len(values))
            return original_fit(scaler, values, *args, **kwargs)

        def tracked_transform(scaler, values, *args, **kwargs):
            transform_calls.append((id(scaler), len(values)))
            return original_transform(scaler, values, *args, **kwargs)

        with patch.object(StandardScaler, "fit", new=tracked_fit), patch.object(
            StandardScaler, "transform", new=tracked_transform
        ):
            response = asyncio.run(
                service.run(
                    file=geotiff_upload(cube),
                    file2=geotiff_upload(labels[:, :, None], "labels.tif"),
                    params_json='{"model": "svm", "test_size": 0.3}',
                )
            )
        self.addCleanup(remove_job_output, response)
        self.assertTrue(response["success"])
        self.assertEqual([response["data"]["n_train"]], fit_rows)
        self.assertEqual(
            {response["data"]["n_train"], response["data"]["n_test"], cube.shape[0] * cube.shape[1]},
            {rows for _, rows in transform_calls},
        )
        self.assertEqual(1, len({scaler_id for scaler_id, _ in transform_calls}))

    def test_rf_does_not_fit_standard_scaler(self) -> None:
        """#34 RF 分支保持原始特征，不强制标准化。"""
        from sklearn.preprocessing import StandardScaler

        cube = np.arange(6 * 5 * 3, dtype=np.float32).reshape(6, 5, 3) + 1
        labels = np.tile(np.array([1, 2, 1, 2, 1], dtype=np.float32), (6, 1))
        service = importlib.import_module("algorithms.34_svm_rf_classify.service")
        with patch.object(StandardScaler, "fit", wraps=StandardScaler.fit) as fit:
            response = asyncio.run(
                service.run(
                    file=geotiff_upload(cube),
                    file2=geotiff_upload(labels[:, :, None], "labels-rf.tif"),
                    params_json='{"model": "rf", "test_size": 0.3, "n_estimators": 5}',
                )
            )
        self.addCleanup(remove_job_output, response)
        self.assertTrue(response["success"])
        fit.assert_not_called()

    def test_red_edge_derivative_contract_is_half_open_680_to_760_nm(self) -> None:
        """#31 页面、知识和代码须统一为 [680, 760) nm 与 1988 文献。"""
        principle = read_algorithm_file("web/src/principles/l3.ts")
        knowledge = read_algorithm_file("source/common/console_output_knowledge/l3.py")
        rededge = read_algorithm_file("source/common/rs/rededge.py")
        for text in (principle, knowledge):
            self.assertIn("680–760 nm", text)
        self.assertIn("[680, 760)", rededge)
        self.assertIn("Guyot & Baret 1988", rededge)

    def test_spectral_matching_principle_uses_response_file_keys(self) -> None:
        """#35 原理页输出名必须与 API files 键一致。"""
        principle = read_algorithm_file("web/src/principles/l3.ts")
        section = principle.split('id: "35_spectral_matching"', 1)[1].split(
            'id: "36_cnn1d_classify"', 1
        )[0]
        self.assertIn('name: "pred_map_tif"', section)
        self.assertIn('name: "angle_tif"', section)
        self.assertNotIn('name: "sam_class.tif"', section)
        self.assertNotIn('name: "angle.tif"', section)

    def test_parcel_scene_stats_exclude_real_nodata_and_nan(self) -> None:
        """#45 连续与分类整景统计只基于真实有效像元。"""
        service = importlib.import_module("algorithms.45_parcel_zonal_stats.service")
        values = np.array([[1.0, 2.0], [np.nan, -9999.0]], dtype=np.float32)
        for mode in ("continuous", "categorical"):
            with self.subTest(mode=mode):
                response = asyncio.run(
                    service.run(
                        file=geotiff_upload(
                            values[:, :, None], f"zonal-{mode}.tif", nodata=-9999
                        ),
                        file2=None,
                        params_json=f'{{"mode": "{mode}"}}',
                    )
                )
                self.addCleanup(remove_job_output, response)
                self.assertTrue(response["success"])
                scene = response["data"]["scene"]
                if mode == "continuous":
                    self.assertEqual(1.5, scene["mean"])
                    self.assertEqual(1.0, scene["min"])
                    self.assertEqual(2.0, scene["max"])
                else:
                    self.assertEqual({"1": 1, "2": 1}, scene["class_pixel_count"])
                    self.assertEqual({"1": 0.5, "2": 0.5}, scene["class_area_ratio"])

    def test_parcel_stats_reject_scene_with_no_valid_pixels(self) -> None:
        """#45 空有效区必须明确失败，不能伪造零统计。"""
        service = importlib.import_module("algorithms.45_parcel_zonal_stats.service")
        values = np.array([[np.nan, -9999.0]], dtype=np.float32)
        response = asyncio.run(
            service.run(
                file=geotiff_upload(values[:, :, None], "empty.tif", nodata=-9999),
                file2=None,
                params_json='{"mode": "continuous"}',
            )
        )
        self.assertFalse(response["success"])
        self.assertIn("有效像元", response["message"])

    def test_mosaic_rejects_mismatched_crs_before_writing_output(self) -> None:
        """不同 CRS 的真实 GeoTIFF 必须在镶嵌前 fail closed。"""
        cube = np.arange(4 * 5 * 2, dtype=np.float32).reshape(4, 5, 2)
        service = importlib.import_module("algorithms.17_mosaic.service")
        response = asyncio.run(
            service.run(
                file=geotiff_upload(
                    cube,
                    "scene-4326.tif",
                    crs=CRS.from_epsg(4326),
                ),
                file2=geotiff_upload(
                    cube,
                    "scene-3857.tif",
                    crs=CRS.from_epsg(3857),
                ),
                params_json="{}",
            )
        )
        self.addCleanup(remove_job_output, response)
        self.assertFalse(response["success"])
        self.assertIn("CRS", response["message"])
        self.assertFalse(response.get("files"))

    def test_mosaic_rejects_missing_crs_before_writing_output(self) -> None:
        """缺失 CRS 的真实 GeoTIFF 必须在镶嵌前 fail closed。"""
        cube = np.arange(4 * 5 * 2, dtype=np.float32).reshape(4, 5, 2)
        service = importlib.import_module("algorithms.17_mosaic.service")
        response = asyncio.run(
            service.run(
                file=geotiff_upload(cube, "scene-with-crs.tif"),
                file2=geotiff_upload(cube, "scene-without-crs.tif", crs=None),
                params_json="{}",
            )
        )
        self.assertFalse(response["success"])
        self.assertIn("CRS", response["message"])
        self.assertFalse(response.get("files"))

    def test_mosaic_accepts_equivalent_crs_encodings(self) -> None:
        """语义等价的 CRS 表达不得被误拒绝。"""
        cube = np.arange(4 * 5 * 2, dtype=np.float32).reshape(4, 5, 2)
        epsg = CRS.from_epsg(4326)
        equivalent_wkt = CRS.from_wkt(epsg.to_wkt())
        service = importlib.import_module("algorithms.17_mosaic.service")
        response = asyncio.run(
            service.run(
                file=geotiff_upload(cube, "scene-epsg.tif", crs=epsg),
                file2=geotiff_upload(
                    cube,
                    "scene-wkt.tif",
                    crs=equivalent_wkt,
                ),
                params_json="{}",
            )
        )
        self.addCleanup(remove_job_output, response)
        self.assertTrue(response["success"])

    def test_mosaic_core_rejects_missing_or_different_crs(self) -> None:
        """直接调用核心函数时也必须执行相同的 CRS 防御检查。"""
        cube = np.ones((3, 4, 1), dtype=np.float32)
        transform = from_origin(114.06, 22.54, 0.00001, 0.00001)
        with self.assertRaisesRegex(ValueError, "CRS"):
            mosaic_georeferenced(
                [cube, cube],
                [
                    {"transform": transform, "crs": CRS.from_epsg(4326)},
                    {"transform": transform, "crs": None},
                ],
            )
        with self.assertRaisesRegex(ValueError, "CRS"):
            mosaic_georeferenced(
                [cube, cube],
                [
                    {"transform": transform, "crs": CRS.from_epsg(4326)},
                    {"transform": transform, "crs": CRS.from_epsg(3857)},
                ],
            )

    def test_bad_band_scene_ratio_is_mean_over_std(self) -> None:
        """兼容函数计算场景像元均值/标准差比，但不得冒充传感器 SNR。"""
        cube = np.array(
            [
                [[1.0, 2.0, 9.0], [3.0, 6.0, 9.0]],
                [[5.0, 10.0, 9.0], [7.0, 14.0, 9.0]],
            ]
        )
        got = band_snr(cube)
        expected = cube.mean((0, 1)) / (cube.std((0, 1)) + 1e-12)
        np.testing.assert_allclose(got, expected)
        self.assertIn("场景像元均值/标准差比", band_snr.__doc__ or "")

        principle = read_algorithm_file("web/src/principles/l2.ts")
        self.assertNotIn("传感器信噪比", principle)
        self.assertIn("场景像元均值/标准差比", principle)

    def test_superpixel_disables_lab_conversion_for_raw_spectral_bands(self) -> None:
        """前三原始光谱波段不是 RGB，SLIC 不得自动转换到 Lab。"""
        cube = np.arange(6 * 7 * 4, dtype=np.float32).reshape(6, 7, 4)
        service = importlib.import_module("algorithms.25_superpixel.service")
        captured: dict[str, object] = {}

        def fake_slic(image: np.ndarray, **kwargs: object) -> np.ndarray:
            captured["image"] = image.copy()
            captured.update(kwargs)
            return np.ones(image.shape[:2], dtype=np.int32)

        with patch.object(service, "slic", side_effect=fake_slic):
            response = asyncio.run(
                service.run(
                    file=geotiff_upload(cube),
                    file2=None,
                    params_json='{"n_segments": 4}',
                )
            )
        self.addCleanup(remove_job_output, response)
        self.assertTrue(response["success"])
        np.testing.assert_allclose(captured["image"], cube[:, :, :3])
        self.assertIs(captured["convert2lab"], False)
        self.assertNotIn("前三主成分", service.run.__doc__ or "")
        self.assertIn("前三原始波段", service.run.__doc__ or "")

    def test_superpixel_principle_describes_raw_spectral_feature_scaling(self) -> None:
        """原则页不得把原始光谱特征冒充 RGB/CIELAB SLIC。"""
        principle = read_algorithm_file("web/src/principles/l2.ts")
        for forbidden in ("取前三波段当 RGB", "颜色与平面坐标"):
            self.assertNotIn(forbidden, principle)
        for required in (
            "前三个原始光谱波段作为三通道特征",
            "光谱特征与平面坐标",
            "全局 min-max",
            "某个波段可能主导",
            "不等同于标准 CIELAB SLIC",
        ):
            self.assertIn(required, principle)

    def test_bad_band_user_copy_never_claims_snr_or_denoising(self) -> None:
        """#20 用户文案必须只描述场景比值筛选与波段剔除。"""
        paths = (
            "source/common/catalog.py",
            "source/algorithms/20_bad_band_remove/service.py",
            "source/algorithms/20_bad_band_remove/router.py",
            "source/algorithms/20_bad_band_remove/README.md",
            "source/algorithms/20_bad_band_remove/testdata/README.md",
            "docs/算法API测试清单.md",
            "docs/采集到算法-算法清单.md",
            "docs/build_algorithm_word.py",
            "docs/generate_training_ppt.py",
            "docs/generate_training_ppt_v4.py",
            "shared/scientific_evidence.json",
            "web/src/principles/l2.ts",
            "web/src/sources.ts",
        )
        combined = "\n".join(read_algorithm_file(path) for path in paths)
        for forbidden in (
            "坏波段剔除与光谱去噪",
            "按信噪比/水汽吸收特征",
            "光谱维轻度去噪",
            "自动 SNR 判定",
        ):
            self.assertNotIn(forbidden, combined)
        field_knowledge = read_algorithm_file(
            "source/common/console_field_knowledge.py"
        )
        self.assertNotIn("自动 SNR 判定", field_knowledge)
        self.assertIn(
            "场景像元均值/标准差比（非传感器 SNR）",
            combined + field_knowledge,
        )

    def test_cloud_copy_matches_low_whiteness_metric(self) -> None:
        """防止移除低可见波段差异条件，或把简化检测冒充完整 Fmask。"""
        cube = np.full((5, 7, 4), 0.1, dtype=np.float64)
        cube[1:4, 0:3, :3] = 0.4
        cube[1:4, 0:3, 3] = 0.4
        cube[1:4, 4:7, 0] = 0.8
        cube[1:4, 4:7, 1:4] = 0.05
        cloud, _ = fmask_spectral(cube, swir=None)
        self.assertTrue(np.all(cloud[1:4, 0:3] == 1))
        self.assertEqual(0, int(cloud[1:4, 4:7].sum()))

        service = importlib.import_module("algorithms.05_cloud_shadow.service")
        response = asyncio.run(
            service.run(file=geotiff_upload(cube), file2=None, params_json="{}")
        )
        self.addCleanup(remove_job_output, response)
        self.assertTrue(response["success"])
        self.assertNotIn("Fmask", response["message"])
        knowledge = get_algorithm_output_knowledge("05_cloud_shadow")
        knowledge_text = " ".join(
            [
                *knowledge["summary"].values(),
                *(
                    str(value)
                    for row in knowledge["outputs"].values()
                    for value in row.values()
                ),
            ]
        )
        self.assertNotIn("完整 Fmask", knowledge_text)
        self.assertIn("暗区启发式", knowledge_text)

        principle = read_algorithm_file("web/src/principles/l0.ts")
        self.assertNotIn("白度高", principle)
        self.assertIn("相对差异较小", principle)

    def test_flight_qc_principle_keeps_snr_out_of_gate(self) -> None:
        """防止原则页声称场景 SNR 会触发通过/复飞门控。"""
        principle = read_algorithm_file("web/src/principles/l0.ts")
        self.assertNotIn("过曝与 SNR 不通过则建议复飞", principle)
        self.assertIn("仅由过曝比例触发通过/复飞", principle)

    def test_bad_pixel_method_uses_neighborhood_mean_name(self) -> None:
        """防止坏点采用非邻域均值填充，或响应误报插值方法。"""
        band = np.arange(1, 10, dtype=np.float64).reshape(3, 3)
        cube = band[:, :, np.newaxis]
        mask = np.zeros((3, 3), dtype=bool)
        mask[1, 1] = True
        repaired = fill_bad_pixels(cube, mask)
        self.assertAlmostEqual(5.0, float(repaired[1, 1, 0]))

        service_cube = np.full((5, 5, 1), 10.0, dtype=np.float64)
        service = importlib.import_module("algorithms.07_bad_pixel.service")
        response = asyncio.run(
            service.run(
                file=geotiff_upload(service_cube),
                file2=None,
                params_json='{"bad_pixels": [[2, 2]], "z_thr": 1000000}',
            )
        )
        self.addCleanup(remove_job_output, response)
        self.assertTrue(response["success"])
        self.assertEqual(
            "median_residual_sigma + neighborhood_mean_fill",
            response["data"]["method"],
        )

    def test_sync_timestamp_copy_does_not_claim_configured_tolerance(self) -> None:
        """防止输出知识把不存在的配置容差写成可执行质检规则。"""
        item = get_algorithm_output_knowledge("02_sync_timestamp")
        copy = " ".join(
            [
                *item["summary"].values(),
                *(
                    str(value)
                    for row in item["outputs"].values()
                    for value in row.values()
                ),
            ]
        )
        self.assertNotIn("配置容差", copy)
        self.assertNotIn("无限放宽时间容差", copy)

    def test_smile_summary_uses_scene_cross_correlation(self) -> None:
        """防止场景互相关估计被写成实验室标定偏移。"""
        item = get_algorithm_output_knowledge("09_smile_keystone")
        summary = " ".join(item["summary"].values())
        output_copy = " ".join(
            str(value)
            for row in item["outputs"].values()
            for value in row.values()
        )
        self.assertNotIn("标定偏移", summary)
        self.assertNotIn("标定偏移", output_copy)
        self.assertIn("场景互相关估计偏移", summary)

    def test_default_radiance_message_does_not_claim_laboratory_calibration(self) -> None:
        """防止线性转换数值错误，或成功消息冒充实验室定标。"""
        cube = np.array(
            [
                [[1.0, 2.0], [3.0, 4.0]],
                [[5.0, 6.0], [7.0, 8.0]],
            ],
            dtype=np.float64,
        )
        service = importlib.import_module(
            "algorithms.10_radiance_calibration.service"
        )
        response = asyncio.run(
            service.run(
                file=geotiff_upload(cube),
                file2=None,
                params_json='{"gain": [2, 3], "offset": [1, -1]}',
            )
        )
        self.addCleanup(remove_job_output, response)
        self.assertTrue(response["success"])
        output, _ = load_raster(Path(response["files"]["radiance_tif"]))
        expected = np.empty_like(cube)
        expected[:, :, 0] = cube[:, :, 0] * 2 + 1
        expected[:, :, 1] = cube[:, :, 1] * 3 - 1
        np.testing.assert_allclose(output, expected)
        self.assertEqual(
            "已按输入 gain/offset 完成线性转换 DN→辐亮度",
            response["message"],
        )
        self.assertNotIn("实验室", response["message"])

    def test_pos_and_flight_qc_titles_match_implemented_scope(self) -> None:
        """防止标题继续声称未实现的 GPS/IMU 解算或丢帧检测。"""
        expected = {
            "03_pos_solution": "POS轨迹平滑与杠杆臂校正",
            "04_flight_qc": "架次过曝与场景统计质检",
        }
        items = {item["id"]: item for item in list_console_algorithms()}
        for algorithm_id, title in expected.items():
            with self.subTest(algorithm_id=algorithm_id):
                service = read_algorithm_file(
                    f"source/algorithms/{algorithm_id}/service.py"
                )
                self.assertEqual(title, items[algorithm_id]["title"])
                self.assertIn(f'TITLE = "{title}"', service)

    def test_l2_narrowed_titles_match_implemented_scope(self) -> None:
        """防止 #15/#18/#19 用户文案继续声称未实现能力。"""
        expected = {
            "15_geo_locate": "POS中心点与GSD粗定位",
            "18_color_balance": "Wallis局部匀色",
            "19_multi_source_register": "HSI-RGB全局平移配准",
        }
        items = {item["id"]: item for item in list_console_algorithms()}
        evidence = {
            row["algorithmId"]: row
            for row in __import__(
                "common.scientific_evidence",
                fromlist=["load_scientific_evidence"],
            ).load_scientific_evidence()
        }
        for algorithm_id, title in expected.items():
            with self.subTest(algorithm_id=algorithm_id):
                self.assertEqual(title, items[algorithm_id]["title"])
                self.assertEqual(title, evidence[algorithm_id]["title"])
                service = read_algorithm_file(
                    f"source/algorithms/{algorithm_id}/service.py"
                )
                self.assertIn(f'TITLE = "{title}"', service)

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
        for expected in ("两景必须同 CRS", "不同", "拒绝"):
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
                self.assertIn("不同", explanation)
                self.assertTrue(
                    "拒绝" in explanation or "fail closed" in explanation,
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

    def test_evi_savi_writes_three_single_band_geotiffs(self) -> None:
        """一次计算三个指数，但按业界交付写成三个单波段 GeoTIFF。"""
        blue, red, nir = 0.05, 0.08, 0.40
        soil_l = 0.5
        cube = np.zeros((2, 3, 4), dtype=np.float32)
        cube[..., 0] = blue
        cube[..., 2] = red
        cube[..., 3] = nir
        expected = {
            "evi_tif": 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1),
            "savi_tif": (1 + soil_l) * (nir - red) / (nir + red + soil_l),
            "msavi_tif": 0.5 * (2 * nir + 1 - np.sqrt((2 * nir + 1) ** 2 - 8 * (nir - red))),
        }
        service = importlib.import_module("algorithms.29_evi_savi.service")
        response = asyncio.run(
            service.run(
                file=geotiff_upload(cube, "evi-savi.tif"),
                file2=None,
                params_json='{"blue_band": 0, "red_band": 2, "nir_band": 3, "L": 0.5}',
            )
        )
        try:
            self.assertTrue(response["success"], response.get("message"))
            self.assertEqual(
                set(response["files"]),
                {"evi_tif", "savi_tif", "msavi_tif", "preview_png"},
            )
            self.assertNotIn("indices_tif", response["files"])
            for key, value in expected.items():
                path = Path(response["files"][key])
                self.assertEqual(path.name, f"{key.removesuffix('_tif')}.tif")
                arr, _profile = load_raster(path)
                self.assertEqual(arr.ndim, 2, key)
                np.testing.assert_allclose(arr, value, rtol=1e-5, atol=1e-6)
            preview = Path(response["files"]["preview_png"])
            self.assertEqual(preview.name, "evi_preview.png")
            self.assertTrue(preview.is_file())
        finally:
            remove_job_output(response)

    def test_ndmi_ndwi_writes_three_single_band_geotiffs(self) -> None:
        """一次计算三个指数，但按业界交付写成三个单波段 GeoTIFF。"""
        green, nir, swir = 0.08, 0.35, 0.12
        cube = np.zeros((2, 3, 6), dtype=np.float32)
        cube[..., 1] = green
        cube[..., 3] = nir
        cube[..., 5] = swir
        expected = {
            "ndmi_tif": (nir - swir) / (nir + swir + 1e-12),
            "ndwi_tif": (green - nir) / (green + nir + 1e-12),
            "mndwi_tif": (green - swir) / (green + swir + 1e-12),
        }
        service = importlib.import_module("algorithms.30_ndmi_ndwi.service")
        response = asyncio.run(
            service.run(
                file=geotiff_upload(cube, "ndmi-ndwi.tif"),
                file2=None,
                params_json='{"green_band": 1, "nir_band": 3, "swir_band": 5}',
            )
        )
        try:
            self.assertTrue(response["success"], response.get("message"))
            self.assertEqual(
                set(response["files"]),
                {"ndmi_tif", "ndwi_tif", "mndwi_tif", "preview_png"},
            )
            self.assertNotIn("indices_tif", response["files"])
            for key, value in expected.items():
                path = Path(response["files"][key])
                self.assertEqual(path.name, f"{key.removesuffix('_tif')}.tif")
                arr, _profile = load_raster(path)
                self.assertEqual(arr.ndim, 2, key)
                np.testing.assert_allclose(arr, value, rtol=1e-5, atol=1e-6)
            preview = Path(response["files"]["preview_png"])
            self.assertEqual(preview.name, "ndwi_preview.png")
            self.assertTrue(preview.is_file())
        finally:
            remove_job_output(response)

    def test_evi_filename_is_previewed_as_index(self) -> None:
        """evi/savi/msavi/ndmi/ndwi/mndwi 单波段必须走指数色带，不能当成假彩色。"""
        from common.console_preview import guess_mode
        from common.console_router import _guess_preview_mode

        plane = np.linspace(0.1, 0.6, 16, dtype=np.float32).reshape(4, 4)
        for name in ("evi.tif", "savi.tif", "msavi.tif", "ndmi.tif", "ndwi.tif", "mndwi.tif"):
            with self.subTest(name=name):
                self.assertEqual(_guess_preview_mode(name), "index")
                self.assertEqual(guess_mode(name, 1, plane), "index")

    def test_index_preview_exposes_numeric_color_scale(self) -> None:
        """指数预览必须标出红端/绿端对应的具体读数。"""
        import tempfile

        from common.console_preview import raster_meta, raster_png_bytes
        from common.io import save_geotiff

        plane = np.linspace(0.20, 0.50, 100, dtype=np.float32).reshape(10, 10)
        plane[0, 0] = -8.0
        plane[-1, -1] = 9.0
        finite = plane[np.isfinite(plane)]
        expected_low, expected_high = np.percentile(finite, (2, 98))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evi.tif"
            save_geotiff(plane, path)
            png, preview_meta = raster_png_bytes(path, mode="index")
            meta = raster_meta(path)
        self.assertGreater(len(png), 200)
        for row in (preview_meta, meta):
            self.assertAlmostEqual(row["colorLow"], float(expected_low), places=5)
            self.assertAlmostEqual(row["colorHigh"], float(expected_high), places=5)
            self.assertEqual(row["colorMap"], "RdYlGn")
            self.assertIn("colorMid", row)

    def test_l3_fixed_multiband_products_preserve_band_order(self) -> None:
        """防止固定多波段产品的波段名称或顺序与真实写出顺序不一致。"""
        expected = {
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

    def test_l3_regression_preprocess_knowledge_matches_executed_branch(self) -> None:
        """#32 知识说明须反映 snv/none 真实执行分支。"""
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
            "实际执行分支",
            "snv",
            "none",
            "请求参数和处理记录",
            "fail closed",
        ):
            self.assertIn(expected, explanation)
        self.assertNotIn("固定回显", explanation)
        self.assertNotIn("未知取值按 none", explanation)

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
