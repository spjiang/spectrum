# 算法 API 测试清单（45 项）

> 格式对齐培训 PPT「对接示例」：`POST /api/v1/{algorithm_id}/run` + `file` / `file2` / `params`。
>
> 工作目录请先进入：`algorithm/source`（样例路径按此相对路径书写）。

## 最近一次自动测试结果

- **时间**：2026-08-09 17:43:20
- **HOST**：`http://127.0.0.1:28800`
- **命令**：`./scripts/smoke_all_algorithms.sh` + 业务字段复核
- **汇总**：HTTP 200 = **45/45**；`success=true` = **45/45**
- **可运行且产出 files**：**9/9**

| # | ID | 状态 | HTTP | success | implemented | files |
|---|----|------|------|---------|-------------|-------|
| 01 | `01_flight_planning` | 骨架 | 200 | True | False | 无 |
| 02 | `02_sync_timestamp` | 骨架 | 200 | True | False | 无 |
| 03 | `03_pos_solution` | 骨架 | 200 | True | False | 无 |
| 04 | `04_flight_qc` | 骨架 | 200 | True | False | 无 |
| 05 | `05_cloud_shadow` | 骨架 | 200 | True | False | 无 |
| 06 | `06_dark_current` | 骨架 | 200 | True | False | 无 |
| 07 | `07_bad_pixel` | 骨架 | 200 | True | False | 无 |
| 08 | `08_destriping` | 骨架 | 200 | True | False | 无 |
| 09 | `09_smile_keystone` | 骨架 | 200 | True | False | 无 |
| 10 | `10_radiance_calibration` | 骨架 | 200 | True | False | 无 |
| 11 | `11_relative_radiometric` | 骨架 | 200 | True | False | 无 |
| 12 | `12_panel_reflectance` | 可运行 | 200 | True | True | 有 |
| 13 | `13_atmospheric_correction` | 骨架 | 200 | True | False | 无 |
| 14 | `14_brdf_correction` | 骨架 | 200 | True | False | 无 |
| 15 | `15_geo_locate` | 骨架 | 200 | True | False | 无 |
| 16 | `16_orthorectify` | 骨架 | 200 | True | False | 无 |
| 17 | `17_mosaic` | 骨架 | 200 | True | False | 无 |
| 18 | `18_color_balance` | 骨架 | 200 | True | False | 无 |
| 19 | `19_multi_source_register` | 骨架 | 200 | True | False | 无 |
| 20 | `20_bad_band_remove` | 可运行 | 200 | True | True | 有 |
| 21 | `21_savgol_smooth` | 可运行 | 200 | True | True | 有 |
| 22 | `22_normalize` | 可运行 | 200 | True | True | 有 |
| 23 | `23_pca` | 可运行 | 200 | True | True | 有 |
| 24 | `24_band_select` | 骨架 | 200 | True | False | 无 |
| 25 | `25_superpixel` | 骨架 | 200 | True | False | 无 |
| 26 | `26_patch_build` | 骨架 | 200 | True | False | 无 |
| 27 | `27_ndvi` | 可运行 | 200 | True | True | 有 |
| 28 | `28_ndre` | 可运行 | 200 | True | True | 有 |
| 29 | `29_evi_savi` | 骨架 | 200 | True | False | 无 |
| 30 | `30_ndmi_ndwi` | 骨架 | 200 | True | False | 无 |
| 31 | `31_red_edge_params` | 骨架 | 200 | True | False | 无 |
| 32 | `32_regression_inversion` | 骨架 | 200 | True | False | 无 |
| 33 | `33_physical_inversion` | 骨架 | 200 | True | False | 无 |
| 34 | `34_svm_rf_classify` | 可运行 | 200 | True | True | 有 |
| 35 | `35_spectral_matching` | 骨架 | 200 | True | False | 无 |
| 36 | `36_cnn1d_classify` | 骨架 | 200 | True | False | 无 |
| 37 | `37_cnn3d_classify` | 骨架 | 200 | True | False | 无 |
| 38 | `38_transformer_classify` | 骨架 | 200 | True | False | 无 |
| 39 | `39_few_shot_classify` | 骨架 | 200 | True | False | 无 |
| 40 | `40_detect_segment` | 骨架 | 200 | True | False | 无 |
| 41 | `41_unmixing` | 骨架 | 200 | True | False | 无 |
| 42 | `42_anomaly_detect` | 骨架 | 200 | True | False | 无 |
| 43 | `43_change_detect` | 骨架 | 200 | True | False | 无 |
| 44 | `44_postprocess_smooth` | 骨架 | 200 | True | False | 无 |
| 45 | `45_parcel_zonal_stats` | 可运行 | 200 | True | True | 有 |

