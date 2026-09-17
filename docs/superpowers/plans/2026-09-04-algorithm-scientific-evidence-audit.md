# 45 项算法科学证据审查 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 逐项核验并修正 01–45 算法的实现、科学文案与文献证据，使所有保留主张可追溯、有限定且与实际代码一致。

**Architecture:** 在现有原理、文献、输出知识和 AI 知识之上增加机器可读的主张—文献—实现证据层。先修复已确认的硬错误和虚假能力标题，再按 L0/L1、L2、L3/L4 三批核验全部内容，最后以静态契约、数值 golden、45 项冒烟和前端构建共同验收。

**Tech Stack:** Python 3.10+/pytest/FastAPI；TypeScript/Vue 3/Vite/Node test；JSON 共享证据清单。

## Global Constraints

- 覆盖控制台全部可见文案、AI 解读知识、产品分析及两份算法清单。
- 同行评审论文优先；标准与官方技术文档可证明工程方法。
- 二手数据库不得作为公式或算法首创的唯一证据。
- 找不到直接证据时，改为“本仓库实现”并写清边界，不补造来源。
- 标题只能包含已实现能力。
- 教学默认参数不得写成行业标准。
- 不自动创建 Git commit。
- 线上部署必须等待 45 项全量验收通过。

---

### Task 1: 建立机器可读证据模型与完整性门禁

**Files:**
- Create: `algorithm/shared/scientific_evidence.json`
- Create: `algorithm/source/common/scientific_evidence.py`
- Create: `algorithm/source/tests/test_scientific_evidence.py`
- Create: `algorithm/web/src/evidence.ts`
- Create: `algorithm/web/tests/evidence.test.mjs`
- Modify: `algorithm/web/tsconfig.json`

**Interfaces:**
- Produces: `get_algorithm_evidence(algorithm_id: str) -> dict`
- Produces: `getAlgorithmEvidence(id: string): AlgorithmEvidence | undefined`
- JSON schema fields: `algorithmId`, `title`, `grade`, `implementation`, `claims`, `references`
- Claim fields: `claimId`, `category`, `text`, `status`, `targets`, `referenceIds`, `implementationRefs`, `reviewNote`
- Reference fields: `referenceId`, `authors`, `year`, `title`, `venue`, `url`, `sourceType`, `summary`, `supports`

- [ ] **Step 1: 写证据完整性失败测试**

```python
def test_all_45_algorithms_have_scientific_evidence():
    rows = load_scientific_evidence()
    assert len(rows) == 45
    assert {row["algorithmId"] for row in rows} == set(ALL_ALGORITHM_IDS)

def test_no_rejected_claim_or_grade_d_can_ship():
    for row in load_scientific_evidence():
        assert row["grade"] in {"A", "B", "C"}
        assert all(c["status"] != "rejected" for c in row["claims"])

def test_core_claim_categories_are_present():
    required = {"definition", "formula", "input", "output", "limitation"}
    for row in load_scientific_evidence():
        assert required <= {c["category"] for c in row["claims"]}
```

- [ ] **Step 2: 运行测试，确认因文件/接口不存在而失败**

Run: `cd algorithm/source && .venv/bin/python -m pytest tests/test_scientific_evidence.py -q`

Expected: FAIL，提示无法导入 `common.scientific_evidence`。

- [ ] **Step 3: 创建证据读取器和 45 项结构骨架**

`scientific_evidence.py` 只负责加载、深拷贝和按 ID 查询；不得把缺失字段静默补为空。JSON 中 45 项先录入当前标题、实现入口及五类核心 claim，所有 claim 必须使用明确状态。

- [ ] **Step 4: 增加文献引用闭合测试**

```python
def test_claim_reference_links_are_closed():
    for row in load_scientific_evidence():
        refs = {r["referenceId"]: r for r in row["references"]}
        for claim in row["claims"]:
            for rid in claim["referenceIds"]:
                assert rid in refs
                assert claim["claimId"] in refs[rid]["supports"]
```

- [ ] **Step 5: 增加二手来源限制测试**

```python
def test_formula_claim_has_primary_or_official_evidence():
    forbidden_only = {"secondary-index", "aggregator", "search-result"}
    for row in load_scientific_evidence():
        refs = {r["referenceId"]: r for r in row["references"]}
        for claim in row["claims"]:
            if claim["category"] != "formula" or claim["status"] == "implementation-only":
                continue
            assert any(refs[r]["sourceType"] not in forbidden_only for r in claim["referenceIds"])
```

