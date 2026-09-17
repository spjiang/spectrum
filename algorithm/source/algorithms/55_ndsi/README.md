# NDSI归一化差值雪指数

- **algorithm_id**: `55_ndsi`
- **层级**: L3
- **实现状态**: 已实现（可运行）

## 作用

计算 NDSI = (GREEN − SWIR)/(GREEN + SWIR)。与 MNDWI 同型，用途是雪。

## 启动（整个算法服务）

```bash
cd algorithm/source
python run.py
```

## 测试数据

本目录 `testdata/` 使用**业界常用格式**（GeoTIFF / GeoJSON / CSV），说明见 `testdata/README.md`。

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/55_ndsi/run" \
  -F "file=@./testdata/input.tif" -F 'params={"green_band": 1, "swir_band": 5}'
```

## 输入 / 输出

- **输入**: `file` = 反射率 GeoTIFF；`params` 波段索引从 0 起
- **输出 JSON**: `data` 含 min/max/mean；`files.ndsi_tif` / `files.preview_png`
