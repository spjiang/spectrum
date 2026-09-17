# 算法 API 测试清单（55 项）

> 格式对齐培训 PPT「对接示例」：`POST /api/v1/{algorithm_id}/run` + `file` / `file2` / `params`。
>
> 工作目录请先进入：`algorithm/source`（样例路径按此相对路径书写）。
>
> **算法介绍**（作用 / 使用场景 / 数据输入 / 数据输出）已与 [采集到算法-算法清单.md](./采集到算法-算法清单.md) 同步。

## 最近一次自动测试结果

- **时间**：2026-09-08 20:19:40
- **HOST**：`http://127.0.0.1:28800`
- **命令**：生产级实现后 `scripts/smoke_all_implemented.py`（curl 冒烟）
- **汇总**：HTTP 200 = **55/55**；`success=true` = **55/55**
- **可运行且产出 files**：**55/55**

| # | ID | 状态 | HTTP | success | implemented | files |
|---|----|------|------|---------|-------------|-------|
| 01 | `01_flight_planning` | 可运行 | 200 | True | True | 有 |
| 02 | `02_sync_timestamp` | 可运行 | 200 | True | True | 有 |
| 03 | `03_pos_solution` | 可运行 | 200 | True | True | 有 |
| 04 | `04_flight_qc` | 可运行 | 200 | True | True | 有 |
| 05 | `05_cloud_shadow` | 可运行 | 200 | True | True | 有 |
| 06 | `06_dark_current` | 可运行 | 200 | True | True | 有 |
| 07 | `07_bad_pixel` | 可运行 | 200 | True | True | 有 |
| 08 | `08_destriping` | 可运行 | 200 | True | True | 有 |
| 09 | `09_smile_keystone` | 可运行 | 200 | True | True | 有 |
| 10 | `10_radiance_calibration` | 可运行 | 200 | True | True | 有 |
| 11 | `11_relative_radiometric` | 可运行 | 200 | True | True | 有 |
| 12 | `12_panel_reflectance` | 可运行 | 200 | True | True | 有 |
| 13 | `13_atmospheric_correction` | 可运行 | 200 | True | True | 有 |
| 14 | `14_brdf_correction` | 可运行 | 200 | True | True | 有 |
| 15 | `15_geo_locate` | 可运行 | 200 | True | True | 有 |
| 16 | `16_orthorectify` | 可运行 | 200 | True | True | 有 |
| 17 | `17_mosaic` | 可运行 | 200 | True | True | 有 |
| 18 | `18_color_balance` | 可运行 | 200 | True | True | 有 |
| 19 | `19_multi_source_register` | 可运行 | 200 | True | True | 有 |
| 20 | `20_bad_band_remove` | 可运行 | 200 | True | True | 有 |
| 21 | `21_savgol_smooth` | 可运行 | 200 | True | True | 有 |
| 22 | `22_normalize` | 可运行 | 200 | True | True | 有 |
| 23 | `23_pca` | 可运行 | 200 | True | True | 有 |
| 24 | `24_band_select` | 可运行 | 200 | True | True | 有 |
| 25 | `25_superpixel` | 可运行 | 200 | True | True | 有 |
| 26 | `26_patch_build` | 可运行 | 200 | True | True | 有 |
| 27 | `27_ndvi` | 可运行 | 200 | True | True | 有 |
| 28 | `28_ndre` | 可运行 | 200 | True | True | 有 |
| 29 | `29_evi_savi` | 可运行 | 200 | True | True | 有 |
| 30 | `30_ndmi_ndwi` | 可运行 | 200 | True | True | 有 |
| 31 | `31_red_edge_params` | 可运行 | 200 | True | True | 有 |
| 32 | `32_regression_inversion` | 可运行 | 200 | True | True | 有 |
| 33 | `33_physical_inversion` | 可运行 | 200 | True | True | 有 |
| 34 | `34_svm_rf_classify` | 可运行 | 200 | True | True | 有 |
| 35 | `35_spectral_matching` | 可运行 | 200 | True | True | 有 |
| 36 | `36_cnn1d_classify` | 可运行 | 200 | True | True | 有 |
| 37 | `37_cnn3d_classify` | 可运行 | 200 | True | True | 有 |
| 38 | `38_transformer_classify` | 可运行 | 200 | True | True | 有 |
| 39 | `39_few_shot_classify` | 可运行 | 200 | True | True | 有 |
| 40 | `40_detect_segment` | 可运行 | 200 | True | True | 有 |
| 41 | `41_unmixing` | 可运行 | 200 | True | True | 有 |
| 42 | `42_anomaly_detect` | 可运行 | 200 | True | True | 有 |
| 43 | `43_change_detect` | 可运行 | 200 | True | True | 有 |
| 44 | `44_postprocess_smooth` | 可运行 | 200 | True | True | 有 |
| 45 | `45_parcel_zonal_stats` | 可运行 | 200 | True | True | 有 |
| 46 | `46_reci` | 可运行 | 200 | True | True | 有 |
| 47 | `47_gndvi` | 可运行 | 200 | True | True | 有 |
| 48 | `48_osavi` | 可运行 | 200 | True | True | 有 |
| 49 | `49_arvi` | 可运行 | 200 | True | True | 有 |
| 50 | `50_vari` | 可运行 | 200 | True | True | 有 |
| 51 | `51_lai_index` | 可运行 | 200 | True | True | 有 |
| 52 | `52_nbr` | 可运行 | 200 | True | True | 有 |
| 53 | `53_sipi` | 可运行 | 200 | True | True | 有 |
| 54 | `54_gci` | 可运行 | 200 | True | True | 有 |
| 55 | `55_ndsi` | 可运行 | 200 | True | True | 有 |

## 使用说明

1. 启动服务：`./scripts/start.sh`（默认 `http://127.0.0.1:28800`）
2. 健康检查：`curl -s http://127.0.0.1:28800/api/v1/algorithms | python -m json.tool | head`
3. 按下列命令逐项测试；**可运行**项应返回 `success=true` 与产物路径；**骨架**项通常返回 `implemented=false`（接口可达即可）
4. 每项含算法介绍 + curl；勾选列供联调/验收打钩

## 总览勾选表

