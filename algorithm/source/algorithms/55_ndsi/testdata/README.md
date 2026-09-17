# testdata · NDSI归一化差值雪指数

反射率 GeoTIFF；须有真实 SWIR。用途是雪，不是水体（那是 MNDWI）。

**格式说明**：栅格为 GeoTIFF（`.tif`）。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/55_ndsi/run" \
  -F "file=@./testdata/input.tif" -F 'params={"green_band": 1, "swir_band": 5}'
```
