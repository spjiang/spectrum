# 2026-09-19 visual_server 深色运维台 UI

## 目标
生产级多光谱拼图管控台：左侧深色侧栏 + 顶栏健康状态 + 内容区双栏执行台；并入库 MAX_20251017 复现模板。

## 视觉
- 侧栏 `#0B1220`，内容 `#111827`，面板 `#1A2332`，描边 `#2A3648`
- 主色 `#2F8CFF`；成功/警告/失败 `#3DDC97` / `#F5A524` / `#FF5C5C`
- Ant Design 5 dark algorithm + CSS 变量

## 布局
- `AppShell`：可折叠侧栏（执行台/参数/记录/CLI）+ 顶栏（健康点、运行中任务、用户）
- 执行台：左启动 / 右监控+日志
- 参数：左模板列表 / 右阶段表单
- 记录：表格+状态色标+日志抽屉

## 复现模板（对照 source/命令行说明.md）
1. `MAX_20251017 复现·套色快路径`（默认选中）— Color + 商业 GSD + benchmark + match_reference_color + reuse_dsm(full_surface) + cache
2. `MAX_20251017 复现·RGB全流程` — 同上但不 reuse_dsm
3. `默认生产模板` — 8 波段通用
4. `仅 RGB 快速预览` — Color 快速几何

新增参数键：`benchmark_dir`、`match_reference_color`。
