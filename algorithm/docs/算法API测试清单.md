# 算法 API 测试清单（45 项）

> 格式对齐培训 PPT「对接示例」：`POST /api/v1/{algorithm_id}/run` + `file` / `file2` / `params`。
>
> 工作目录请先进入：`algorithm/source`（样例路径按此相对路径书写）。
>
> **算法介绍**（作用 / 使用场景 / 数据输入 / 数据输出）已与 [采集到算法-算法清单.md](./采集到算法-算法清单.md) 同步。

## 最近一次自动测试结果

- **时间**：2026-08-19 17:51:49
- **HOST**：`http://127.0.0.1:28800`
- **命令**：生产级实现后 `scripts/smoke_all_implemented.py`（curl 冒烟）
- **汇总**：HTTP 200 = **45/45**；`success=true` = **45/45**
- **可运行且产出 files**：**45/45**

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

## 使用说明

1. 启动服务：`./scripts/start.sh`（默认 `http://127.0.0.1:28800`）
2. 健康检查：`curl -s http://127.0.0.1:28800/api/v1/algorithms | python -m json.tool | head`
3. 按下列命令逐项测试；全部 45 项均为**可运行**：应返回 `success=true`、`implemented=true` 与 `files` 产物路径
4. 每项含算法介绍 + curl；勾选列供联调/验收打钩

## 总览勾选表

| # | 算法 ID | 标题 | 层级 | 状态 | 通过 |
|---|---------|------|------|------|------|
| 01 | `01_flight_planning` | 航线规划与覆盖优化 | L0前 | 可运行 | ✅ |
| 02 | `02_sync_timestamp` | 同步曝光与时间戳对齐 | L0 | 可运行 | ✅ |
| 03 | `03_pos_solution` | POS解算（GPS+IMU） | L0 | 可运行 | ✅ |
| 04 | `04_flight_qc` | 架次质检（丢帧/过曝） | L0 | 可运行 | ✅ |
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
| 15 | `15_geo_locate` | 几何粗校正/地理定位 | L1→L2 | 可运行 | ✅ |
| 16 | `16_orthorectify` | 正射校正 | L1→L2 | 可运行 | ✅ |
| 17 | `17_mosaic` | 影像匹配与镶嵌 | L2 | 可运行 | ✅ |
| 18 | `18_color_balance` | 匀色与接缝线优化 | L2 | 可运行 | ✅ |
| 19 | `19_multi_source_register` | 多源配准 HSI-RGB-矢量 | L2 | 可运行 | ✅ |
| 20 | `20_bad_band_remove` | 坏波段剔除与光谱去噪 | L2 | 可运行 | ✅ |
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
| 36 | `36_cnn1d_classify` | 1D-CNN/RNN光谱分类 | L3 | 可运行 | ✅ |
| 37 | `37_cnn3d_classify` | 2D/3D-CNN空谱分类 | L3 | 可运行 | ✅ |
| 38 | `38_transformer_classify` | Transformer/GCN分类 | L3 | 可运行 | ✅ |
| 39 | `39_few_shot_classify` | 少样本/迁移学习分类 | L3 | 可运行 | ✅ |
| 40 | `40_detect_segment` | 语义分割/目标检测 | L3 | 可运行 | ✅ |
| 41 | `41_unmixing` | 混合像元分解 | L3 | 可运行 | ✅ |
| 42 | `42_anomaly_detect` | 异常检测 | L3 | 可运行 | ✅ |
| 43 | `43_change_detect` | 多时相变化检测 | L3 | 可运行 | ✅ |
| 44 | `44_postprocess_smooth` | 分类后处理平滑/小斑剔除 | L3→L4 | 可运行 | ✅ |
| 45 | `45_parcel_zonal_stats` | 地块汇总与专题统计 | L4 | 可运行 | ✅ |

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

- **主文件 file**：`algorithms/02_sync_timestamp/testdata/input.json`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/02_sync_timestamp/run" \
  -F "file=@algorithms/02_sync_timestamp/testdata/input.json" \
  -F 'params={}'
