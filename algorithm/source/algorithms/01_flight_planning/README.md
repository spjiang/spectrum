# 航线规划与覆盖优化

- **algorithm_id**: `01_flight_planning`
- **层级**: L0前
- **实现状态**: 骨架（implemented=false）

## 作用

航线规划与覆盖优化（对齐业界算法清单 #1）。

## 使用场景

见 `algorithm/docs/采集到算法-算法清单.md` 对应条目。

## 启动（整个算法服务）

```bash
cd algorithm/source
python run.py
```

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/01_flight_planning/run" \
  -F "file=@./data/examples/sample_cube.npy"
```

## 输入 / 输出

- **输入**: `multipart` 字段 `file`（主文件），可选 `file2`，`params`（JSON 字符串）
- **输出**: JSON；若有产物，路径在 `files` 字段中

当前为骨架（implemented=false）。
