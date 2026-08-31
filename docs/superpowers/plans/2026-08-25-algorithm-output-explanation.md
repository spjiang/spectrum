# 算法输出详细说明与专家分析工作台实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 45 个算法的所有文件产物和核心业务指标建立逐项专业说明，并在运行前后通过专家分析工作台展示实际效果、质量判断和下游用途。

**Architecture:** 后端新增按 L0/L2/L3 分组的输出知识库，以 `service.py` 真实返回键为骨架并由 `console_catalog.py` 合并；前端新增独立 `OutputWorkbench.vue`，运行前渲染预期产物，运行后按 `files_http` 和 `data` 路径绑定实际值。质量状态仅依据显式结构化规则计算，没有业务阈值时返回“不可判定”。

**Tech Stack:** Python 3.10、FastAPI、AST/`unittest`、Vue 3 Composition API、TypeScript、Vite、原生 HTML 可访问组件。

## Global Constraints

- 禁止使用过时 API；不新增无必要依赖。
- 代码注释统一使用中文。
- 输出键必须来自服务真实返回，不修改 45 个算法计算实现和响应协议。
- 所有文件输出全部说明；`data` 只建模核心业务或质量指标。
- 不根据单次运行无依据宣称效果优秀；PNG 和色带不得作为定量依据。
- 页面文案来自结构化知识库，Vue 模板不得拼接专业长句。
- 未经用户明确要求不得执行 `git commit`、`git push`。

---

## 文件职责

- Create: `algorithm/source/common/console_output_knowledge/__init__.py`  
  输出知识库公共接口、数据校验和分组聚合。
- Create: `algorithm/source/common/console_output_knowledge/common.py`  
  公共构造器、格式级基础结构和质量规则类型。
- Create: `algorithm/source/common/console_output_knowledge/l0.py`  
  算法 01–11 的专属输出说明。
- Create: `algorithm/source/common/console_output_knowledge/l2.py`  
  算法 12–26 的专属输出说明。
- Create: `algorithm/source/common/console_output_knowledge/l3.py`  
  算法 27–45 的专属输出说明。
- Modify: `algorithm/source/common/console_catalog.py`  
  合并真实输出骨架、核心指标和专业知识。
- Create: `algorithm/source/tests/test_console_output_knowledge.py`  
  输出知识覆盖、键一致性、多波段和条件输出测试。
- Modify: `algorithm/web/src/types.ts`  
  增加输出知识、波段、质量规则和摘要类型。
- Create: `algorithm/web/src/outputWorkbench.ts`  
  嵌套路径取值、实际产物绑定和质量状态纯函数。
- Create: `algorithm/web/src/components/OutputWorkbench.vue`  
  专家分析工作台 UI。
- Modify: `algorithm/web/src/views/AlgoView.vue`  
  接入运行前后工作台，移除重复的独立结果列表。
- Modify: `algorithm/web/src/style.css`  
  工作台、指标、状态和响应式样式。

---

### Task 1: 建立输出知识契约与失败测试

**Files:**

- Create: `algorithm/source/common/console_output_knowledge/__init__.py`
- Create: `algorithm/source/common/console_output_knowledge/common.py`
- Create: `algorithm/source/tests/test_console_output_knowledge.py`

**Interfaces:**

- Produces: `get_algorithm_output_knowledge(algorithm_id: str) -> dict[str, Any]`
- Produces: `list_known_output_paths(algorithm_id: str) -> set[str]`
- Produces: `make_output(...) -> dict[str, Any]`
- Produces: 每个算法知识对象包含 `summary` 与 `outputs`。

- [ ] **Step 1: 写契约失败测试**

测试至少断言：

```python
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

def test_output_knowledge_contract_is_structured():
    item = get_algorithm_output_knowledge("27_ndvi")
    assert set(item["summary"]) == {"what", "value", "caution"}
    ndvi = item["outputs"]["files.ndvi_tif"]
    assert REQUIRED_OUTPUT_DETAILS <= ndvi.keys()
    assert ndvi["parent"] == "files"
    assert ndvi["apiKey"] == "ndvi_tif"

def test_quality_rule_is_machine_readable():
    row = get_algorithm_output_knowledge("27_ndvi")["outputs"]["data.min"]
    assert row["qualityRule"] == {
        "kind": "between",
        "min": -1.0,
        "max": 1.0,
        "passWhenInside": True,
        "basis": "NDVI 理论定义域",
    }
```

