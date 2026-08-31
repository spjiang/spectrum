"""控制台算法元数据：清单文案 + testdata + 可视化类型。"""
from __future__ import annotations

import json
import re
from pathlib import Path

from common.catalog import ALGORITHMS
from common.config import SOURCE_ROOT
from common.console_field_knowledge import get_field_detail
from common.console_output_knowledge import get_algorithm_output_knowledge
from common.console_params import (
    get_service_param_type,
    get_service_params,
    service_requires_file2,
)
from common.console_paths import PRIMARY_NAMES, SECONDARY_NAMES, find_named, testdata_dir

DOC_PATH = SOURCE_ROOT.parent / "docs" / "采集到算法-算法清单.md"

PARAM_HELP = {
    "red_band": "红光波段索引（0 起）",
    "nir_band": "近红外波段索引（0 起）",
    "re_band": "红边波段索引（0 起）",
    "blue_band": "蓝光波段索引（0 起）",
    "green_band": "绿光波段索引（0 起）",
    "swir_band": "短波红外波段索引（0 起）",
    "L": "SAVI 土壤调节系数",
    "max_saturated_ratio": "过曝像元比例告警阈值",
    "bit_depth": "传感器位深（用于饱和判定）",
    "drop_bands": "额外剔除的波段索引列表",
    "snr_ratio": "相对中位 SNR 的坏波段阈值",
    "window_length": "Savitzky–Golay 窗口（奇数）",
    "polyorder": "SG 多项式阶数",
    "method": "算法子方法（如 zscore/snv、mnf/pca、sam/sid）",
    "n_components": "主成分/PLS 成分数",
    "k": "选取波段数",
    "patch_size": "邻域窗口边长（奇数）",
    "epochs": "训练轮数",
    "test_size": "测试集比例",
    "shots": "少样本每类原型数",
    "percentile": "百分位阈值",
    "min_pixels": "小斑剔除最小像元数",
    "ace_percentile": "ACE 得分告警百分位",
    "overlap": "航向重叠",
    "sidelap": "旁向重叠",
    "alt_m": "相对航高（米）",
    "focal_mm": "焦距（毫米）",
    "pixel_um": "像元尺寸（微米）",
    "cruise_speed_m_s": "巡航速度（米/秒）",
    "solar_zenith": "太阳天顶角（度）",
    "view_zenith": "观测天顶角（度）",
    "panel_reflectance": "参考板反射率",
    "model": "分类器 svm 或 rf",
    "kernel": "SVM 核函数",
    "n_estimators": "随机森林树数",
    "pca_components": "3D-CNN 前 PCA 维数",
    "batch_size": "训练 batch",
    "delta": "FCLS 和为 1 的惩罚",
    "win": "局部 RX 外窗",
    "inner": "局部 RX 内窗",
    "max_iter": "IR-MAD 迭代次数",
    "mode": "continuous 或 categorical",
    "roi": "像素窗 [r0,r1,c0,c1]（有 GeoJSON 时以矢量为主）",
    "z_thr": "坏像元检测 σ 倍数",
    "alpha": "POS 互补滤波系数",
    "preprocess": "回归前预处理（snv）",
}

