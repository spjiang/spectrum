# L3 AI 参谋设计

## 1. 背景

中达瑞和以高光谱硬件为主，MAX 等产品已内置 NDVI / NDRE / EVI。资本方入驻的 AI 团队需要证明：增量不在「会不会算指数」，而在「这场该用哪个、图能不能信、建议说到哪一层」。

L3（算法 27–43）产出分类图、指数图、反演图，分析师部分能看懂；面向拍板的是 L4 地块汇总。大模型不能替代 NDVI 公式或空谱分类小模型，也不应把原始高维立方体送进 LLM。仓库内 LUMIR 已采用同一原则：大模型做调度与叙述，本地算法做计算。

本设计第一期做给中达瑞和领导与资本方看的演示：一条长势 / 氮素样板链，独立站点一页讲完。

## 2. 目标

### 2.1 核心目标

- 用一条业务链体现 AI 团队价值：问题 → 选 L3 算法 → 出图解释 → 带边界的建议。
- 对外叙事是「L3 整层参谋」；对内第一期只接线农业长势 / 氮素。
- 计算仍走现有 27 / 28（及场景表中声明跳过的 29），不改算法公式与 `/run` 契约。
- 现场无大模型密钥时，四段内容仍然完整。

### 2.2 非目标

- 不为 27–43 每个算法页各接一套 Copilot。
- 不实现作物分类、水质 / 水分的真实编排插件（只在页脚声明同一编排器可扩展）。
- 不输出公斤 / 亩施肥处方，不调用 45 地块汇总。
- 不把 GeoTIFF、立方体数组或 PNG 字节送进大模型。
- 不把参谋嵌进 `algorithm/web` 的 `/algo/:id`。
- 不根据 PNG 色带下定量结论。

## 3. 已确认决策

| 决策 | 结论 |
| --- | --- |
| 受众 | 中达瑞和领导 / 资本方，演示与叙事优先 |
| 形态 | 一条业务链打通：问题 → 选型 → 出图解释 → 建议 |
| 样板链 | 农业长势 / 氮素；分类与水质只作口头扩展 |
| 架构 | 整层编排器 + 被选中算法的解释插件；大模型不重算指数 |
| 站点 | 独立前端，目录 `ai-web/`，不并入算法控制台 |
| 布局 | A · 一页四段故事 |
| 默认场景 | 密植水稻 · MAX-S810 · 要不要补氮（`rice_dense_max_n`） |
| 选型权威 | 场景规则表；LLM 只润色中文，不能改主跑算法 |
| 计算入口 | 现有 `POST /api/v1/{id}/run`，第一期用内置 testdata，不上传用户影像 |
| 失败策略 | 无密钥 / 超时走模板；单图失败不编造结果 |

## 4. 信息架构（页面）

站点顶栏：`中达瑞和 × AI 团队`，副标题 `L3 参谋 · 长势与氮素`。主按钮：「开始参谋」。

### ① 问题

固定文案，第一期不可切换场景：

- 标题：密植水稻，MAX-S810 刚采完，要不要补氮？
- 元数据：作物水稻、冠层密植封垄、相机 MAX-S810（7 通道，含 720/750 nm 红边）、任务氮素辅助判断。
- 钩子：对方机载已经会出 NDVI/NDRE；本页证明 AI 决定「这场用哪个」，并挡住误用。

### ② 选型

三张卡片，内容由场景表决定，不由模型即兴发挥：

- 主跑 28 NDRE：密冠层红边更敏感，MAX 720/750 即为这条准备。
- 对照 27 NDVI：当面指出封垄后 NDVI 易饱和，不能单独当补氮依据。
- 不跑 29 EVI/SAVI：本场景土壤背景不重；苗期稀疏才上 SAVI。分类 / 水质换插件，不在本链。

### ③ 出图解释

两列并排：NDRE 主图、NDVI 对照图。每列含预览、min/max/mean、质量状态、解读。质量只依据结构化规则与本次统计，不依据 PNG 颜色。

### ④ 建议

深色结论卡。必须同时出现：

- 按 NDRE 相对空间格局做分区巡田 / 关注。
- 不是施肥处方，不给公斤 / 亩。
- 定量与亩均报表要地面化验和 L4（45），本期只点到这里。

页脚一句：分类、水质可接同一编排器，本期不跑。

## 5. 架构

```text
ai-web（Vite，127.0.0.1:5174）
        │  POST /api/v1/l3-aide/run
        │  JSON { "scenarioId": "rice_dense_max_n" }
        ▼
algorithm 服务 :28800
  l3_aide 路由（新增）
        ├─ 场景表 → 计划（主 28、对照 27、跳过 29）
        ├─ 内置 testdata 调 27/28 的 service.run（同景立方体）
        ├─ 解释插件：统计 + 质量规则
        ├─ 叙述器：模板必出；可选 LLM 润色
        └─ 返回一页 JSON
```