| # | 算法 ID | 标题 | 层级 | 状态 | 通过 |
|---|---------|------|------|------|------|
| 01 | `01_flight_planning` | 航线规划与覆盖优化 | L0前 | 可运行 | ✅ |
| 02 | `02_sync_timestamp` | 同步曝光与时间戳对齐 | L0 | 可运行 | ✅ |
| 03 | `03_pos_solution` | POS轨迹平滑与杠杆臂校正 | L0 | 可运行 | ✅ |
| 04 | `04_flight_qc` | 架次过曝与场景统计质检 | L0 | 可运行 | ✅ |
| 05 | `05_cloud_shadow` | 云/云影检测 | L0 | 可运行 | ✅ |
| 06 | `06_dark_current` | 暗电流校正 | L0→L1 | 可运行 | ✅ |
| 07 | `07_bad_pixel` | 坏线/坏像元修复 | L0→L1 | 可运行 | ✅ |
| 08 | `08_destriping` | 条带噪声去除 | L0→L1 | 可运行 | ✅ |
| 09 | `09_smile_keystone` | 光谱微笑/关键畸变校正 | L0→L1 | 可运行 | ✅ |
| 10 | `10_radiance_calibration` | 辐射定标 DN→辐亮度 | L0→L1 | 可运行 | ✅ |
| 11 | `11_relative_radiometric` | 相对辐射归一 | L1 | 可运行 | ✅ |
| 12 | `12_panel_reflectance` | 白板/灰板反射率定标 | L1→L2 | 可运行 | ✅ |
| 13 | `13_atmospheric_correction` | 大气校正 | L1→L2 | 可运行 | ✅ |
| 14 | `14_brdf_correction` | BRDF/观测几何校正 | L1→L2 | 可运行 | ✅ |
| 15 | `15_geo_locate` | POS中心点与GSD粗定位 | L1→L2 | 可运行 | ✅ |
| 16 | `16_orthorectify` | 正射校正 | L1→L2 | 可运行 | ✅ |
| 17 | `17_mosaic` | 影像匹配与镶嵌 | L2 | 可运行 | ✅ |
| 18 | `18_color_balance` | Wallis局部匀色 | L2 | 可运行 | ✅ |
| 19 | `19_multi_source_register` | HSI-RGB全局平移配准 | L2 | 可运行 | ✅ |
| 20 | `20_bad_band_remove` | 坏波段剔除 | L2 | 可运行 | ✅ |
| 21 | `21_savgol_smooth` | Savitzky-Golay平滑 | L2 | 可运行 | ✅ |
| 22 | `22_normalize` | 标准化/归一化 | L2 | 可运行 | ✅ |
| 23 | `23_pca` | PCA/MNF降维 | L2 | 可运行 | ✅ |
| 24 | `24_band_select` | 波段/特征选择 | L2 | 可运行 | ✅ |
| 25 | `25_superpixel` | 超像素/对象分割 | L2 | 可运行 | ✅ |
| 26 | `26_patch_build` | Patch/样本构建 | L2 | 可运行 | ✅ |
| 27 | `27_ndvi` | NDVI植被指数 | L3 | 可运行 | ✅ |
| 28 | `28_ndre` | NDRE红边植被指数 | L3 | 可运行 | ✅ |
| 29 | `29_evi_savi` | EVI/SAVI/MSAVI | L3 | 可运行 | ✅ |
| 30 | `30_ndmi_ndwi` | NDMI/NDWI/MNDWI | L3 | 可运行 | ✅ |
| 31 | `31_red_edge_params` | 红边位置与光谱特征参数 | L3 | 可运行 | ✅ |
| 32 | `32_regression_inversion` | 经验回归反演 | L3 | 可运行 | ✅ |
| 33 | `33_physical_inversion` | 辐射传输物理反演 | L3 | 可运行 | ✅ |
| 34 | `34_svm_rf_classify` | SVM/随机森林分类 | L3 | 可运行 | ✅ |
| 35 | `35_spectral_matching` | 光谱匹配分类(SAM) | L3 | 可运行 | ✅ |
| 36 | `36_cnn1d_classify` | 1D-CNN光谱分类 | L3 | 可运行 | ✅ |
| 37 | `37_cnn3d_classify` | 2D/3D-CNN空谱分类 | L3 | 可运行 | ✅ |
| 38 | `38_transformer_classify` | SpectralFormer光谱分类 | L3 | 可运行 | ✅ |
| 39 | `39_few_shot_classify` | SAM均值原型少样本分类 | L3 | 可运行 | ✅ |
| 40 | `40_detect_segment` | 低NDVI种子ACE目标检测 | L3 | 可运行 | ✅ |
| 41 | `41_unmixing` | 混合像元分解 | L3 | 可运行 | ✅ |
| 42 | `42_anomaly_detect` | 异常检测 | L3 | 可运行 | ✅ |
| 43 | `43_change_detect` | 多时相变化检测 | L3 | 可运行 | ✅ |
| 44 | `44_postprocess_smooth` | 分类后处理平滑/小斑剔除 | L3→L4 | 可运行 | ✅ |
| 45 | `45_parcel_zonal_stats` | 地块汇总与专题统计 | L4 | 可运行 | ✅ |
| 46 | `46_reci` | RECI红边叶绿素指数 | L3 | 可运行 | ✅ |
| 47 | `47_gndvi` | GNDVI绿色归一化植被指数 | L3 | 可运行 | ✅ |
| 48 | `48_osavi` | OSAVI优化土壤调节植被指数 | L3 | 可运行 | ✅ |
| 49 | `49_arvi` | ARVI耐大气植被指数 | L3 | 可运行 | ✅ |
| 50 | `50_vari` | VARI可见大气阻力指数 | L3 | 可运行 | ✅ |
| 51 | `51_lai_index` | 叶面积经验指数 | L3 | 可运行 | ✅ |
| 52 | `52_nbr` | NBR标准化燃烧率 | L3 | 可运行 | ✅ |
| 53 | `53_sipi` | SIPI结构不敏感色素指数 | L3 | 可运行 | ✅ |
| 54 | `54_gci` | GCI绿色叶绿素指数 | L3 | 可运行 | ✅ |
| 55 | `55_ndsi` | NDSI归一化差值雪指数 | L3 | 可运行 | ✅ |

## 逐项：算法介绍 + 调用命令

说明：下列 `curl` 均在 `algorithm/source` 下执行。介绍字段来自算法清单详表。

### 1. 航线规划与覆盖优化

- **一句话**：决定怎么飞才采得全
- **algorithm_id**：`01_flight_planning`
- **层级**：L0前
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 规划航高、重叠、航迹，保证测区采全、可拼接 |
| **使用场景** | 无人机起飞前；大田、园区、矿区测绘任务 |
| **数据输入** | 测区边界、DEM、相机参数、分辨率要求、禁飞区 |
| **数据输出** | 航线文件、航点列表、预估架次与时长 |
| **方法边界** | 当前只在测区外包矩形上铺直线往返航点，不处理 DEM、障碍、禁飞区、转弯动力学或飞控格式；理论 GSD 与简化航时不能替代可飞性审查。 |