# 当前实现方法名（给领导看，与 service 一致）
METHODS = {
    "01_flight_planning": "摄影测量 GSD 往返航线",
    "02_sync_timestamp": "POS 内插 + RGB 最近邻 + 钟差",
    "03_pos_solution": "互补滤波 + RTS 平滑 + 杠杆臂",
    "04_flight_qc": "位深饱和 + 波段 SNR",
    "05_cloud_shadow": "Fmask 光谱规则",
    "06_dark_current": "暗帧相减 + 列 FPN",
    "07_bad_pixel": "6σ 热/死像元 + 邻域填充",
    "08_destriping": "列向矩匹配",
    "09_smile_keystone": "场景内互相关 smile/keystone",
    "10_radiance_calibration": "逐波段 gain/offset",
    "11_relative_radiometric": "直方图匹配",
    "12_panel_reflectance": "经验线 ELM",
    "13_atmospheric_correction": "Chavez DOS2",
    "14_brdf_correction": "Ross-Thick / Li-Sparse",
    "15_geo_locate": "POS + GSD 直接地理定位",
    "16_orthorectify": "共线方程 + DEM",
    "17_mosaic": "地理羽化镶嵌",
    "18_color_balance": "Wallis 匀光",
    "19_multi_source_register": "Foroosh 亚像元相位相关",
    "20_bad_band_remove": "SNR + 大气吸收窗口",
    "21_savgol_smooth": "Savitzky–Golay",
    "22_normalize": "SNV / Z-score / MinMax / L2",
    "23_pca": "MNF（Green 1988）/ PCA",
    "24_band_select": "ANOVA F / 方差",
    "25_superpixel": "SLIC",
    "26_patch_build": "邻域立方体采样",
    "27_ndvi": "NDVI = (NIR-RED)/(NIR+RED)",
    "28_ndre": "NDRE = (NIR-RE)/(NIR+RE)",
    "29_evi_savi": "EVI / SAVI / MSAVI",
    "30_ndmi_ndwi": "NDMI / NDWI / MNDWI",
    "31_red_edge_params": "Guyot 线性内插 + SG 导数",
    "32_regression_inversion": "SNV + PLS",
    "33_physical_inversion": "PROSAIL-5 + 4SAIL LUT",
    "34_svm_rf_classify": "SVM / 随机森林",
    "35_spectral_matching": "SAM / SID",
    "36_cnn1d_classify": "Hu 2015 1-D CNN",
    "37_cnn3d_classify": "HybridSN",
    "38_transformer_classify": "SpectralFormer",
    "39_few_shot_classify": "SAM 原型网络",
    "40_detect_segment": "ACE 目标探测",
    "41_unmixing": "FCLS",
    "42_anomaly_detect": "局部 RX / 全局 RX",
    "43_change_detect": "IR-MAD",
    "44_postprocess_smooth": "众数滤波 + 筛斑",
    "45_parcel_zonal_stats": "GeoJSON 栅格化分区统计",
}

COMPARE = {
    "01_flight_planning": "single",
    "02_sync_timestamp": "single",
    "03_pos_solution": "single",
    "04_flight_qc": "cube_to_product",
    "05_cloud_shadow": "cube_to_product",
    "06_dark_current": "before_after",
    "07_bad_pixel": "before_after",
    "08_destriping": "before_after",
    "09_smile_keystone": "before_after",
    "10_radiance_calibration": "before_after",
    "11_relative_radiometric": "before_after",
    "12_panel_reflectance": "before_after",
    "13_atmospheric_correction": "before_after",
    "14_brdf_correction": "before_after",
    "15_geo_locate": "before_after",
    "16_orthorectify": "before_after",
    "17_mosaic": "before_after",
    "18_color_balance": "before_after",
    "19_multi_source_register": "before_after",
    "20_bad_band_remove": "before_after",
    "21_savgol_smooth": "before_after",
    "22_normalize": "before_after",
    "23_pca": "cube_to_product",
    "24_band_select": "cube_to_product",
    "25_superpixel": "cube_to_product",
    "26_patch_build": "cube_to_product",
    "27_ndvi": "cube_to_product",
    "28_ndre": "cube_to_product",
    "29_evi_savi": "cube_to_product",
    "30_ndmi_ndwi": "cube_to_product",
    "31_red_edge_params": "cube_to_product",
    "32_regression_inversion": "cube_to_product",
    "33_physical_inversion": "cube_to_product",
    "34_svm_rf_classify": "cube_to_product",
    "35_spectral_matching": "cube_to_product",
    "36_cnn1d_classify": "cube_to_product",
    "37_cnn3d_classify": "cube_to_product",
    "38_transformer_classify": "cube_to_product",
    "39_few_shot_classify": "cube_to_product",
    "40_detect_segment": "cube_to_product",
    "41_unmixing": "cube_to_product",
    "42_anomaly_detect": "cube_to_product",
    "43_change_detect": "before_after",
    "44_postprocess_smooth": "before_after",
    "45_parcel_zonal_stats": "cube_to_product",
}

