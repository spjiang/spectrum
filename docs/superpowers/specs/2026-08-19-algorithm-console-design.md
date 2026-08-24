# 高光谱算法可视化控制台 — 设计规格

**日期：** 2026-08-19  
**状态：** 待用户审阅  
**依据：** 用户确认「独立 Vite 前端」、testdata 一键演示 + 可上传自有数据、首页 L0–L4 业务流程图、输入/输出必须可视化、字段必须说明。

---

## 1. 目标

做一个给领导看、也能给研发调接口的 **算法可视化控制台**：

- 左边选算法，右边上看介绍与业务场景，右下调用真实 `POST /api/v1/{id}/run`
- 默认用 testdata 一键跑；也可上传 `file` / `file2` 并改 `params`
- **能可视化的输入必须可视化，输出必须可视化**，对照看出算法做了什么
- 每个算法有 **输入/输出字段详细说明**
- 首页是 **九段产线**（与左侧菜单同名，可点击跳到对应算法组）

成功标准：打开 Vite 开发页，点 NDVI / 云检测 / 航线 / POS 四类代表算法，均能看到输入图（或轨迹/航线）和输出图（或报表），且 `<img>` 能显示 PNG/预览图（不依赖本机磁盘路径）。

## 2. 已确认决策

| 决策点 | 结论 |
|--------|------|
| 前端形态 | **独立 Vite 工程**（Vue 3 + TypeScript） |
| 调用方式 | 默认 testdata 一键演示 **且** 支持上传自有文件 |
| 首页图 | **业务流程图** L0 原始 → L1 辐亮度 → L2 反射率立方体 → L3 指数/分类 → L4 地块结论 |
| 算法服务 | 仍为 `http://127.0.0.1:28800` |
| 前端开发 | `http://127.0.0.1:5173`，通过 Vite **proxy** 访问 `/api` |
| 跨域 | 开发靠代理（浏览器视为同源）；后端仍加 CORS，允许 `5173`，避免漏代理时失败 |
| 图片显示 | **禁止**把磁盘绝对路径当 `img src`；必须走 HTTP：静态产物 + GeoTIFF 转 PNG 预览接口 |

## 3. 仓库位置与启动

```text
algorithm/
  source/          # 现有 FastAPI（28800）
  web/             # 新建 Vite + Vue3 控制台
    package.json
    vite.config.ts
    src/
```

启动（两个进程）：

1. `algorithm/source/scripts/start.sh` → 28800  
2. `cd algorithm/web && npm install && npm run dev` → 5173  

给领导演示时打开 **5173**。不把前端强行塞进 28800 的 `/`，避免和现有 JSON 根路由冲突。

## 4. 跨域与图片：具体机制

### 4.1 Vite 代理

`algorithm/web/vite.config.ts`：

- `server.proxy['/api']` → `http://127.0.0.1:28800`
- 前端所有请求只用相对路径 `/api/v1/...`
- `<img src="/api/v1/console/outputs/.../pred_preview.png">` 同样走代理，**能显示**

### 4.2 CORS 兜底

FastAPI 增加 `CORSMiddleware`：

- `allow_origins`: `http://127.0.0.1:5173`、`http://localhost:5173`
- `allow_methods`: `*`
- `allow_headers`: `*`

不替代代理，只防止有人把 API 基址写成 `http://127.0.0.1:28800` 时预检失败。

### 4.3 文件为什么必须改接口

当前 `files` 形如 `/Users/.../data/outputs/xxx/pred_preview.png`。浏览器不能读该路径。无论 Vite 还是同端口，都必须提供 HTTP。

**保留**现有 `files` 磁盘路径（冒烟脚本依赖「files 非空」）。控制台另外使用 `files_http`。

## 5. 后端新增能力（28800）

全部挂在 `/api/v1/console/`，不改 45 个 `service.run` 的磁盘 `files` 字段语义。

### 5.1 静态目录挂载（PNG/JSON/CSV/GeoJSON 可直接下载或当图片）

| 前缀 | 目录 | 用途 |
|------|------|------|
| `/api/v1/console/outputs/` | `algorithm/source/data/outputs/` | 运行产物 |
| `/api/v1/console/testdata/` | `algorithm/source/algorithms/` 下仅 testdata（见 5.4 白名单） | 输入样例 |

`img` 可直接显示 `.png`。`.tif` **不能**当图片，必须走预览接口。

### 5.2 栅格预览

`GET /api/v1/console/preview/raster`

Query：

