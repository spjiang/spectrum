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
| `--out` | 本次运行输出根；航摄原片不写回 `--input`，成果全部落在此目录 |
| 禁止 | `--out` 落在 `--input` 目录树内 |
| 默认行为 | 通用任务：UTM + 航高估 GSD + 足迹格网；**不会**因旁边有参考 `拼图结果/` 就自动锁格或套色 |

`--out` 下各子目录分工如下（交付看 `拼图结果/`，出问题查 `log/`）：

```text
--out/
  拼图结果/          正式交付：DSM 与各波段正射 GeoTIFF
  附件/              辅助查看：伪彩、测区 KML、拼接线
  cache/             中间缓存：特征点与空三，续跑可复用
  log/               运行日志与暂停/继续控制
  report/            质量报告附图与 JSON/Markdown
  质量报告.pdf
  比对报告.txt       仅设置了 --benchmark-dir 时出现
```

| 目录 / 文件 | 存放什么 | 起什么作用 |
| --- | --- | --- |
| `拼图结果/` | `DSM.tif`；`Orthomosaic_pix_surf_group0.tif`（RGB 正射）；`group1`～`group7`（450–850 nm 多光谱正射） | **主交付**。坐标系、GSD、覆盖以这里为准，下载与验收都看这一层 |
| `附件/` | `DSM_pseudocolor.tif`（高程伪彩）；`area.kml`（测区范围，可在地球软件打开）；`seamlines.geojson`（正射拼接线） | 给人看缝、看范围、看高程起伏，一般不当主成果 |
| `cache/` | `features/`（每张影像的 RootSIFT 特征）；`at_result.npz`（空三：相机、姿态、稀疏点） | 中途失败或只重做正射时不必从提特征重跑。清空则空三重做 |
| `log/` | `run.log`（文本日志，界面可拉进度）；`run.json`（质量统计副本）；`control.json`（暂停/继续/取消） | 查这次怎么跑的、任务卡在哪 |
| `report/` | `quality.json`、`quality.md`、`figures/` | 质量报告的数据和插图源 |
| `质量报告.pdf` | 空三精度、覆盖、重叠等汇总 | 给人阅读的报告 |
| `比对报告.txt` | 与商业 `拼图结果/` 的 CRS、GSD、格网、覆盖对照 | 只当尺子，**不改出图** |

---

## 二、命令行参数说明

入口：

```bash
"$PY" -m ms_mosaic --input <MAX目录> --out <输出根> [选项...]
# 或
./run.sh [选项...]     # 未写 --out 时落到 runs/manual_时间戳
```

阶段顺序：`S0_io → S1_catalog → S2_at → S3_dense → S4_dsm → S5_ortho → S6_report`。左侧目录按阶段展开，点参数名跳到说明。

### 1 输入输出（S0_io）

校验路径、创建输出目录。成果不得写回航摄原片。

#### 1.1 --input

拍完后的 `MAX_*` 任务目录，**只读**。本机有默认测区时可省略。

#### 1.2 --out

本次运行输出根。其下生成 `拼图结果/`、`附件/`、`cache/`、`log/` 等。禁止落在 `--input` 目录树内。目录含义见 **1.4**。

#### 1.3 --run-mode

`full` 全流程（默认）；`until_stage` 跑到停点；`step` 只跑起始阶段。

#### 1.4 --start-stage

起始阶段，如 `S0_io` / `S2_at` / `S5_ortho`。从密集匹配之后续跑须已有空三缓存。

#### 1.5 --stop-after-stage

`until_stage` 时在该阶段结束后停止（返回码 10）。例如先停在 `S4_dsm` 看 DSM，再决定是否正射。

#### 1.6 --grid-reference

锁定交付格网：取该目录或 GeoTIFF 的 GSD/原点/宽高。只锁格网，高程与颜色仍自算。合格主路径可不填。

### 2 影像编目（S1_catalog）

扫描曝光、读 POS，丢掉白板与无效帧。

#### 2.1 --max-frames

过滤后只用前 N 个可用曝光。交付留空；调试可缩小。

#### 2.2 --max-index

只扫描文件名编号 ≤ 该值的曝光。用于局部调试。

### 3 空三解算（S2_at）

主波段提特征、匹配、平差。结果写入 `cache/`。

#### 3.1 --cache-dir

特征与空三缓存目录。指向已有 `features` 可跳过提特征。默认 `{--out}/cache/features`。

#### 3.2 --workers

进程数。空三/密集匹配/正射共用此上限，默认 CPU−1。内存不够时系统会自动下调。

### 4 密集匹配（S3_dense）

在 DSM 格网上求每个点的高程。可跳过本阶段、直接复用已有 DSM。

#### 4.1 --reuse-dsm

已有 `DSM.tif` 路径。填写后跳过密集匹配，按足迹补覆盖缺口，适合只重做正射。

#### 4.2 --dsm-gsd

DSM 地面分辨率（米）。省略则按航高/焦距估计，正射为其一半。不要为对齐某份商业图手写。

#### 4.3 --terrain-margin-lo-m

DSM 合理高程带下余量（米），空三点 p1 再往下留。默认 30。

#### 4.4 --terrain-margin-hi-m

DSM 合理高程带上余量（米），空三点 p99 再往上留。默认 50。

#### 4.5 --terrain-min-half-span-m

无空三参考时，DSM 中值 ± 半宽的下限（米）。默认 80。

### 5 DSM 生成（S4_dsm）

去尖刺、补洞，写出 `拼图结果/DSM.tif`。本阶段命令行无额外开关，受上一阶段 `--dsm-gsd` 与地形余量约束。

### 6 正射镶嵌（S5_ortho）

按 DSM 真正射并镶嵌成大图。

#### 6.1 --bands

逗号分隔。省略 = 8 波段全量 `Color,450nm,…,850nm`。仅 RGB 预览：`Color`。

### 7 质量报告（S6_report）

写出 `质量报告.pdf`。可选对照商业成品。

#### 7.1 --benchmark-dir

对照该目录写 `比对报告.txt`。不改格网、覆盖、颜色。留空则不比对。

#### 7.2 --radiometric-normalize

按 `--benchmark-dir` 做全局仿射辐射归一化（每波段 gain/offset），只改档位不动纹理。调试用。

#### 7.3 --match-reference-color

用参考正射的低频底套色。合格主路径不要开，出图不应依赖它。

### 8 退出码

| 码 | 含义 |
| --- | --- |
| 0 | 成功 |
| 10 | 阶段完成，等待继续（`awaiting_continue`） |
| 2 | 失败 |
| 130 | 取消 |

### 9 成果布局

相对 `--out`。完整说明见 **1.4**。

| 路径 | 内容 |
| --- | --- |
| `拼图结果/DSM.tif` | 数字表面模型（高程） |
| `拼图结果/Orthomosaic_pix_surf_group0.tif` | RGB 正射（含透明通道） |
| `拼图结果/Orthomosaic_pix_surf_group1.tif` … `group7.tif` | 全量时的 7 个多光谱正射 |
| `附件/DSM_pseudocolor.tif` | DSM 伪彩色 |
| `附件/area.kml` | 测区范围 |
| `附件/seamlines.geojson` | 拼接线 |
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
