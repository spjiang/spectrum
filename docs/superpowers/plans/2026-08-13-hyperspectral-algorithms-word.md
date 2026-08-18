# 高光谱 45 项算法能力 Word Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 生成一份面向领导汇报、含 45 项算法详解、统一封装策略、架构图和真实服务截图的正式 Word。

**Architecture:** 以三份 Markdown 为权威数据源，通过 Python 解析算法清单与 API 状态，生成结构化算法数据；使用 Matplotlib/Graphviz 风格绘制架构图，启动 FastAPI 并采集真实接口与产物截图；最后用 python-docx 统一排版成可复现的 `.docx`。

**Tech Stack:** Python 3、python-docx、Markdown/正则解析、Matplotlib、FastAPI、HTTPX/requests、Playwright（Swagger 页面截图，若环境不可用则用真实 OpenAPI/JSON 渲染截图）

## Global Constraints

- 输出文件：`algorithm/docs/高光谱45项算法能力与服务封装方案.docx`
- 图片目录：`algorithm/docs/word-assets/`
- 生成脚本：`algorithm/docs/build_algorithm_word.py`
- 45 项必须连续、无遗漏、无重复。
- 最新状态采用 API 测试清单：12 项可运行、33 项骨架。
- 骨架项不得描述为已实现；HTTP 200 只代表接口契约可达。
- 至少 2 张架构图、3 张真实服务/产物截图。
- 所有新增代码注释使用中文。
- 不提交生成物或代码，除非用户另行明确要求。

---

### Task 1: 建立结构化算法数据与一致性校验

**Files:**
- Create: `algorithm/docs/build_algorithm_word.py`
- Read: `algorithm/docs/采集到算法-算法清单.md`
- Read: `algorithm/docs/当前服务简单介绍.md`
- Read: `algorithm/docs/算法API测试清单.md`

**Interfaces:**
- Produces: `parse_algorithms() -> list[dict]`
- Produces: `validate_algorithms(items: list[dict]) -> None`
- 每个条目字段：`number,id,title,level,status,summary,purpose,scenario,input,output,params`

- [ ] **Step 1:** 编写解析器，优先从 API 清单逐项章节提取 45 项完整字段，从状态总表提取 ID/状态。
- [ ] **Step 2:** 编写校验：断言编号等于 `list(range(1, 46))`、ID 唯一、可运行数为 12、骨架数为 33。
- [ ] **Step 3:** 运行：

```bash
python algorithm/docs/build_algorithm_word.py --validate-only
```

预期输出：

```text
算法数据校验通过：45 项；可运行 12；骨架 33
```

---

### Task 2: 生成正式架构图

**Files:**
- Modify: `algorithm/docs/build_algorithm_word.py`
- Create: `algorithm/docs/word-assets/l0-l4-pipeline.png`
- Create: `algorithm/docs/word-assets/service-architecture.png`
- Create: `algorithm/docs/word-assets/request-flow.png`

**Interfaces:**
- Produces: `build_diagrams(asset_dir: Path) -> list[Path]`

- [ ] **Step 1:** 用 Matplotlib 绘制 L0→L4 数据处理链，标出 45 项算法分布与每层典型交付。
- [ ] **Step 2:** 绘制“调用方→FastAPI→统一契约→算法适配器→CPU/GPU→产物管理”封装架构图。
- [ ] **Step 3:** 绘制“GeoTIFF/GeoJSON/CSV→run→JSON+专题图/统计表”的请求数据流。
- [ ] **Step 4:** 校验三张 PNG 分辨率不低于 1800×900，中文字体可显示且无裁切。

---

### Task 3: 启动服务并采集真实截图

**Files:**
- Read: `algorithm/source/scripts/start.sh`
- Create: `algorithm/docs/word-assets/swagger-overview.png`
- Create: `algorithm/docs/word-assets/algorithm-list.png`
- Create: `algorithm/docs/word-assets/ndvi-result.png`
- Create: `algorithm/docs/word-assets/anomaly-result.png`
- Create: `algorithm/docs/word-assets/classification-result.png`