OUTPUT_VIS = {
    "cube_tif": ("raster_falsecolor", "处理后多波段立方体 GeoTIFF"),
    "radiance_tif": ("raster_falsecolor", "辐亮度立方体"),
    "reflectance_tif": ("raster_falsecolor", "地表反射率立方体"),
    "ortho_tif": ("raster_falsecolor", "正射后影像"),
    "mosaic_tif": ("raster_falsecolor", "镶嵌结果"),
    "hsi_tif": ("raster_falsecolor", "HSI 参考影像"),
    "rgb_aligned_tif": ("raster_falsecolor", "配准后的 RGB"),
    "pca_tif": ("raster_falsecolor", "MNF/PCA 成分立方体"),
    "ndvi_tif": ("raster_index", "NDVI 专题图"),
    "ndre_tif": ("raster_index", "NDRE 专题图"),
    "indices_tif": ("raster_index", "多指数堆叠（看第一波段预览）"),
    "params_tif": ("raster_index", "红边位置/振幅"),
    "inversion_tif": ("raster_index", "回归反演连续量"),
    "lai_tif": ("raster_index", "PROSAIL 反演 LAI"),
    "cab_tif": ("raster_index", "叶绿素 Cab"),
    "pred_map_tif": ("raster_class", "分类结果图"),
    "labels_tif": ("raster_class", "超像素或平滑后标签"),
    "sam_class": ("raster_class", "SAM 类别图"),
    "angle_tif": ("raster_index", "最小光谱角"),
    "cloud_mask_tif": ("raster_class", "云掩膜"),
    "shadow_mask_tif": ("raster_class", "云影掩膜"),
    "combo_mask_tif": ("raster_class", "云/影组合掩膜"),
    "score_tif": ("raster_index", "探测/异常得分"),
    "mask_tif": ("raster_class", "二值掩膜"),
    "detect_score.tif": ("raster_index", "ACE 得分"),
    "abundance_tif": ("raster_index", "FCLS 丰度（第一端元预览）"),
    "magnitude_tif": ("raster_index", "变化幅度"),
    "chi2_tif": ("raster_index", "IR-MAD χ²"),
    "preview_png": ("png", "预览 PNG（给人看）"),
    "waypoints_geojson": ("geojson_map", "航点 GeoJSON"),
    "polygons_geojson": ("geojson_map", "探测斑块多边形"),
    "parcel_geojson": ("geojson_map", "上传/样例地块"),
    "annotation_geojson": ("geojson_map", "标注矢量"),
    "mission_json": ("json_table", "航线任务参数"),
    "aligned_json": ("json_table", "时间对齐表"),
    "pos_json": ("json_table", "POS 解算 JSON"),
    "pos_csv": ("csv_track", "POS 轨迹 CSV"),
    "report_json": ("json_table", "质检或分区统计报表"),
    "zonal_report.json": ("json_table", "地块统计"),
    "meta_json": ("json_table", "几何定位元数据"),
    "ranking_json": ("json_table", "波段得分排序"),
    "manifest_json": ("json_table", "Patch 清单"),
    "patches_npz": ("png", "样本立方体（配合预览图）"),
}

FRONTEND_VIS_KINDS = {
    "raster_falsecolor",
    "raster_index",
    "raster_class",
    "geojson_map",
    "csv_track",
    "csv_spectrum",
    "csv_table",
    "json_table",
    "png",
    "none",
}


def _parse_doc() -> dict[int, dict]:
    """从算法清单解析作用/场景/输入/输出。"""
    items: dict[int, dict] = {}
    if not DOC_PATH.is_file():
        return items
    num = None
    buf: dict = {}
    key_map = {"作用": "purpose", "使用场景": "scenario", "数据输入": "doc_input", "数据输出": "doc_output"}
    for line in DOC_PATH.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#### (\d+)\.", line)
        if m:
            if num is not None:
                items[num] = buf
            num = int(m.group(1))
            buf = {}
            continue
        m2 = re.match(r"\| \*\*(作用|使用场景|数据输入|数据输出)\*\*\s+\|\s*(.*?)\s*\|", line)
        if m2 and num is not None:
            buf[key_map[m2.group(1)]] = m2.group(2).strip()
    if num is not None:
        items[num] = buf
    return items


def _kind_from_suffix(name: str) -> str:
    s = Path(name).suffix.lower()
    if s in {".tif", ".tiff"}:
        return "geotiff"
    if s in {".geojson"}:
        return "geojson"
    if s == ".csv":
        return "csv"
    if s in {".json"}:
        return "json"
    if s == ".png":
        return "png"
    return s or "file"


def _testdata_block(algorithm_id: str) -> dict:
    folder = testdata_dir(algorithm_id)
    primary = find_named(folder, PRIMARY_NAMES)
    secondary = find_named(folder, SECONDARY_NAMES)
    params = {}
    pj = folder / "params.json"
    if pj.is_file():
        params = json.loads(pj.read_text(encoding="utf-8") or "{}")
        service_keys = get_service_params(algorithm_id)
        params = {key: value for key, value in params.items() if key in service_keys}
    return {
        "dir": str(folder),
        "file": None if primary is None else primary.name,
        "file2": None if secondary is None else secondary.name,
        "params": params,
        "exists": primary is not None,
    }