- `src`: `testdata` 或 `outputs`
- `algorithm_id`: 如 `27_ndvi`（testdata 时必填）
- `name`: 如 `input.tif` 或 `ndvi.tif`
- `job`：outputs 时的作业目录名（如 `27_ndvi_abc123`）
- `mode`: `falsecolor` \| `gray` \| `index` \| `class`
- `bands`: 可选，假彩色波段索引，默认 NIR/R/G 或最后三波段

返回：`image/png`。

规则：

- 多波段立方体 → 假彩色（线性拉伸）
- 单波段连续量（NDVI/得分/LAI）→ `RdYlGn` 或 `turbo` 色带
- 分类/掩膜整数图 → 离散调色板

### 5.3 点选光谱

`GET /api/v1/console/preview/spectrum`

Query：同上，外加 `row`、`col`。

返回 JSON：`{ "wavelengths_nm": [...], "values": [...], "row", "col" }`。无波长则用波段序号。

仅当栅格 `bands >= 3` 时前端展示「点图看光谱」。

### 5.4 路径白名单（安全）

只允许解析到：

- `algorithm/source/data/outputs/`
- `algorithm/source/data/uploads/`
- `algorithm/source/algorithms/{id}/testdata/`

禁止 `..`、禁止绝对路径入参。前端只传 `algorithm_id` / `job` / `name`。

### 5.5 运行结果改写（控制台用）

在 **不破坏** `/run` 的前提下，增加：

`POST /api/v1/console/run/{algorithm_id}`

行为：内部调用同一 `service.run`，然后：

1. 把 `files` 里每个绝对路径转成 `files_http`（png/json/csv/geojson 用静态 URL；tif 用 preview URL）
2. 增加 `job_id`（输出目录名）
3. 原 `files` 仍保留

控制台 **只调这个 console/run**。现有 curl 冒烟仍调 `/api/v1/{id}/run`。

testdata 一键跑：console/run 支持 `use_testdata=true`（Form），服务端读取该算法 `testdata/input.*` 与可选 `file2.*`、`params.json`，不必前端先拉文件再上传。上传模式则仍收 multipart。

### 5.6 元数据

`GET /api/v1/console/algorithms`  
`GET /api/v1/console/algorithms/{id}`

每项至少包含：

- `id` `title` `level` `group`（L0前 / L0 / L0→L1 / L1→L2 / L2 / L3 / L3→L4 / L4）
- `purpose` 作用  
- `scenario` 业务场景  
- `method` 当前实现方法名（如 DOS2、PROSAIL、HybridSN）  
- `endpoint`：`POST /api/v1/{id}/run`  
- `fields.inputs[]`：`name`（file / file2 / params.xxx）、`type`、`required`、`format`、`description`  
- `fields.outputs[]`：`name`（data.xxx / files.xxx）、`type`、`description`、`vis`（raster_falsecolor / raster_index / raster_class / geojson_map / csv_track / json_table / png / none）  
- `testdata`: `{ file, file2, params }`  
- `compare`: `before_after` \| `cube_to_product` \| `single`（决定右下对照布局）

文案来源：`采集到算法-算法清单.md` 的作用/场景 + 各算法真实 `params`/`files` 键。做成 `algorithm/source/common/console_catalog.py`（一份 Python 数据，接口直接读），避免前端硬编码 45 套说明后又和后端漂移。

## 6. 前端信息架构

### 6.1 布局

```text
┌────────────┬──────────────────────────────────────────┐
│ 全流程      │  右上：标题、层级、方法名                      │
│ 航线规划    │  接口：POST /api/v1/{id}/run               │
│  01 航线    │  作用（介绍）                                │
│ L0         │  业务场景                                    │
│  …         ├──────────────────────────────────────────┤
│ L3 NDVI    │  右下调用                                    │
│ …          │  [一键 testdata] [上传 file/file2] [params] │
│            │  ┌ 输入可视化 ┐  ┌ 输出可视化 ┐              │
│            │  │            │  │            │              │
│            │  └ 点选光谱    ┘  └            ┘              │
│            │  输入字段表 | 输出字段表 | 本次 data JSON      │
└────────────┴──────────────────────────────────────────┘
```

左栏按层级分组，可折叠。当前算法高亮。宽度约 260px。

### 6.2 首页（全流程）

全宽流程图，九段（与左侧菜单同名）：

1. 航线规划（L0前，#01）
2. 采集质检（L0，#02–05）
3. 辐射校正（L0→L1，#06–10）
4. 相对归一（L1，#11）
5. 反射率与正射（L1→L2，#12–16）
6. 镶嵌与特征（L2，#17–26）
7. 指数与识别（L3，#27–43）
8. 图斑整理（L3→L4，#44）
9. 地块汇总（L4，#45）

点击某一段：路由到该组第一个算法，左栏展开该组。每块下列代表算法小标签，可直接点进算法页。

