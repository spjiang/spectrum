# L3 AI 参谋目录钻取 Implementation Plan

> **For agentic workers:** 本会话按用户「实施」在当前仓库内联执行，不另开 worktree。

**Goal:** 5174 变为整层 L3 入口 + 27–43 各一页三栏知识与 testdata 演示。

**Architecture:** 知识库与单算法 run 放在 `l3_aide`；首页 `/run` 不变。`ai-web` 加侧栏路由。

**Tech Stack:** FastAPI、unittest、Vue 3、Vue Router、Vite。

## Global Constraints

- 不改 27–43 的 `/run` 契约与公式。
- 立方体/GeoTIFF/PNG 不进大模型。
- `accuracy` 条目不得包含「大模型」。
- 建议与 `runComment` 不是处方。

### Task 1: 知识库与 HTTP

- Create: `algorithm/source/common/l3_aide/knowledge.py`
- Modify: `algorithm/source/common/l3_aide/runner.py`、`narrator.py`、`interpreter.py`、`router.py`
- Test: `algorithm/source/tests/test_l3_aide.py`

### Task 2: ai-web 壳与两页

- Modify: `ai-web/src/*`，增加 `vue-router`
- 路由 `/` 与 `/algo/:id`