def _input_fields(algorithm_id: str, td: dict, doc_input: str) -> list[dict]:
    rows = []
    if td.get("file"):
        kind = _kind_from_suffix(td["file"])
        vis = {
            "geotiff": "raster_falsecolor",
            "geojson": "geojson_map",
            "csv": "csv_track" if algorithm_id.startswith("03") else "csv_table",
            "json": "json_table",
        }.get(kind, "none")
        if algorithm_id == "41_unmixing" or algorithm_id == "35_spectral_matching":
            if kind == "csv":
                vis = "csv_spectrum"
        rows.append(
            {
                "name": "file",
                "type": kind,
                "required": True,
                "format": td["file"],
                "description": doc_input or "主输入文件",
                "vis": vis,
                **get_field_detail(algorithm_id, "file", td["file"]),
            }
        )
    if td.get("file2"):
        kind = _kind_from_suffix(td["file2"])
        vis = {
            "geotiff": "raster_index" if "file2" in td["file2"] else "raster_falsecolor",
            "geojson": "geojson_map",
            "csv": "csv_spectrum" if kind == "csv" else "csv_table",
            "json": "json_table",
        }.get(kind, "none")
        if kind == "geotiff":
            vis = "raster_class" if algorithm_id not in {
                "06_dark_current",
                "11_relative_radiometric",
                "16_orthorectify",
                "17_mosaic",
                "19_multi_source_register",
                "43_change_detect",
                "32_regression_inversion",
            } else ("raster_index" if algorithm_id == "16_orthorectify" else "raster_falsecolor")
            if algorithm_id == "16_orthorectify":
                vis = "raster_index"
            if algorithm_id == "32_regression_inversion":
                vis = "raster_index"
        desc = "第二输入（标签/暗帧/DEM/第二时相/端元/地块等）"
        rows.append(
            {
                "name": "file2",
                "type": kind,
                "required": service_requires_file2(algorithm_id),
                "format": td["file2"],
                "description": desc,
                "vis": vis,
                **get_field_detail(algorithm_id, "file2", td["file2"]),
            }
        )
    testdata_params = td.get("params") or {}
    for key, service_default in get_service_params(algorithm_id).items():
        val = testdata_params.get(key, service_default)
        detail = get_field_detail(
            algorithm_id,
            key,
            val,
            default_source="testdata" if key in testdata_params else "service",
        )
        rows.append(
            {
                "name": f"params.{key}",
                "type": get_service_param_type(algorithm_id, key, val),
                "required": False,
                "format": "JSON",
                "description": PARAM_HELP.get(key, detail["label"]),
                "vis": "none",
                **detail,
            }
        )
    return rows


def _output_detail(name: str, vis: str) -> dict:
    """按输出可视化类型补充结果解读、质检方法与下游用途。"""
    if vis == "raster_falsecolor":
        return {
            "label": name,
            "unit": "与对应处理级别一致",
            "range": "由传感器位深、定标尺度和处理方法决定",
            "qualityCheck": "检查空间尺寸、坐标参考、NoData、波段数及异常条带，并与输入同位置对照。",
            "downstreamUse": "可作为后续反射率、特征提取、分类或制图算法的栅格输入。",
        }
    if vis == "raster_index":
        return {
            "label": name,
            "unit": "见具体指标定义",
            "range": "见算法公式；不能只按预览色带判断数值",
            "qualityCheck": "检查数值范围、NaN/NoData、极端值比例和空间连续性，并与原始波段或真值抽样核对。",
            "downstreamUse": "用于阈值分区、时空对比、地块统计或业务专题图。",
        }
    if vis == "raster_class":
        return {
            "label": name,
            "unit": "类别编码",
            "range": "由类别表或掩膜定义决定",
            "qualityCheck": "核对背景值、类别编码、碎斑、边界与混淆矩阵；颜色只用于显示，不代表类别顺序。",
            "downstreamUse": "用于面积统计、对象整理、变化分析或业务告警。",
        }
    if vis == "geojson_map":
        return {
            "label": name,
            "unit": "地理坐标",
            "range": "由 GeoJSON 几何和坐标参考决定",
            "qualityCheck": "检查几何有效性、坐标顺序、坐标参考、闭合性及与底图/栅格的套合。",
            "downstreamUse": "用于地图展示、任务下发、地块统计或 GIS 系统交换。",
        }
    if vis in {"json_table", "csv_table", "csv_track", "csv_spectrum"}:
        return {
            "label": name,
            "unit": "见各列定义",
            "range": "由报表字段定义决定",
            "qualityCheck": "检查字段完整性、单位、记录数量、空值、时间或空间顺序及关键统计量。",
            "downstreamUse": "用于质量审计、统计分析、报表归档或其他系统接入。",
        }
    if vis == "png":
        return {
            "label": name,
            "unit": "显示图",
            "range": "仅供可视化",
            "qualityCheck": "用于快速检查空间格局；定量结论必须读取对应 GeoTIFF、JSON 或 CSV。",
            "downstreamUse": "用于汇报、人工复核和结果预览，不作为定量计算输入。",
        }
    return {
        "label": name,
        "unit": "—",
        "range": "由文件格式决定",
        "qualityCheck": "检查文件可读性、结构和与本次作业的对应关系。",
        "downstreamUse": "按具体算法产物说明使用。",
    }