### 6.3 算法页右下：调用

- 默认选中「使用 testdata」并展示将要发送的 `file` / `file2` / `params`（只读预览）
- 「运行算法」→ `POST /api/v1/console/run/{id}` + `use_testdata=true`
- 切换「上传文件」：`<input type=file>` ×2 + params 文本框（JSON）
- 运行中按钮 loading；失败展示 `message`，不空白

### 6.4 可视化规则（强制）

| 输入/输出类型 | 可视化 |
|---------------|--------|
| 多波段 GeoTIFF | 假彩色图；点击像元出光谱曲线 |
| 单波段指数/得分 | 色带专题图 + 色标 |
| 分类/掩膜 | 类别色块图 |
| 已有 PNG | 直接 `<img>` |
| GeoJSON | Leaflet 地图（多边形/航点） |
| POS CSV | 经纬度轨迹折线 + roll/pitch/yaw 曲线 |
| 时间戳 JSON | 表格 + 时间轴 Δt |
| 报表 JSON | 关键数字卡片 + 表格 |
| 端元 CSV | 多条光谱曲线叠图 |
| npz | 不强制 3D；展示 patch 均值预览 PNG（已有则用） |

对照模式：

- `before_after`：左右「输入栅格 | 输出栅格」（暗电流、去条带、正射、匀色等）
- `cube_to_product`：左立方体假彩色，右指数/分类/得分
- `single`：仅输出（纯报表类仍尽量把输入 JSON/CSV 可视化）

**不能**只丢一句「已生成 tif」。领导必须看见图或曲线或地图。

### 6.5 字段说明

右下固定两张表：

- 输入：字段名、类型、是否必填、格式、含义  
- 输出：字段名、类型、含义、对应可视化

表下方可展开「本次响应 `data`」原始 JSON，便于研发核对。

## 7. 技术选型

| 层 | 选型 | 原因 |
|----|------|------|
| 前端 | Vue 3 + TS + Vue Router | 控制台结构清晰，构建快 |
| 图 | ECharts | 光谱/轨迹 |
| 地图 | Leaflet | GeoJSON 航线/地块 |
| 样式 | 自写 CSS（深色侧栏 + 浅色内容） | 汇报页，不用通用后台模板 |
| 后端预览 | rasterio + matplotlib/Pillow | 与现有栈一致 |

不用 Geotiff.js 在浏览器解 45 种 tif：统一后端出 PNG，显示稳定。

## 8. 错误与边界

- 28800 未启动：顶栏红条「算法服务未连接」，预览/运行不可用  
- testdata 缺失：禁用一键跑并写明缺哪个文件  
- tif 预览失败：显示错误文案，不破页面  
- 大图：预览最长边限制 512 或 1024，避免 16 位立方体撑爆内存（当前 testdata 为 16×16，预留余量）  
- 不实现登录、排队、集群  

## 9. 明确不做

- 不把 Vite 打进 28800 作为本阶段唯一入口（需要时可另加任务）  
- 不改 45 项算法核心公式  
- 不把 `files` 磁盘路径改掉（保护冒烟）  
- 不做 WebGL 三维立方体漫游（领导场景不需要）  
- 不接外网底图密钥；Leaflet 可用简易 OSM 或纯 GeoJSON 无底图（内网可关瓦片）

## 10. 验收清单

1. `npm run dev` 打开首页，流程图五层可点  
2. 左栏 45 项都能进入详情，右上有介绍+场景+接口路径  
3. 每项有输入/输出字段表  
4. 代表项可视化：  
   - `01` 航线：输入多边形 + 输出航点地图  
   - `03` POS：输入/输出轨迹  
   - `05` 云：输入假彩色 + 输出掩膜  
   - `06` 暗电流：输入/输出对照  
   - `27` NDVI：立方体 + 指数图 + 可点光谱  
   - `34` 分类：标签/预测色块图  
   - `45` 地块：栅格 + 报表数字  
5. 上传自有 tif 跑 NDVI，输出图能显示  
6. 图片均来自 `/api/v1/console/...`，Network 里不是 `file://`  
7. 原 `scripts/smoke_all_implemented.py` 仍 45/45  

## 11. 模块边界

| 单元 | 职责 | 依赖 |
|------|------|------|
| `console_catalog.py` | 45 项文案与字段、可视化类型 | catalog.id |
| `console_preview.py` | tif→png、光谱取样 | rasterio、白名单 |
| `console_router.py` | FastAPI 路由与 StaticFiles、CORS、console/run | service.run |
| `algorithm/web` | 壳、首页图、算法页、调用与展示 | 只打 `/api` |

改预览实现不改 Vue 页面；改文案不改算法 service。
