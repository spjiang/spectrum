# testdata · NBR标准化燃烧率

反射率 GeoTIFF；须有真实 SWIR。教学默认约 1600 nm，不是 Landsat SWIR2。

**格式说明**：栅格为 GeoTIFF（`.tif`）。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/52_nbr/run" \
  -F "file=@./testdata/input.tif" -F 'params={"nir_band": 3, "swir_band": 5}'
```