- **主文件 file**：`algorithms/01_flight_planning/testdata/input.geojson`
- **第二文件 file2**：无
- **params**：`{"cruise_speed_m_s": 8}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/01_flight_planning/run" \
  -F "file=@algorithms/01_flight_planning/testdata/input.geojson" \
  -F 'params={"cruise_speed_m_s":8}'
```

### 2. 同步曝光与时间戳对齐

- **一句话**：多拍传感器时间对齐
- **algorithm_id**：`02_sync_timestamp`
- **层级**：L0
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 让高光谱、RGB、POS 在时间轴上对齐，避免「图对不上姿态」 |
| **使用场景** | 多传感器挂载同飞；后续几何与融合的前提 |
| **数据输入** | 各传感器时间戳、触发脉冲记录 |
| **数据输出** | 对齐后的帧-姿态对应表 |
| **方法边界** | 结果是无容差拒绝、无漂移模型的软件后处理配对，不代表 PPS/PTP 硬件同步；固定钟差与端点外推可能在长任务或快速运动中失效。 |

- **主文件 file**：`algorithms/02_sync_timestamp/testdata/input.json`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/02_sync_timestamp/run" \
  -F "file=@algorithms/02_sync_timestamp/testdata/input.json" \
  -F 'params={}'
```

### 3. POS轨迹平滑与杠杆臂校正

- **一句话**：平滑轨迹并改正安装偏移
- **algorithm_id**：`03_pos_solution`
- **层级**：L0
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 对已解算 POS CSV 做轨迹平滑与杠杆臂校正 |
| **使用场景** | 所有需要正射、镶嵌、上地图的飞行任务 |
| **数据输入** | 已解算 POS CSV（time,lat,lon,alt,roll,pitch,yaw） |
| **数据输出** | 平滑后的位置、姿态、速度与 gnss_ok 标志（JSON/CSV） |
| **方法边界** | 该服务不读取原始 IMU 比力或角速度，不是 GNSS/IMU 紧组合解算，也未提供 RTK 状态、协方差或可溯源精度评定。 |

- **主文件 file**：`algorithms/03_pos_solution/testdata/input.csv`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/03_pos_solution/run" \
  -F "file=@algorithms/03_pos_solution/testdata/input.csv" \
  -F 'params={}'
```

### 4. 架次过曝与场景统计质检

- **一句话**：过曝门控与场景统计
- **algorithm_id**：`04_flight_qc`
- **层级**：L0
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 统计过曝/欠曝比例与场景亮度，门控本架是否可进入后续处理 |
| **使用场景** | 落地后第一道关；光照突变、颠簸、存储异常时 |
| **数据输入** | L0 DN GeoTIFF，可选 bit_depth 与过曝比例阈值 |
| **数据输出** | 质检报告（过曝/欠曝比例、场景统计、通过/复飞建议） |
| **方法边界** | 全景 mean/std 混入地物组成和空间纹理，不能称为 EMVA 1288 传感器 SNR；服务也不检测丢帧、模糊、几何或定标质量。 |

- **主文件 file**：`algorithms/04_flight_qc/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"max_saturated_ratio": 0.01}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/04_flight_qc/run" \
  -F "file=@algorithms/04_flight_qc/testdata/input.tif" \
  -F 'params={"max_saturated_ratio":0.01}'
```

### 5. 云/云影检测

- **一句话**：遮挡区域打标
- **algorithm_id**：`05_cloud_shadow`
- **层级**：L0
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 识别云与阴影覆盖，避免当正常地物分析 |
| **使用场景** | 卫星与高空数据常见；低空偶发薄云/树影也可借鉴 |
| **数据输入** | L0/L1 多波段或 RGB |
| **数据输出** | 云/影掩膜（0/1 或概率图） |
| **方法边界** | 该实现无亮温、云概率、云对象、云高、太阳/观测几何与投影匹配，不能宣称完整 Fmask 或经几何确认的云影，暗水体、树影和地形阴影可能误报。 |

- **主文件 file**：`algorithms/05_cloud_shadow/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/05_cloud_shadow/run" \
  -F "file=@algorithms/05_cloud_shadow/testdata/input.tif" \
  -F 'params={}'
```

### 6. 暗电流校正

- **一句话**：去本底噪声
- **algorithm_id**：`06_dark_current`
- **层级**：L0→L1
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 减去传感器在无光时的本底，降低固定偏差 |
| **使用场景** | 高光谱相机预处理几乎标配 |
| **数据输入** | 原始 DN、暗电流参考帧 |
| **数据输出** | 去本底后的 DN |
| **方法边界** | 无匹配暗帧时的逐波段最小值可能移除真实暗地物；温度、曝光或增益不匹配会造成过扣/欠扣，截零还会隐藏负残差。 |

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

### 7. 坏线/坏像元修复

- **一句话**：修传感器缺陷
- **algorithm_id**：`07_bad_pixel`
- **层级**：L0→L1
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 修复探测器坏点、坏列，避免条纹伪影 |
| **使用场景** | 推扫相机老化或出厂缺陷 |
| **数据输入** | DN、坏像元表 |
| **数据输出** | 修复后 DN（插值或邻域填充） |
| **方法边界** | 单景统计可能把高对比边缘和小目标误判为缺陷；填充值不是独立观测，且本服务没有出厂坏元时序表或跨批次稳定性验证。 |

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

### 8. 条带噪声去除

- **一句话**：去推扫条纹
- **algorithm_id**：`08_destriping`
- **层级**：L0→L1
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 去除推扫方向周期性亮暗条纹 |
| **使用场景** | 机载/星载推扫高光谱常见问题 |
| **数据输入** | 校正中 DN 或辐亮度 |
| **数据输出** | 去条带影像 |
| **方法边界** | 矩匹配依赖各列观测到统计相似地物的假设；贯穿列的真实结构或列间地物组成差异可能被误校正，结果不是平场绝对响应标定。 |

- **主文件 file**：`algorithms/08_destriping/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/08_destriping/run" \
  -F "file=@algorithms/08_destriping/testdata/input.tif" \
  -F 'params={}'
```

### 9. 光谱微笑/关键畸变校正

- **一句话**：修光谱几何畸变
- **algorithm_id**：`09_smile_keystone`
- **层级**：L0→L1
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 校正光谱维与空间维耦合畸变，保证「同一波段真的是同一波长」 |
| **使用场景** | 精密定量与光谱库匹配前；高端机载/星载处理 |
| **数据输入** | 传感器模型、实验室光谱定标数据、DN/辐亮度 |
| **数据输出** | 光谱几何校正后的数据立方体 |
| **方法边界** | 结果是场景互相关估计的相对偏移，不是实验室标定偏移；弱纹理、相关峰歧义与两次插值会影响稳定性和光谱/空间细节。 |

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