def _output_selection_guide(description: str, vis: str) -> str:
    """生成输出结果的专业解读提示。"""
    if vis == "raster_class":
        return f"{description}中的像元值表示类别编码；应结合类别表读取，不能把预览颜色当作数值大小。"
    if vis == "raster_index":
        return f"{description}应读取原始像元值，并依据该算法公式、单位和有效范围解释；预览色带只表达相对空间差异。"
    if vis == "raster_falsecolor":
        return f"{description}用于检查空间结构与处理效果；定量分析应读取原始波段值、单位和 NoData。"
    if vis == "geojson_map":
        return f"{description}中的几何表示空间位置，属性表承载类别或统计量；解释前先核对坐标参考。"
    if vis in {"json_table", "csv_table", "csv_track", "csv_spectrum"}:
        return f"{description}应按字段名、单位和统计口径逐列读取，并与本次输入、参数和样本范围对应。"
    if vis == "png":
        return f"{description}仅用于快速人工预览，不能替代对应数值文件进行定量判断。"
    return f"{description}应结合文件格式、字段定义、单位和本次运行参数解释。"


def _output_fields(algorithm_id: str, doc_output: str) -> list[dict]:
    # 按算法列出主要产物键（与 service 一致）
    keys = {
        "01_flight_planning": ["mission_json", "waypoints_geojson"],
        "02_sync_timestamp": ["aligned_json"],
        "03_pos_solution": ["pos_json", "pos_csv"],
        "04_flight_qc": ["report_json"],
        "05_cloud_shadow": ["cloud_mask_tif", "shadow_mask_tif", "combo_mask_tif", "preview_png"],
        "06_dark_current": ["cube_tif"],
        "07_bad_pixel": ["cube_tif"],
        "08_destriping": ["cube_tif"],
        "09_smile_keystone": ["cube_tif"],
        "10_radiance_calibration": ["radiance_tif"],
        "11_relative_radiometric": ["cube_tif"],
        "12_panel_reflectance": ["reflectance_tif"],
        "13_atmospheric_correction": ["reflectance_tif"],
        "14_brdf_correction": ["cube_tif"],
        "15_geo_locate": ["cube_tif", "meta_json"],
        "16_orthorectify": ["ortho_tif"],
        "17_mosaic": ["mosaic_tif"],
        "18_color_balance": ["cube_tif", "preview_png"],
        "19_multi_source_register": ["hsi_tif", "rgb_aligned_tif"],
        "20_bad_band_remove": ["cube_tif"],
        "21_savgol_smooth": ["cube_tif"],
        "22_normalize": ["cube_tif"],
        "23_pca": ["pca_tif"],
        "24_band_select": ["cube_tif", "ranking_json"],
        "25_superpixel": ["labels_tif", "preview_png"],
        "26_patch_build": ["patches_npz", "manifest_json", "preview_png"],
        "27_ndvi": ["ndvi_tif", "preview_png"],
        "28_ndre": ["ndre_tif", "preview_png"],
        "29_evi_savi": ["indices_tif", "preview_png"],
        "30_ndmi_ndwi": ["indices_tif", "preview_png"],
        "31_red_edge_params": ["params_tif", "preview_png"],
        "32_regression_inversion": ["inversion_tif", "preview_png"],
        "33_physical_inversion": ["lai_tif", "cab_tif", "preview_png"],
        "34_svm_rf_classify": ["pred_map_tif", "preview_png"],
        "35_spectral_matching": ["pred_map_tif", "angle_tif", "preview_png"],
        "36_cnn1d_classify": ["pred_map_tif", "preview_png"],
        "37_cnn3d_classify": ["pred_map_tif", "preview_png"],
        "38_transformer_classify": ["pred_map_tif", "preview_png"],
        "39_few_shot_classify": ["pred_map_tif", "preview_png"],
        "40_detect_segment": [
            "score_tif",
            "mask_tif",
            "polygons_geojson",
            "annotation_geojson",
            "preview_png",
        ],
        "41_unmixing": ["abundance_tif", "preview_png"],
        "42_anomaly_detect": ["score_tif", "mask_tif", "preview_png"],
        "43_change_detect": ["magnitude_tif", "chi2_tif", "mask_tif", "preview_png"],
        "44_postprocess_smooth": ["labels_tif", "preview_png"],
        "45_parcel_zonal_stats": ["report_json", "parcel_geojson"],
    }.get(algorithm_id, [])
    knowledge = get_algorithm_output_knowledge(algorithm_id)
    known_outputs = knowledge.get("outputs", {})
    rows = []
    for k in keys:
        vis, desc = OUTPUT_VIS.get(k, ("none", k))
        path = f"files.{k}"
        detail = known_outputs.get(path)
        if detail:
            # 算法专属知识必须覆盖旧的格式级泛化说明。
            detail_vis = detail.get("vis")
            rows.append(
                {
                    "name": path,
                    "type": "file",
                    **detail,
                    "vis": detail_vis if detail_vis in FRONTEND_VIS_KINDS else vis,
                    "selectionGuide": detail["interpretation"],
                    "knowledgeSource": "algorithm",
                }
            )
            continue
        fallback = _output_detail(desc, vis)
        rows.append(
            {
                "name": path,
                "type": "file",
                "description": desc,
                "vis": vis,
                **fallback,
                "effect": desc,
                "businessMeaning": fallback["downstreamUse"],
                "interpretation": _output_selection_guide(desc, vis),
                "abnormalSigns": ["缺少算法专属输出知识，需人工核对产物。"],
                "misuseWarning": "当前仅有格式级回退说明，不得据此作专业结论。",
                "selectionGuide": _output_selection_guide(desc, vis),
                "knowledgeSource": "fallback",
            }
        )
    for path, detail in known_outputs.items():
        if not path.startswith("data."):
            continue
        rows.append(
            {
                "name": path,
                "type": "value",
                **detail,
                # data 的抽象知识类型不直接传给前端可视化分发器。
                "vis": (
                    detail.get("vis")
                    if detail.get("vis") in FRONTEND_VIS_KINDS
                    else "none"
                ),
                "selectionGuide": detail["interpretation"],
                "knowledgeSource": "algorithm",
            }
        )
    return rows


