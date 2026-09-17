# testdata · OSAVI优化土壤调节植被指数

反射率 GeoTIFF；L 默认 0.16。输出 OSAVI GeoTIFF。

**格式说明**：栅格为 GeoTIFF（`.tif`）。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/48_osavi/run" \
  -F "file=@./testdata/input.tif" -F 'params={"red_band": 2, "nir_band": 3, "L": 0.16}'
```