- [ ] **Step 6: 实现前端类型与 Node 完整性测试**

Node 测试读取共享 JSON，断言 45 项、引用闭合、URL 以 `https://` 开头、中文提要长度不少于 20 个字符。

- [ ] **Step 7: 运行 Task 1 测试**

Run:

```bash
cd algorithm/source && .venv/bin/python -m pytest tests/test_scientific_evidence.py -q
cd ../web && npm run build && node --test tests/evidence.test.mjs
```

Expected: PASS。

---

### Task 2: 修复 L0/L1 已确认硬错误并建立回归测试

**Files:**
- Modify: `algorithm/source/common/rs/cloud.py`
- Modify: `algorithm/source/algorithms/07_bad_pixel/service.py`
- Modify: `algorithm/source/common/console_output_knowledge/l0.py`
- Modify: `algorithm/source/algorithms/10_radiance_calibration/service.py`
- Modify: `algorithm/source/common/catalog.py`
- Modify: `algorithm/source/algorithms/03_pos_solution/service.py`
- Modify: `algorithm/source/algorithms/04_flight_qc/service.py`
- Modify: `algorithm/web/src/principles/l0.ts`
- Modify: `algorithm/web/src/sources.ts`
- Modify: `algorithm/shared/scientific_evidence.json`
- Test: `algorithm/source/tests/test_console_output_knowledge.py`
- Test: `algorithm/source/tests/test_scientific_evidence.py`

**Interfaces:**
- #05 文案使用“可见光波段间相对差异较小/低白度指标”，不得写“白度高”。
- #07 返回方法名使用 `median_residual_sigma + neighborhood_mean_fill`。
- #09 输出知识使用“场景互相关估计偏移”，不得使用“标定偏移”。
- #10 默认成功消息不得声称完成实验室定标。

- [ ] **Step 1: 为 #05、#07、#09、#10 写失败测试**

```python
def test_cloud_copy_matches_low_whiteness_metric():
    assert "白度高" not in read_principle("05_cloud_shadow")
    assert "相对差异较小" in read_principle("05_cloud_shadow")

def test_bad_pixel_method_does_not_claim_bilinear_fill():
    source = read_service("07_bad_pixel")
    assert "bilinear_fill" not in source

def test_smile_summary_does_not_claim_calibration_offset():
    summary = get_algorithm_output_knowledge("09_smile_keystone")["summary"]
    assert "标定偏移" not in " ".join(summary.values())

def test_default_radiance_message_does_not_claim_laboratory_calibration():
    assert "实验室线性辐射定标" not in read_service("10_radiance_calibration")
```

- [ ] **Step 2: 运行新测试确认失败**

Run: `cd algorithm/source && .venv/bin/python -m pytest tests/test_console_output_knowledge.py tests/test_scientific_evidence.py -q`

- [ ] **Step 3: 修正四处硬冲突**

保留代码实际行为；#05 不改变 `whiteness < 0.7` 算法，只把显示定义改成可复核的“可见光波段间相对差异指标低于工程阈值”。#07、#09、#10 修正 API/知识文案。

- [ ] **Step 4: 收缩标题**

将标题调整为实际实现：

- #03 `POS轨迹平滑与杠杆臂校正`
- #04 `架次过曝与场景统计质检`

同步 `catalog.py`、service `TITLE`、原理标题来源、两份文档和证据清单。

- [ ] **Step 5: 核验 01–11 文献**

逐项打开 DOI/官方页面；对 #02 钟差中位估计、#03 互补滤波、#05 简化阈值、#07 6σ/4σ 等无直接来源内容标 `implementation-only`。不得把 EMVA 或完整 Fmask 论文写成阈值出处。

- [ ] **Step 6: 运行 L0/L1 回归**

Run:

```bash
cd algorithm/source
.venv/bin/python -m pytest tests/test_console_output_knowledge.py tests/test_console_professional_metadata.py tests/test_scientific_evidence.py -q
```

Expected: PASS。

---

### Task 3: 修复 L2 实现与标题错误

