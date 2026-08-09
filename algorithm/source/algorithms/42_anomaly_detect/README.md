# 异常检测

- **algorithm_id**: `42_anomaly_detect`
- **层级**: L3
- **实现状态**: **可运行**（教学实现）

## 作用

用 Reed–Xiaoli (RX) 光谱异常检测，找出「不像背景大多数」的像元（对齐清单 #42）。

## 方法（教学级）

对全图像元光谱估计均值 μ 与协方差 Σ，计算马氏距离平方作为异常得分，再按百分位阈值生成告警掩膜。

## 参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `percentile` | 95 | 得分高于该百分位判为异常 |
| `min_pixels` | 2 | 告警小斑剔除 |

## 启动

```bash
cd algorithm/source
./scripts/start.sh
```

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/42_anomaly_detect/run" \
  -F "file=@algorithms/42_anomaly_detect/testdata/input.tif" \
  -F 'params={"percentile":95,"min_pixels":2}'
```

## 输出

- `files.score_tif`：RX 异常得分图  
- `files.mask_tif`：告警二值掩膜  
- `files.preview_png`：预览  
