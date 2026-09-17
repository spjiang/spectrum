# 叶面积经验指数

- **algorithm_id**: `51_lai_index`
- **层级**: L3
- **实现状态**: 已实现（可运行）

## 作用

先算 EVI，再做 LAI = max(3.618×EVI − 0.118, 0)。系数是教学默认，不是 #33。

## 启动（整个算法服务）

```bash
cd algorithm/source
python run.py
```

## 测试数据

本目录 `testdata/` 使用**业界常用格式**（GeoTIFF / GeoJSON / CSV），说明见 `testdata/README.md`。

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/51_lai_index/run" \
  -F "file=@./testdata/input.tif" -F 'params={"blue_band": 0, "red_band": 2, "nir_band": 3}'
```

## 输入 / 输出

- **输入**: `file` = 反射率 GeoTIFF；`params` 波段索引从 0 起
- **输出 JSON**: `data` 含 min/max/mean；`files.lai_index_tif` / `files.preview_png`