- **一句话**：变成物理量
- **algorithm_id**：`10_radiance_calibration`
- **层级**：L0→L1
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 把仪器计数变成有单位的辐亮度，具备物理可比性 |
| **使用场景** | 定量遥感、跨传感器对比、进入大气校正前 |
| **数据输入** | 校正后 DN、定标系数、积分时间等元数据 |
| **数据输出** | L1 辐亮度产品（Radiance Cube/条带） |
| **方法边界** | 只有系数与设备、波段、曝光/增益模式及单位匹配时，输出才具有对应辐亮度意义；默认系数结果不得用于正式定量产品，线性转换也不等于反射率。 |

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

- **一句话**：不同架次亮度对齐
- **algorithm_id**：`11_relative_radiometric`
- **层级**：L1
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 消除不同架次光照、增益差异，使亮度可对比 |
| **使用场景** | 一天多架次、多日监测、镶嵌前匀光 |
| **数据输入** | 多景 L1/L2、重叠区或伪不变特征 |
| **数据输出** | 辐射一致化后的多景数据 |
| **方法边界** | 直方图匹配是轻量归一化而非物理辐射定标；未配准或地物组成不同会把场景差异写入映射，并可能压缩真实时相变化或形成处理边界接缝。 |

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

### 12. 白板/灰板反射率定标

- **一句话**：无人机常用变反射率
- **algorithm_id**：`12_panel_reflectance`
- **层级**：L1→L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 用地面参考板把辐亮度转为地表反射率（无人机最常用） |
| **使用场景** | 低空农情、植被指数、分类前；替代完整大气校正 |
| **数据输入** | 辐亮度、白板光谱/同步测量 |
| **数据输出** | 近似/地表 反射率立方体 |
| **方法边界** | 单板与自动亮端不能替代多目标 ELM、板证书光谱和照度/BRDF 控制。 |

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

- **一句话**：去大气影响（多用于星载）
- **algorithm_id**：`13_atmospheric_correction`
- **层级**：L1→L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 扣除大气吸收散射，得到更接近真实的地表反射率 |
| **使用场景** | 卫星高光谱、有人机高空；跨区域定量对比 |
| **数据输入** | 辐亮度、大气参数（水汽、气溶胶等） |
| **数据输出** | 地表反射率产品（常称 L2A 一类） |
| **方法边界** | COST 是一阶影像近似，不替代含气溶胶、水汽和现场大气参数的辐射传输校正。 |

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

- **一句话**：减弱观测角造成的明暗差
- **algorithm_id**：`14_brdf_correction`
- **层级**：L1→L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 减弱太阳-观测角度不同造成的「一边亮一边暗」 |
| **使用场景** | 宽视场航带边缘、多日多角度合成 |
| **数据输入** | 反射率、太阳/观测天顶角方位角 |
| **数据输出** | 角度归一后的反射率 |
| **方法边界** | 单景固定核权重和统一太阳角不等价于 MODIS 多角度反演，也不能保证跨地物定量准确。 |

- **主文件 file**：`algorithms/14_brdf_correction/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"solar_zenith": 30, "view_zenith": 10}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/14_brdf_correction/run" \
  -F "file=@algorithms/14_brdf_correction/testdata/input.tif" \
  -F 'params={"solar_zenith":30,"view_zenith":10}'
```

### 15. POS中心点与GSD粗定位

- **一句话**：像素落到大概坐标
- **algorithm_id**：`15_geo_locate`
- **层级**：L1→L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 以单个 POS 中心点与 GSD 写北向上仿射，不使用姿态 |
| **使用场景** | 正射前；快速预览落点 |
| **数据输入** | 影像条带、POS、相机内参 |
| **数据输出** | 带粗略地理参考的条带 |
| **方法边界** | 精密直接地理定位依赖同步 GPS/INS、完整外方位、相机标定和地面交会；该论文只作完整方法背景。 |

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

- **一句话**：消地形与姿态畸变
- **algorithm_id**：`16_orthorectify`
- **层级**：L1→L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 消除地形起伏与姿态引起的几何畸变，像素可准确落图 |
| **使用场景** | 要量面积、叠地块、做 GIS 的所有项目 |
| **数据输入** | 条带、POS、DEM、相机模型 |
| **数据输出** | 正射条带（Orthophoto / Ortho Cube） |
| **方法边界** | 当前实现没有空三/GCP、畸变模型、遮挡处理和真实地图格网。 |

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

- **一句话**：多航带拼成整景
- **algorithm_id**：`17_mosaic`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 多航带拼成测区完整一张图 |
| **使用场景** | 大田多航线飞行；生成整景 L2 |
| **数据输入** | 多条正射条带、重叠区 |
| **数据输出** | 整景反射率正射立方体（典型 L2 交付） |
| **方法边界** | 羽化不会修复错位、视差、移动目标或辐射差异；仓库也不搜索接缝线和处理 NoData 掩膜。 |

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

### 18. Wallis局部匀色

- **一句话**：改善局部亮度观感
- **algorithm_id**：`18_color_balance`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 逐波段 Wallis 局部匀光，不执行接缝线优化 |
| **使用场景** | 出图给客户看；镶嵌后美化 |
| **数据输入** | 镶嵌前多条带或初镶嵌图 |
| **数据输出** | 匀色后镶嵌产品 |
| **方法边界** | Wallis 是视觉增强而非物理辐射校正；逐波段应用可能改变光谱形状。 |

- **主文件 file**：`algorithms/18_color_balance/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/18_color_balance/run" \
  -F "file=@algorithms/18_color_balance/testdata/input.tif" \
  -F 'params={}'
```

### 19. HSI-RGB全局平移配准

- **一句话**：RGB 平移对齐 HSI
- **algorithm_id**：`19_multi_source_register`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 估计全局亚像元平移，把 RGB 对齐到 HSI |
| **使用场景** | 已粗对齐、仅剩平移差异的 HSI-RGB 栅格 |
| **数据输入** | HSI Cube、RGB 栅格 |
| **数据输出** | HSI 参考栅格与平移后的 RGB |
| **方法边界** | 单个全局平移不能处理旋转、尺度、透视、CRS 差异或局部形变。 |

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

### 20. 坏波段剔除

- **一句话**：清洗立方体
- **algorithm_id**：`20_bad_band_remove`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 去掉水汽强吸收等噪声波段，提升后续稳定 |
| **使用场景** | 分类/指数/反演前；1400、1900 nm 附近常剔除 |
| **数据输入** | L2 反射率 Cube |
| **数据输出** | 清洗后 Cube（波段数减少） |
| **方法边界** | HITRAN 谱线库不能为固定宽窗口、场景 μ/σ 阈值或坏波段结论直接背书。 |

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