- [ ] **Step 2: 运行测试并确认因模块不存在而失败**

Run:

```bash
cd algorithm/source
./.venv/bin/python -m unittest tests.test_console_output_knowledge -v
```

Expected: FAIL，错误明确指向 `common.console_output_knowledge` 不存在。

- [ ] **Step 3: 实现公共构造器和聚合接口**

`make_output` 的固定签名：

```python
def make_output(
    path: str,
    label: str,
    *,
    description: str,
    effect: str,
    business_meaning: str,
    interpretation: str,
    quality_check: str,
    abnormal_signs: list[str],
    downstream_use: str,
    unit: str = "—",
    range_text: str = "由输入数据与算法定义决定",
    format_name: str = "",
    vis: str = "none",
    optional: bool = False,
    conditional: str = "",
    bands: list[dict[str, Any]] | None = None,
    misuse_warning: str = "",
    related_outputs: list[str] | None = None,
    quality_rule: dict[str, Any] | None = None,
) -> dict[str, Any]:
```

函数从 `path` 拆出 `parent` 和 `apiKey`，禁止接受不以 `files.` 或 `data.` 开头的路径。`get_algorithm_output_knowledge` 从 L0/L2/L3 字典中查找，不存在时返回空结构但不得伪造说明。

- [ ] **Step 4: 添加最小 NDVI 样例使契约测试通过**

先在 `common.py` 或测试专用最小字典中加入 `27_ndvi.files.ndvi_tif` 与 `27_ndvi.data.min`，用真实中文说明验证接口，不使用“结果文件”“按实际情况判断”等泛化句。

- [ ] **Step 5: 运行契约测试**

Expected: 新增契约测试 PASS。

---

### Task 2: 完成 L0（01–11）输出知识

**Files:**

- Create: `algorithm/source/common/console_output_knowledge/l0.py`
- Modify: `algorithm/source/tests/test_console_output_knowledge.py`

**Interfaces:**

- Produces: `L0_OUTPUT_KNOWLEDGE: dict[str, dict[str, Any]]`
- Consumes: `make_output`。

- [ ] **Step 1: 写 L0 覆盖失败测试**

精确覆盖：

```python
L0_EXPECTED = {
    "01_flight_planning": {
        "files": {"mission_json", "waypoints_geojson"},
        "data": {"gsd_m", "swath_m", "footprint_along_m", "line_spacing_m",
                 "photo_spacing_m", "n_lines", "n_waypoints", "est_path_m",
                 "est_duration_s"},
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
        "data": {"passed", "suggest_refly", "saturation_level", "saturated_ratio",
                 "underexposed_ratio", "max_saturated_ratio", "snr_per_band",
                 "snr_min", "snr_median", "min", "max", "mean"},
    },
    "05_cloud_shadow": {
        "files": {"cloud_mask_tif", "shadow_mask_tif", "combo_mask_tif", "preview_png"},
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
```

测试还必须断言：

- `05.combo_mask_tif` 的 `bands`/编码说明包含 `0=clear, 1=shadow, 2=cloud`。
- `06.cube_tif` 说明 `dark_frame` 与 `per_band_min` 两种效果。
- `09` 两个动态数组明确各自与列/波段的对应关系。
- 所有 `preview_png` 均通过 `relatedOutputs` 指向定量文件。

- [ ] **Step 2: 运行 L0 测试确认缺少 01–11 内容**

- [ ] **Step 3: 填写 01–11 专属内容**

每条记录必须回答：

1. 产物或指标是什么；
2. 用户应看到什么效果；
3. 该效果代表什么业务意义；
4. 怎样检查可用性；
5. 哪些异常表示输入、参数或算法存在问题；
6. 下游如何使用以及禁止怎样误用。

不得把 `snr_per_band` 等动态数组展开为固定长度波段；使用 `bands` 或解释字段描述索引关系。

- [ ] **Step 4: 运行 L0 测试**

Expected: 01–11 覆盖与专业字段测试 PASS。

---

### Task 3: 完成 L2（12–26）输出知识

