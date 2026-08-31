# QGIS 打开 GeoTIFF 与导出操作手册

面向本仓库教学数据：用 QGIS 打开 `.tif`、查看每个像元的数值、把整表导出为 CSV。菜单名称按 **英文界面** 书写（与当前演示环境一致）；中文界面在括号里给出对照。

教学文件示例：

- 输入立方体：`algorithm/source/algorithms/27_ndvi/testdata/input.tif`（16×16 像元，8 个波段）
- NDVI 结果：控制台运行 `#27` 后生成的 `ndvi.tif`（16×16 像元，1 个波段）

---

## 1. 安装 QGIS

1. 打开官网：[https://qgis.org/download/](https://qgis.org/download/)，选择 **macOS**。
2. 不确定版本时下载 **LTR**（长期支持版）。
3. 打开 `.dmg`，把 QGIS 拖进「应用程序」。
4. 首次打开若提示未验证：系统设置 → 隐私与安全性 → 仍要打开。

QGIS 能直接打开 GeoTIFF（`.tif` / `.tiff`），不能打开 MATLAB 的 `.mat`。

---

## 2. 打开 TIF

1. 启动 QGIS，关闭欢迎页后进入空白工程。
2. 任选一种方式加载栅格：
   - 把 `.tif` 拖进中间地图窗口；或
   - **Layer → Add Layer → Add Raster Layer**（图层 → 添加图层 → 添加栅格图层），选文件后 **Add**。
3. 教学数据只有 16×16 格，全图会缩成一个小点。在图层面板中 **右键该图层 → Zoom to Layer**（缩放到图层），再滚轮放大，直到每个格子都是大方块。

图层名称可能显示为哈希串（例如 `c97b29ffa4de`），以文件为准即可。

默认渲染常把 **Band 1 / 2 / 3** 映射为红 / 绿 / 蓝，所以看到的是一张彩色（或灰度）图，不是数字表。数值仍在文件里。

---

## 3. 显示图层面板 Layers

后续「选中图层、导出」都依赖 Layers。若左边只有 Browser（文件树）没有图层名单：

**View → Panels**，勾选 **Layers**（视图 → 面板 → 图层）。

列表里应能看到 `input` / `ndvi` 等栅格；转点之后还会多出一个点图层。

---

## 4. 安装插件 Value Tool（看单个像元的值）

1. **Plugins → Manage and Install Plugins…**（插件 → 管理和安装插件）。
2. 打开 **All** 页，搜索 `Value Tool`。
3. 选中 **Value Tool** → **Install Plugin**。
4. 安装后：**View → Panels**，勾选 **Value Tool**。
5. 面板里勾上 **Enable**；需要更多小数位时勾 **Decimals**（例如 10）。

把鼠标移到某个彩色格子上，Table 页会显示该像元：

| 列 | 含义 |
| --- | --- |
| Layer | 图层名 |
| Value | 该波段的像元值 |
| Row | 行号（从上往下，从 0 起） |
| Column | 列号（从左往右，从 0 起） |

`input.tif` 会列出 Band 1～Band 8；`ndvi.tif` 只有一个 NDVI 值。

底部 Coordinate 一般是 **经度, 纬度, 当前值**。本仓库教学 GeoTIFF 使用示意坐标（EPSG:4326，约 114.06°E、22.54°N），不是真实农田。

**Identify Features**（工具栏蓝色 **i**）也可以点像元看值，但 Value Tool 随鼠标移动更方便。

---

## 5. 读数时容易混的两件事

### 5.1 文件有 8 层，不等于 NDVI 用了 8 层

`input.tif` 是反射率立方体，每个像元 8 个数，QGIS 会全部列出。算法 `#27` 只抽取两层：

| 控制台参数（从 0 起） | QGIS 波段号（从 1 起） | 角色 |
| --- | --- | --- |
| `red_band=2` | **Band 3** | 红光 |
| `nir_band=3` | **Band 4** | 近红外 |

其余 6 层这次不算 NDVI，但仍在文件里。

这份教学 tif **没有写入波长**。网页光谱图上的 450–850 nm 是控制台默认补的轴，QGIS 里看不到纳米数。

### 5.2 要看 NDVI，必须打开 `ndvi.tif`

`input.tif` 里没有 NDVI。先在算法控制台运行 `#27`，再把输出的 `ndvi.tif` 拖进 QGIS。Value Tool 里 Layer 为 `ndvi`、Value 约在 −1～1。

教学数据左半边（列 0–7）按植被造数，右半边（列 8–15）接近土壤。NDVI 左边通常更高。

---

## 6. 把整张图变成属性表（256 行）

栅格没有「一行一个像元」的属性表。要看/导出全部 NDVI，先转成点：

1. **Processing → Toolbox**（处理 → 工具箱），或快捷键依版本而异。
2. 搜索 **Raster pixels to points**（栅格像素转点）。
3. **Raster layer** 选 `ndvi`（不要选 8 波段的 `input`，除非你要导出 8 列反射率）。
4. **Field name** 填 `ndvi`。
5. **Run**。地图上出现 16×16=256 个点。

打开属性表：

1. 在 **Layers** 里 **左键选中点图层**（名称常含 `points`），不要选灰色栅格 `ndvi`。
2. 任选一种：
   - 键盘 **F6**
   - **Layer → Open Attribute Table**
   - 工具栏表格图标（取消选择按钮右侧，黄表头小表）

点图层未选中时，表格按钮是灰的。栅格图层通常没有 Open Attribute Table。

---

## 7. 导出 CSV

在已选中 **点图层** 的前提下：

1. **Layer → Save As…** / **Save Features As…**（图层 → 另存为）。
2. 出现 **Save Vector Layer as…** 窗口后：
   - **Format**：`Comma Separated Value [CSV]`
   - **File name**：点右侧 **…**，选桌面，文件名例如 `ndvi.csv`（不填路径时 **OK** 是灰的）
   - **CRS**：保持 `EPSG:4326 - WGS 84` 即可
   - **Layer Options → GEOMETRY**：改为 **AS_XY**（CSV 中写出 X、Y 两列；不要留 `<Default>` 只出 WKT）
   - **HEADER**：`YES`
3. 点 **OK**。

用 Excel 或「预览」打开 `ndvi.csv`：每一行一个像元，含坐标和 NDVI。教学数据应为 **256 行**（另加 1 行表头）。

可选：属性表打开后，用表窗口的保存/导出到 CSV，效果相同。

---

## 8. 流程速查

```
安装 QGIS
  → 打开 input.tif 或 ndvi.tif
  → Zoom to Layer 并放大
  → 勾选 View → Panels → Layers
  → 安装 Value Tool，Enable 后指到格子上看值
  →（看全表）Raster pixels to points
  → Layers 中选中点图层
  → Layer → Save As → CSV，GEOMETRY = AS_XY
```

---

## 9. 常见问题

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 地图上几乎看不见图 | 16×16 太小 | Zoom to Layer 再放大 |
| 只能看见颜色，没有数字 | 栅格默认是渲染图 | 用 Value Tool 或 Identify |
| 点了表格没反应 | 选中的是栅格，或 Layers 面板未打开 | 勾选 Layers，再选点图层 |
| 找不到 Open Attribute Table | 没转点，或图层列表被收起 | 先 Raster pixels to points；View → Panels → Layers |
| Save 窗口 OK 是灰色 | File name 为空 | 用 … 选保存路径 |
| CSV 里没有经纬度 | GEOMETRY 未改 | 设为 AS_XY |
| QGIS 里 8 个波段都有值 | 文件就是立方体 | 正常；NDVI 只用 Band 3 和 Band 4 |
| 想看波长 nm | 教学 tif 无波长标签 | 到控制台原理页 / 光谱图查看默认轴 |
| 打开 .mat 失败 | QGIS 不支持 | 先转成 GeoTIFF |

---

## 10. 和本仓库算法控制台的关系

| 步骤 | 软件 |
| --- | --- |
| 算 NDVI = (NIR − RED) / (NIR + RED) | 算法控制台 `27_ndvi` |
| 上地图、点像元、导出表格 | QGIS |
| 看假彩色预览、点像元光谱 | 控制台网页（光谱轴为无波长头时的默认 450–850 nm） |

QGIS 负责 **看图和导出**；公式、波段索引、教学波长轴以控制台为准。
