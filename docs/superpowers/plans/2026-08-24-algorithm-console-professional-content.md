# 高光谱算法控制台专业内容改版 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 45 个算法的“算法原理、运行演示、适用场景、表单字段”升级为领导可快速理解、专业人员可深入审阅的渐进式内容。

**Architecture:** 保留现有 Vue 3 三个一级 Tab。算法原理专业内容继续按现有 `principles/l0.ts`、`l2.ts`、`l3.ts` 分层维护；运行演示复用同一份原理文档中的业务与工程说明，避免重复文案。表单字段的类型、默认值及专业解释由后端控制台元数据统一提供，前端只负责渐进式展示。

**Tech Stack:** Python 3、FastAPI、Vue 3.5、TypeScript 5.7、Vite 6、原生 `<details>` 渐进展开

## Global Constraints

- 覆盖全部 45 个算法，不只优化截图中的 NDVI。
- 所有内容以真实 `service.py`、testdata 和返回字段为准。
- 明确区分当前实现、标准方法和生产级完整做法。
- 中文表达专业、清晰、短句优先；首次出现缩写给出中英文全称。
- 代码注释统一使用中文。
- 不改变现有运行 API 路径和 multipart 协议。
- 不引入新的前端依赖。
- 不提交 Git commit，除非用户另行明确要求。

---

### Task 1: 扩展专业内容数据契约

**Files:**
- Modify: `algorithm/web/src/principles/types.ts`
- Modify: `algorithm/web/src/types.ts`
- Create: `algorithm/source/common/console_field_knowledge.py`
- Modify: `algorithm/source/common/console_catalog.py`
- Create: `algorithm/source/tests/test_console_professional_metadata.py`

**Interfaces:**
- Produces: `PrincipleDoc` 的专业章节字段，供 `PrinciplePanel`、`AlgoView` 读取。
- Produces: 扩展后的 `FieldRow` 字段，供 `RunForm` 与字段抽屉读取。
- Produces: `get_field_detail(algorithm_id: str, key: str, value: object) -> dict`。

- [ ] **Step 1: 编写失败的后端元数据测试**

测试至少断言：

```python
def test_all_algorithms_expose_professional_field_metadata():
    items = list_console_algorithms()
    assert len(items) == 45
    for item in items:
        for field in item["fields"]["inputs"]:
            assert field["label"]
            assert field["description"]
            assert "selectionGuide" in field
            assert "risk" in field


def test_ndvi_band_fields_explain_zero_based_index():
    item = get_console_algorithm("27_ndvi")
    red = next(row for row in item["fields"]["inputs"] if row["name"] == "params.red_band")
    assert red["unit"] == "波段索引（从 0 开始）"
    assert "不是波长值" in red["selectionGuide"]
    assert "620–680 nm" in red["selectionGuide"]
```

- [ ] **Step 2: 运行测试并确认因缺少扩展字段失败**

Run:

```bash
cd algorithm/source
python -m unittest tests.test_console_professional_metadata -v
```

Expected: FAIL，缺少 `label`、`selectionGuide` 或 `risk`。

- [ ] **Step 3: 扩展前端类型**

`FieldRow` 新增可选字段：

```ts
label?: string;
unit?: string;
default?: unknown;
defaultReason?: string;
range?: string;
selectionGuide?: string;
effect?: string;
risk?: string;
example?: string;
qualityCheck?: string;
downstreamUse?: string;
```

`PrincipleDoc` 新增：

```ts
summary: {
  definition: string;
  value: string;
  keyInput: string;
  keyOutput: string;
  keyLimit: string;
};
background: string[];
prerequisites: string[];
parameterNotes: Array<{
  name: string;
  role: string;
  guidance: string;
  effect: string;
  risk: string;
}>;
resultInterpretation: string[];
applicable: string[];
notApplicable: string[];
risks: string[];
upstream: string[];
downstream: string[];
demoFocus: string[];
```

- [ ] **Step 4: 建立后端字段知识库**

`console_field_knowledge.py` 提供：

```python
def get_field_detail(algorithm_id: str, key: str, value: object) -> dict:
    """返回字段的中文名称、单位、范围、选择方法、参数影响和误配风险。"""
```

知识库分三层合并：

1. 通用文件字段：`file`、`file2`。
2. 通用参数字段：波段索引、阈值、窗口、训练参数、几何参数。
3. `algorithm_id + key` 专属覆盖：解决同名 `method`、`mode`、`percentile` 在不同算法中的语义差异。

- [ ] **Step 5: 在 `console_catalog.py` 合并字段详情**

对 `file`、`file2` 和 `params.*` 均调用 `get_field_detail`。真实 testdata 值写入 `default` 和 `example`；原始文档输入说明保留在 `description`。

- [ ] **Step 6: 运行测试并确认通过**

Run:

```bash
cd algorithm/source
python -m unittest tests.test_console_professional_metadata -v
```

Expected: PASS，45 个算法所有输入字段均有基础专业信息。

---

### Task 2: 完善 L0 前至 L1→L2 的 16 个算法原理