**Files:**

- Create: `algorithm/source/common/console_output_knowledge/l2.py`
- Modify: `algorithm/source/tests/test_console_output_knowledge.py`

**Interfaces:**

- Produces: `L2_OUTPUT_KNOWLEDGE`。

- [ ] **Step 1: 写 L2 覆盖失败测试**

按下列精确清单建模：

```text
12 files=reflectance_tif
   data=panel_reflectance,panel_radiance,dark_radiance,min,max,mean
13 files=reflectance_tif
   data=solar_zenith,doy,haze_radiance,wavelengths_nm,min,max
14 files=cube_tif
   data=solar_zenith,view_zenith_edge,relative_azimuth
15 files=cube_tif,meta_json
   data=lon,lat,alt_m,gsd_m,res_deg,yaw,crs
16 files=ortho_tif
   data=gsd_m,focal_px,altitude_m,roll_deg,pitch_deg,yaw_deg,dem_min,dem_max
17 files=mosaic_tif
   data=n_scenes,bounds,resolution
18 files=cube_tif,preview_png
   data=window,contrast,brightness
19 files=hsi_tif,rgb_aligned_tif
   data=dy,dx,peak_response
20 files=cube_tif
   data=input_bands,dropped,kept,snr_per_band,wavelength_nm,snr_ratio
21 files=cube_tif
   data=window_length,polyorder
22 files=cube_tif
   data=method,mean,std
23 files=pca_tif
   data=method,eigenvalues,explained_variance_ratio,n_components
24 files=cube_tif,ranking_json
   data=method,selected,scores
25 files=labels_tif,preview_png
   data=n_segments,compactness,n_unique
26 files=patches_npz,manifest_json,preview_png
   data=n,patch_size,bands,classes
```

额外断言：

- 20 的输出波段 `k` 对应原始索引 `kept[k]`。
- 23 的波段顺序为按特征值降序的第 1..K 主成分。
- 24 的输出波段 `j` 对应 `selected[j]`。
- 25 的标签从 1 开始，预览颜色不代表类别大小。
- 26 的 NPZ 明确包含 `patches`、`labels`、`coords`，末维保持输入波段顺序。

- [ ] **Step 2: 运行测试确认失败**

- [ ] **Step 3: 填写 12–26 专属内容**

对必须使用 `file2` 的 16、17、19、26，在产物说明中明确缺少辅文件不会产生有效输出。对动态波长、波段、类别和数组只描述索引关系，不固化长度。

- [ ] **Step 4: 运行 L2 测试**

Expected: 12–26 全部 PASS。

---

### Task 4: 完成 L3（27–45）输出知识

**Files:**

- Create: `algorithm/source/common/console_output_knowledge/l3.py`
- Modify: `algorithm/source/tests/test_console_output_knowledge.py`

**Interfaces:**

- Produces: `L3_OUTPUT_KNOWLEDGE`。

- [ ] **Step 1: 写 L3 覆盖失败测试**

```text
27 files=ndvi_tif,preview_png data=min,max,mean
28 files=ndre_tif,preview_png data=min,max,mean
29 files=indices_tif,preview_png data=L,evi_mean,savi_mean,msavi_mean
30 files=indices_tif,preview_png data=ndmi_mean,ndwi_mean,mndwi_mean
31 files=params_tif,preview_png data=anchors_nm,rep_mean,amp_mean,deriv_rep_mean,wl_start_nm,wl_end_nm
32 files=inversion_tif,preview_png data=r2,rmse,n_components,n_train,n_test,preprocess
33 files=lai_tif,cab_tif,preview_png data=model,lut_size,lai_mean,lai_max,cab_mean,wavelengths_nm
34 files=pred_map_tif,preview_png data=oa,aa,kappa,n_train,n_test,classes,model
35 files=pred_map_tif,angle_tif,preview_png data=method,n_endmembers,score_mean,classes
36 files=pred_map_tif,preview_png data=oa,aa,kappa,n_train,n_test,classes,device,architecture,epochs
37 files=pred_map_tif,preview_png data=oa,aa,kappa,n_train,n_test,classes,device,bands_after_pca,architecture,patch_size,epochs
38 files=pred_map_tif,preview_png data=oa,aa,kappa,n_train,n_test,classes,device,architecture,epochs
39 files=pred_map_tif,preview_png data=shots,n_support,classes,oa,aa,kappa,n_query
40 files=score_tif,mask_tif,polygons_geojson,annotation_geojson,preview_png
   data=threshold_ndvi,ace_percentile,n_objects,n_positive_pixels,has_annotation_geojson,annotation_features
41 files=abundance_tif,preview_png data=n_endmembers,abundance_mean,sum_to_one_mean
42 files=score_tif,mask_tif,preview_png data=method,percentile,threshold,n_anomaly_pixels,score_min,score_max,score_mean
43 files=magnitude_tif,chi2_tif,mask_tif,preview_png data=canonical_correlations,chi2_mean,chi2_df,percentile,threshold,n_change
44 files=labels_tif,preview_png data=min_pixels,window,n_changed,classes
45 files=report_json,parcel_geojson data=mode,n_parcels,n_parcels_with_pixels,scene,parcels
```