## 使用说明

1. 启动服务：`./scripts/start.sh`（默认 `http://127.0.0.1:28800`）
2. 健康检查：`curl -s http://127.0.0.1:28800/api/v1/algorithms | python -m json.tool | head`
3. 按下列命令逐项测试；**可运行**项应返回 `success=true` 与产物路径；**骨架**项通常返回 `implemented=false`（接口可达即可）
4. 勾选列供联调/验收打钩

## 总览勾选表

| # | 算法 ID | 标题 | 层级 | 状态 | 通过 |
|---|---------|------|------|------|------|
| 01 | `01_flight_planning` | 航线规划与覆盖优化 | L0前 | 骨架 | ✅ |
| 02 | `02_sync_timestamp` | 同步曝光与时间戳对齐 | L0 | 骨架 | ✅ |
| 03 | `03_pos_solution` | POS解算（GPS+IMU） | L0 | 骨架 | ✅ |
| 04 | `04_flight_qc` | 架次质检（丢帧/过曝） | L0 | 骨架 | ✅ |
| 05 | `05_cloud_shadow` | 云/云影检测 | L0 | 骨架 | ✅ |
| 06 | `06_dark_current` | 暗电流校正 | L0→L1 | 骨架 | ✅ |
| 07 | `07_bad_pixel` | 坏线/坏像元修复 | L0→L1 | 骨架 | ✅ |
| 08 | `08_destriping` | 条带噪声去除 | L0→L1 | 骨架 | ✅ |
| 09 | `09_smile_keystone` | 光谱微笑/关键畸变校正 | L0→L1 | 骨架 | ✅ |
| 10 | `10_radiance_calibration` | 辐射定标 DN→辐亮度 | L0→L1 | 骨架 | ✅ |
| 11 | `11_relative_radiometric` | 相对辐射归一 | L1 | 骨架 | ✅ |
| 12 | `12_panel_reflectance` | 白板/灰板反射率定标（示意） | L1→L2 | 可运行 | ✅ |
| 13 | `13_atmospheric_correction` | 大气校正 | L1→L2 | 骨架 | ✅ |
| 14 | `14_brdf_correction` | BRDF/观测几何校正 | L1→L2 | 骨架 | ✅ |
| 15 | `15_geo_locate` | 几何粗校正/地理定位 | L1→L2 | 骨架 | ✅ |
| 16 | `16_orthorectify` | 正射校正 | L1→L2 | 骨架 | ✅ |
| 17 | `17_mosaic` | 影像匹配与镶嵌 | L2 | 骨架 | ✅ |
| 18 | `18_color_balance` | 匀色与接缝线优化 | L2 | 骨架 | ✅ |
| 19 | `19_multi_source_register` | 多源配准 HSI-RGB-矢量 | L2 | 骨架 | ✅ |
| 20 | `20_bad_band_remove` | 坏波段剔除与光谱去噪 | L2 | 可运行 | ✅ |
| 21 | `21_savgol_smooth` | Savitzky-Golay平滑 | L2 | 可运行 | ✅ |
| 22 | `22_normalize` | 标准化/归一化 | L2 | 可运行 | ✅ |
| 23 | `23_pca` | PCA/MNF降维 | L2 | 可运行 | ✅ |
| 24 | `24_band_select` | 波段/特征选择 | L2 | 骨架 | ✅ |
| 25 | `25_superpixel` | 超像素/对象分割 | L2 | 骨架 | ✅ |
| 26 | `26_patch_build` | Patch/样本构建 | L2 | 骨架 | ✅ |
| 27 | `27_ndvi` | NDVI植被指数 | L3 | 可运行 | ✅ |
| 28 | `28_ndre` | NDRE红边植被指数 | L3 | 可运行 | ✅ |
| 29 | `29_evi_savi` | EVI/SAVI/MSAVI | L3 | 骨架 | ✅ |
| 30 | `30_ndmi_ndwi` | NDMI/NDWI/MNDWI | L3 | 骨架 | ✅ |
| 31 | `31_red_edge_params` | 红边位置与光谱特征参数 | L3 | 骨架 | ✅ |
| 32 | `32_regression_inversion` | 经验回归反演 | L3 | 骨架 | ✅ |
| 33 | `33_physical_inversion` | 辐射传输物理反演 | L3 | 骨架 | ✅ |
| 34 | `34_svm_rf_classify` | SVM/随机森林分类 | L3 | 可运行 | ✅ |
| 35 | `35_spectral_matching` | 光谱匹配分类(SAM) | L3 | 骨架 | ✅ |
| 36 | `36_cnn1d_classify` | 1D-CNN/RNN光谱分类 | L3 | 骨架 | ✅ |
| 37 | `37_cnn3d_classify` | 2D/3D-CNN空谱分类 | L3 | 骨架 | ✅ |
| 38 | `38_transformer_classify` | Transformer/GCN分类 | L3 | 骨架 | ✅ |
| 39 | `39_few_shot_classify` | 少样本/迁移学习分类 | L3 | 骨架 | ✅ |
| 40 | `40_detect_segment` | 语义分割/目标检测 | L3 | 骨架 | ✅ |
| 41 | `41_unmixing` | 混合像元分解 | L3 | 骨架 | ✅ |
| 42 | `42_anomaly_detect` | 异常检测 | L3 | 骨架 | ✅ |
| 43 | `43_change_detect` | 多时相变化检测 | L3 | 骨架 | ✅ |
| 44 | `44_postprocess_smooth` | 分类后处理平滑/小斑剔除 | L3→L4 | 骨架 | ✅ |
| 45 | `45_parcel_zonal_stats` | 地块汇总与专题统计 | L4 | 可运行 | ✅ |

