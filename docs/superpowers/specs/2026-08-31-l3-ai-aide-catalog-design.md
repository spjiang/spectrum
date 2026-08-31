# L3 AI 参谋：整层入口 + 17 算法钻取

## 1. 关系与背景

本文取代 [2026-08-25-l3-ai-aide-design.md](./2026-08-25-l3-ai-aide-design.md) 中的**页面信息架构**（单页四段、不覆盖 27–43）。下列约束继续有效，本文不重复发明：

- 计算走现有 `POST /api/v1/{algorithm_id}/run`，不改 27–43 公式与契约。
- 原始立方体、GeoTIFF、PNG 字节不进大模型。
- 选型权威是场景表；大模型只润色中文，不能改主跑算法。
- 无密钥时模板叙事完整；建议不是处方；不接 #45。
- 站点仍是独立 `ai-web/`，端口 `127.0.0.1:5174`，`/api` 代理到 `28800`。

第一期站点只做「一条补氮演示链」，领导会误以为 L3 只有 NDVI/NDRE。本设计改为：**整层讲清大模型怎么接 L3，同时为 27–43 各做一页钻取。**

## 2. 目标与非目标

### 2.1 目标

- 首页回答：L3 整层如何结合大模型（编排：选算法、讲图、把建议停在辅助层）。
- 算法页回答：该算法自己算什么、精度靠什么、大模型可做/禁止什么；并可跑 testdata。
- 三栏知识库可审、可测；运行后的「本次解读」不得推翻知识库禁区。
- 目录始终能看见 17 个 L3 算法，按三组排列。

### 2.2 非目标

- 不为每个算法各接一套自由对话 Copilot。
- 不把 5173 原理页（公式课、示意滑块）整页搬到 5174。
- 不新增多条业务场景（分类链、水质链）的真实编排；首页「开始参谋」第一期仍只跑 `rice_dense_max_n`。
- 不输出公斤/亩处方，不调用 45。
- 不修改 27–43 的 `service.py` 公式与 `/run` 请求字段。
- 不根据 PNG 色带下定量结论。
- 不在 5174 做 L0–L2 或 L4。

## 3. 已确认决策

| 决策 | 结论 |
| --- | --- |
| 形态 | 方案 1：整层入口 + 17 算法钻取 |
| 分析栏目标题 | 不用「AI 参与 / 提精度 / 辅助」；改为「算法自己算什么 / 精度靠什么 / 大模型可做与禁止」 |
| 大模型主接口 | 整层编排；单算法只补位与挡误用 |
| 知识库权威 | 结构化 JSON；LLM 不得改「禁止」与选型 |
| 本次解读 | 跑成功后可润色统计解释，不得改知识库结论 |
| 默认可跑链 | 仅 `rice_dense_max_n`（主 28、对照 27、跳过 29） |
| 单算法演示 | testdata + 现有 `service.run`，经参谋封装接口返回 |
| 导航 | 左侧常驻 L3 目录；窄屏可收起 |
| 与 5173 | 算法页页脚链到控制台同 id 原理页 |

## 4. 信息架构

```text
/                 首页：整层叙事 + 开始参谋
/algo/:id         算法页：三栏知识 + testdata 演示
```

`:id` 仅允许下列 17 个：

`27_ndvi` `28_ndre` `29_evi_savi` `30_ndmi_ndwi` `31_red_edge_params` `32_regression_inversion` `33_physical_inversion` `34_svm_rf_classify` `35_spectral_matching` `36_cnn1d_classify` `37_cnn3d_classify` `38_transformer_classify` `39_few_shot_classify` `40_detect_segment` `41_unmixing` `42_anomaly_detect` `43_change_detect`

其它 id：前端显示「不是 L3 算法页」，后端知识/演示接口返回 404。

### 4.1 目录分组

| 组 | id |
| --- | --- |
| 指数与反演 | 27–33 |
| 分类与识别 | 34–40 |
| 解混 / 异常 / 变化 | 41–43 |

当前路由对应项高亮。组名可折叠，默认全部展开。

### 4.2 首页

必须同时具备：

1. 一句定位：大模型接 L3 的主接口是编排，不是重算指数或替代小模型。
2. 四段：问题 → 选型 → 出图解释 → 建议（「开始参谋」后填入后三段；问题在请求前也可显示默认场景文案）。
3. 左侧目录可见 17 项，避免再被理解成「只有长势链」。

默认场景文案与计划与 2026-08-25 规格第 4、7 节一致（密植水稻 / MAX-S810 / 补氮辅助；主 NDRE、对照 NDVI、不跑 EVI/SAVI）。

