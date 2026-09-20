# 多光谱拼图命令行使用说明

先进入**主程序安装目录**再执行命令。下文相对路径都相对该目录，与文件夹叫什么无关。

---

## 一、部署与安装

### 1.1 主程序目录

安装后工作目录就是这一层（名称不限），不要再往上找仓库布局：

```text
./
├── ms_mosaic/     # Python 包（入口 python -m ms_mosaic）
├── tests/
├── scripts/
├── docs/          # 本手册
├── runs/          # 运行输出（默认 --out 落在这里）
├── run.sh
└── README.md
```

`--input` 可以指向本目录以外的航摄数据。`--out` 默认写到本目录的 `runs/`。

### 1.2 准备 Python 环境

需要能 `import rasterio, numpy, cv2` 的 Python 3。解释器路径按本机设置：

```bash
# 本机默认（run.sh 已写死，可用 MS_MOSAIC_PYTHON 覆盖）
PY="/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/source/.venv/bin/python"
"$PY" -c "import rasterio, numpy, cv2; print('ok', rasterio.__version__)"
```

没有现成环境时，在主程序目录创建即可：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install rasterio numpy opencv-python tifffile Pillow scipy
export MS_MOSAIC_PYTHON="$(pwd)/.venv/bin/python"
```

`run.sh` 读取环境变量 `MS_MOSAIC_PYTHON`。

### 1.3 校验可运行

```bash
cd /Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/server/worker
"$PY" -m ms_mosaic --help
./run.sh --help
```

### 1.4 读写约定（生产必守）

| 项 | 规则 |
| --- | --- |
| `--input` | 拍完后的 `MAX_*` 任务目录，**只读** |
| `--out` | 本次运行输出根；其下生成 `拼图结果/`、`附件/`、`cache/`、`log/` 等 |
| 禁止 | `--out` 落在 `--input` 目录树内 |
| 默认行为 | 通用任务：UTM + 航高估 GSD + 足迹格网；**不会**因旁边有参考 `拼图结果/` 就自动锁格或套色 |

---

## 二、命令行参数说明

入口：

```bash
"$PY" -m ms_mosaic --input <MAX目录> --out <输出根> [选项...]
# 或
./run.sh [选项...]     # 未写 --out 时落到 runs/manual_时间戳
```

### 2.1 必填 / 路径

| 参数 | 含义 |
| --- | --- |
| `--input` | 拍完后的 `MAX_*` 目录 |
| `--out` | 输出根目录 |
| `--cache-dir` | 特征/空三缓存；续跑可复用，避免重复提特征 |
| `--reuse-dsm` | 已有 `DSM.tif`，跳过密集匹配 |
| `--benchmark-dir` | 对照该目录写 `比对报告.txt`。不改格网、覆盖、颜色 |
| `--workers` | 密集匹配 / 正射进程数，默认 CPU−1 |

### 2.2 波段与分辨率

| 参数 | 含义 |
| --- | --- |
| `--bands` | 逗号分隔。省略 = 8 波段全量 `Color,450nm,…,850nm`。仅 RGB：`Color` |
| `--dsm-gsd` | DSM 地面分辨率（米）；省略则按航高/焦距估计，正射为其一半 |
| `--match-reference-color` | 调试套色，合格主路径不要开 |

### 2.3 运行模式与阶段

| 参数 | 含义 |
| --- | --- |
| `--run-mode` | `full` 全流程（默认）；`until_stage` 跑到停点；`step` 只跑起始阶段 |
| `--start-stage` | 起始阶段，如 `S0_io` / `S2_at` / `S5_ortho` |
| `--stop-after-stage` | `until_stage` 时在该阶段结束后停止（返回码 10） |

阶段顺序：`S0_io → S1_catalog → S2_at → S3_dense → S4_dsm → S5_ortho → S6_report`。

### 2.4 调试（非交付）

| 参数 | 含义 |
| --- | --- |
| `--max-frames` | 只用前 N 个可用曝光 |
| `--max-index` | 只扫描文件名编号 ≤ 该值的曝光 |

### 2.5 退出码

| 码 | 含义 |
| --- | --- |
| 0 | 成功 |
| 10 | 阶段完成，等待继续（`awaiting_continue`） |
| 2 | 失败 |
| 130 | 取消 |

### 2.6 成果布局（相对 `--out`）

| 路径 | 内容 |
| --- | --- |
| `拼图结果/DSM.tif` | DSM |
| `拼图结果/Orthomosaic_pix_surf_group0.tif` | RGB 正射 |
| `拼图结果/Orthomosaic_pix_surf_group1.tif` … `group7.tif` | 全量时的 7 个多光谱 |
| `质量报告.pdf` | 自研质量报告 |
| `比对报告.txt` | 仅设置了 `--benchmark-dir` 时生成 |

---

## 三、本机测区示例（MAX_20251017）

下面都是这台机器上的绝对路径，进主程序目录后可直接复制执行。

```bash
cd "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/server/worker"