## 逐项调用命令

说明：下列 `curl` 均在 `algorithm/source` 下执行。

### 01. 航线规划与覆盖优化

- **algorithm_id**：`01_flight_planning`
- **层级**：L0前
- **状态**：骨架
- **主文件 file**：`algorithms/01_flight_planning/testdata/input.geojson`
- **第二文件 file2**：无
- **params**：`{"cruise_speed_m_s": 8}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/01_flight_planning/run" \
  -F "file=@algorithms/01_flight_planning/testdata/input.geojson" \
  -F 'params={"cruise_speed_m_s":8}'
```

### 02. 同步曝光与时间戳对齐

- **algorithm_id**：`02_sync_timestamp`
- **层级**：L0
- **状态**：骨架
- **主文件 file**：`algorithms/02_sync_timestamp/testdata/input.json`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/02_sync_timestamp/run" \
  -F "file=@algorithms/02_sync_timestamp/testdata/input.json" \
  -F 'params={}'
```

### 03. POS解算（GPS+IMU）

- **algorithm_id**：`03_pos_solution`
- **层级**：L0
- **状态**：骨架
- **主文件 file**：`algorithms/03_pos_solution/testdata/input.csv`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/03_pos_solution/run" \
  -F "file=@algorithms/03_pos_solution/testdata/input.csv" \
  -F 'params={}'
```

### 04. 架次质检（丢帧/过曝）