**Files:**
- Modify: `algorithm/source/algorithms/15_geo_locate/service.py`
- Modify: `algorithm/source/common/rs/mosaic.py`
- Modify: `algorithm/source/algorithms/17_mosaic/service.py`
- Modify: `algorithm/source/algorithms/18_color_balance/service.py`
- Modify: `algorithm/source/algorithms/19_multi_source_register/service.py`
- Modify: `algorithm/source/common/rs/qc.py`
- Modify: `algorithm/source/algorithms/20_bad_band_remove/service.py`
- Modify: `algorithm/source/algorithms/25_superpixel/service.py`
- Modify: `algorithm/source/common/catalog.py`
- Modify: `algorithm/web/src/principles/l2.ts`
- Modify: `algorithm/web/src/sources.ts`
- Modify: `algorithm/shared/scientific_evidence.json`
- Test: `algorithm/source/tests/test_console_professional_metadata.py`
- Test: `algorithm/source/tests/test_console_output_knowledge.py`
- Test: `algorithm/source/tests/test_scientific_evidence.py`

**Interfaces:**
- #17 两景 CRS 不同必须返回错误，不生成镶嵌。
- #20 返回字段保留兼容性时必须显示为“场景均值/标准差比”，不得宣称实验室 SNR。
- #25 调用 `slic(..., convert2lab=False)`，因为输入是光谱特征而非 RGB 图像。

- [ ] **Step 1: 写 #17 CRS 失败测试**

构造两个相同数组但 CRS 分别为 EPSG:4326/EPSG:3857 的测试 GeoTIFF，调用服务后断言 `success == False` 且消息包含“CRS”。

- [ ] **Step 2: 写 #20 指标语义测试**

```python
def test_bad_band_scene_ratio_is_mean_over_std():
    cube = known_cube()
    got = band_snr(cube)
    np.testing.assert_allclose(got, cube.mean((0, 1)) / (cube.std((0, 1)) + 1e-12))
    assert "传感器信噪比" not in read_principle("20_bad_band_remove")
```

- [ ] **Step 3: 写 #25 颜色空间测试**

用 monkeypatch 捕获 `slic` 调用，断言 `convert2lab is False`；断言 service docstring 不含“前三主成分”。

- [ ] **Step 4: 运行测试确认失败**

Run: `cd algorithm/source && .venv/bin/python -m pytest tests/test_console_professional_metadata.py tests/test_scientific_evidence.py -q`

- [ ] **Step 5: 实施 #17、#20、#25 最小修复**

#20 内部函数可保留兼容名 `band_snr`，但 docstring、返回知识和页面统一称“场景均值/标准差比”；证据清单记录旧 API 字段 `snr_per_band` 为兼容键。

- [ ] **Step 6: 收缩 #15/#18/#19 标题与定义**

- #15 `POS中心点与GSD粗定位`
- #18 `Wallis局部匀色`
- #19 `HSI-RGB全局平移配准`

#15 定义明确实现不使用姿态；#18 不写接缝线优化；#19 不写矢量配准。

- [ ] **Step 7: 替换失配文献链**

- #16 增加直接支持共线方程 + DEM 正射的 DOI/ISPRS 来源。
- #17 增加直接支持距离加权羽化的遥感镶嵌论文。
- #18 增加 Wallis 1976 方法及可访问的 ISPRS 后续公式来源。
- #15 现有精密直接地理定位论文仅作完整方法背景，本仓库粗仿射标 `implementation-only`。

- [ ] **Step 8: 运行 12–26 回归**

Run:

```bash
cd algorithm/source
.venv/bin/python -m pytest tests/test_console_output_knowledge.py tests/test_console_professional_metadata.py tests/test_scientific_evidence.py -q
```

Expected: PASS。

---

### Task 4: 修复 L3/L4 实现、返回与标题错误

**Files:**
- Modify: `algorithm/source/algorithms/32_regression_inversion/service.py`
- Modify: `algorithm/source/algorithms/34_svm_rf_classify/service.py`
- Modify: `algorithm/source/common/rs/rededge.py`
- Modify: `algorithm/source/algorithms/35_spectral_matching/service.py`
- Modify: `algorithm/source/algorithms/45_parcel_zonal_stats/service.py`
- Modify: `algorithm/source/common/catalog.py`
- Modify: `algorithm/web/src/principles/l3.ts`
- Modify: `algorithm/web/src/sources.ts`
- Modify: `algorithm/source/common/console_output_knowledge/l3.py`
- Modify: `algorithm/source/common/l3_aide/knowledge.py`
- Modify: `algorithm/shared/scientific_evidence.json`
- Test: `algorithm/source/tests/test_l3_aide.py`
- Test: `algorithm/source/tests/test_console_output_knowledge.py`
- Test: `algorithm/source/tests/test_console_professional_metadata.py`
- Test: `algorithm/source/tests/test_scientific_evidence.py`

