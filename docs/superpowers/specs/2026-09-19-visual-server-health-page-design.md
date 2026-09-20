# 2026-09-19 visual_server 健康检查页

## 目标

将 PostgreSQL / RabbitMQ 状态从顶栏挪到独立「健康检查」菜单页，并增加对主命令行程序（`ms_mosaic`）的**可调用**探测；主程序路径可由页面配置（写入 `system_settings`），与后续 worker 起任务共用同一套解析逻辑。

## 已确认决策

| 项 | 选择 |
| --- | --- |
| 探测深度 | A：可调用（按配置执行探测参数，退出码 0 即 ok） |
| 顶栏绿灯 | A：完全移除，其它页不再轮询 health |
| 方案 | 1：配置拆分 + 专用页；页面可编辑写入 DB（覆盖 env） |
| 编辑权限 | B：admin + configurator |

## 页面与导航

- 侧栏 **「健康检查」** `/health`；顶栏无健康灯。
- 三项状态 + 主命令行表单（解释器 / 模块 / 工作目录 / 探测参数）+「保存并检查」/「重新检查」。
- 无写权限时表单只读。

## 配置优先级

1. `system_settings.key=cli`（页面保存）
2. 环境变量 `CLI_PYTHON` / `CLI_MODULE` / `CLI_CWD` / `CLI_PROBE_ARGS`
3. 默认：`sys.executable`、`ms_mosaic`、`{DATA_ROOTS[0]}/source`、`-h`

## API

- `GET /api/health`：仅 PG+RQ（无 CLI）
- `GET /api/system/status`：PG+RQ+CLI+`cli_config`+`can_edit_cli`
- `PUT /api/system/cli-config`：admin/configurator；保存后立即按新配置探测并返回完整 status