```

### 3. POS 解算（GPS + IMU）

- **一句话**：算出位置和姿态
- **algorithm_id**：`03_pos_solution`
- **层级**：L0
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 算出每帧/每条带的位置与姿态（POS）；IMU 提供姿态与加速度 |
| **使用场景** | 所有需要正射、镶嵌、上地图的飞行任务 |
| **数据输入** | GPS 轨迹、IMU 角速度/加速度、可选基站差分 |
| **数据输出** | 逐帧位置 (x,y,z) + 姿态角（俯仰/横滚/航向） |

- **主文件 file**：`algorithms/03_pos_solution/testdata/input.csv`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/03_pos_solution/run" \
  -F "file=@algorithms/03_pos_solution/testdata/input.csv" \
  -F 'params={}'
```

### 4. 架次质检（丢帧 / 过曝 / 欠曝）

- **一句话**：坏数据先拦下
- **algorithm_id**：`04_flight_qc`
- **层级**：L0
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 判断本架原始数据是否可用，避免垃圾进管线 |
| **使用场景** | 落地后第一道关；光照突变、颠簸、存储异常时 |
| **数据输入** | L0 DN、曝光增益日志、POS 完整性 |
| **数据输出** | 质检报告、坏帧列表、重飞建议 |

- **主文件 file**：`algorithms/04_flight_qc/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"max_saturated_ratio": 0.01}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/04_flight_qc/run" \
  -F "file=@algorithms/04_flight_qc/testdata/input.tif" \
  -F 'params={"max_saturated_ratio":0.01}'
```

### 5. 云 / 云影检测

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

### 7. 坏线 / 坏像元修复

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

- **主文件 file**：`algorithms/08_destriping/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/08_destriping/run" \
  -F "file=@algorithms/08_destriping/testdata/input.tif" \
  -F 'params={}'
```

### 9. 光谱微笑 / 关键畸变校正（Smile / Keystone）

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

- **主文件 file**：`algorithms/09_smile_keystone/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/09_smile_keystone/run" \
  -F "file=@algorithms/09_smile_keystone/testdata/input.tif" \
  -F 'params={}'
```

### 10. 辐射定标（DN → 辐亮度）

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

- **主文件 file**：`algorithms/10_radiance_calibration/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"gain": 0.01, "offset": 0.0}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/10_radiance_calibration/run" \
  -F "file=@algorithms/10_radiance_calibration/testdata/input.tif" \
  -F 'params={"gain":0.01,"offset":0.0}'
```

### 11. 相对辐射归一（多架次 / 多时相）

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

### 12. 白板 / 灰板反射率定标（经验线法）

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

- **主文件 file**：`algorithms/13_atmospheric_correction/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/13_atmospheric_correction/run" \
  -F "file=@algorithms/13_atmospheric_correction/testdata/input.tif" \
  -F 'params={}'
```

### 14. BRDF / 观测几何校正

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

- **主文件 file**：`algorithms/14_brdf_correction/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"solar_zenith": 30, "view_zenith": 10}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/14_brdf_correction/run" \
  -F "file=@algorithms/14_brdf_correction/testdata/input.tif" \
  -F 'params={"solar_zenith":30,"view_zenith":10}'
```

### 15. 几何粗校正 / 地理定位

- **一句话**：像素落到大概坐标
- **algorithm_id**：`15_geo_locate`
- **层级**：L1→L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 依据 POS 与相机模型，给影像赋予初始地理坐标 |
| **使用场景** | 正射前；快速预览落点 |
| **数据输入** | 影像条带、POS、相机内参 |
| **数据输出** | 带粗略地理参考的条带 |

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

- **一句话**：拼接更自然
- **algorithm_id**：`18_color_balance`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 消除拼接接缝处色差与硬边，提高可读性 |
| **使用场景** | 出图给客户看；镶嵌后美化 |
| **数据输入** | 镶嵌前多条带或初镶嵌图 |
| **数据输出** | 匀色后镶嵌产品 |

- **主文件 file**：`algorithms/18_color_balance/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/18_color_balance/run" \
  -F "file=@algorithms/18_color_balance/testdata/input.tif" \
  -F 'params={}'
```