额外断言：

- 29 `indices_tif` 波段固定为 `[EVI, SAVI, MSAVI]`。
- 30 `indices_tif` 波段固定为 `[NDMI, NDWI, MNDWI]`。
- 31 `params_tif` 固定为 `[guyot_rep_nm, red_edge_amplitude, sg_derivative_rep_nm]`。
- 39 的 OA/AA/Kappa/n_query 为条件指标，仅存在查询样本时显示。
- 40 `annotation_geojson` 标记 `optional=True`，条件为提供 GeoJSON 标注/AOI。
- 41 丰度波段与端元 CSV 列顺序一致，不能固化端元数量。
- 45 `parcel_geojson` 为条件输出；`scene` 与 `parcels` 以短结构说明建模，不展开动态地块列表。

- [ ] **Step 2: 运行测试确认失败**

- [ ] **Step 3: 填写 27–45 专属内容**

指数理论定义域可设置结构化范围检查；OA/AA/Kappa、R²/RMSE 等没有业务验收阈值时只能说明“越高/越低通常更好”和对比前提，质量状态保持“不可判定”。分类色图必须说明颜色仅映射类别 ID。

- [ ] **Step 4: 运行 L3 测试**

Expected: 27–45 全部 PASS。

---

### Task 5: 将输出知识合并到控制台元数据

**Files:**

- Modify: `algorithm/source/common/console_catalog.py`
- Modify: `algorithm/source/tests/test_console_output_knowledge.py`
- Modify: `algorithm/source/tests/test_console_professional_metadata.py`

**Interfaces:**

- Consumes: `get_algorithm_output_knowledge`
- Produces: `build_item(meta, doc)["output_summary"]`
- Produces: `fields.outputs` 中逐个 `files.*` 与 `data.*` 行。

- [ ] **Step 1: 写元数据集成失败测试**

```python
def test_catalog_exposes_output_summary_and_core_metrics():
    item = get_console_algorithm("27_ndvi")
    assert item["output_summary"]["what"]
    rows = {row["name"]: row for row in item["fields"]["outputs"]}
    assert {"files.ndvi_tif", "files.preview_png", "data.min", "data.max", "data.mean"} <= rows.keys()
    assert rows["files.ndvi_tif"]["effect"]
    assert rows["data.mean"]["businessMeaning"]

def test_no_real_file_output_uses_generic_fallback():
    for item in list_console_algorithms():
        for row in item["fields"]["outputs"]:
            if row["name"].startswith("files."):
                assert row["knowledgeSource"] == "algorithm"
```

- [ ] **Step 2: 运行测试确认当前 catalog 缺少核心指标行**

- [ ] **Step 3: 修改 `_output_fields`**

行为要求：

- 继续以当前逐算法真实 `files` 键表生成骨架。
- 对每个文件键强制取得知识记录；缺失时设置 `knowledgeSource="fallback"`，测试将阻止验收。
- 将知识库中 `data.*` 记录追加为独立输出行。
- 删除当前通用 `name="data"` 聚合行；原始 JSON 仍由返回数据抽屉显示。
- `output_summary` 原样加入算法元数据。
- 保留 `vis` 与运行时预览兼容，知识库的专属 `vis` 优先。

- [ ] **Step 4: 增加全量一致性测试**

