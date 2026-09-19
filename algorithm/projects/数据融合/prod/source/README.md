# 多光谱拼图（MAX 目录 → 大图）

入口只有拍完后的那一个目录：

```text
MAX_20251017_001/ 里的 MAX_*.jpg / MAX_*.tif
        ↓
认文件、读 POS、按曝光捆帧、正射镶嵌
        ↓
mosaics/*.tif + report/quality.json
```

依赖使用仓库里 `algorithm/source/.venv`（rasterio / numpy / tifffile / Pillow）。

**`MAX_20251017_001` 只读。** 程序只打开里面的 jpg/tif，不在该目录创建、覆盖或改时间戳。所有中间帧和大图写到 `--out`（例如 `prod/runs/`）。若 `--out` 落在输入目录里会直接报错退出。

执行：

```bash
cd algorithm/projects/数据融合/prod/source

# 先跑 12 帧，看 process/ 中途文件
./run.sh --max-frames 12

# 全目录，输出到带时间戳的 ../runs/manual_* 
./run.sh

# 指定输出目录
./run.sh --out ../runs/manual_01
```

依赖使用仓库里 `algorithm/source/.venv`（rasterio / numpy / tifffile / Pillow）。

```bash
PY=../../../../source/.venv/bin/python
```

当前几何是 **POS 直接地理定位 + 北向上重投影 + merge**，还没有空三。大图带 UTM 坐标，可丢进 QGIS。白板 `_W` 和 AGL≈0 的地面帧会自动丢掉。

流程图见 [执行流程.md](执行流程.md)。全量 / 只 RGB 的完整命令见 [命令行说明.md](命令行说明.md)。
