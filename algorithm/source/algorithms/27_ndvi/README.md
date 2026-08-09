# NDVI 植被指数

- **algorithm_id**: `27_ndvi`
- **层级**: L3
- **实现状态**: 已实现（可运行）

## 作用

计算 NDVI = (NIR - RED) / (NIR + RED)，生成指数图与预览 PNG。

## 使用场景

作物长势监测、物候观察；农情最常用指数。

## 启动（整个算法服务）

```bash
cd algorithm/source
python run.py
```

## 测试数据

本目录 `testdata/` 使用**业界常用格式**（GeoTIFF / GeoJSON / CSV），说明见 `testdata/README.md`。

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/27_ndvi/run" \
  -F "file=@./testdata/input.tif" -F 'params={"red_band": 2, "nir_band": 3}'
```

## 输入 / 输出

- **输入**: `file` = HxWxB `.npy`；`params.red_band` / `nir_band`（默认 2/3）
- **输出 JSON**:
  - `data`: min/max/mean
  - `files.ndvi_npy` / `files.preview_png`