**Files:**
- Modify: `algorithm/web/src/principles/l0.ts`

**Interfaces:**
- Consumes: Task 1 扩展后的 `PrincipleDoc`。
- Produces: 算法 01–16 的完整专业章节。

- [ ] **Step 1: 为 01–05 补齐采集规划与质检内容**

逐项补充 `summary`、问题背景、数据前提、参数敏感性、适用/不适用条件、风险、上下游关系和演示观察点。必须说明：

- 航线规划中的 GSD、航高、焦距、像元尺寸、重叠率关系。
- 时间同步的时钟偏差、插值和匹配容差。
- POS 解算的坐标系、姿态角约定和杠杆臂。
- 飞行质检中的位深饱和与相对 SNR 仅是告警指标。
- 云影规则对波段配置、地表高亮目标和低空数据的限制。

- [ ] **Step 2: 为 06–11 补齐辐射校正和相对归一内容**

必须说明暗电流、坏像元、条带、smile/keystone、gain/offset 和相对辐射归一之间的处理顺序，以及错误修正如何向后传播。

- [ ] **Step 3: 为 12–16 补齐反射率、几何定位与正射内容**

必须说明：

- ELM 经验线法的参考板与照明一致性。
- DOS2 的暗像元假设和简化大气模型边界。
- BRDF 几何角与模型核的意义。
- 直接定位与严格共线方程的差异。
- DEM、坐标参考系、内外方位元素对正射结果的影响。

- [ ] **Step 4: 运行 TypeScript 检查**

Run:

```bash
cd algorithm/web
npx vue-tsc --noEmit
```

Expected: PASS，01–16 均满足扩展后的 `PrincipleDoc`。

---

### Task 3: 完善 L2 的 10 个算法原理

**Files:**
- Modify: `algorithm/web/src/principles/l2.ts`

**Interfaces:**
- Consumes: Task 1 扩展后的 `PrincipleDoc`。
- Produces: 算法 17–26 的完整专业章节。

- [ ] **Step 1: 为 17–19 补齐镶嵌、匀光和多源配准内容**

说明地理重叠、接缝、羽化、辐射一致性、相位相关、亚像元位移和不同分辨率数据的限制。

- [ ] **Step 2: 为 20–24 补齐坏波段、平滑、归一、降维和选波段内容**

说明：

- SNR 与大气吸收窗的判定依据。
- Savitzky–Golay 窗口和多项式阶数的约束。
- SNV、Z-score、MinMax、L2 的不同用途。
- PCA 与 MNF 的噪声建模差异。
- 方差选波段与有监督 ANOVA F 的适用前提。

- [ ] **Step 3: 为 25–26 补齐超像素和 Patch 构建内容**

说明对象尺度、紧凑度、标签中心像元、边界填充、样本泄漏和类别不平衡风险。

- [ ] **Step 4: 运行 TypeScript 检查**

Run:

```bash
cd algorithm/web
npx vue-tsc --noEmit
```

Expected: PASS，17–26 均满足扩展后的 `PrincipleDoc`。

---

### Task 4: 完善 L3 至 L4 的 19 个算法原理

**Files:**
- Modify: `algorithm/web/src/principles/l3.ts`

**Interfaces:**
- Consumes: Task 1 扩展后的 `PrincipleDoc`。
- Produces: 算法 27–45 的完整专业章节。

- [ ] **Step 1: 为 27–31 补齐指数和红边参数内容**

必须说明波段索引与波长的区别、反射率前提、指数范围、饱和、土壤/大气背景和同名 NDWI 版本差异。

- [ ] **Step 2: 为 32–35 补齐回归、物理反演、传统分类和光谱匹配内容**

必须说明空间泄漏、训练/验证划分、LUT 网格、几何角、指标 OA/AA/Kappa、端元库一致性和未知类别拒识。

- [ ] **Step 3: 为 36–39 补齐深度学习和少样本内容**

说明输入张量、光谱与空间感受野、PCA 预降维、训练轮数、batch、随机种子、样本数量、过拟合和模型不确定性。

- [ ] **Step 4: 为 40–45 补齐探测、解混、异常、变化、后处理和地块汇总内容**

说明 ACE、FCLS、RX、IR-MAD 的统计假设，阈值百分位的相对性，丰度约束，配准误差，筛斑尺度和分区统计中的 NoData/像元面积问题。

- [ ] **Step 5: 运行 TypeScript 检查**

Run:

```bash
cd algorithm/web
npx vue-tsc --noEmit
```

Expected: PASS，27–45 均满足扩展后的 `PrincipleDoc`。

---

### Task 5: 重构算法原理页的渐进式展示

**Files:**
- Modify: `algorithm/web/src/components/PrinciplePanel.vue`
- Modify: `algorithm/web/src/components/PrincipleViz.vue`
- Modify: `algorithm/web/src/style.css`

**Interfaces:**
- Consumes: 扩展后的 `PrincipleDoc`。
- Produces: 首屏领导摘要、默认展开的核心原理、可展开的专家章节。

- [ ] **Step 1: 改造首屏摘要**

