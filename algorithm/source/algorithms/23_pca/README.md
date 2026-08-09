# PCA/MNF降维

- **algorithm_id**: `23_pca`
- **层级**: L2
- **实现状态**: 已实现（可运行）

## 作用

PCA/MNF降维（对齐业界算法清单 #23）。

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
curl -X POST "http://127.0.0.1:28800/api/v1/23_pca/run" \
  -F "file=@./testdata/input.tif" -F 'params={"n_components": 3}'
```

## 输入 / 输出

- **输入**: `multipart` 字段 `file`（主文件），可选 `file2`，`params`（JSON 字符串）
- **输出**: JSON；若有产物，路径在 `files` 字段中

当前为已实现（可运行）。
