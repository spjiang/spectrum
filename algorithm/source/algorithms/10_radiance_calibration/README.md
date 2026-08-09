# 辐射定标 DN→辐亮度

- **algorithm_id**: `10_radiance_calibration`
- **层级**: L0→L1
- **实现状态**: 骨架（implemented=false）

## 作用

辐射定标 DN→辐亮度（对齐业界算法清单 #10）。

## 使用场景

见 `algorithm/docs/采集到算法-算法清单.md` 对应条目。

## 启动（整个算法服务）

```bash
cd algorithm/source
python run.py
```

## 测试数据

本目录 `testdata/` 使用**业界常用格式**（GeoTIFF / GeoJSON / CSV），说明见 `testdata/README.md`。

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/10_radiance_calibration/run" \
  -F "file=@./testdata/input.tif" -F 'params={"gain": 0.01, "offset": 0.0}'
```

## 输入 / 输出

- **输入**: `multipart` 字段 `file`（主文件），可选 `file2`，`params`（JSON 字符串）
- **输出**: JSON；若有产物，路径在 `files` 字段中

当前为骨架（implemented=false）。
