# testdata · 光谱匹配分类(SAM)

Cube GeoTIFF；file2 为端元光谱库 CSV（业界常见）。

**格式说明**：栅格为 GeoTIFF（`.tif`）；地块/AOI 为 GeoJSON；POS 为 CSV。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `file2.csv` | 附加输入（字段 `file2`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/35_spectral_matching/run" \
  -F "file=@./testdata/input.tif" -F "file2=@./testdata/file2.csv"
```