- **algorithm_id**：`04_flight_qc`
- **层级**：L0
- **状态**：骨架
- **主文件 file**：`algorithms/04_flight_qc/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"max_saturated_ratio": 0.01}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/04_flight_qc/run" \
  -F "file=@algorithms/04_flight_qc/testdata/input.tif" \
  -F 'params={"max_saturated_ratio":0.01}'
```

### 05. 云/云影检测

- **algorithm_id**：`05_cloud_shadow`
- **层级**：L0
- **状态**：骨架
- **主文件 file**：`algorithms/05_cloud_shadow/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/05_cloud_shadow/run" \
  -F "file=@algorithms/05_cloud_shadow/testdata/input.tif" \
  -F 'params={}'
```

### 06. 暗电流校正

- **algorithm_id**：`06_dark_current`
- **层级**：L0→L1
- **状态**：骨架
- **主文件 file**：`algorithms/06_dark_current/testdata/input.tif`
- **第二文件 file2**：`algorithms/06_dark_current/testdata/file2.tif`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/06_dark_current/run" \
  -F "file=@algorithms/06_dark_current/testdata/input.tif" \
  -F "file2=@algorithms/06_dark_current/testdata/file2.tif" \
  -F 'params={}'
```

### 07. 坏线/坏像元修复

- **algorithm_id**：`07_bad_pixel`
- **层级**：L0→L1
- **状态**：骨架
- **主文件 file**：`algorithms/07_bad_pixel/testdata/input.tif`
- **第二文件 file2**：`algorithms/07_bad_pixel/testdata/file2.json`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/07_bad_pixel/run" \
  -F "file=@algorithms/07_bad_pixel/testdata/input.tif" \
  -F "file2=@algorithms/07_bad_pixel/testdata/file2.json" \
  -F 'params={}'
```

### 08. 条带噪声去除

- **algorithm_id**：`08_destriping`
- **层级**：L0→L1
- **状态**：骨架
- **主文件 file**：`algorithms/08_destriping/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/08_destriping/run" \
  -F "file=@algorithms/08_destriping/testdata/input.tif" \
  -F 'params={}'
```

### 09. 光谱微笑/关键畸变校正

- **algorithm_id**：`09_smile_keystone`
- **层级**：L0→L1
- **状态**：骨架
- **主文件 file**：`algorithms/09_smile_keystone/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/09_smile_keystone/run" \
  -F "file=@algorithms/09_smile_keystone/testdata/input.tif" \
  -F 'params={}'
```

### 10. 辐射定标 DN→辐亮度

- **algorithm_id**：`10_radiance_calibration`
- **层级**：L0→L1
- **状态**：骨架
- **主文件 file**：`algorithms/10_radiance_calibration/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"gain": 0.01, "offset": 0.0}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/10_radiance_calibration/run" \
  -F "file=@algorithms/10_radiance_calibration/testdata/input.tif" \
  -F 'params={"gain":0.01,"offset":0.0}'
```

### 11. 相对辐射归一

- **algorithm_id**：`11_relative_radiometric`
- **层级**：L1
- **状态**：骨架
- **主文件 file**：`algorithms/11_relative_radiometric/testdata/input.tif`
- **第二文件 file2**：`algorithms/11_relative_radiometric/testdata/file2.tif`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/11_relative_radiometric/run" \
  -F "file=@algorithms/11_relative_radiometric/testdata/input.tif" \
  -F "file2=@algorithms/11_relative_radiometric/testdata/file2.tif" \
  -F 'params={}'
```

### 12. 白板/灰板反射率定标（示意）

- **algorithm_id**：`12_panel_reflectance`
- **层级**：L1→L2
- **状态**：可运行
- **主文件 file**：`algorithms/12_panel_reflectance/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"scale": 0.001}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/12_panel_reflectance/run" \
  -F "file=@algorithms/12_panel_reflectance/testdata/input.tif" \
  -F 'params={"scale":0.001}'
