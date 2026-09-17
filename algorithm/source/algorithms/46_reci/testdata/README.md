# testdata · RECI红边叶绿素指数

反射率 GeoTIFF；须有真实红边。输出 RECI GeoTIFF。

**格式说明**：栅格为 GeoTIFF（`.tif`）。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/46_reci/run" \
  -F "file=@./testdata/input.tif" -F 'params={"re_band": 4, "nir_band": 3}'
```