### 19. 多源配准（高光谱 ↔ RGB ↔ 地块矢量）

- **一句话**：人看图、算法吃谱、按地块裁
- **algorithm_id**：`19_multi_source_register`
- **层级**：L2
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 让光谱、真彩色、田块边界对齐，便于标注与按地块统计 |
| **使用场景** | 「人看 RGB、算法吃 HSI、报表按地块」的标准业务 |
| **数据输入** | HSI Cube、RGB 正射、shp/geojson |
| **数据输出** | 共配准多层数据（同一网格/坐标系） |

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

- **主文件 file**：`algorithms/20_bad_band_remove/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"drop_bands": [0, 5]}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/20_bad_band_remove/run" \
  -F "file=@algorithms/20_bad_band_remove/testdata/input.tif" \
  -F 'params={"drop_bands":[0,5]}'
```

### 21. Savitzky–Golay 平滑 / 包络线去除

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

- **主文件 file**：`algorithms/21_savgol_smooth/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"window_length": 5, "polyorder": 2}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/21_savgol_smooth/run" \
  -F "file=@algorithms/21_savgol_smooth/testdata/input.tif" \
  -F 'params={"window_length":5,"polyorder":2}'
```

### 22. 标准化 / 归一化

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

- **主文件 file**：`algorithms/22_normalize/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"method": "zscore"}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/22_normalize/run" \
  -F "file=@algorithms/22_normalize/testdata/input.tif" \
  -F 'params={"method":"zscore"}'
```

### 23. 降维（PCA / MNF / ICA）

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

- **主文件 file**：`algorithms/23_pca/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"n_components": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/23_pca/run" \
  -F "file=@algorithms/23_pca/testdata/input.tif" \
  -F 'params={"n_components":3}'
```

### 24. 波段选择 / 特征选择

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

### 25. 超像素 / 面向对象分割

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

- **主文件 file**：`algorithms/25_superpixel/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"n_segments": 20}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/25_superpixel/run" \
  -F "file=@algorithms/25_superpixel/testdata/input.tif" \
  -F 'params={"n_segments":20}'
```

### 26. Patch / 样本构建

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

### 27. NDVI（归一化植被指数）

- **一句话**：最常用长势指数
- **algorithm_id**：`27_ndvi`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 快速表征植被绿度与光合活性 |
| **使用场景** | 长势监测、物候；农情最通用指标 |
| **数据输入** | 红光、近红外反射率 |
| **数据输出** | NDVI 单波段图（约 −1～1） |

- **主文件 file**：`algorithms/27_ndvi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"red_band": 2, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/27_ndvi/run" \
  -F "file=@algorithms/27_ndvi/testdata/input.tif" \
  -F 'params={"red_band":2,"nir_band":3}'
```

### 28. NDRE / 红边植被指数

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

- **主文件 file**：`algorithms/28_ndre/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"re_band": 4, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/28_ndre/run" \
  -F "file=@algorithms/28_ndre/testdata/input.tif" \
  -F 'params={"re_band":4,"nir_band":3}'
```

### 29. EVI / SAVI / MSAVI（改进植被指数）

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

- **主文件 file**：`algorithms/29_evi_savi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"blue_band": 0, "red_band": 2, "nir_band": 3}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/29_evi_savi/run" \
  -F "file=@algorithms/29_evi_savi/testdata/input.tif" \
  -F 'params={"blue_band":0,"red_band":2,"nir_band":3}'
```

### 30. NDMI / NDWI / MNDWI（水分与水体指数）

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

- **主文件 file**：`algorithms/30_ndmi_ndwi/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"green_band": 1, "nir_band": 3, "swir_band": 5}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/30_ndmi_ndwi/run" \
  -F "file=@algorithms/30_ndmi_ndwi/testdata/input.tif" \
  -F 'params={"green_band":1,"nir_band":3,"swir_band":5}'
```

### 31. 红边位置与光谱特征参数提取

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

