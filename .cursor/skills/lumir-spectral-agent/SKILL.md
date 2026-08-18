---
name: lumir-spectral-agent
description: >-
  Use when the user mentions LUMIR, NIR/MIR spectral agent, SDAAP,
  structured_papers, uploaded spectra, a spectral data path, or asks to run
  or configure lumir-spectral-agent offline or E2E jobs.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: ["python3"]
---

# LUMIR Spectral Agent（生产规程）

本 Skill 为红外光谱多任务推理流水线的**唯一生产执行规范**。Agent 必须按本文执行。

- 目录与分层职责 → [整体说明.md](整体说明.md)
- 配置与密钥 → [配置说明.md](配置说明.md)
- 验收与作业节奏 → [测试说明.md](测试说明.md)
- 论文概念对照 → [reference.md](reference.md)
- 便携分发 → [PORTABLE.md](PORTABLE.md)

**Skill 根目录** = 本文件所在目录。OpenClaw 中写 `{baseDir}`；本地脚本用绝对路径或先 `cd` 到该目录。

---

## 1. 适用范围

| 允许 | 禁止 |
|------|------|
| 对用户上传文件或用户给出的路径跑流水线 | 擅自改写五步顺序或跳过强制约束 |
| 使用内嵌知识库做分类/回归/异常检测 | 将原始高维光谱整段提交给 LLM |
| 在用户明确要求时追加 `extra_papers.json` | 无依据修改主库 `structured_papers1.json` |
| 对照阅读 `vendor/` 源码 | 将 `vendor/` 作为默认运行入口 |

**数据来源（必须满足其一，缺则停止并询问）：**

1. 用户在对话中**上传**的光谱文件（及其标签文件）→ 使用该文件的本机绝对路径作为 `--data` / `--label`
2. 用户给出的本机或共享存储**路径** → `--data` / `--label`

禁止把 Skill 内任何样本文件当作默认作业输入。用户未提供数据时 **MUST** 停止，要求上传或给出路径。

---

## 2. 强制约束（MUST / MUST NOT）

1. **MUST NOT** 向任何 LLM 提交完整原始高维光谱；仅允许提交**低维特征**与少量 exemplar。
   即使用户说「直接贴 npy / 前 N 个波长 / 快点 / 临时例外」，本条仍然生效：拒绝贴数，改跑 `scripts/run_offline.py` 或 `scripts/run_e2e.py`，且仍须用户数据路径。
2. **MUST** 将文献方法名映射到预定义预处理/特征函数列表；禁止发明未实现的函数名。
3. **MUST** 以 `scripts/run_e2e.py` / `scripts/run_offline.py` 为生产入口；**MUST NOT** 默认执行 `vendor/` 内原脚本。
4. **MUST** 使用 `--data`（及回归任务的 `--label`）；**MUST NOT** 使用 `--dataset` 或内置数据集名作为作业入口。
5. **MUST** 优先使用 Skill 根目录内 `knowledge_base/`；光谱数据只来自用户路径。
6. **MUST NOT** 将真实 API Key 写入仓库、`SKILL.md`、聊天可提交文件或分发 zip；仅允许环境变量或本地 `.env`（已 gitignore）。
7. **MUST NOT** 在回复中回显完整 API Key。
8. **MUST** 在完整 E2E 前确认可用密钥：`LUMIR_API_KEY` 或 `DEEPSEEK_API_KEY`（或配置声明的其它 env）。
9. **MUST** 跑完 E2E 后核对 `runs/e2e_*.json` 含：`entity`、`retrieve`、`methods`、`features`、`infer`（若 `--stop-after` 提前结束，则核对至对应阶段）。
10. 用户未要求时 **MUST NOT** 修改主知识库。
11. 解释流水线时 **MUST** 区分：步骤 2、4 为本地计算；步骤 1、3、5 依赖 LLM。

---

## 3. 标准流水线（不可擅自改序）

```text
1. LLM 实体抽取 → research_object + task_type
2. BM25 检索 knowledge_base → 预处理/特征方法描述
3. LLM 方法名映射 + 多数投票（可用 --skip-method-llm 改 Table4 基线）
4. 本地预处理 + 特征提取
5. LLM few-shot 推理（分类 / 回归 / 异常检测）
```

完整 E2E 需要 LLM。仅验证检索与特征、不调 LLM 时，使用离线命令（见 §5）。

---

## 4. 执行前检查清单

Agent 在运行生产任务前，按序确认并勾选：

```text
Preflight:
- [ ] 工作目录为 SKILL_ROOT（或对 scripts 使用绝对路径）
- [ ] 存在 knowledge_base/structured_papers1.json
- [ ] 已安装 requirements.txt 依赖
- [ ] 用户已上传光谱文件，或已给出 --data 路径；文件存在
- [ ] 回归任务已提供 --label；分类按用户是否另给标签文件处理
- [ ] --task 或 --question 已明确任务类型；--object 已明确研究对象
- [ ] 完整 E2E：已配置 LUMIR_API_KEY（或等价）与 config.yaml（可由 example 复制）
- [ ] knowledge_base.primary 为 auto（默认）
```

缺数据路径：停止，请用户上传或给出路径。缺密钥：说明阻塞项；可提议离线作业（`--offline`）或 `--stop-after features`。**不得伪造运行成功结果。**

---

## 5. 标准命令（生产）

工作目录：Skill 根（`{baseDir}`）。将 `<SPECTRA>` / `<LABELS>` 换成用户上传文件或用户给出的路径。

