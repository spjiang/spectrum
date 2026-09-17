# testdata · GCI绿色叶绿素指数

反射率 GeoTIFF；输出 GCI GeoTIFF。

**格式说明**：栅格为 GeoTIFF（`.tif`）。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/54_gci/run" \
  -F "file=@./testdata/input.tif" -F 'params={"green_band": 1, "nir_band": 3}'
```
