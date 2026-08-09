# 语义分割/目标检测

- **algorithm_id**: `40_detect_segment`
- **层级**: L3
- **实现状态**: **可运行**（教学实现）

## 作用

基于 NDVI 低值斑块，检测病斑/胁迫等候选目标，输出掩膜与斑块矢量（对齐清单 #40）。

## 方法（教学级）

1. 由红光/近红外计算 NDVI  
2. 低于指定百分位的像元作为候选  
3. 形态学开运算 + 小斑剔除  
4. 连通域 → 分割掩膜与 GeoJSON 多边形  

## 参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `red_band` | 2 | 红光波段索引（0-based） |
| `nir_band` | 3 | 近红外波段索引 |
| `percentile` | 20 | NDVI 低值百分位阈值 |
| `min_pixels` | 4 | 最小斑块像素数 |

`file2` 可选传入标注/AOI GeoJSON（记录到结果，不强制参与阈值）。

## 启动

```bash
cd algorithm/source
./scripts/start.sh
```

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/40_detect_segment/run" \
  -F "file=@algorithms/40_detect_segment/testdata/input.tif" \
  -F "file2=@algorithms/40_detect_segment/testdata/file2.geojson" \
  -F 'params={"red_band":2,"nir_band":3,"percentile":20,"min_pixels":4}'
```

## 输出

- `files.score_tif`：检测得分图  
- `files.mask_tif`：二值掩膜  
- `files.polygons_geojson`：斑块矢量  
- `files.preview_png`：预览  