def build_item(meta: dict, doc: dict) -> dict:
    """组装单个算法的控制台元数据。"""
    aid = meta["id"]
    td = _testdata_block(aid)
    output_knowledge = get_algorithm_output_knowledge(aid)
    return {
        "id": aid,
        "title": meta["title"],
        "level": meta["level"],
        "group": meta["level"],
        "implemented": meta["implemented"],
        "purpose": doc.get("purpose", meta["title"]),
        "scenario": doc.get("scenario", ""),
        "doc_input": doc.get("doc_input", ""),
        "doc_output": doc.get("doc_output", ""),
        "output_summary": output_knowledge.get("summary", {}),
        "method": METHODS.get(aid, ""),
        "endpoint": f"POST /api/v1/{aid}/run",
        "console_run": f"POST /api/v1/console/run/{aid}",
        "compare": COMPARE.get(aid, "single"),
        "testdata": {k: td[k] for k in ("file", "file2", "params", "exists")},
        "fields": {
            "inputs": _input_fields(aid, td, doc.get("doc_input", "")),
            "outputs": _output_fields(aid, doc.get("doc_output", "")),
        },
    }


def list_console_algorithms() -> list[dict]:
    """全部算法控制台卡片。"""
    docs = _parse_doc()
    out = []
    for meta in ALGORITHMS:
        num = int(meta["id"].split("_", 1)[0])
        out.append(build_item(meta, docs.get(num, {})))
    return out


def get_console_algorithm(algorithm_id: str) -> dict | None:
    """按 id 取详情。"""
    for item in list_console_algorithms():
        if item["id"] == algorithm_id:
            return item
    return None
