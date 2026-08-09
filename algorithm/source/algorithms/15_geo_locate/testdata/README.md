# testdata · 几何粗校正/地理定位

影像 GeoTIFF + POS JSON。

**格式说明**：栅格为 GeoTIFF（`.tif`）；地块/AOI 为 GeoJSON；POS 为 CSV。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `file2.json` | 附加输入（字段 `file2`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/15_geo_locate/run" \
  -F "file=@./testdata/input.tif" -F "file2=@./testdata/file2.json"
```