```

### 13. 大气校正

- **algorithm_id**：`13_atmospheric_correction`
- **层级**：L1→L2
- **状态**：骨架
- **主文件 file**：`algorithms/13_atmospheric_correction/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/13_atmospheric_correction/run" \
  -F "file=@algorithms/13_atmospheric_correction/testdata/input.tif" \
  -F 'params={}'
```

### 14. BRDF/观测几何校正

- **algorithm_id**：`14_brdf_correction`
- **层级**：L1→L2
- **状态**：骨架
- **主文件 file**：`algorithms/14_brdf_correction/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"solar_zenith": 30, "view_zenith": 10}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/14_brdf_correction/run" \
  -F "file=@algorithms/14_brdf_correction/testdata/input.tif" \
  -F 'params={"solar_zenith":30,"view_zenith":10}'
```

### 15. 几何粗校正/地理定位

- **algorithm_id**：`15_geo_locate`
- **层级**：L1→L2
- **状态**：骨架
- **主文件 file**：`algorithms/15_geo_locate/testdata/input.tif`
- **第二文件 file2**：`algorithms/15_geo_locate/testdata/file2.json`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/15_geo_locate/run" \
  -F "file=@algorithms/15_geo_locate/testdata/input.tif" \
  -F "file2=@algorithms/15_geo_locate/testdata/file2.json" \
  -F 'params={}'
```

### 16. 正射校正

- **algorithm_id**：`16_orthorectify`
- **层级**：L1→L2
- **状态**：骨架
- **主文件 file**：`algorithms/16_orthorectify/testdata/input.tif`
- **第二文件 file2**：`algorithms/16_orthorectify/testdata/file2.tif`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/16_orthorectify/run" \
  -F "file=@algorithms/16_orthorectify/testdata/input.tif" \
  -F "file2=@algorithms/16_orthorectify/testdata/file2.tif" \
  -F 'params={}'
```

### 17. 影像匹配与镶嵌

- **algorithm_id**：`17_mosaic`
- **层级**：L2
- **状态**：骨架
- **主文件 file**：`algorithms/17_mosaic/testdata/input.tif`
- **第二文件 file2**：`algorithms/17_mosaic/testdata/file2.tif`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/17_mosaic/run" \
  -F "file=@algorithms/17_mosaic/testdata/input.tif" \
  -F "file2=@algorithms/17_mosaic/testdata/file2.tif" \
  -F 'params={}'
```

### 18. 匀色与接缝线优化

- **algorithm_id**：`18_color_balance`
- **层级**：L2
- **状态**：骨架
- **主文件 file**：`algorithms/18_color_balance/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/18_color_balance/run" \
  -F "file=@algorithms/18_color_balance/testdata/input.tif" \
  -F 'params={}'
```

### 19. 多源配准 HSI-RGB-矢量

- **algorithm_id**：`19_multi_source_register`
- **层级**：L2
- **状态**：骨架
- **主文件 file**：`algorithms/19_multi_source_register/testdata/input.tif`
- **第二文件 file2**：`algorithms/19_multi_source_register/testdata/file2.tif`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/19_multi_source_register/run" \
  -F "file=@algorithms/19_multi_source_register/testdata/input.tif" \
  -F "file2=@algorithms/19_multi_source_register/testdata/file2.tif" \
  -F 'params={}'
```

### 20. 坏波段剔除与光谱去噪

- **algorithm_id**：`20_bad_band_remove`
- **层级**：L2
- **状态**：可运行
- **主文件 file**：`algorithms/20_bad_band_remove/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"drop_bands": [0, 5]}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/20_bad_band_remove/run" \
  -F "file=@algorithms/20_bad_band_remove/testdata/input.tif" \
  -F 'params={"drop_bands":[0,5]}'