- **一句话**：光谱平滑与特征增强
- **algorithm_id**：`21_savgol_smooth`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 平滑光谱噪声；包络线去除突出吸收特征 |
| **使用场景** | 矿物识别、精细光谱匹配、特征工程 |
| **数据输入** | 像素光谱或整景 Cube |
| **数据输出** | 平滑谱 / 去包络光谱特征 |
| **方法边界** | SG 不是包络线去除，窗口过大会削弱窄吸收峰；偶数窗口自动加一是仓库规则。 |

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

- **一句话**：给模型统一量纲
- **algorithm_id**：`22_normalize`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 统一数值范围，便于机器学习 |
| **使用场景** | 几乎所有 ML/DL 训练与推理前 |
| **数据输入** | Cube 或光谱向量 |
| **数据输出** | z-score / minmax 等标准化特征 |
| **方法边界** | 归一化改变物理量纲；当前整景 zscore/minmax 若在切分前拟合会引入数据泄漏。 |

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

- **一句话**：百波段压到几十维
- **algorithm_id**：`23_pca`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 压缩高度相关的上百波段，降冗余与噪声 |
| **使用场景** | 深度学习前、小样本、算力有限；本仓库部分模型内含 PCA |
| **数据输入** | 高维 Cube |
| **数据输出** | 低维特征立方体（如 10–40 维） |
| **方法边界** | 空间差分会把真实边缘混入噪声估计；单景现场拟合分量也不具有跨景固定语义。 |

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

- **一句话**：选出最有用的波段
- **algorithm_id**：`24_band_select`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 选出对任务最有区分力的波段或指数，而不是盲目全波段 |
| **使用场景** | 特定作物区分、传感器定波段、边缘设备轻量化 |
| **数据输入** | Cube +（可选）样区标签 |
| **数据输出** | 优选波段列表 / 特征表 |
| **方法边界** | 单变量 F 或方差不控制波段冗余；无效标签会静默退回方差法。 |

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

- **一句话**：按斑块而非纯像素分析
- **algorithm_id**：`25_superpixel`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 把影像切成均质小对象，再以对象为单位分类，减少椒盐噪声 |
| **使用场景** | 农田斑块、林斑；对象级分类前处理 |
| **数据输入** | L2 影像（可含 RGB） |
| **数据输出** | 超像素标签图 / 对象多边形 |
| **方法边界** | 前三原始光谱波段未必具有适合分割的尺度或边界信息，且不能借 CIELAB SLIC 论文声称颜色感知等价。 |

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

- **一句话**：切出训练推理小块
- **algorithm_id**：`26_patch_build`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 切出模型可训练、可推理的邻域立方体或光谱向量 |
| **使用场景** | CNN/Transformer 训练；本仓库常见 `createImageCubes` |
| **数据输入** | Cube、标签图、窗宽 |
| **数据输出** | 样本张量 `(N,W,W,B)` 或 `(N,B)` + 类别 |
| **方法边界** | 相邻中心 Patch 高度重叠，先全图构建再随机切分会造成严重空间泄漏；HybridSN 的 PCA 前置也不是本服务自动步骤。 |

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

- **一句话**：最常用长势指数
- **algorithm_id**：`27_ndvi`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 表征植被绿度、活力及冠层覆盖状况 |
| **使用场景** | 长势监测、物候；农情最通用指标 |
| **数据输入** | 反射率立方体（按索引取红光与近红外） |
| **数据输出** | NDVI 单波段图（约 −1～1） |
| **方法边界** | 高叶面积条件下 NDVI 容易饱和，对生物量增量敏感性下降；土壤、大气、云影和定标差异会影响数值，不能直接作为叶绿素含量或生物量定量产品。 |

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

- **一句话**：密冠层/氮相关
- **algorithm_id**：`28_ndre`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 利用红边对叶绿素更敏感，适合密冠层 |
| **使用场景** | 成熟期、氮营养相关监测；高光谱优势场景 |
| **数据输入** | 近红外、红边反射率 |
| **数据输出** | NDRE（或同类红边指数）图 |
| **方法边界** | 缺少真实红边通道、宽带内插或波长错配会使名称失去物理含义；指数不能直接换算叶绿素或氮含量。 |

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

- **一句话**：抑大气或土壤背景
- **algorithm_id**：`29_evi_savi`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 减轻大气干扰、土壤背景或 NDVI 饱和 |
| **使用场景** | 茂密冠层用 EVI；苗期稀疏用 SAVI/MSAVI |
| **数据输入** | NIR、RED，及 BLUE 或土壤因子 L |
| **数据输出** | 对应指数专题图 |
| **方法边界** | 三种指数的背景敏感性、值域和饱和行为不同；参数 L 与波段响应必须记录，不能把指数直接当作生物物理绝对量。 |

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

- **一句话**：水分与水体
- **algorithm_id**：`30_ndmi_ndwi`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 估计冠层水分或提取水体/淹田 |
| **使用场景** | 干旱、灌溉、湿地、农田积水 |
| **数据输入** | NIR+SWIR 或 GREEN+NIR/SWIR |
| **数据输出** | 水分/水体指数图 |
| **方法边界** | 同名水分/水体指数不可混用；无真实 SWIR 时 NDMI 与 MNDWI 不具备相应物理定义，阈值也不能跨场景直接复用。 |

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

- **一句话**：高光谱特色物候/胁迫特征
- **algorithm_id**：`31_red_edge_params`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 从连续光谱提取红边位置、吸收谷深度等参数 |
| **使用场景** | 物候、胁迫早期、高光谱相对多光谱的差异化能力 |
| **数据输入** | 连续反射率光谱 |
| **数据输出** | 参数栅格（如红边位置 nm） |
| **方法边界** | 宽带采样、错误波长轴、低信噪或分母接近零会使纳米级峰位不可信；REP 不是叶绿素含量。 |

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

- **一句话**：叶绿素、氮等连续量
- **algorithm_id**：`32_regression_inversion`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 把光谱映射为叶绿素、氮含量、含水率等连续生化量 |
| **使用场景** | 精准施肥、长势诊断；有地面化验样本时 |
| **数据输入** | 光谱/指数特征 + 地面真值（训练时） |
| **数据输出** | 连续量专题图（带物理单位） |
| **方法边界** | 同景像元随机拆分会产生空间泄漏；真值 NoData、外推、成分数和跨传感器域差异必须另行控制。 |

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