**Interfaces:**
- #32 `data.preprocess` 与实际执行分支一致。
- #34 SVM 使用训练集拟合的 `StandardScaler`，并对测试集和整图复用。
- #31 导数窗口统一为代码实际的 `[680, 760)` nm。
- #45 连续和分类统计均排除显式 NoData/非有限值。

- [ ] **Step 1: 写 #32 preprocess 回显失败测试**

分别传 `preprocess=snv` 和 `preprocess=none`，断言返回值分别为 `snv` 和 `none`。

- [ ] **Step 2: 写 #34 SVM 标准化失败测试**

monkeypatch `StandardScaler.fit`，断言 SVM 分支调用一次、RF 分支不调用；整图预测使用同一 scaler。

- [ ] **Step 3: 写 #31、#35、#45 契约测试**

- #31 断言页面与输出知识均包含 `680–760 nm`，代码注释年份为 Guyot & Baret 1988。
- #35 断言页面输出名使用 API 键 `pred_map_tif`、`angle_tif`。
- #45 构造含 NoData/NaN 栅格，断言统计不包含无效像元。

- [ ] **Step 4: 运行测试确认失败**

Run: `cd algorithm/source && .venv/bin/python -m pytest tests/test_l3_aide.py tests/test_console_output_knowledge.py tests/test_console_professional_metadata.py tests/test_scientific_evidence.py -q`

- [ ] **Step 5: 实施五项最小修复**

不得改变已验证公式；仅修分支回显、标准化、窗口/注释一致性、输出名和 NoData 过滤。

- [ ] **Step 6: 收缩未实现能力标题**

- #36 `1D-CNN光谱分类`
- #38 `SpectralFormer光谱分类`
- #39 `SAM均值原型少样本分类`
- #40 `低NDVI种子ACE目标检测`

同步目录、service、原理、输出知识、AI 知识、文档和证据清单。RNN、GCN、迁移学习、语义分割仅在“未实现/行业完整做法”中出现。

- [ ] **Step 7: 补齐 #44/#45 手写 AI 知识**

新增定义、精度前提、可解读字段、禁止项和赋能维度，确保只讨论本算法，不改推其他算法。

- [ ] **Step 8: 核验 #28/#40 直接来源**

- #28 打开 USDA/NAL Barnes 2000 全文核对 `(R790−R720)/(R790+R720)`；若无法核对，公式主张保持 `qualified`，不得写“首创”。
- #40 使用 ACE 原始论文 DOI `10.1109/ACSSC.1996.599116` 支持检测器；低 NDVI 种子策略标 `implementation-only`。

- [ ] **Step 9: 运行 27–45 回归**

Run:

```bash
cd algorithm/source
.venv/bin/python -m pytest tests/test_l3_aide.py tests/test_console_output_knowledge.py tests/test_console_professional_metadata.py tests/test_scientific_evidence.py -q
```

Expected: PASS。

---

### Task 5: 对齐产品分析、AI 知识与两份算法清单

**Files:**
- Modify: `algorithm/web/src/wayho/l0.ts`
- Modify: `algorithm/web/src/wayho/l2.ts`
- Modify: `algorithm/web/src/wayho/l3.ts`
- Modify: `algorithm/source/common/l3_aide/interpreter.py`
- Modify: `algorithm/source/common/l3_aide/layers.py`
- Modify: `algorithm/source/common/l3_aide/scenarios.py`
- Modify: `algorithm/docs/采集到算法-算法清单.md`
- Modify: `algorithm/docs/算法API测试清单.md`
- Modify: `algorithm/shared/scientific_evidence.json`
- Test: `algorithm/source/tests/test_scientific_evidence.py`
- Test: `algorithm/source/tests/test_l3_aide.py`

**Interfaces:**
- 产品型号规格必须绑定官方产品页或产品手册 reference。
- 无官方来源的“精确、必须、最稳、高客单价、竞争优势”删除或改为条件性工程判断。
- AI 解读不得写固定业务场景、处方或未实现算法。

- [ ] **Step 1: 增加夸大措辞门禁**

对标题和完成性文案扫描 `最稳|精确取|独家|高客单价|标准实现|实验室定标完成`；仅当证据清单存在对应 `supported` 产品 claim 时允许。

- [ ] **Step 2: 清理产品分析**

逐项核对中达瑞和型号波段范围、通道数和官方能力；无法访问官方资料的规格删除或标 `qualified`。产品“直接使用/需要改编/不建议”只表示型号适配，不表示算法科学正确性。

- [ ] **Step 3: 清理场景化 AI 遗留**

从通用算法解读中移除封垄、补氮主图、固定水稻场景等表述；保留“不是处方”和“不改推其他算法”护栏。

