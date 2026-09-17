# testdata · 叶面积经验指数

反射率 GeoTIFF；经验 LAI，不是 PROSAIL。输出 lai_index.tif。

**格式说明**：栅格为 GeoTIFF（`.tif`）。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/51_lai_index/run" \
  -F "file=@./testdata/input.tif" -F 'params={"blue_band": 0, "red_band": 2, "nir_band": 3}'
```
