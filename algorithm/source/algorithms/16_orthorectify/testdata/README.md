# testdata · 正射校正

input=影像 GeoTIFF；file2=DEM GeoTIFF。

**格式说明**：栅格为 GeoTIFF（`.tif`）；地块/AOI 为 GeoJSON；POS 为 CSV。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `file2.tif` | 附加输入（字段 `file2`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/16_orthorectify/run" \
  -F "file=@./testdata/input.tif" -F "file2=@./testdata/file2.tif"
```