职责边界：

| 单元 | 做什么 | 不做什么 |
| --- | --- | --- |
| `ai-web` | 四段展示、一键请求、健康告警 | 不算指数、不持有 API Key |
| 编排器 | 场景 → 算法清单与角色 | 不改波段公式 |
| 算法 API | 继续算 NDVI/NDRE | 不感知参谋、不调大模型 |
| 解释插件 | 统计与质量状态 | 不把 PNG 当定量依据 |
| 叙述器 | 中文理由与建议 | 不得推翻场景表选型 |

27 / 28 / 29 的 `service.py` 与现有 `/run` 契约第一期禁止修改。

## 6. 组件与文件

### 6.1 后端（`algorithm/source`）

- `common/l3_aide/scenarios.py`：场景表，唯一选型权威。
- `common/l3_aide/orchestrator.py`：`build_plan(scenario_id) -> plan`。
- `common/l3_aide/runner.py`：用 testdata 调用指定算法 `service.run`，并经现有 `files_to_http` 暴露预览。
- `common/l3_aide/interpreter.py`：从 `data.min/max/mean` 计算质量状态。
- `common/l3_aide/narrator.py`：模板文案；可选 LLM；校验模型不得改 `plan.primary.algorithmId`。
- `common/l3_aide/service.py`：组装一次参谋运行。
- `common/l3_aide/router.py`：`POST /api/v1/l3-aide/run`、`GET /api/v1/l3-aide/health`。
- `tests/test_l3_aide.py`：选型、兜底、禁改计划、禁止栅格进提示词、单图失败。

同景立方体：两次运行都使用 `28_ndre/testdata/input.tif`。28 使用其 `params.json`（`re_band`/`nir_band`）；27 使用 `red_band=2`、`nir_band=3`（与 27 的 testdata 参数一致）。禁止 27、28 各用各的 testdata，以免对照失去「同景」含义。

### 6.2 前端（`ai-web/`）

独立 Vue 3 + Vite + TypeScript 站点，端口 `5174`，`/api` 代理到 `127.0.0.1:28800`。单页、无侧栏 45 算法导航。CORS 在算法服务中增加 `http://127.0.0.1:5174` 与 `http://localhost:5174`。

## 7. 数据合同

`POST /api/v1/l3-aide/run`

请求：

```json
{ "scenarioId": "rice_dense_max_n" }
```

未知 `scenarioId`：HTTP 400，body 含中文 `message`，不跑算法。

成功（HTTP 200，即使 LLM 走了模板）：

```json
{
  "success": true,
  "scenarioId": "rice_dense_max_n",
  "question": {
    "title": "密植水稻，MAX-S810 刚采完，要不要补氮？",
    "crop": "水稻",
    "canopy": "密植封垄",
    "sensor": "MAX-S810",
    "task": "氮素辅助判断",
    "hook": "对方机载已经会出 NDVI/NDRE。本页要证明的是：AI 团队决定「这场用哪个」，并挡住误用。"
  },
  "plan": {
    "primary": {
      "algorithmId": "28_ndre",
      "title": "NDRE",
      "role": "primary",
      "reason": "密冠层红边对叶绿素更敏感，封垄后不易饱和。MAX 的 720/750 就是为这条准备的。"
    },
    "contrast": {
      "algorithmId": "27_ndvi",
      "title": "NDVI",
      "role": "contrast",
      "reason": "用来当面指出：密冠层 NDVI 容易顶满，不能单独当补氮依据。"
    },
    "skipped": [
      {
        "algorithmId": "29_evi_savi",
        "title": "EVI/SAVI/MSAVI",
        "reason": "土壤背景不重。苗期稀疏才上 SAVI；分类/水质换插件，不在本链。"
      }
    ]
  },
  "results": [
    {
      "algorithmId": "28_ndre",
      "success": true,
      "message": "",
      "stats": { "min": 0.0, "max": 0.0, "mean": 0.0 },
      "previewUrl": "/api/v1/console/outputs/…/ndre_preview.png",
      "quality": {
        "status": "pass",
        "label": "可作为分区关注的主图",
        "detail": "落在红边指数合理区间。低值斑块优先当「相对弱区」看，不能换算成公斤/亩。"
      }
    }
  ],
  "advice": {
    "headline": "按 NDRE 低值区做分区巡田；本次不给施肥剂量",
    "bullets": [
      "主依据是 NDRE 相对空间格局，不是 NDVI，也不是机载实时绿度一条数。",
      "建议停留在「哪里先看、哪里可能更弱」。没有地面化验，不输出公斤/亩。",
      "要亩均报表和告警，下一层接 L4 地块汇总（45），本期演示只点到这里。"
    ],
    "isPrescription": false
  },
  "llm": {
    "used": false,
    "fallback": true,
    "reason": "no_key"
  }
}
```