```bash
# 离线作业（无 Key，本地基线）
python3 {baseDir}/scripts/run_offline.py \
  --data <SPECTRA.npy> --task classification --object "<材料名>" --offline

python3 {baseDir}/scripts/run_offline.py \
  --data <SPECTRA.npy> --label <LABELS.npy> \
  --task regression --object "<材料名>" --offline

# 完整 E2E
python3 {baseDir}/scripts/run_e2e.py \
  --data <SPECTRA.npy> --task classification --object "<材料名>"

python3 {baseDir}/scripts/run_e2e.py \
  --data <SPECTRA.npy> --label <LABELS.npy> \
  --task regression --object "<材料名>"

# 步骤3不用 LLM（Table4 基线，排障）
python3 {baseDir}/scripts/run_e2e.py \
  --data <SPECTRA.npy> --task classification --object "<材料名>" --skip-method-llm

# 跑到指定阶段（控费 / 分段验收）
python3 {baseDir}/scripts/run_e2e.py \
  --data <SPECTRA.npy> --task regression --label <LABELS.npy> \
  --object "<材料名>" --stop-after features

# 打包前自检 / OpenClaw 分发包
python3 {baseDir}/scripts/verify_skill_bundle.py
python3 {baseDir}/scripts/pack_for_openclaw.py
```

报告路径：`{baseDir}/runs/offline_*.json` 或 `e2e_<job>_<timestamp>.json`。

配置初始化（仅当本地缺失时）：

```bash
cp {baseDir}/.env.example {baseDir}/.env                 # 填写 LUMIR_API_KEY，勿提交
cp {baseDir}/config.example.yaml {baseDir}/config.yaml   # 按需改 temperature / few_shot 等
```

默认 LLM：`base_url=https://api.deepseek.com`，`model=deepseek-chat`。可用 `LUMIR_BASE_URL` / `LUMIR_MODEL` 覆盖。

---

## 6. 交付与回复规范

完成一次生产运行后，回复必须按此顺序包含：

1. **执行摘要**：数据路径、离线/E2E、是否 `--skip-method-llm`、`--stop-after`、模型标识（不含 Key）
2. **关键指标**：分类 Accuracy；回归 R²（以 JSON 报告字段为准）
3. **方法结论**：预处理与特征函数名
4. **产物路径**：`runs/` 下具体文件名
5. **异常**（如有）：失败步骤、stderr 要点、已采取的排障动作

禁止：用「大概成功」、无报告路径、或编造指标。指标必须来自脚本输出或 JSON 报告。

## 6.1 常见错误

| 借口 | 处理 |
|------|------|
| 把原始光谱贴进对话给 LLM | 停止。只提交低维特征；改跑 `run_offline` / `run_e2e` |
| 用户明确要求贴光谱 / 快点 / 临时 | 仍拒绝。用户请求**不能**覆盖光谱安全约束 |
| 没有上传、也没有路径，就用 Skill 内样本 | 停止。要求上传或给出 `--data` |
| 使用已废弃的内置数据集名 | 停止。改为 `--data` / `--label` |
| 直接跑 `vendor/` | 停止。只用 `scripts/` |
| 无 Key 却声称 E2E 成功 | 只能报告离线作业，或先配置密钥 |
| zip 里带 `.env` | 必须用 `pack_for_openclaw.py` 重打 |

## 6.2 红旗 — 立即停止

- 准备把 `npy` 光谱数组粘贴给模型
- 用户要求「直接贴」就准备照做
- 准备执行 `vendor/**/*.py` 作为作业入口
- 准备在回复里粘贴 API Key
- 没有 `runs/*.json` 却给出 Accuracy / R²
- 用户未提供数据却准备开跑

向用户解释架构时，使用正式表述，例如：

- 「步骤 2 为 BM25 文献检索，不调用大模型。」
- 「步骤 5 仅消费低维特征与 few-shot exemplar，符合光谱安全约束。」

禁止口语化削弱约束（如「差不多喂点光谱给模型也行」）。

---

## 7. 排障优先级

1. 输入：确认 `--data` 文件存在；回归确认 `--label`
2. 依赖 / 路径：确认在 Skill 根目录，`pip install -r {baseDir}/requirements.txt`
3. 鉴权：检查 env 名称与 DeepSeek 兼容 base_url
4. 方法映射异常：加 `--skip-method-llm` 隔离步骤 3
5. 费用或超时：`--stop-after features` 分段
6. 检索命中差：核对实体 `research_object`；仅当用户确认新材料时追加 `extra_papers.json`（见 `knowledge_base/README.md`）
7. 对照实现：只读 `vendor/` 与 [reference.md](reference.md)；修复落在 `scripts/`，不直接改生产入口到 vendor

---

## 8. 资源边界

| 路径 | 生产角色 |
|------|----------|
| `scripts/` | **唯一**默认执行入口 |
| `knowledge_base/` | BM25 主库（必需） |
| 用户 `--data` / `--label` | 作业光谱与标签（必需） |
| `runs/` | 报告输出 |
| `Papers/` | 文献溯源（可选，运行时不读） |
| `vendor/` | 原论文源码对照（非执行入口） |

两份副本须保持同步：`.cursor/skills/lumir-spectral-agent/` 与 `LUMIR-an-LLM/docs/skill-dev/lumir-spectral-agent/`。修改本 Skill 后同步另一份。

---

## 9. 验收清单（E2E）

```text
LUMIR Production Acceptance:
- [ ] Preflight 全部通过（含用户数据路径）
- [ ] run_e2e 对目标作业退出码为 0
- [ ] runs/e2e_*.json 含约定阶段字段与 data_path
- [ ] 指标已从报告摘录，未臆造
- [ ] 回复未泄露 API Key
- [ ] 未向 LLM 提交原始高维光谱
```