- **一句话**：不用化验估叶面积和叶绿素
- **algorithm_id**：`33_physical_inversion`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 不用化验图，一次给出叶面积和叶绿素两张图，用来分清是叶子少还是叶子黄 |
| **使用场景** | 已有反射率与采集几何，要看同一架次里哪里稀、哪里开始退绿 |
| **数据输入** | file=地表反射率立方体（非 DN）；wavelengths_nm；solar_zenith / view_zenith / relative_azimuth；n_lai、n_cab、best_frac、cost_method |
| **数据输出** | lai.tif 看密不密、cab.tif 看绿不绿、preview 只渲 LAI；lut_size、best_n、n_boundary_lai/cab 及全图均值 |
| **方法边界** | 土壤、叶倾角、叶片水和干物质仍固定，查找表不是全参数空间；未引入先验约束；边界命中不是可靠极值。 |

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

- **一句话**：传统像素分类
- **algorithm_id**：`34_svm_rf_classify`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 按像素判别作物/地物类别 |
| **使用场景** | 小样本基线、快速上线、可解释要求高；本仓库含此类 |
| **数据输入** | 光谱或降维特征 + 训练标签 |
| **数据输出** | 分类图 LabelMap；可算 OA/AA/Kappa |
| **方法边界** | 像元随机拆分仍有空间泄漏；背景也会被强制赋为已知类，且当前未做超参数搜索、未知类拒绝或概率校准。 |

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

- **一句话**：与光谱库比对识物
- **algorithm_id**：`35_spectral_matching`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 用光谱形状与标准光谱库比对识别物质 |
| **使用场景** | 矿物填图、已知光谱库的目标识别 |
| **数据输入** | 像素光谱、端元/光谱库 |
| **数据输出** | 匹配类别图或光谱角距离图 |
| **方法边界** | 当前无拒绝阈值，所有像元都会硬分类；最小角/散度不是概率，混合像元也不能由唯一类别充分描述。 |

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

### 36. 1D-CNN光谱分类

- **一句话**：沿光谱深度学习
- **algorithm_id**：`36_cnn1d_classify`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 沿光谱维自动提取特征做像素分类 |
| **使用场景** | 光谱可分性强、空间纹理弱的场景 |
| **数据输入** | 单像素光谱 `(B,)` |
| **数据输出** | 像素类别 / 全图分类图 |
| **方法边界** | 默认短训和像元随机拆分不能证明收敛或空间泛化；模型不使用空间邻域，RNN 仅是未实现差距。 |

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

- **一句话**：业界与论文主流分类
- **algorithm_id**：`37_cnn3d_classify`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 同时利用邻域空间与光谱，提高分类精度 |
| **使用场景** | 农田作物精细分类、城市地物一张图；业界与论文主流；本仓库核心 |
| **数据输入** | 邻域立方体 `(W,W,B)` |
| **数据输出** | 分类着色图（各类作物/地物） |
| **方法边界** | 重叠 patch 的随机拆分会严重泄漏空间邻域；当前缩小短训结构不是论文完整复现。 |

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

### 38. SpectralFormer光谱分类

- **一句话**：光谱序列分类
- **algorithm_id**：`38_transformer_classify`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 用注意力或图结构捕捉长程依赖，冲击更高精度 |
| **使用场景** | 复杂地物、大场景、研究型与高端产品 |
| **数据输入** | Patch / 超像素图结构特征 |
| **数据输出** | 像素或对象级分类图 |
| **方法边界** | 本仓库通道和层数缩小且短训；像元随机拆分会高估泛化，不能把它称为论文官方复现或 GCN。 |

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

### 39. SAM均值原型少样本分类

- **一句话**：少量支持样本分类
- **algorithm_id**：`39_few_shot_classify`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 标注很少或换了一个农场时仍能分类 |
| **使用场景** | 新区域快速部署、降低外业认种成本 |
| **数据输入** | 源域模型 + 目标域少量标签 Cube |
| **数据输出** | 目标场景分类图 |
| **方法边界** | 当前无可学习嵌入、源域预训练、迁移学习或未知类拒绝；随机支持集使单次结果不稳定。 |

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

### 40. 低NDVI种子ACE目标检测

- **一句话**：相对目标候选斑块
- **algorithm_id**：`40_detect_segment`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 用低 NDVI 种子构造目标光谱，以 ACE 得分找出候选斑块 |
| **使用场景** | 植保巡田、精准喷药；常融合 RGB |
| **数据输入** | 反射率立方体、红/近红外波段索引、分位数与最小斑块参数 |
| **数据输出** | ACE 得分图、候选掩膜、GeoJSON 斑块 |
| **方法边界** | 高 ACE 仅表示与构造目标方向相似，不是概率或已确认类别；百分位只对本景有效，语义分割网络未实现。 |

#### 当前示例数据说明

- **解决什么问题**：植保场景需要知道「病斑/胁迫/杂草在哪一块」，而不是整幅只给出作物类别。本示例演示：从多波段反射率立方体中自动找出低长势斑块，并输出可上图的掩膜与矢量边界，便于后续人工复核或作为空间筛查输入。
- **本示例输入什么**：
  - `file` → `input.tif`：模拟 **16×16×8** 波段反射率 GeoTIFF（EPSG:4326）
  - 左半区为较高 NDVI 植被；在像素窗 `[行 4:10, 列 2:8]` 人为写入一块低 NDVI「胁迫斑」（压低近红外、抬高红光）
  - `file2` → `file2.geojson`：可选标注/AOI（属性 `label=weed`），接口会记录路径与要素数，不强制参与阈值
  - `params`：`red_band=2`、`nir_band=3` 算 NDVI；`percentile=20` 取低值阈值；`min_pixels=4` 剔除碎斑
- **本示例输出什么**：
  - `files.score_tif`：检测得分图（NDVI 低于阈值的程度）
  - `files.mask_tif`：二值分割掩膜（1=候选斑块）
  - `files.polygons_geojson`：连通斑块多边形（含 `object_id`、`area_pixels`）
  - `files.preview_png`：得分预览图
  - `data`：阈值、斑块数 `n_objects`、阳性像素数等；当前样例通常约 **1 个斑块 / 数十像素**

- **主文件 file**：`algorithms/40_detect_segment/testdata/input.tif`
- **第二文件 file2**：`algorithms/40_detect_segment/testdata/file2.geojson`
- **params**：`{"red_band": 2, "nir_band": 3, "percentile": 20, "min_pixels": 4}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/40_detect_segment/run" \
  -F "file=@algorithms/40_detect_segment/testdata/input.tif" \
  -F "file2=@algorithms/40_detect_segment/testdata/file2.geojson" \
  -F 'params={"red_band":2,"nir_band":3,"percentile":20,"min_pixels":4}'
```

### 41. 混合像元分解