### 4.3 算法页

上半三栏（来自知识库，进页即有，不依赖本次运行）：

1. **算法自己算什么**：`definition`、`method`、`input`、`output`。
2. **精度靠什么**：`accuracy` 字符串数组，3–5 条；内容必须是本地数据或算法流程可改进的项。
3. **大模型可做 / 禁止**：`llmMay`、`llmMustNot`，各 1–3 条。

下半 testdata 演示：按钮「运行本算法示例」→ 预览图、`min/max/mean`（或该算法 `data` 中已有的对应统计）、质量状态、`runComment`（本次解读）。失败时无假图。

页脚：链到 `http://127.0.0.1:5173/algo/{id}`，文案「在算法控制台看原理」。

## 5. 知识库字段与写法约束

每条算法一份对象，字段全部必填（数组至少 1 条，精度栏至少 3 条）：

```json
{
  "id": "27_ndvi",
  "title": "NDVI植被指数",
  "group": "index",
  "definition": "以近红外与红光反射率的归一化差衡量绿色植被活力。",
  "method": "NDVI = (NIR − RED) / (NIR + RED)",
  "input": "反射率立方体；按波长选择红光与近红外索引。",
  "output": "单波段 NDVI GeoTIFF，理论范围约 −1～1。",
  "accuracy": [
    "输入必须是可比反射率，不能用 DN 直接当 NDVI。",
    "按元数据波长选红光与近红外，不能死记教学默认 2/3。",
    "云、云影、NoData 应先掩膜，再做全图或地块统计。",
    "密冠层易饱和时改用 NDRE/EVI，而不是把阈值调得更碎。"
  ],
  "llmMay": [
    "在密冠层场景建议主看 NDRE、NDVI 只作对照。",
    "根据本次 min/max/mean 说明是否落在理论定义域。",
    "提醒固定阈值不能跨地区、季节、传感器复用。"
  ],
  "llmMustNot": [
    "不得重算或改写 NDVI 公式。",
    "不得根据预览 PNG 颜色下定量长势或补氮结论。",
    "不得把立方体或 GeoTIFF 送进大模型。"
  ]
}
```

`group` 取值只能是 `index` | `classify` | `mix`。

禁止出现的写法：

- 「用大模型提高 NDVI/指数计算精度」
- 把 CNN/PLS 与大模型混称为同一个「AI」而不加区分
- 把一次 testdata 的 OA 或均值写成业务验收通过

样例口径（实现时 17 份都要写满，不能留空）：

- **27 NDVI**：精度靠反射率、波长、掩膜；大模型可改荐 NDRE，禁止重算公式。
- **34 SVM/RF**：精度靠标签对齐与地块级留出；大模型可解释 OA/Kappa，禁止把一次随机划分 OA 说成业务过关。

定义与公式优先摘自 `algorithm/web/src/principles/l3.ts` 与 `sources.ts`，允许压缩，不允许改公式含义。

## 6. 架构与接口

```text
ai-web :5174
  GET  /api/v1/l3-aide/algorithms
  GET  /api/v1/l3-aide/algorithms/{id}
  POST /api/v1/l3-aide/algorithms/{id}/run
  POST /api/v1/l3-aide/run            （首页，已有）
  GET  /api/v1/l3-aide/health         （已有）
        ▼
algorithm :28800
  l3_aide
    knowledge.py     17 份三栏 JSON
    scenarios.py     选型权威（已有）
    runner.py        testdata + service.run（已有，单算法复用）
    interpreter.py   统计与质量（已有，按算法扩展规则表）
    narrator.py      模板 + 可选润色（已有；算法页只用 runComment）
```

### 6.1 列表

`GET /api/v1/l3-aide/algorithms` 返回：

```json
{
  "groups": [
    {
      "id": "index",
      "title": "指数与反演",
      "items": [{ "id": "27_ndvi", "title": "NDVI植被指数" }]
    }
  ]
}
```

三组顺序固定为 `index`、`classify`、`mix`；每组内按算法编号升序。必须正好 17 项，无重复。

### 6.2 详情

`GET /api/v1/l3-aide/algorithms/{id}` 返回第 5 节对象。未知或不属于 L3 的 id：HTTP 404，`{"success":false,"message":"不是 L3 算法"}`。

### 6.3 单算法运行

`POST /api/v1/l3-aide/algorithms/{id}/run` 无必填 body（第一期不接用户上传）。行为：