**Interfaces:**
- Consumes: `http://127.0.0.1:28800`
- Produces: `capture_service_assets(asset_dir: Path) -> dict[str, Path]`

- [ ] **Step 1:** 检查已有终端，确认服务是否运行；未运行则在 `algorithm/source` 启动 `./scripts/start.sh`。
- [ ] **Step 2:** 调用 `/api/v1/algorithms`，保存真实 45 项响应并渲染列表截图。
- [ ] **Step 3:** 对 NDVI、分类、异常检测各执行一次真实请求；保存响应 JSON 和输出产物。
- [ ] **Step 4:** 使用 Playwright 截取 `/docs`；若 Playwright 不可用，安装最新版本并安装 Chromium。
- [ ] **Step 5:** 将 GeoTIFF/JSON 产物绘制为标注清晰的 PNG，标题注明算法、输入和来源为本地实测。
- [ ] **Step 6:** 核验截图不含本机密钥、用户隐私或无关路径。

---

### Task 4: 编写 45 项增强说明

**Files:**
- Modify: `algorithm/docs/build_algorithm_word.py`

**Interfaces:**
- Produces: `enrich_algorithm(item: dict) -> dict`
- 新增字段：`principle,business_value,packaging_strategy,production_note`

- [ ] **Step 1:** 按 L0–L4 编写每项 2–4 句原理与解决问题说明，避免只复述“一句话”。
- [ ] **Step 2:** 为每项写具体封装建议：同步/异步、CPU/GPU、依赖文件、输出产物、生产限制。
- [ ] **Step 3:** 对 33 个骨架项统一添加明确状态声明；对 12 个可运行项按源码说明现有实现。
- [ ] **Step 4:** 执行文本校验：每项 `principle`、`packaging_strategy` 不少于 30 个中文字符。

---

### Task 5: 生成 Word

**Files:**
- Modify: `algorithm/docs/build_algorithm_word.py`
- Create: `algorithm/docs/高光谱45项算法能力与服务封装方案.docx`

**Interfaces:**
- Produces: `build_document(items, assets, output_path) -> Path`

- [ ] **Step 1:** 配置 A4、页边距、中文字体、标题层级、页眉页脚、页码与自动目录域。
- [ ] **Step 2:** 写执行摘要，明确“45 项接口覆盖；12 项可运行；33 项骨架；45/45 HTTP 200”。
- [ ] **Step 3:** 插入 L0–L4 总图、服务架构、调用链及图片题注。
- [ ] **Step 4:** 生成 45 项总览表。
- [ ] **Step 5:** 按 L0–L4 分组生成 45 项详解，每项包含九个固定字段与状态标签。
- [ ] **Step 6:** 写完整封装策略：API、契约、适配、数据、执行、治理、交付七层。
- [ ] **Step 7:** 插入真实 Swagger、接口列表和典型产物截图。
- [ ] **Step 8:** 写生产化路线与附录调用示例。

---

### Task 6: 文档质量验收

**Files:**
- Read: `algorithm/docs/高光谱45项算法能力与服务封装方案.docx`
- Optionally Create: `algorithm/docs/word-assets/docx-preview.pdf`

**Interfaces:**
- Produces: 验收结果与最终文件路径

- [ ] **Step 1:** 用 python-docx 回读，断言 45 个算法标题均出现一次。
- [ ] **Step 2:** 解包 DOCX，确认所有图片关系有效，无缺图。
- [ ] **Step 3:** 使用 LibreOffice（若已安装）无界面转换 PDF，检查转换退出码与页数；未安装则用 DOCX 结构校验替代并明确说明。
- [ ] **Step 4:** 检查敏感信息：API Key、`.env` 内容不得出现。
- [ ] **Step 5:** 汇报 Word 路径、页数/文件大小、截图数量、45 项状态统计及未完成限制。
