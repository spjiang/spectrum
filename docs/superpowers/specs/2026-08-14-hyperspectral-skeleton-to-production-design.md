# 33 项骨架算法升级为生产级实现 — 设计规格

**日期：** 2026-08-14  
**状态：** 待用户审阅  
**依据：** `algorithm/docs/采集到算法-算法清单.md`、`algorithm/docs/算法API测试清单.md`、现有 12 项可运行实现

---

## 1. 目标

将 API 测试清单中全部 **33 项骨架算法**升级为可联调、可验收的**生产级实现**，最终达到：

- **45/45** 项 `HTTP 200`、`success=true`、`implemented=true`、`files` 非空
- 测试清单中不再保留「骨架」口径
- 用户可按 `算法API测试清单.md` 中的 curl **逐项验证**

## 2. 已确认决策

| 决策点 | 结论 |
|--------|------|
| 质量底线 | 与现有 12 项可运行对齐（统一 IO/响应/testdata） |
| 质量上限 | **全部 33 项都必须达到生产级**（不是只升级重点项） |
| 交付节奏 | **方案 C：分波交付，每波直接生产级** |
| 技术栈上限 | 在 FastAPI + numpy/scipy/sklearn/rasterio/torch（及必要轻量增补）内实现；不假装完整商用处理中心 |

## 3. 生产级定义（本仓库）

每项算法必须同时满足：

1. **真实算法逻辑**：禁止 `stub_response` / `implemented=false`
2. **契约完整**：`success=true`、`implemented=true`、`files` 含可读产物路径
3. **业界 I/O**：主路径 GeoTIFF / CSV / GeoJSON / JSON（按算法类型）
4. **参数与错误**：非法 JSON、缺 file2、波段越界等返回明确 `err_response`
5. **方法可陈述**：响应 `message`/`data` 标明所用方法名与适用边界
6. **可复现**：目录内 `testdata` + 测试清单 curl 可跑通
7. **工程一致**：复用 `common/io.py`、`common/response.py`；中文注释；不破坏现有 12 项行为

### 3.1 诚实边界（仍算生产实现，但写明限制）

| 算法类型 | 本仓库生产实现 | 明确不做 |
|----------|----------------|----------|
| #13 大气校正 | DOS / 经验线近似，可参数化 | 完整 MODTRAN/6S 联机大气库 |
| #16 正射 | GDAL/rasterio + DEM/仿射几何校正 | 完整 SfM/摄影测量建站 |
| #01 航线规划 | 基于 AOI/重叠率/航高的几何航迹规划 | 厂商飞控私有协议对接 |
| #36/#38/#39 深度学习 | 可训练/可推理轻量网络 + 可复现 testdata | 超大预训练与分布式长训 |
| #03 POS | GPS/IMU CSV 融合（互补滤波等） | 商业精密差分 POS 黑盒 |

## 4. 分波计划（方案 C）

每波结束即可对该波全部项做 HTTP 验收；不在该波内保留骨架。

| 波次 | 覆盖编号 | 项数 | 生产级要点 |
|------|----------|------|------------|
| **W1** | #24 #25 #26 | 3 | 波段/特征选择；SLIC 超像素；Patch/样本构建 |
| **W2** | #29–#33 | 5 | EVI/SAVI；NDMI/NDWI；红边参数；回归反演；简化物理反演 |
| **W3** | #35 #36 #38 #39 #41 #43 #44 | 7 | SAM；1D-CNN；轻量 Transformer；少样本；解混；变化检测；分类后处理 |
| **W4** | #01–#11 | 11 | 航线、时间戳、POS、质检、云影、暗电流、坏像元、去条带、smile/keystone、辐射定标、相对辐射归一 |
| **W5** | #13–#19 | 7 | 大气、BRDF、地理定位、正射、镶嵌、匀色、多源配准 |

**顺序理由：** 先补与现有可运行项衔接紧、便于立即联调的 L2/L3（W1–W3），再攻坚采集与几何链（W4–W5）。

## 5. 架构与改动面

### 5.1 单算法目录（保持现有约定）

```text
algorithms/{id}/
  service.py      # run() 真实实现；IMPLEMENTED = True
  router.py       # 不变或仅改标题说明
  README.md       # 方法、参数、产物、边界
  testdata/       # input / file2 / params.json
```

### 5.2 公共层

- 优先扩展 `common/io.py`（读写、预览、矢量）与必要时新增 `common/geo.py` / `common/ml_utils.py`，避免 33 处复制粘贴
- `common/catalog.py` / 注册逻辑：确保 `IMPLEMENTED` 变更后清单接口反映真实状态
- 确需新依赖（如 `scikit-image` 做 SLIC）写入 `algorithm/source/requirements.txt` 并验证可安装

### 5.3 文档同步

每波结束后更新：

- `algorithm/docs/算法API测试清单.md`：状态列、汇总表、最近一次测试结果
- 必要时微调对应算法 README；**不改**清单编号与 `algorithm_id` 映射