- **一句话**：像素内各类占比
- **algorithm_id**：`41_unmixing`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 一个像素里有多种物质时，估计各类占地比例 |
| **使用场景** | 分辨率不够细、混种、稀疏植被、矿物丰度填图 |
| **数据输入** | 混合光谱、端元库或自动端元 |
| **数据输出** | 各类丰度图（0～1 连续） |
| **方法边界** | 线性混合、端元完整性与矩阵条件数限制可辨识性；丰度不必等于面积、质量或产量比例。 |

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

- **一句话**：找「不像周围」的点
- **algorithm_id**：`42_anomaly_detect`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 找出光谱上「不像周围大部分」的像元 |
| **使用场景** | 病虫害爆发点、污染点、未知目标初筛 |
| **数据输入** | 单时相 Cube |
| **数据输出** | 异常得分图 / 告警点位 |
| **方法边界** | 异常高分不是已命名类别；云影、饱和、坏波段与小样本协方差不稳都会制造伪异常。 |

#### 当前示例数据说明

- **解决什么问题**：无充分标注时，需要先找出光谱上「不像周围大多数」的像元，用于病虫害爆发点、污染点等初筛告警。
- **本示例输入什么**：
  - `file` → `input.tif`：模拟多波段反射率 GeoTIFF（16×16×8）
  - `params`：`percentile=95` 将高 RX 得分判为异常；`min_pixels=2` 去掉过小噪点
- **本示例输出什么**：
  - `files.score_tif`：RX 异常得分图
  - `files.mask_tif`：告警二值掩膜
  - `files.preview_png`：预览图
  - `data`：阈值、异常像素数、得分统计

- **主文件 file**：`algorithms/42_anomaly_detect/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"percentile": 95, "min_pixels": 2}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/42_anomaly_detect/run" \
  -F "file=@algorithms/42_anomaly_detect/testdata/input.tif" \
  -F 'params={"percentile":95,"min_pixels":2}'
```

### 43. 多时相变化检测

- **一句话**：前后对比找变化
- **algorithm_id**：`43_change_detect`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 对比两个或多个时相，找出变化区域 |
| **使用场景** | 灾损、砍伐、作物轮作、施工占地 |
| **数据输入** | 配准后的多时相 L2/L3 |
| **数据输出** | 变化掩膜、变化类型图 |
| **方法边界** | 错位、云影、物候与观测差异会形成假变化；输出只表示统计变化，不给出原因或灾损等级。 |

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

- **一句话**：图更好看更稳
- **algorithm_id**：`44_postprocess_smooth`
- **层级**：L3→L4
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 去掉椒盐噪声与过小斑块，使结果符合地物连续性 |
| **使用场景** | 像素分类出图前；验收图美化 |
| **数据输入** | 原始 LabelMap |
| **数据输出** | 平滑后的分类图、更干净的作物斑块 |
| **方法边界** | 平滑会吞并细线、小目标和边界，视觉整齐不代表分类精度提高；官方工具仅支持操作类型，不背书仓库具体组合。 |

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

- **一句话**：领导/客户最终交付
- **algorithm_id**：`45_parcel_zonal_stats`
- **层级**：L4
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 把像素结果变成「人能拍板」的亩数、占比、告警和建议 |
| **使用场景** | 领导汇报、农事 App、补贴核对、产量预估输入 |
| **数据输入** | L3 分类图/指数图 + 地块矢量 + 阈值规则 |
| **数据输出** | 面积表、地块 JSON、着色专题图、shp 斑块、告警列表、API |
| **方法边界** | 模式错配、NoData 元数据错误、NaN、CRS/栅格化边界规则会改变统计口径；空有效区不得解释为 0。 |

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

### 46. RECI红边叶绿素指数

- **一句话**：红边叶绿素相对指数
- **algorithm_id**：`46_reci`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 用近红外与红边比值减 1 表征叶绿素相关相对差异 |
| **使用场景** | 密冠层叶绿素相关对照；须有真红边 |
| **数据输入** | 反射率立方体（红边、近红外） |
| **数据输出** | 单波段 reci.tif |
| **方法边界** | 必须使用真实红边通道；不能把 RECI 直接当作叶绿素含量。 |

- **主文件 file**：`algorithms/46_reci/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"re_band": 4, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/46_reci/run" \
  -F "file=@algorithms/46_reci/testdata/input.tif" \
  -F 'params={"re_band":4,"nir_band":3}'
```

### 47. GNDVI绿色归一化植被指数

- **一句话**：绿光归一化绿度
- **algorithm_id**：`47_gndvi`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 用绿光代替红光做归一化差 |
| **使用场景** | 绿光通道的相对绿度 |
| **数据输入** | 反射率立方体（绿光、近红外） |
| **数据输出** | 单波段 gndvi.tif |
| **方法边界** | 绿光窗口依传感器而定；不能直接当作叶绿素含量；高覆盖时仍可能饱和。 |

- **主文件 file**：`algorithms/47_gndvi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"green_band": 1, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/47_gndvi/run" \
  -F "file=@algorithms/47_gndvi/testdata/input.tif" \
  -F 'params={"green_band":1,"nir_band":3}'
```

### 48. OSAVI优化土壤调节植被指数

- **一句话**：固定土壤项 L=0.16
- **algorithm_id**：`48_osavi`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 在 NDVI 分母上加固定土壤项 |
| **使用场景** | 稀疏植被、土壤背景明显时的相对绿度 |
| **数据输入** | 反射率立方体（红光、近红外）与 L |
| **数据输出** | 单波段 osavi.tif |
| **方法边界** | L=0.16 不是现场标定；改 L 后不能与未改的图横比；不能直接当作叶面积或产量。 |

- **主文件 file**：`algorithms/48_osavi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"red_band": 2, "nir_band": 3, "L": 0.16}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/48_osavi/run" \
  -F "file=@algorithms/48_osavi/testdata/input.tif" \
  -F 'params={"red_band":2,"nir_band":3,"L":0.16}'
```

### 49. ARVI耐大气植被指数

- **一句话**：蓝光修正红光
- **algorithm_id**：`49_arvi`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 用蓝光修正红光后再做归一化差 |
| **使用场景** | 气溶胶残差可见时的相对绿度对照 |
| **数据输入** | 反射率立方体（蓝、红、近红外）与 γ |
| **数据输出** | 单波段 arvi.tif |
| **方法边界** | ARVI 不能替代大气校正产品；蓝光差或阴影重时指数会乱。 |

- **主文件 file**：`algorithms/49_arvi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"blue_band": 0, "red_band": 2, "nir_band": 3, "gamma": 1.0}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/49_arvi/run" \
  -F "file=@algorithms/49_arvi/testdata/input.tif" \
  -F 'params={"blue_band":0,"red_band":2,"nir_band":3,"gamma":1.0}'
```

### 50. VARI可见大气阻力指数