```

### 21. Savitzky-Golay平滑

- **algorithm_id**：`21_savgol_smooth`
- **层级**：L2
- **状态**：可运行
- **主文件 file**：`algorithms/21_savgol_smooth/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"window_length": 5, "polyorder": 2}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/21_savgol_smooth/run" \
  -F "file=@algorithms/21_savgol_smooth/testdata/input.tif" \
  -F 'params={"window_length":5,"polyorder":2}'
```

### 22. 标准化/归一化

- **algorithm_id**：`22_normalize`
- **层级**：L2
- **状态**：可运行
- **主文件 file**：`algorithms/22_normalize/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"method": "zscore"}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/22_normalize/run" \
  -F "file=@algorithms/22_normalize/testdata/input.tif" \
  -F 'params={"method":"zscore"}'
```

### 23. PCA/MNF降维

- **algorithm_id**：`23_pca`
- **层级**：L2
- **状态**：可运行
- **主文件 file**：`algorithms/23_pca/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"n_components": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/23_pca/run" \
  -F "file=@algorithms/23_pca/testdata/input.tif" \
  -F 'params={"n_components":3}'
```

### 24. 波段/特征选择

- **algorithm_id**：`24_band_select`
- **层级**：L2
- **状态**：骨架
- **主文件 file**：`algorithms/24_band_select/testdata/input.tif`
- **第二文件 file2**：`algorithms/24_band_select/testdata/file2.tif`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/24_band_select/run" \
  -F "file=@algorithms/24_band_select/testdata/input.tif" \
  -F "file2=@algorithms/24_band_select/testdata/file2.tif" \
  -F 'params={}'
```

### 25. 超像素/对象分割

- **algorithm_id**：`25_superpixel`
- **层级**：L2
- **状态**：骨架
- **主文件 file**：`algorithms/25_superpixel/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"n_segments": 20}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/25_superpixel/run" \
  -F "file=@algorithms/25_superpixel/testdata/input.tif" \
  -F 'params={"n_segments":20}'
```

### 26. Patch/样本构建

- **algorithm_id**：`26_patch_build`
- **层级**：L2
- **状态**：骨架
- **主文件 file**：`algorithms/26_patch_build/testdata/input.tif`
- **第二文件 file2**：`algorithms/26_patch_build/testdata/file2.tif`
- **params**：`{"patch_size": 5}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/26_patch_build/run" \
  -F "file=@algorithms/26_patch_build/testdata/input.tif" \
  -F "file2=@algorithms/26_patch_build/testdata/file2.tif" \
  -F 'params={"patch_size":5}'
```

### 27. NDVI植被指数

- **algorithm_id**：`27_ndvi`
- **层级**：L3
- **状态**：可运行
- **主文件 file**：`algorithms/27_ndvi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"red_band": 2, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/27_ndvi/run" \
  -F "file=@algorithms/27_ndvi/testdata/input.tif" \
  -F 'params={"red_band":2,"nir_band":3}'
```

### 28. NDRE红边植被指数

- **algorithm_id**：`28_ndre`
- **层级**：L3
- **状态**：可运行
- **主文件 file**：`algorithms/28_ndre/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"re_band": 4, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/28_ndre/run" \
  -F "file=@algorithms/28_ndre/testdata/input.tif" \
  -F 'params={"re_band":4,"nir_band":3}'
```

### 29. EVI/SAVI/MSAVI

- **algorithm_id**：`29_evi_savi`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/29_evi_savi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"blue_band": 0, "red_band": 2, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/29_evi_savi/run" \
  -F "file=@algorithms/29_evi_savi/testdata/input.tif" \
  -F 'params={"blue_band":0,"red_band":2,"nir_band":3}'
```

### 30. NDMI/NDWI/MNDWI

- **algorithm_id**：`30_ndmi_ndwi`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/30_ndmi_ndwi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"green_band": 1, "nir_band": 3, "swir_band": 5}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/30_ndmi_ndwi/run" \
  -F "file=@algorithms/30_ndmi_ndwi/testdata/input.tif" \
  -F 'params={"green_band":1,"nir_band":3,"swir_band":5}'
```

### 31. 红边位置与光谱特征参数

