# 多光谱拼图可视化管控台（visual_server）

生产交付：参数配置 / 阶段执行控制 / 进度可视化 / 执行溯源。  
计算仍在宿主机 `source`，本目录 docker 只跑 **PostgreSQL + RabbitMQ + backend + frontend**。

## 快速启动

```bash
cd algorithm/projects/数据融合/prod/visual_server
cp .env.example .env
# 按需改 HOST_DATA_ROOT / JWT_SECRET / 密码
docker compose up -d --build
```

- 前端：http://localhost:8080  
- API：http://localhost:8000/api/health  
- RabbitMQ 管理：http://localhost:15672 （mosaic / mosaic_secret）  
- 默认管理员：`admin` / `admin123`（请立刻修改）

## 宿主机 Worker（必须）

```bash
cd ../source
export RABBITMQ_URL=amqp://mosaic:mosaic_secret@127.0.0.1:5672/
chmod +x scripts/run_worker.sh
./scripts/run_worker.sh
```

Worker 消费 `mosaic.jobs`，调用 `run_stages`，回传进度到 `mosaic.progress` / `mosaic.events`。

## 功能要点

| 能力 | 说明 |
| --- | --- |
| 按阶段参数 | 参数配置页分组 + 中文说明 |
| 仅 RGB | 预设 `rgb_preview` / `bands=["Color"]` |
| 阶段控制 | `run_mode`: full / until_stage / step；执行台「继续下一阶段」 |
| 溯源 | `job_runs.params_snapshot` + 目录字段 + 日志/报告下载 |
| CLI 教学 | 前端「命令行教学」页 = `source/docs/cli-usage.md` |

## 不部署可视化时

见 `../source/docs/cli-usage.md`，例如：

```bash
python -m ms_mosaic --input ... --out ... --bands Color
python -m ms_mosaic --input ... --out ... --run-mode until_stage --stop-after-stage S4_dsm
```

## 开发后端（无 compose）

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://mosaic:mosaic_secret@127.0.0.1:5432/mosaic_visual
export RABBITMQ_URL=amqp://mosaic:mosaic_secret@127.0.0.1:5672/
uvicorn app.main:app --reload --port 8000
```

## 测试

```bash
# source
cd ../source && PYTHONPATH=. pytest tests/test_progress_control.py -q

# backend（需在 backend 目录，PYTHONPATH=.）
cd ../visual_server/backend && PYTHONPATH=. pytest tests/test_job_paths.py -q
```
