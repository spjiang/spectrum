# testdata · VARI可见大气阻力指数

反射率 GeoTIFF；只用可见光。输出 VARI GeoTIFF。

**格式说明**：栅格为 GeoTIFF（`.tif`）。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/50_vari/run" \
  -F "file=@./testdata/input.tif" -F 'params={"blue_band": 0, "green_band": 1, "red_band": 2}'
```