- **algorithm_id**：`31_red_edge_params`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/31_red_edge_params/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/31_red_edge_params/run" \
  -F "file=@algorithms/31_red_edge_params/testdata/input.tif" \
  -F 'params={}'
```

### 32. 经验回归反演

- **algorithm_id**：`32_regression_inversion`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/32_regression_inversion/testdata/input.tif`
- **第二文件 file2**：`algorithms/32_regression_inversion/testdata/file2.tif`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/32_regression_inversion/run" \
  -F "file=@algorithms/32_regression_inversion/testdata/input.tif" \
  -F "file2=@algorithms/32_regression_inversion/testdata/file2.tif" \
  -F 'params={}'
```

### 33. 辐射传输物理反演

- **algorithm_id**：`33_physical_inversion`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/33_physical_inversion/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/33_physical_inversion/run" \
  -F "file=@algorithms/33_physical_inversion/testdata/input.tif" \
  -F 'params={}'
```

### 34. SVM/随机森林分类

- **algorithm_id**：`34_svm_rf_classify`
- **层级**：L3
- **状态**：可运行
- **主文件 file**：`algorithms/34_svm_rf_classify/testdata/input.tif`
- **第二文件 file2**：`algorithms/34_svm_rf_classify/testdata/file2.tif`
- **params**：`{"test_size": 0.3, "kernel": "rbf"}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/34_svm_rf_classify/run" \
  -F "file=@algorithms/34_svm_rf_classify/testdata/input.tif" \
  -F "file2=@algorithms/34_svm_rf_classify/testdata/file2.tif" \
  -F 'params={"test_size":0.3,"kernel":"rbf"}'
```

### 35. 光谱匹配分类(SAM)

- **algorithm_id**：`35_spectral_matching`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/35_spectral_matching/testdata/input.tif`
- **第二文件 file2**：`algorithms/35_spectral_matching/testdata/file2.csv`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/35_spectral_matching/run" \
  -F "file=@algorithms/35_spectral_matching/testdata/input.tif" \
  -F "file2=@algorithms/35_spectral_matching/testdata/file2.csv" \
  -F 'params={}'
```

### 36. 1D-CNN/RNN光谱分类

- **algorithm_id**：`36_cnn1d_classify`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/36_cnn1d_classify/testdata/input.tif`
- **第二文件 file2**：`algorithms/36_cnn1d_classify/testdata/file2.tif`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/36_cnn1d_classify/run" \
  -F "file=@algorithms/36_cnn1d_classify/testdata/input.tif" \
  -F "file2=@algorithms/36_cnn1d_classify/testdata/file2.tif" \
  -F 'params={}'
```

### 37. 2D/3D-CNN空谱分类

- **algorithm_id**：`37_cnn3d_classify`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/37_cnn3d_classify/testdata/input.tif`
- **第二文件 file2**：`algorithms/37_cnn3d_classify/testdata/file2.tif`
- **params**：`{"patch_size": 5}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/37_cnn3d_classify/run" \
  -F "file=@algorithms/37_cnn3d_classify/testdata/input.tif" \
  -F "file2=@algorithms/37_cnn3d_classify/testdata/file2.tif" \
  -F 'params={"patch_size":5}'
```

### 38. Transformer/GCN分类

- **algorithm_id**：`38_transformer_classify`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/38_transformer_classify/testdata/input.tif`
- **第二文件 file2**：`algorithms/38_transformer_classify/testdata/file2.tif`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/38_transformer_classify/run" \
  -F "file=@algorithms/38_transformer_classify/testdata/input.tif" \
  -F "file2=@algorithms/38_transformer_classify/testdata/file2.tif" \
  -F 'params={}'