- **主文件 file**：`algorithms/31_red_edge_params/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/31_red_edge_params/run" \
  -F "file=@algorithms/31_red_edge_params/testdata/input.tif" \
  -F 'params={}'
```

### 32. 经验回归反演（PLS / 随机森林 / 神经网络等）

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

### 33. 辐射传输物理模型反演

- **一句话**：机理法反演 LAI 等
- **algorithm_id**：`33_physical_inversion`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 用冠层辐射传输机理反演 LAI、叶绿素等 |
| **使用场景** | 高精度定量科研与业务；成本高于简单指数 |
| **数据输入** | 反射率、模型先验参数 |
| **数据输出** | 物理参数图（如 LAI） |

- **主文件 file**：`algorithms/33_physical_inversion/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/33_physical_inversion/run" \
  -F "file=@algorithms/33_physical_inversion/testdata/input.tif" \
  -F 'params={}'
```

### 34. 传统机器学习分类（SVM / 随机森林 / 逻辑回归）

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

### 35. 光谱匹配分类（如 SAM 光谱角制图）

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

### 36. 光谱深度学习分类（1D-CNN / RNN）

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

### 37. 空–谱 CNN 分类（2D/3D-CNN）

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

### 38. Transformer / GCN 等现代分类网络

- **一句话**：复杂场景高精度分类
- **algorithm_id**：`38_transformer_classify`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 用注意力或图结构捕捉长程依赖，冲击更高精度 |
| **使用场景** | 复杂地物、大场景、研究型与高端产品 |
| **数据输入** | Patch / 超像素图结构特征 |
| **数据输出** | 像素或对象级分类图 |

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

### 39. 少样本 / 迁移学习分类

- **一句话**：标注少也能上线
- **algorithm_id**：`39_few_shot_classify`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 标注很少或换了一个农场时仍能分类 |
| **使用场景** | 新区域快速部署、降低外业认种成本 |
| **数据输入** | 源域模型 + 目标域少量标签 Cube |
| **数据输出** | 目标场景分类图 |

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

### 40. 语义分割 / 目标检测（病斑、杂草等）

- **一句话**：病斑、杂草斑块
- **algorithm_id**：`40_detect_segment`
- **层级**：L3
- **状态**：可运行

| 项 | 内容 |
|----|------|
| **作用** | 找出病变、杂草等目标的位置与边界，而不是整幅填类别 |
| **使用场景** | 植保巡田、精准喷药；常融合 RGB |
| **数据输入** | Cube 和/或 RGB、框/掩膜标注 |
| **数据输出** | 检测框、分割掩膜、斑块矢量（shp） |

#### 当前示例数据说明

- **解决什么问题**：植保场景需要知道「病斑/胁迫/杂草在哪一块」，而不是整幅只给出作物类别。本示例演示：从多波段反射率立方体中自动找出低长势斑块，并输出可上图的掩膜与矢量边界，便于后续精准喷药或人工复核。
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

### 41. 混合像元分解（端元提取 + 丰度反演）

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

### 44. 分类后处理（形态学滤波 / CRF / 小斑剔除）

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

- **主文件 file**：`algorithms/44_postprocess_smooth/testdata/input.tif`
- **第二文件 file2**：无
- **params**：`{"min_pixels": 4}`
- **测试结果**：✅ 通过（自动冒烟 200 + success）

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/44_postprocess_smooth/run" \
  -F "file=@algorithms/44_postprocess_smooth/testdata/input.tif" \
  -F 'params={"min_pixels":4}'
```

### 45. 地块汇总、专题制图与业务告警（L4 核心）

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
./scripts/smoke_all_implemented.py
# 或仅检查 HTTP 200：
./scripts/smoke_all_algorithms.sh
```

## 期望结果速查

| 状态 | 期望 |
|------|------|
| 可运行 | `success=true`，`implemented=true`，`data` 有统计/指标，`files` 含产物路径 |

可运行清单：全部 45 项（`01_flight_planning` … `45_parcel_zonal_stats`）

介绍来源：[采集到算法-算法清单.md](./采集到算法-算法清单.md)（同步生成于 2026-08-19 17:27）