- **一句话**：只用可见光估覆盖
- **algorithm_id**：`50_vari`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 只用可见光三通道估相对覆盖 |
| **使用场景** | 没有近红外时的相对覆盖示意 |
| **数据输入** | 反射率立方体（蓝、绿、红） |
| **数据输出** | 单波段 vari.tif |
| **方法边界** | 没有近红外不等于能替代 NDVI；分母可能接近零；不能直接写成覆盖度百分比。 |

- **主文件 file**：`algorithms/50_vari/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"blue_band": 0, "green_band": 1, "red_band": 2}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/50_vari/run" \
  -F "file=@algorithms/50_vari/testdata/input.tif" \
  -F 'params={"blue_band":0,"green_band":1,"red_band":2}'
```

### 51. 叶面积经验指数

- **一句话**：EVI 线性式，不是 #33
- **algorithm_id**：`51_lai_index`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 由 EVI 线性变换得到教学叶面积指数 |
| **使用场景** | 指数菜单里的经验 LAI 示意；不是 #33 |
| **数据输入** | 反射率立方体（蓝、红、近红外） |
| **数据输出** | 单波段 lai_index.tif |
| **方法边界** | 该线性式不是全球 LAI 产品，也不是 #33 PROSAIL；负值被裁成 0 不表示真实零叶面积。 |

- **主文件 file**：`algorithms/51_lai_index/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"blue_band": 0, "red_band": 2, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/51_lai_index/run" \
  -F "file=@algorithms/51_lai_index/testdata/input.tif" \
  -F 'params={"blue_band":0,"red_band":2,"nir_band":3}'
```

### 52. NBR标准化燃烧率

- **一句话**：过火相对差异
- **algorithm_id**：`52_nbr`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 近红外与短波红外归一化差，用于过火相对差异 |
| **使用场景** | 过火前后对照；须有真 SWIR |
| **数据输入** | 反射率立方体（近红外、短波红外） |
| **数据输出** | 单波段 nbr.tif |
| **方法边界** | 必须有真实 SWIR；Landsat NBR 常用 SWIR2 约 2.1 μm，与教学约 1600 nm 不能混比；不能直接写成过火面积。 |

- **主文件 file**：`algorithms/52_nbr/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"nir_band": 3, "swir_band": 5}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/52_nbr/run" \
  -F "file=@algorithms/52_nbr/testdata/input.tif" \
  -F 'params={"nir_band":3,"swir_band":5}'
```

### 53. SIPI结构不敏感色素指数

- **一句话**：色素比值相对指数
- **algorithm_id**：`53_sipi`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 色素比值相关、对冠层结构相对不敏感的相对指数 |
| **使用场景** | 色素相对对照 |
| **数据输入** | 反射率立方体（蓝、红、近红外） |
| **数据输出** | 单波段 sipi.tif |
| **方法边界** | NIR 接近 RED 时分母接近零；不能直接当作类胡萝卜素或叶绿素含量。 |

- **主文件 file**：`algorithms/53_sipi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"blue_band": 0, "red_band": 2, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/53_sipi/run" \
  -F "file=@algorithms/53_sipi/testdata/input.tif" \
  -F 'params={"blue_band":0,"red_band":2,"nir_band":3}'
```

### 54. GCI绿色叶绿素指数

- **一句话**：绿光叶绿素相对指数
- **algorithm_id**：`54_gci`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 近红外与绿光比值减 1 |
| **使用场景** | 无红边时的叶绿素相关相对对照 |
| **数据输入** | 反射率立方体（绿光、近红外） |
| **数据输出** | 单波段 gci.tif |
| **方法边界** | 与 RECI 同型但分母是绿光；不能直接当作叶绿素含量。 |

- **主文件 file**：`algorithms/54_gci/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"green_band": 1, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/54_gci/run" \
  -F "file=@algorithms/54_gci/testdata/input.tif" \
  -F 'params={"green_band":1,"nir_band":3}'
```

### 55. NDSI归一化差值雪指数

- **一句话**：积雪相对指数，不是水
- **algorithm_id**：`55_ndsi`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 绿光与短波红外归一化差，用于积雪相对识别 |
| **使用场景** | 积雪相对格局；不是水体 |
| **数据输入** | 反射率立方体（绿光、短波红外） |
| **数据输出** | 单波段 ndsi.tif |
| **方法边界** | 与 MNDWI 公式同型但用途是雪不是水；本仓库不输出积雪二值图；无真实 SWIR 时无物理意义。 |

- **主文件 file**：`algorithms/55_ndsi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"green_band": 1, "swir_band": 5}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/55_ndsi/run" \
  -F "file=@algorithms/55_ndsi/testdata/input.tif" \
  -F 'params={"green_band":1,"swir_band":5}'
```

## 批量冒烟（可选）

服务已启动后，在 `algorithm/source` 执行：

```bash
./scripts/smoke_all_algorithms.sh
```

## 期望结果速查

| 状态 | 期望 |
|------|------|
| 可运行 | `success=true`，`data` 有统计/指标，`files` 含 `.tif` 等产物路径 |
| 骨架 | 接口 200，正文标明未实现或 `implemented=false`；不应 500 |

可运行清单：`01_flight_planning`、`02_sync_timestamp`、`03_pos_solution`、`04_flight_qc`、`05_cloud_shadow`、`06_dark_current`、`07_bad_pixel`、`08_destriping`、`09_smile_keystone`、`10_radiance_calibration`、`11_relative_radiometric`、`12_panel_reflectance`、`13_atmospheric_correction`、`14_brdf_correction`、`15_geo_locate`、`16_orthorectify`、`17_mosaic`、`18_color_balance`、`19_multi_source_register`、`20_bad_band_remove`、`21_savgol_smooth`、`22_normalize`、`23_pca`、`24_band_select`、`25_superpixel`、`26_patch_build`、`27_ndvi`、`28_ndre`、`29_evi_savi`、`30_ndmi_ndwi`、`31_red_edge_params`、`32_regression_inversion`、`33_physical_inversion`、`34_svm_rf_classify`、`35_spectral_matching`、`36_cnn1d_classify`、`37_cnn3d_classify`、`38_transformer_classify`、`39_few_shot_classify`、`40_detect_segment`、`41_unmixing`、`42_anomaly_detect`、`43_change_detect`、`44_postprocess_smooth`、`45_parcel_zonal_stats`、`46_reci`、`47_gndvi`、`48_osavi`、`49_arvi`、`50_vari`、`51_lai_index`、`52_nbr`、`53_sipi`、`54_gci`、`55_ndsi`

介绍来源：[采集到算法-算法清单.md](./采集到算法-算法清单.md)（由 catalog/evidence 同步生成）