PY="/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/source/.venv/bin/python"
INPUT="/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/docs/需求/测试正式数据/MAX_20251017/MAX_20251017_001"
BENCH="/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/docs/需求/测试正式数据/MAX_20251017/拼图结果"
CACHE="/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/runs/full_MAX_20251017_001/cache/features"
DSM="/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/runs/full_surface_rgb/拼图结果/DSM.tif"
```

```bash
test -d "$INPUT" && echo "测区数据 OK"
```

> 正在跑的任务不要再往同一个 `--out` 写。

### 3.1 本测区出图

```bash
"$PY" -u -m ms_mosaic \
  --input "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/docs/需求/测试正式数据/MAX_20251017/MAX_20251017_001" \
  --out "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/server/worker/runs/replay_max_20251017_rgb" \
  --bands Color \
  --cache-dir "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/runs/full_MAX_20251017_001/cache/features" \
  --workers 12
```

要顺便对照商业尺子、写出 `比对报告.txt`，**多加一行即可**，出图不变：

```bash
  --benchmark-dir "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/docs/需求/测试正式数据/MAX_20251017/拼图结果"
```

不要加 `--match-reference-color`。那是把商业颜色抄过来，调算法时开了等于作弊。

### 3.2 复用已有 DSM 只重做正射

```bash
"$PY" -u -m ms_mosaic \
  --input "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/docs/需求/测试正式数据/MAX_20251017/MAX_20251017_001" \
  --out "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/server/worker/runs/replay_max_20251017_smooth" \
  --bands Color \
  --reuse-dsm "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/runs/full_surface_rgb/拼图结果/DSM.tif" \
  --cache-dir "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/runs/full_MAX_20251017_001/cache/features" \
  --workers 12
```

### 3.3 跑全量（RGB + 7 多光谱）

```bash
"$PY" -u -m ms_mosaic \
  --input "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/docs/需求/测试正式数据/MAX_20251017/MAX_20251017_001" \
  --out "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/server/worker/runs/full_surface_all" \
  --cache-dir "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/runs/full_MAX_20251017_001/cache/features" \
  --workers 12
```

### 3.4 阶段调试 / 少帧预览

```bash
"$PY" -u -m ms_mosaic \
  --input "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/docs/需求/测试正式数据/MAX_20251017/MAX_20251017_001" \
  --out "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/server/worker/runs/dbg_until_dsm" \
  --bands Color \
  --run-mode until_stage \
  --stop-after-stage S4_dsm

./run.sh --max-frames 12 --bands Color \
  --out "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/server/worker/runs/preview_rgb"
```

### 3.5 如何确认跑完

```bash
pgrep -lf ms_mosaic
ls -lh "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/server/worker/runs/replay_max_20251017_rgb/拼图结果"
ls "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/server/worker/runs/replay_max_20251017_rgb/比对报告.txt"
grep 未达标 "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合/prod/server/worker/runs/replay_max_20251017_rgb/比对报告.txt"
```

进程已退出且 `拼图结果/` 已写出，才算本趟结束。