```

### 39. 少样本/迁移学习分类

- **algorithm_id**：`39_few_shot_classify`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/39_few_shot_classify/testdata/input.tif`
- **第二文件 file2**：`algorithms/39_few_shot_classify/testdata/file2.tif`
- **params**：`{"shots": 5}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/39_few_shot_classify/run" \
  -F "file=@algorithms/39_few_shot_classify/testdata/input.tif" \
  -F "file2=@algorithms/39_few_shot_classify/testdata/file2.tif" \
  -F 'params={"shots":5}'
```

### 40. 语义分割/目标检测

- **algorithm_id**：`40_detect_segment`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/40_detect_segment/testdata/input.tif`
- **第二文件 file2**：`algorithms/40_detect_segment/testdata/file2.geojson`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/40_detect_segment/run" \
  -F "file=@algorithms/40_detect_segment/testdata/input.tif" \
  -F "file2=@algorithms/40_detect_segment/testdata/file2.geojson" \
  -F 'params={}'
```

### 41. 混合像元分解

- **algorithm_id**：`41_unmixing`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/41_unmixing/testdata/input.tif`
- **第二文件 file2**：`algorithms/41_unmixing/testdata/file2.csv`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/41_unmixing/run" \
  -F "file=@algorithms/41_unmixing/testdata/input.tif" \
  -F "file2=@algorithms/41_unmixing/testdata/file2.csv" \
  -F 'params={}'
```

### 42. 异常检测

- **algorithm_id**：`42_anomaly_detect`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/42_anomaly_detect/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/42_anomaly_detect/run" \
  -F "file=@algorithms/42_anomaly_detect/testdata/input.tif" \
  -F 'params={}'
```

### 43. 多时相变化检测

- **algorithm_id**：`43_change_detect`
- **层级**：L3
- **状态**：骨架
- **主文件 file**：`algorithms/43_change_detect/testdata/input.tif`
- **第二文件 file2**：`algorithms/43_change_detect/testdata/file2.tif`
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/43_change_detect/run" \
  -F "file=@algorithms/43_change_detect/testdata/input.tif" \
  -F "file2=@algorithms/43_change_detect/testdata/file2.tif" \
  -F 'params={}'
```

### 44. 分类后处理平滑/小斑剔除

- **algorithm_id**：`44_postprocess_smooth`
- **层级**：L3→L4
- **状态**：骨架
- **主文件 file**：`algorithms/44_postprocess_smooth/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"min_pixels": 4}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/44_postprocess_smooth/run" \
  -F "file=@algorithms/44_postprocess_smooth/testdata/input.tif" \
  -F 'params={"min_pixels":4}'
```

### 45. 地块汇总与专题统计

- **algorithm_id**：`45_parcel_zonal_stats`
- **层级**：L4
- **状态**：可运行
- **主文件 file**：`algorithms/45_parcel_zonal_stats/testdata/input.tif`
- **第二文件 file2**：`algorithms/45_parcel_zonal_stats/testdata/file2.geojson`
- **params**：`{"mode": "continuous", "roi": [0, 8, 0, 8]}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/45_parcel_zonal_stats/run" \
  -F "file=@algorithms/45_parcel_zonal_stats/testdata/input.tif" \
  -F "file2=@algorithms/45_parcel_zonal_stats/testdata/file2.geojson" \
  -F 'params={"mode":"continuous","roi":[0,8,0,8]}'
```

## 批量冒烟（可选）

服务已启动后，在 `algorithm/source` 执行：

```bash
./scripts/smoke_all_algorithms.sh
```

脚本会按本清单相同参数逐项 `POST /run`，统计 HTTP 200 通过数（不强制业务已实现）。

## 期望结果速查

| 状态 | 期望 |
|------|------|
| 可运行 | `success=true`，`data` 有统计/指标，`files` 含 `.tif` 等产物路径 |
| 骨架 | 接口 200，正文标明未实现或 `implemented=false`；不应 500 |

可运行清单：`12_panel_reflectance`、`20_bad_band_remove`、`21_savgol_smooth`、`22_normalize`、`23_pca`、`27_ndvi`、`28_ndre`、`34_svm_rf_classify`、`45_parcel_zonal_stats`
