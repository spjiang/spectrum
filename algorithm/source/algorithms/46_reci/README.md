# RECI红边叶绿素指数

- **algorithm_id**: `46_reci`
- **层级**: L3
- **实现状态**: 已实现（可运行）

## 作用

计算 RECI = NIR/RE − 1，写出 reci.tif。

## 启动（整个算法服务）

```bash
cd algorithm/source
python run.py
```

## 测试数据

本目录 `testdata/` 使用**业界常用格式**（GeoTIFF / GeoJSON / CSV），说明见 `testdata/README.md`。

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/46_reci/run" \
  -F "file=@./testdata/input.tif" -F 'params={"re_band": 4, "nir_band": 3}'
```

## 输入 / 输出

- **输入**: `file` = 反射率 GeoTIFF；`params` 波段索引从 0 起
- **输出 JSON**: `data` 含 min/max/mean；`files.reci_tif` / `files.preview_png`