- 用该算法目录 `testdata/` 调已有 `service.run`（与现 runner 相同白名单）。
- 需要双文件的算法（如 32 的真值图、43 的第二时相）使用该目录内已有 `file` / `file2`；缺文件则 `success: false`，说明缺 testdata，不编造栅格。
- 返回：

```json
{
  "success": true,
  "algorithmId": "27_ndvi",
  "message": "",
  "stats": { "min": 0.0, "max": 0.0, "mean": 0.0 },
  "previewUrl": "/api/v1/console/outputs/…/ndvi_preview.png",
  "quality": { "status": "pass", "label": "…", "detail": "…" },
  "runComment": "本次 min/max 落在 [-1,1]。这是教学立方体统计，不能当农情结论。",
  "llm": { "used": false, "fallback": true, "reason": "no_key" }
}
```

`stats` 若该算法 `data` 无 min/max/mean：三个字段为 `null`，`quality.status` 为 `unknown`，`runComment` 只准说「本算法本次未提供全图 min/max/mean」，不准编造区间。

`runComment` 必须同时满足：引用本次 `stats` 或明确写「无统计」；不得出现「必须补氮」「公斤」「处方」；不得与该算法 `llmMustNot` 矛盾。LLM 润色失败则用模板句。

首页 `POST /api/v1/l3-aide/run` 合同保持 2026-08-25 第 7 节，不在本迭代改字段。

## 7. 前端结构

现有单页 `App.vue` 拆为：

- `AppShell.vue`：左侧目录 + `<router-view>`
- `HomeView.vue`：整层四段 + 开始参谋
- `AlgoAideView.vue`：三栏 + 演示
- 路由：`/` 与 `/algo/:id`

样式保持现有灰绿纸面体系，去掉「分类/水质本期不接」占主视觉的页脚长句；该句可缩成首页四段下的一行小字。目录宽度约 240px，三栏桌面并排、窄屏单列。

## 8. 叙述器与 LLM

- 首页：沿用 2026-08-25 第 9 节（场景事实 + 计划 ID + 统计；禁栅格；改选型则整段丢弃）。
- 算法页：提示词只含 `id`、三栏原文、`stats`、`quality`。禁止附带文件路径与图像。模型若改写 `llmMustNot` 或输出处方词，丢弃，用模板 `runComment`。
- `ai-web` 不持有 API Key。

## 9. 错误处理

| 情况 | 行为 |
| --- | --- |
| 28800 不可达 | 顶栏告警；目录仍可用本地缓存失败时显示「知识库未加载」；无假图 |
| 未知算法 id | 404；算法页「不是 L3 算法」 |
| testdata 缺失或 `/run` 失败 | 该页演示失败文案；三栏仍在 |
| LLM 无密钥/超时/违规 | `fallback: true`；模板会话完整 |
| 首页一侧出图失败 | 保持 2026-08-25：建议含「证据不完整」 |

## 10. 测试与验收

后端 unittest（不打真实 LLM）：

1. 列表正好 17 个 L3 id，分组与第 4.1 节一致。
2. 每个 id 的详情含 `accuracy` ≥3、`llmMay`/`llmMustNot` 各 ≥1；任意 `accuracy` 条目不得包含「大模型」（精度只写本地数据与算法流程）。
3. `GET/POST …/algorithms/01_flight_planning` 为 404。
4. `POST …/27_ndvi/run` 无密钥成功时有预览或明确失败信息，且 `runComment` 不含「公斤」「处方」。
5. 提示词装配不含 `.tif`、`outputs/`、base64 PNG。
6. 伪造 LLM 把 27 的 `runComment` 写成「必须补氮 10 公斤/亩」：返回模板，`llm.reason` 必须为 `invalid`。
7. 首页 `rice_dense_max_n` 计划仍为主 28、对照 27、跳过 29（回归 2026-08-25）。

前端：

1. 打开 `/` 可见三组目录和整层定位句。
2. 打开 `/algo/27_ndvi` 未运行即可见三栏。
3. 运行示例后出现统计或失败说明；无假图。
4. `/algo/01_flight_planning` 显示不是 L3。
5. 28800 不可达：告警，无假图。

现场：能从首页点到 NDVI、NDRE、SVM 三页看出「精度靠数据/流程、大模型有禁区」，再回到首页跑通补氮链。

## 11. 实现范围（单计划）

一次实现计划覆盖：知识库 17 份、三个新/扩路由、`ai-web` 路由与两页、单测。不拆成「先只做目录再补文案」的第二期——没有 17 份三栏就不算完成。

首页演示链与解释规则复用现有 `l3_aide` 模块，不重写 2026-08-25 的 runner。
