# 高光谱算法体系 v4 PPT Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 保留 v3 的 62 页结构，生成视觉统一、内容专业、状态口径准确的政企科技蓝版 `高光谱算法体系-v4.pptx`。

**Architecture:** 复用现有 `generate_training_ppt.py` 中的 45 项专业增强内容，新建 v4 专用生成脚本，统一设计令牌、页面模板和状态口径。使用 python-pptx 生成并回读校验，再通过 Keynote 导出 PDF/预览图进行视觉抽检。

**Tech Stack:** Python 3、python-pptx、Keynote/AppleScript（只用于渲染验收）、Markdown 数据源

## Global Constraints

- 输入：`algorithm/docs/高光谱算法体系-v3.pptx`
- 输出：`algorithm/docs/高光谱算法体系-v4.pptx`
- v3 不覆盖。
- 页数必须为 62。
- 45 项算法编号连续、标题完整。
- 状态口径必须为 12 项可运行、33 项骨架。
- 所有新增代码注释使用中文。
- 未经用户明确要求不创建 Git 提交。

---

### Task 1: 固化内容数据与状态口径

**Files:**
- Create: `algorithm/docs/generate_training_ppt_v4.py`
- Read: `algorithm/docs/generate_training_ppt.py`
- Read: `algorithm/docs/采集到算法-算法清单.md`
- Read: `algorithm/docs/算法API测试清单.md`

**Interfaces:**
- Produces: `parse_algorithms(md_text: str) -> list[dict]`
- Produces: `validate_content(algorithms: list[dict]) -> None`

- [ ] 复制现有 45 项 `ENRICH` 专业内容到 v4 生成器，保留方法、价值、风险、流程和工程提示。
- [ ] 从 API 测试清单解析最新状态，得到可运行集合 `{12,20,21,22,23,27,28,34,37,40,42,45}`。
- [ ] 校验 45 项编号连续、algorithm_id 唯一、状态统计为 12/33。
- [ ] 修正服务能力页中“已实现 9/11 项”等旧口径，统一为“12 项可运行、33 项骨架”。

验证命令：

```bash
algorithm/source/.venv/bin/python algorithm/docs/generate_training_ppt_v4.py --validate-only
```

预期：

```text
内容校验通过：45 项；可运行 12；骨架 33
```

---

### Task 2: 建立统一设计系统与页面组件

**Files:**
- Modify: `algorithm/docs/generate_training_ppt_v4.py`

**Interfaces:**
- Produces: `Theme` 配色/字体/字号常量
- Produces: `add_header()`、`add_footer()`、`add_status_badge()`、`add_card()`、`add_flow_node()`

- [ ] 定义政企科技蓝设计令牌：深蓝、科技青、浅蓝灰、正文深灰、橙色风险色。
- [ ] 字体统一为中文 `Noto Sans SC`、英文数字 `Inter`。
- [ ] 标题、正文、图注和标签分别限定为 30、17、12、12 pt 左右，单页不超过 4 个字号层级。
- [ ] 页眉统一显示章节/层级，页脚统一显示文档名和 `当前页 / 62`。
- [ ] 卡片统一采用白底、浅灰描边、小圆角，不使用阴影、渐变和多色装饰。
- [ ] 可运行使用青绿色标签；骨架使用橙色标签并显示“接口已预留，核心算法待实现”。

---

### Task 3: 重建 62 页并专业化文案

**Files:**
- Modify: `algorithm/docs/generate_training_ppt_v4.py`
- Create: `algorithm/docs/高光谱算法体系-v4.pptx`

**Interfaces:**
- Produces: `build_presentation() -> Presentation`

- [ ] 按 v3 顺序生成封面、目录、第一部分架构、第二部分 45 项算法、第三部分服务、总结和致谢，共 62 页。
- [ ] 修复所有残缺标题，算法页标题严格使用 `NN. 中文名称`。
- [ ] 架构页优先使用 L0→L4 流程、双业务链、文件格式矩阵，减少连续段落。
- [ ] 每个算法页统一为五区：
  - 解决问题
  - 技术原理
  - 输入/输出
  - 业务价值
  - 状态/工程提示
- [ ] 服务页明确统一 API 契约、12/33 状态、能力边界和生产化路线。
- [ ] 保存为 `algorithm/docs/高光谱算法体系-v4.pptx`。

---

### Task 4: 自动化结构与版面校验

**Files:**
- Create: `algorithm/docs/validate_training_ppt_v4.py`
- Read: `algorithm/docs/高光谱算法体系-v4.pptx`

**Interfaces:**
- Produces: PPT 校验报告

- [ ] 回读 PPT，断言幻灯片数量等于 62。
- [ ] 断言 45 个算法标题均出现且编号连续。
- [ ] 统计字体仅允许 `Noto Sans SC`、`Inter` 及必要回退字体。
- [ ] 统计可运行标签 12 个、骨架标签 33 个。
- [ ] 检测文本框越过页面边界、空标题、仅编号标题和小于 11 pt 的正文。
- [ ] 检测包含“已实现 9 项”“其余 36 项”“已实现 11 项”“其余 34 项”等过期口径。

验证命令：

```bash
algorithm/source/.venv/bin/python algorithm/docs/validate_training_ppt_v4.py
```

预期：

```text
PPT 校验通过：62 页；45 项算法；12 可运行；33 骨架；0 个越界文本框
```

---

### Task 5: 渲染预览与视觉抽检

**Files:**
- Create: `algorithm/docs/ppt-v4-preview/`
- Optionally Create: `algorithm/docs/高光谱算法体系-v4.pdf`

**Interfaces:**
- Produces: 至少 6 张关键页预览图

- [ ] 优先使用 Keynote 打开 v4 并导出 PDF；若系统自动化权限受限，保留 PPT 并用结构校验替代 PDF。
- [ ] 生成封面、L0–L4 架构、算法总览、典型可运行算法、典型骨架算法、服务能力和总结页预览。
- [ ] 人工抽检标题对齐、正文可读性、状态颜色、文本溢出和投屏对比度。
- [ ] 最终汇报输出文件、页数、文件大小、预览数量和未完成限制。
