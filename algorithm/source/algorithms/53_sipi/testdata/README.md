# testdata · SIPI结构不敏感色素指数

反射率 GeoTIFF；输出 SIPI GeoTIFF。值域不必落在 −1～1。

**格式说明**：栅格为 GeoTIFF（`.tif`）。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/53_sipi/run" \
  -F "file=@./testdata/input.tif" -F 'params={"blue_band": 0, "red_band": 2, "nir_band": 3}'
```