测试 45 个算法：

- 文件键与 catalog 真实键集合一致。
- 核心指标路径唯一。
- 条件输出、固定多波段输出符合 Task 2–4 断言。
- 所有输出具备设计规格要求的专业字段。

- [ ] **Step 5: 运行后端全量测试**

```bash
cd algorithm/source
./.venv/bin/python -m unittest \
  tests.test_console_output_knowledge \
  tests.test_console_professional_metadata -v
```

Expected: 全部 PASS。

---

### Task 6: 实现前端输出类型与纯函数

**Files:**

- Modify: `algorithm/web/src/types.ts`
- Create: `algorithm/web/src/outputWorkbench.ts`
- Create: `algorithm/web/tests/outputWorkbench.test.mjs`
- Modify: `algorithm/web/package.json`

**Interfaces:**

- Produces: `OutputFieldRow`、`OutputBand`、`OutputQualityRule`、`OutputSummary`
- Produces: `readDataPath(data, "data.scene.mean")`
- Produces: `resolveOutputValue(row, result)`
- Produces: `evaluateOutputStatus(row, value) -> "pass" | "attention" | "unknown" | "not-produced"`。

- [ ] **Step 1: 写纯函数失败测试**

覆盖：

- `files.ndvi_tif` 从 `result.files_http.ndvi_tif` 绑定。
- `data.mean` 从 `result.data.mean` 绑定。
- `data.scene.mean` 可读取嵌套对象。
- 条件输出缺失返回 `not-produced`。
- 无 `qualityRule` 返回 `unknown`。
- NDVI 值超出 `[-1, 1]` 返回 `attention`，范围内返回 `pass`。

- [ ] **Step 2: 增加无依赖测试脚本并确认失败**

在 `package.json` 增加：

```json
"test:output": "rm -rf .tmp-output-test && tsc src/outputWorkbench.ts --target ES2022 --module ESNext --moduleResolution Bundler --outDir .tmp-output-test --skipLibCheck && node --test tests/outputWorkbench.test.mjs"
```

`tests/outputWorkbench.test.mjs` 使用 Node 内置 `node:test` 与 `node:assert/strict`，从 `../.tmp-output-test/outputWorkbench.js` 导入纯函数，不新增测试依赖。

Run:

```bash
cd algorithm/web
npm run test:output
```

Expected: FAIL，错误明确指向 `outputWorkbench.ts` 或导出函数尚不存在。

- [ ] **Step 3: 扩展类型**

`AlgorithmCard` 增加：

```typescript
output_summary: {
  what: string;
  value: string;
  caution: string;
};
```

`FieldRow` 扩展为可承载输出知识，或新增 `OutputFieldRow extends FieldRow`，字段名必须与设计规格一致，并加入：

```typescript
qualityRule?: {
  kind: "between" | "min" | "max" | "equals";
  min?: number;
  max?: number;
  value?: string | number | boolean;
  passWhenInside?: boolean;
  basis: string;
};
knowledgeSource?: "algorithm" | "fallback";
```

- [ ] **Step 4: 实现纯函数**

所有路径读取必须防御 `null`、数组和不存在键；不得使用 `eval`。状态解释与 UI 文案分离。

- [ ] **Step 5: 运行纯函数测试与类型检查**

```bash
cd algorithm/web
npm run test:output
npx vue-tsc --noEmit
```

Expected: 两条命令均 PASS。

---

### Task 7: 实现专家分析工作台并接入运行页

**Files:**

- Create: `algorithm/web/src/components/OutputWorkbench.vue`
- Modify: `algorithm/web/src/views/AlgoView.vue`
- Modify: `algorithm/web/src/style.css`

**Interfaces:**

- Consumes: `algo: AlgorithmCard`
- Consumes: `result: RunResult | null`
- Emits: 无；所有展示由 props 派生。

- [ ] **Step 1: 建立组件验收检查**

组件模板必须包含可访问的四个真实 `<button>` 标签：

- 文件产物
- 核心指标
- 质量检查
- 下游应用

每个按钮具有 `aria-selected`，面板具有对应 `role="tabpanel"`。运行前 `result=null` 仍显示预期输出。

- [ ] **Step 2: 实现顶部决策摘要**

