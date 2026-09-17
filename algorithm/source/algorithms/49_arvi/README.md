# ARVI耐大气植被指数

- **algorithm_id**: `49_arvi`
- **层级**: L3
- **实现状态**: 已实现（可运行）

## 作用

计算 ARVI = (NIR − RB)/(NIR + RB)，RB = RED − γ(BLUE − RED)，默认 γ=1。

## 启动（整个算法服务）

```bash
cd algorithm/source
python run.py
```

## 测试数据

本目录 `testdata/` 使用**业界常用格式**（GeoTIFF / GeoJSON / CSV），说明见 `testdata/README.md`。

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/49_arvi/run" \
  -F "file=@./testdata/input.tif" -F 'params={"blue_band": 0, "red_band": 2, "nir_band": 3, "gamma": 1.0}'
```

## 输入 / 输出

- **输入**: `file` = 反射率 GeoTIFF；`params` 波段索引从 0 起
- **输出 JSON**: `data` 含 min/max/mean；`files.arvi_tif` / `files.preview_png`