## 6. 各波方法选型（摘要）

### W1

| ID | 方法 |
|----|------|
| 24_band_select | 方差 / 互信息 / 指定索引；输出子集立方体 |
| 25_superpixel | SLIC；输出标签图 + 对象均值谱可选 |
| 26_patch_build | 滑窗/标注驱动 patch；输出 npy/json 清单 |

### W2

| ID | 方法 |
|----|------|
| 29_evi_savi | EVI / SAVI / MSAVI 公式；专题 GeoTIFF |
| 30_ndmi_ndwi | NDMI / NDWI / MNDWI；专题 GeoTIFF |
| 31_red_edge_params | 红边位置/斜率等光谱特征参数图或表 |
| 32_regression_inversion | PLS/岭回归；需 file2 标签或训练表 |
| 33_physical_inversion | 简化经验物理模型（可参数化） |

### W3

| ID | 方法 |
|----|------|
| 35_spectral_matching | SAM / SID；光谱库 CSV |
| 36_cnn1d_classify | 轻量 1D-CNN（torch） |
| 38_transformer_classify | 轻量光谱 Transformer |
| 39_few_shot_classify | 原型网络/度量少样本 |
| 41_unmixing | 端元提取 + FCLS/NNLS 丰度 |
| 43_change_detect | 影像差分 / CVA / 阈值变化图 |
| 44_postprocess_smooth | 众数滤波 / 小斑剔除 |

### W4

| ID | 方法 |
|----|------|
| 01_flight_planning | AOI + 航高/重叠 → 航点 GeoJSON/CSV |
| 02_sync_timestamp | 多传感器时间戳最近邻/插值对齐表 |
| 03_pos_solution | GPS+IMU CSV → 位姿轨迹 |
| 04_flight_qc | 丢帧/过曝/欠曝统计报告 |
| 05_cloud_shadow | 光谱/亮度阈值云影掩膜 |
| 06_dark_current | 暗帧减除 |
| 07_bad_pixel | 坏线/坏像元检测与邻域修复 |
| 08_destriping | 列向/行向统计去条带 |
| 09_smile_keystone | 多项式/插值几何-光谱校正示意实现 |
| 10_radiance_calibration | DN→辐亮度增益偏置 |
| 11_relative_radiometric | 直方图匹配/增益归一 |

### W5

| ID | 方法 |
|----|------|
| 13_atmospheric_correction | DOS / 经验近似反射率 |
| 14_brdf_correction | 简易核驱动/余弦几何校正 |
| 15_geo_locate | 仿射/RPC 粗定位写地理参考 |
| 16_orthorectify | GDAL warp + DEM（有则用） |
| 17_mosaic | 重叠区融合镶嵌 |
| 18_color_balance | 直方图/增益匀色 + 接缝权重 |
| 19_multi_source_register | 互相关/仿射配准 HSI–RGB/矢量 |

## 7. 测试与验收

### 7.1 单波验收

对波内每项：

```bash
# 工作目录 algorithm/source
curl -s -X POST "http://127.0.0.1:28800/api/v1/{id}/run" \
  -F "file=@algorithms/{id}/testdata/..." \
  -F "file2=@..." \   # 如需要
  -F "params=$(cat algorithms/{id}/testdata/params.json)"
```

断言：`success=true`、`implemented=true`、`files` 非空且文件存在。

### 7.2 全量验收

- 45/45 HTTP 200、success、implemented、files
- 回归：原 12 项行为不回退
- 更新测试清单「最近一次自动测试结果」区块

### 7.3 自动化

优先复用/扩展仓库已有 checklist 同步脚本（若存在 `sync_api_test_checklist`）；否则新增 `algorithm/source/scripts/verify_all_algorithms.py` 做批量验收。

## 8. 非目标

- 不替换业务系统 GIS 平台
- 不引入未声明的商业许可 SDK
- 不在本阶段改动 LUMIR skill / PPT / Word 汇报材料（除非用户另行要求）
- 未经用户要求不创建 Git 提交

## 9. 风险与缓解

| 风险 | 缓解 |
|------|------|
| W4/W5 几何链对 testdata 要求高 | 为缺省样例生成合成 AOI/轨迹/DEM；README 标明真实项目数据替换方式 |
| torch 模型训练超时 | 极小网络 + 极少 epoch；允许 params 切换 `mode=infer` 使用内置小权重 |
| 依赖膨胀 | 仅增加必要包；安装失败则改用不增依赖的等价算法 |
| 用户并行手测与实现冲突 | 每波结束明确「可测波次」清单，避免测未交付项 |

## 10. 成功标准

- [ ] W1–W5 全部完成
- [ ] `算法API测试清单.md` 汇总：**可运行且产出 files = 45/45**，无骨架行
- [ ] 用户可按清单逐项 curl 验证通过
- [ ] 现有 12 项回归通过

---

**请审阅本规格。** 确认后进入 `writing-plans` 制定实施计划，再按 W1→W5 开工。