- [ ] **Step 4: 同步两份清单**

标题、作用、输入、输出、方法边界与最终证据清单一致；文档不再维护与控制台矛盾的旧标题。

- [ ] **Step 5: 运行文案与 AI 测试**

Run:

```bash
cd algorithm/source
.venv/bin/python -m pytest tests/test_l3_aide.py tests/test_scientific_evidence.py -q
```

Expected: PASS。

---

### Task 6: 让算法文献页展示主张—证据绑定

**Files:**
- Modify: `algorithm/web/src/components/SourcePanel.vue`
- Modify: `algorithm/web/src/evidence.ts`
- Modify: `algorithm/web/src/sources.ts`
- Modify: `algorithm/web/src/types.ts`
- Modify: `algorithm/web/src/style.css`
- Create: `algorithm/web/tests/sourceEvidence.test.mjs`

**Interfaces:**
- 文献页按“核心主张”“参考文献”“本仓库实现差异”三部分展示。
- 每条主张显示状态与证据等级，不显示内部源码绝对路径。
- 每条文献显示它支持的主张，不允许孤立引用。

- [ ] **Step 1: 写前端证据绑定失败测试**

测试 45 项均可通过 `getAlgorithmEvidence` 获取；每个显示 claim 的 `referenceIds` 可解析；`rejected` claim 不得进入 SourcePanel 数据。

- [ ] **Step 2: 运行测试确认失败**

Run: `cd algorithm/web && node --test tests/sourceEvidence.test.mjs`

- [ ] **Step 3: 实现证据页绑定视图**

沿用算法 27 的视觉风格；A/B/C 用文字标签说明，不用颜色暗示“科学正确率”。`implementation-only` 显示“本仓库实现依据”，避免误称文献证明。

- [ ] **Step 4: 前端测试与构建**

Run:

```bash
cd algorithm/web
npm run test:output
node --test tests/*.test.mjs
npm run build
```

Expected: 所有测试和构建 PASS；只允许现有 chunk size warning。

---

### Task 7: 全量验收、审查报告与线上部署

**Files:**
- Create: `algorithm/docs/45项算法科学证据审查报告.md`
- Create: `/Users/jiangshengping/.cursor/projects/Users-jiangshengping-wwwroot-shenzhen-spectrum/canvases/algorithm-scientific-audit.canvas.tsx`
- Modify: `algorithm/shared/scientific_evidence.json`

**Interfaces:**
- 报告逐项列证据等级、修订摘要、实现差异、剩余限制和测试状态。
- Canvas 内嵌最终 45 项真实数据，不读取网络。

- [ ] **Step 1: 运行全量后端测试**

Run:

```bash
cd algorithm/source
.venv/bin/python -m pytest -q
```

Expected: PASS，不能忽略失败。

- [ ] **Step 2: 运行前端全量测试与生产构建**

Run:

```bash
cd algorithm/web
npm run test:output
node --test tests/*.test.mjs
npm run build
```

Expected: PASS。

- [ ] **Step 3: 运行 45 项 testdata 冒烟**

Run:

```bash
cd algorithm/source
.venv/bin/python scripts/smoke_all_implemented.py
```

若仓库实际入口为 shell 脚本，则运行 `scripts/smoke_all_algorithms.sh`；验收要求 45/45 成功且每项 `files` 非空。

- [ ] **Step 4: 生成审查报告**

报告必须列出 45 项，不得只写统计摘要；所有 C 级主张明确剩余证据边界；不存在 D 级。

- [ ] **Step 5: 生成 Canvas**

以证据清单内嵌数据展示等级分布、P0/P1 关闭情况、45 项筛选列表及每项主张/来源。遵守 Canvas 设计规则，不用渐变、emoji、阴影或空状态。

- [ ] **Step 6: 检查上线门槛**

断言：

- `grade == D` 数量为 0。
- `status == rejected` 数量为 0。
- P0/P1 未关闭数量为 0。
- 后端、前端、构建、45 项冒烟全部通过。

- [ ] **Step 7: 更新线上并公网验收**

使用现有 rsync 部署流程同步 `algorithm/` 到 `/home/spjiangl/algo/`，排除 `.venv`、`node_modules`、上传与输出数据；重启 `algo` systemd。公网核验：

- `/health` 返回 45/45。
- `/api/v1/algorithms` 返回最终标题。
- 随机抽检 01、05、15、20、25、27、32、40、45。
- 算法 27 和至少一个 C 级算法的文献页显示主张—证据绑定。