`results` 顺序：先 primary，后 contrast。某一侧 `success: false` 时：`previewUrl` 为 `null`，`stats` 为 `null`，`message` 为接口错误摘要，`quality.status` 为 `unknown`。此时 `advice.headline` 必须含「证据不完整」，且不得给出肯定补氮判断。`advice.isPrescription` 恒为 `false`。

`llm.reason` 取值：`no_key` | `timeout` | `invalid` | `plan_override_rejected` | `ok`。

## 8. 质量规则

解释插件只使用 `data` 中的 `min`、`max`、`mean`。缺任一字段 → `status: "unknown"`，标签「不可判定」。

| 算法 | 规则 | 通过 | 警告 |
| --- | --- | --- | --- |
| 27 NDVI | `kind: between`，min/max 均在 `[-1, 1]` | 范围合法，且本场景角色为对照 | 越出 `[-1, 1]` |
| 28 NDRE | 同上 | 范围合法，角色为主图 | 越出 `[-1, 1]` |

额外业务规则（不替代区间规则）：

- 本场景下 NDVI 无论均值高低，质量标签必须表明「本场景不能当补氮主依据」（理由来自密冠层选型，不依赖 testdata 是否真的饱和）。
- 若 NDVI `mean >= 0.65`，解读中追加「高值区接近饱和，空间反差可能偏弱」。
- 不得根据单次 testdata 宣称「长势优秀」或「必须补氮」。

## 9. 叙述器与 LLM

模板是默认路径，必须覆盖 ② 的三条理由、③ 的解读骨架、④ 的三条边界。

可选 LLM：环境变量 `L3_AIDE_API_KEY`（若空则再读 `DEEPSEEK_API_KEY`）。存在密钥时，把结构化事实（场景字段、计划 ID、统计、质量状态、模板句子）发给兼容 DeepSeek 的 Chat Completions；禁止附带任何文件路径、数组或 base64。超时 8 秒。

模型输出若出现以下任一情况，整段丢弃，`llm.fallback = true`：

- 非 JSON 或缺字段。
- `plan.primary.algorithmId` 不是 `28_ndre`。
- 建议中出现「公斤」「kg/亩」「处方」且未同时保留「不是处方」。
- 提示词装配函数的单测必须断言：输入事实里即使有 `files` 路径，装配结果也不包含 `.tif`、`outputs/`、numpy 数组字面量。

无密钥时不发起网络请求。`ai-web` 不读取任何 Key。

## 10. 错误处理

- 未知场景：400，不跑算法。
- 场景表缺 `primary` / `contrast`：视为配置错误，200 且 `success: false`，页面「参谋配置不完整」，不编造理由。
- 27 与 28 分开跑；一侧失败另一侧仍返回；失败侧不使用占位假图。
- 算法服务不可达：`ai-web` 顶栏「无法连接 127.0.0.1:28800」，不渲染假图。
- LLM 失败或试图改选型：模板叙事，角落「本次为规则叙事」。

## 11. 验收

后端 unittest（不依赖真实 LLM）：

1. `rice_dense_max_n` 的计划必须是主 28、对照 27、跳过 29。
2. 无密钥：HTTP 200，`llm.fallback == true`，四段字段齐全，`advice.isPrescription is False`。
3. 伪造 LLM 返回主跑 NDVI：计划仍为 NDRE，`llm.reason` 必须为 `plan_override_rejected`。
4. 提示词不含栅格路径、立方体或 PNG 字节。
5. 模拟 28 失败、27 成功：对照图在，建议含「证据不完整」。
6. 未知场景：400。

前端：

1. 点「开始参谋」后 ①②③④ 均有中文；建议含「不是处方」。
2. 28800 不可达：顶栏告警，无假图。
3. `fallback: true` 时可见「规则叙事」。

现场：只开 `ai-web` 与算法服务，一键能讲完「硬件会出 NDVI，密冠层要用 NDRE，建议不是处方」。

不测：全 L3 Copilot、真实施肥剂量、45 地块汇总、真实 LLM 费用进 CI。

## 12. 扩展预留

编排器接口保持 `build_plan(scenario_id)`。未来增加 `crop_class_max`、`water_ndwi_ndmi` 只需加场景行与解释插件，不改 `ai-web` 四段骨架。第一期禁止实现这些场景。
