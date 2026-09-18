# 多光谱拼图命令行使用说明

不部署 `visual_server` 时，可直接在宿主机用本目录运行。

## 环境

```bash
cd algorithm/projects/数据融合/prod/source
# 按项目依赖安装 rasterio / opencv / numpy 等
```

## 全流程（8 波段）

```bash
python -m ms_mosaic \
  --input /data/MAX_20251017_001 \
  --out /data/runs/full_01
```

## 仅 RGB 快速看结果

只正射 `Color`，跳过 7 个光谱通道，显著缩短 S5：

```bash
python -m ms_mosaic \
  --input /data/MAX_20251017_001 \
  --out /data/runs/rgb_preview \
  --bands Color
```

可再叠加少帧调试：

```bash
python -m ms_mosaic --input ... --out ... --bands Color --max-frames 30
```

## 跑到指定阶段后停下（验收再继续）

```bash
# 先跑到 DSM
python -m ms_mosaic --input ... --out /data/runs/dbg \
  --run-mode until_stage --stop-after-stage S4_dsm
# 退出码 10 = awaiting_continue
```

确认 DSM 无误后，继续正射（可仅 RGB）：

```bash
python -m ms_mosaic --input ... --out /data/runs/dbg \
  --run-mode until_stage --start-stage S5_ortho --stop-after-stage S5_ortho \
  --bands Color --reuse-dsm /data/runs/dbg/拼图结果/DSM.tif
```

## 逐步确认（每阶段停一次）

```bash
python -m ms_mosaic --input ... --out ... --run-mode step --start-stage S2_at
```

## 复用 DSM

```bash
python -m ms_mosaic --input ... --out ... --reuse-dsm /path/to/DSM.tif --bands Color
```

## 退出码

| 码 | 含义 |
| --- | --- |
| 0 | 成功（全流程 succeeded） |
| 10 | 阶段完成，等待继续（awaiting_continue） |
| 2 | 失败 |
| 130 | 取消 |

## 可视化服务（可选）

见 `../visual_server/README.md`：docker compose 起 PG/RabbitMQ/前后端，宿主机再起 worker。