默认显示 `output_summary.what/value/caution`。摘要不显示接口键，接口键留在专家卡片。

- [ ] **Step 3: 实现文件产物标签**

逐 `files.*` 行显示：

- 名称、API 键、格式、单位、范围和条件。
- `effect`、`businessMeaning`、`interpretation`。
- 多波段结构。
- 运行后对应 `VisPanel`。
- 未产生的必需输出标记“未返回”；条件输出标记“本次条件未满足”。

- [ ] **Step 4: 实现核心指标与质量标签**

核心指标显示定义、实际值、单位、范围、规则依据和四态状态。质量标签按状态聚合，但不得把 `unknown` 改写成“通过”。

- [ ] **Step 5: 实现下游应用标签**

显示 `downstreamUse`、`misuseWarning` 与 `relatedOutputs`，明确 PNG 和定量文件关系。

- [ ] **Step 6: 修改 `AlgoView.vue`**

在运行演示中接入：

```vue
<OutputWorkbench :algo="algo" :result="result" />
```

移除当前独立遍历 `outputAssets` 的重复结果区；返回数据抽屉继续保留原始 JSON。`VisPanel` 由工作台文件卡片调用。

- [ ] **Step 7: 添加响应式与状态样式**

桌面端采用专家标签和卡片网格；窄屏改为纵向。状态不得只依赖颜色，必须有“通过/需关注/不可判定/未产生”文本。

- [ ] **Step 8: 运行前端验证**

```bash
cd algorithm/web
npx vue-tsc --noEmit
npm run build
```

Expected: 两条命令均 exit 0。

---

### Task 8: 运行时与内容验收

**Files:**

- Modify: `algorithm/source/tests/test_console_output_knowledge.py`（仅补充验收中发现的遗漏）

- [ ] **Step 1: 启动隔离后端并检查元数据**

在不干扰 28800 的情况下使用 28801，验证：

- `27_ndvi` 返回 2 个文件输出和 3 个核心指标。
- `29_evi_savi.files.indices_tif` 返回固定三波段说明。
- `34_svm_rf_classify` 返回 OA/AA/Kappa 说明但不伪造业务阈值。
- `40_detect_segment.files.annotation_geojson` 是条件输出。
- `45_parcel_zonal_stats` 返回 scene/parcels 结构说明。

- [ ] **Step 2: 代表性真实运行**

使用内置 testdata 运行 27、32、34、40、45，验证实际文件和核心指标能按键绑定；若某算法环境依赖导致无法执行，记录具体依赖错误，不把元数据检查冒充算法运行成功。

- [ ] **Step 3: 全量静态验收**

```bash
cd algorithm/source
./.venv/bin/python -m unittest \
  tests.test_console_output_knowledge \
  tests.test_console_professional_metadata -v

cd ../web
npx vue-tsc --noEmit
npm run build
```

- [ ] **Step 4: IDE 诊断与最终检查**

检查所有改动文件无新增 lint 错误；确认 45 个算法、所有文件产物和核心指标覆盖数量与测试输出一致。

- [ ] **Step 5: 重启 28800 服务并验证 5173 页面**

仅在所有验收通过后重启现有后端，使 Vite 页面使用新元数据。检查一个 L0、一个 L2、一个 L3 页面可访问。

---

## 实施顺序与并行边界

1. Task 1 必须先完成，锁定契约。
2. Task 2、3、4 可在独立文件中并行，但不得同时修改测试文件；协调者先为三组写好测试骨架，内容执行者只修改各自知识文件。
3. Task 5 在三组内容完成后执行。
4. Task 6 可与 Task 2–4 并行，前提是严格使用 Task 1 定义的字段名。
5. Task 7 依赖 Task 5 和 Task 6。
6. Task 8 最后执行。

## 完成标准

- 45 个算法全部存在决策摘要。
- 所有真实文件输出均为算法专属说明，不使用兜底知识。
- 已列核心指标全部存在结构化说明。
- 固定多波段与条件输出均通过专门测试。
- 工作台运行前后使用同一元数据，并正确绑定实际值。
- 质量状态没有无依据的“通过”。
- 后端测试、前端类型检查、生产构建、代表性运行与现有 28800/5173 页面检查全部通过。
