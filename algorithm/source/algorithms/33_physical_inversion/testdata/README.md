# testdata · 辐射传输物理反演

反射率 GeoTIFF。本算法不用化验图，一次给出叶面积和叶绿素两张图，用来分清是叶子少还是叶子黄。

**格式说明**：栅格为 GeoTIFF（`.tif`）；地块/AOI 为 GeoJSON；POS 为 CSV。

## 文件

| 文件 | 说明 |
|------|------|
| `input.tif` | 主输入（API 字段 `file`）：地表反射率立方体，不能是 DN |
| `params.json` | 推荐请求参数：几何角、LUT 档数、`best_frac`、`cost_method` |

空 `params={}` 时服务默认：`n_lai=25`、`n_cab=16`、`best_frac=0.05`、`cost_method=rmse`、太阳天顶 30°、观测天顶 0°、相对方位 0°。波长缺省会用 450–850 nm 假等间隔。

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/33_physical_inversion/run" \
  -F "file=@./testdata/input.tif"
```
