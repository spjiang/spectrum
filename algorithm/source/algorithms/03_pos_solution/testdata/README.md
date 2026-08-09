# testdata · POS解算（GPS+IMU）

GPS/IMU 轨迹 CSV（POS 常用落盘形态之一）。

**格式说明**：栅格为 GeoTIFF（`.tif`）；地块/AOI 为 GeoJSON；POS 为 CSV。

## 文件

| 文件 | 说明 |
|------|------|
| `input.csv` | 主输入（API 字段 `file`） |
| `params.json` | 推荐请求参数 |

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/03_pos_solution/run" \
  -F "file=@./testdata/input.csv"
```