展示“一句话定义、核心价值、关键输入、关键输出、关键限制”。公式区保留在首屏，但变量解释进入专业章节。

- [ ] **Step 2: 增加默认展开的核心章节**

默认展示：

- 问题背景。
- 原理依据与计算步骤。
- 原理示意。
- 数据前提。
- 结果解读。

- [ ] **Step 3: 增加专业细节展开区**

使用原生 `<details>` 展示：

- 参数敏感性。
- 适用与不适用条件。
- 误差、风险与质量检查。
- 上下游关系。
- 本仓库与业界完整做法。
- 学完自检。

- [ ] **Step 4: 优化术语收集**

将新增章节加入 `termsForAlgorithm` 输入，保证新增缩写仍可显示释义。

- [ ] **Step 5: 优化样式与无障碍**

键盘焦点使用品牌色 `outline`，不移除焦点可见性；正文行宽、字号、行距和风险提示满足长文阅读；窄屏为单列。

- [ ] **Step 6: 运行类型检查与构建**

Run:

```bash
cd algorithm/web
npx vue-tsc --noEmit
npm run build
```

Expected: 两条命令均成功。

---

### Task 6: 重构运行演示与字段说明

**Files:**
- Modify: `algorithm/web/src/views/AlgoView.vue`
- Modify: `algorithm/web/src/components/RunForm.vue`
- Modify: `algorithm/web/src/style.css`

**Interfaces:**
- Consumes: `PrincipleDoc` 的 `summary`、`prerequisites`、`applicable`、`notApplicable`、`demoFocus`、`upstream`、`downstream`。
- Consumes: 后端扩展后的 `FieldRow`。
- Produces: 专业运行说明、场景说明和逐字段渐进帮助。

- [ ] **Step 1: 替换自动拼接的功能说明**

`AlgoView` 通过 `getPrinciple(algo.id)` 获取结构化内容，展示：

- 功能定位。
- 处理对象与变化。
- 主要产物与业务价值。
- 本次演示重点。
- 使用前提。

- [ ] **Step 2: 重构适用场景**

展示适用对象、推荐数据条件、可回答的问题、不建议场景和上下游组合，不再把原始 `scenario` 简单加“适用于”。

- [ ] **Step 3: 增加四步运行提示**

表单上方展示“准备数据 → 检查条件 → 设置参数 → 解读结果”，并明确示例默认参数不能照搬到其他传感器。

- [ ] **Step 4: 改造表单字段摘要**

默认显示：

- 中文名称、键名、类型、必填状态。
- 字段作用。
- 单位、范围、默认值。

文件字段同时说明格式、空间/波段/坐标要求。

- [ ] **Step 5: 增加字段详细说明**

每个字段用 `<details>` 展示：

- 默认值依据。
- 选择方法。
- 调大/调小影响。
- 错误配置风险。
- 示例值。

无内容的条目不渲染空标题。

- [ ] **Step 6: 同步字段抽屉**

输入和输出字段抽屉增加单位/范围、选择方法、风险、质量检查和下游用途，窄屏使用块状布局避免超宽表格。

- [ ] **Step 7: 运行类型检查与构建**

Run:

```bash
cd algorithm/web
npx vue-tsc --noEmit
npm run build
```

Expected: 两条命令均成功。

---

### Task 7: 全量内容与运行验收

**Files:**
- Verify only; fix scoped defects in files from Tasks 1–6.

**Interfaces:**
- Verifies: 45 个算法的专业内容、元数据和现有运行能力。

- [ ] **Step 1: 运行后端专业元数据测试**

Run:

```bash
cd algorithm/source
python -m unittest tests.test_console_professional_metadata -v
```

Expected: PASS。

- [ ] **Step 2: 验证 45 项元数据完整性**

执行脚本遍历 `list_console_algorithms()`，断言：

- 数量等于 45。
- 每个输入字段有 `label`、`description`、`selectionGuide`、`risk`。
- 每个算法至少有一个输出字段。
- 参数默认值与 testdata 一致。

- [ ] **Step 3: 运行前端静态验证**

Run:

```bash
cd algorithm/web
npx vue-tsc --noEmit
npm run build
```

Expected: PASS。

- [ ] **Step 4: 验证代表性页面**

检查：

- `01_flight_planning`：几何参数与航线业务。
- `10_radiance_calibration`：辐射参数与单位。
- `16_orthorectify`：DEM、坐标系与几何风险。
- `27_ndvi`：波段索引、反射率和指数解读。
- `34_svm_rf_classify`：标签、模型参数和精度指标。
- `37_cnn3d_classify`：Patch、PCA、训练参数。
- `42_anomaly_detect`：RX 窗口与阈值。
- `45_parcel_zonal_stats`：地块矢量、NoData 和统计输出。

- [ ] **Step 5: 检查现有演示不回归**

在已运行的 Vite 与 FastAPI 服务中，加载代表性算法示例数据，确认：

- 文件预览正常。
- 参数可编辑。
- 执行请求成功。
- 输出可视化正常。
- 三个一级 Tab 可切换。
