# 算法可视化控制台 Implementation Plan

> **For agentic workers:** 按任务顺序实现；每完成一块用 curl/页面验收。

**Goal:** 独立 Vite 控制台（5173）+ FastAPI `/api/v1/console/*`，领导可看 L0–L4 架构与 45 项算法输入/输出可视化。

**Architecture:** 后端白名单读 testdata/outputs，tif 转 PNG；前端 Vue3 只请求 `/api`（Vite 代理 28800）。

**Tech Stack:** FastAPI, rasterio, matplotlib, Vue 3, Vite, ECharts, Leaflet

## Global Constraints

- 不改 45 项 `service.run` 的 `files` 磁盘路径（冒烟 45/45 必须保持）
- 前端禁止 `file://` 或绝对磁盘路径当图片
- 中文 UI 与中文注释
- CORS 允许 5173；Vite proxy `/api` → 28800

---

### Task 1: 后端 console 路径/预览/目录/路由
### Task 2: 挂载 CORS、console 路由、outputs 静态
### Task 3: Vite Vue 工程与页面
### Task 4: 验收代表算法可视化 + 冒烟回归
