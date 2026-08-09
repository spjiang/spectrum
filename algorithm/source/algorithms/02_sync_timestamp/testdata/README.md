# testdata · 同步曝光与时间戳对齐

多传感器时间戳 JSON（工程元数据）。

**格式说明**：栅格为 GeoTIFF（`.tif`）；地块/AOI 为 GeoJSON；POS 为 CSV。

## 文件

| 文件 | 说明 |
|------|------|
| `input.json` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/02_sync_timestamp/run" \
  -F "file=@./testdata/input.json"
```
