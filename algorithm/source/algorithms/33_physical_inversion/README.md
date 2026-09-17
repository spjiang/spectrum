# 辐射传输物理反演

- **algorithm_id**: `33_physical_inversion`
- **层级**: L3
- **实现状态**: 已实现（可运行）

## 作用

不用化验图，一次给出叶面积和叶绿素两张图，用来分清是叶子少还是叶子黄。

默认用 PROSAIL 查找表、RMSE 代价，对最优若干条的 LAI/Cab 取平均。输入必须是反射率，并提供真实波长与太阳/观测几何。

## 使用场景

见 `algorithm/docs/采集到算法-算法清单.md` 对应条目。

## 启动（整个算法服务）

```bash
cd algorithm/source
python run.py
```

## 测试数据

本目录 `testdata/` 使用**业界常用格式**（GeoTIFF / GeoJSON / CSV），说明见 `testdata/README.md`。

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/33_physical_inversion/run" \
  -F "file=@./testdata/input.tif"
```

## 输入 / 输出

`multipart`：`file` 必填，无 `file2`；其余走 `params` JSON。

| 输入 | 默认 | 起什么作用 |
| --- | --- | --- |
| `file` | testdata 反射率 GeoTIFF | 每个像元的地表反射率光谱拿去和查找表比对。不能是 DN 或辐亮度。 |
| `wavelengths_nm` | 缺省则按 450–850 nm 假等间隔 | 把 PROSAIL 模拟光谱插到你的波段位置。 |
| `solar_zenith` | 30° | 太阳有多斜，改表里光谱被照亮的形状。默认不是现场角。 |
| `view_zenith` | 0° | 相机有多斜；天底为 0。 |
| `relative_azimuth` | 0° | 太阳和观测谁在前谁在后。 |
| `n_lai` | 25（范围 0.2–6.0） | 叶面积表有几档。档数×叶绿素档数 = 表有多少条。 |
| `n_cab` | 16（范围 10–70 μg/cm²） | 叶绿素表有几档。 |
| `best_frac` | 0.05 | 平均代价最好的那部分表行。400 条大约平均 20 条。 |
| `cost_method` | `rmse` | 比像不像的尺子；也可 `sam`。乱填会失败。 |

土壤、叶倾角、叶片结构 N、叶片水 Cw、干物质 Cm 当前写死，不能调。

| 输出 | 起什么作用 |
| --- | --- |
| `files.lai_tif` | 叶面积图，看密不密。 |
| `files.cab_tif` | 叶绿素图，看绿不绿。 |
| `files.preview_png` | 只渲 LAI 的预览，颜色不是数值。 |
| `data.lut_size` | `n_lai × n_cab`，默认 400。 |
| `data.best_n` | `round(best_frac × lut_size)`，默认约 20。 |
| `data.n_boundary_lai` / `n_boundary_cab` | 贴网格边界的像元数，不要当实测极值。 |
| `data.lai_mean` / `lai_max` / `cab_mean` | 全图扫一眼，不能代替两张图对照。 |

当前为已实现（可运行）。
