# AI 探索赋能分析方案 A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「大模型赋能分析」从三项护栏改成四段：提高本次运行、接到应用、方法限制、拦住说错。

**Architecture:** 扩展 `llmLeverage` 增加 `sections`；分析页渲染四段专属正文；原三维分数仅保留给效果页计量。45 项均手写，禁止默认句充数。

**Tech Stack:** Python/pytest；Vue 3；现有 l3_aide 知识接口。

## Global Constraints

- 大模型不重算、不改代码、不改推其他算法、不输出处方。
- 应用路径必须含「这是下游用法」且不是本页已交付产品。
- 文案不得与已审查科学主张冲突。
- 不自动创建 Git commit。

---

### Task 1: 契约测试与数据模型

**Files:**
- Modify: `algorithm/source/tests/test_l3_aide.py`
- Modify: `algorithm/source/common/l3_aide/knowledge.py`
- Modify: `algorithm/web/src/types.ts`

- [x] 写失败测试：45 项均有四段；标签固定；toApplication 含「这是下游用法」；无三项旧标签作为分析页唯一结构；NDVI 含反射率、饱和、不能直接作为叶绿素/生物量。
- [x] 跑测试确认失败。
- [x] 实现 `sections` 与 45 项专属正文；`llm_leverage_of` 返回 sections + 保留 dims 分数。
- [x] 提示词加入下游限定要求。
- [x] 测试通过。

### Task 2: 前端分析页

**Files:**
- Modify: `algorithm/web/src/components/AiExplorePanel.vue`
- Modify: `algorithm/web/src/types.ts`

- [x] 分析页渲染 `sections` 四段；导语改为提高本次运行与接到应用。
- [x] `npm run build` 通过。

### Task 3: 回归

- [x] `pytest tests/test_l3_aide.py -q`
- [x] 本地 5173 可加载 NDVI 赋能分析四段。
