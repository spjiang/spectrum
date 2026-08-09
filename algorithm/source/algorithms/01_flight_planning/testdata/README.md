# testdata · 航线规划与覆盖优化

测区 GeoJSON（业界常用矢量交换格式）。

**格式说明**：栅格为 GeoTIFF（`.tif`）；地块/AOI 为 GeoJSON；POS 为 CSV。

## 文件

| 文件 | 说明 |
|------|------|
| `input.geojson` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/01_flight_planning/run" \
  -F "file=@./testdata/input.geojson" -F 'params={"cruise_speed_m_s": 8}'
```
