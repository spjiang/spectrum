# testdata · 分类后处理平滑/小斑剔除

分类标签 GeoTIFF。

**格式说明**：栅格为 GeoTIFF（`.tif`）；地块/AOI 为 GeoJSON；POS 为 CSV。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/44_postprocess_smooth/run" \
  -F "file=@./testdata/input.tif" -F 'params={"min_pixels": 4}'
```
