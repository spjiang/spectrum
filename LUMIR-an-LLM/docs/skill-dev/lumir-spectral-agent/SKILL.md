---
name: lumir-spectral-agent
description: >-
  Executes and explains the production LUMIR infrared/NIR spectral reasoning
  pipeline: LLM entity extraction, BM25 literature retrieval, method-name
  mapping with majority vote, local chemometric preprocess/feature extraction,
  and LLM few-shot classification/regression/anomaly detection. Use when the
  user mentions LUMIR, NIR/MIR spectral agent, SDAAP literature-guided
  chemometrics, structured_papers knowledge base, or asks to run/configure/
  troubleshoot lumir-spectral-agent E2E or offline demos.
---

# LUMIR Spectral Agent（生产规程）

本 Skill 为红外光谱多任务推理流水线的**唯一生产执行规范**。Agent 必须按本文执行；细节文档仅在需要时按需打开，不得用非正式演示话术替代本规程。

- 目录与分层职责 → [整体说明.md](整体说明.md)
- 配置与密钥 → [配置说明.md](配置说明.md)
- 验收演示节奏 → [测试说明.md](测试说明.md)
- 论文概念对照 → [reference.md](reference.md)
- 便携分发 → [PORTABLE.md](PORTABLE.md)

**Skill 根目录** = 本文件所在目录（下称 `SKILL_ROOT`）。所有命令默认在 `SKILL_ROOT` 下执行。

---

## 1. 适用范围

| 允许 | 禁止 |
|------|------|
| 运行 / 解释 / 排障本 Skill 内流水线 | 擅自改写五步顺序或跳过强制约束 |
| 使用内置数据集与知识库做分类/回归任务 | 将原始高维光谱整段提交给 LLM |
| 在用户明确要求时追加 `extra_papers.json` | 无依据修改主库 `structured_papers1.json` |
| 对照阅读 `vendor/` 源码 | 将 `vendor/` 作为默认运行入口 |

支持的 `--dataset`：`chenpi` | `milk` | `cn_medicine` | `corn` | `tecator`。

---

## 2. 强制约束（MUST / MUST NOT）

1. **MUST NOT** 向任何 LLM 提交完整原始高维光谱；仅允许提交**低维特征**与少量 exemplar。
2. **MUST** 将文献方法名映射到预定义预处理/特征函数列表；禁止发明未实现的函数名。
3. **MUST** 以 `scripts/run_e2e.py` / `scripts/demo_pipeline.py` 为生产入口；**MUST NOT** 默认执行 `vendor/` 内原脚本。
4. **MUST** 优先使用 `SKILL_ROOT` 内 `knowledge_base/` 与 `data/`；不得假定依赖仓库外路径。
5. **MUST NOT** 将真实 API Key 写入仓库、`SKILL.md`、聊天可提交文件或分发 zip；仅允许环境变量或本地 `.env`（已 gitignore）。
6. **MUST NOT** 在回复中回显完整 API Key。
7. **MUST** 在完整 E2E 前确认可用密钥：`LUMIR_API_KEY` 或 `DEEPSEEK_API_KEY`（或配置声明的其它 env）。
8. **MUST** 跑完 E2E 后核对 `runs/e2e_*.json` 含：`entity`、`retrieve`、`methods`、`features`、`infer`（若 `--stop-after` 提前结束，则核对至对应阶段）。
9. 用户未要求时 **MUST NOT** 修改主知识库；内置对象（牛奶/陈皮/中药材/Corn 等）优先用现有库。
10. 解释流水线时 **MUST** 区分：步骤 2、4 为本地计算；步骤 1、3、5 依赖 LLM。

---

## 3. 标准流水线（不可擅自改序）

```text
1. LLM 实体抽取 → research_object + task_type
2. BM25 检索 knowledge_base → 预处理/特征方法描述
3. LLM 方法名映射 + 多数投票（可用 --skip-method-llm 改 Table4 基线）
4. 本地预处理 + 特征提取
5. LLM few-shot 推理（分类 / 回归 / 异常检测）
```

完整 E2E 需要 LLM。仅验证检索与特征、不调 LLM 时，使用离线冒烟命令（见 §5）。

---

## 4. 执行前检查清单

Agent 在运行生产任务前，按序确认并勾选：

```text
Preflight:
- [ ] 工作目录为 SKILL_ROOT（或对 scripts 使用绝对路径）
- [ ] 存在 knowledge_base/structured_papers1.json 与 data/
- [ ] 已安装 requirements.txt 依赖
- [ ] 完整 E2E：已配置 LUMIR_API_KEY（或等价）与 config.yaml（可由 example 复制）
- [ ] knowledge_base.primary 为 auto（默认）
- [ ] 用户目标数据集已明确；未明确则使用 config 中 datasets.default（默认 chenpi）
```

缺密钥时：先说明阻塞项；可提议 `--offline` 冒烟或 `--stop-after features`（仍可能需要部分 LLM，以脚本行为为准）。**不得伪造运行成功结果。**

---

## 5. 标准命令（生产）

在 `SKILL_ROOT`：

```bash
# 离线冒烟（无 Key）
python scripts/demo_pipeline.py --dataset chenpi --offline

# 完整 E2E
python scripts/run_e2e.py --dataset chenpi
python scripts/run_e2e.py --dataset milk
python scripts/run_e2e.py --dataset corn

# 步骤3不用 LLM（Table4 基线，排障）
python scripts/run_e2e.py --dataset milk --skip-method-llm

# 跑到指定阶段（控费 / 分段验收）
python scripts/run_e2e.py --dataset corn --stop-after features
```

报告路径：`SKILL_ROOT/runs/e2e_<dataset>_<timestamp>.json`。

配置初始化（仅当本地缺失时）：

```bash
cp .env.example .env                 # 填写 LUMIR_API_KEY，勿提交
cp config.example.yaml config.yaml   # 按需改 temperature / few_shot 等
```

默认 LLM：`base_url=https://api.deepseek.com`，`model=deepseek-chat`。可用 `LUMIR_BASE_URL` / `LUMIR_MODEL` 覆盖。

---

## 6. 交付与回复规范

完成一次生产运行后，Agent 回复必须包含：

1. **执行摘要**：数据集、是否跳过 method-LLM、`--stop-after`、模型标识（不含 Key）
2. **关键指标**：分类报告 Accuracy；回归报告 R² / RMSE（以报告字段为准）
3. **方法结论**：投票后的预处理与特征函数名
4. **产物路径**：`runs/` 下具体文件名
5. **异常**（如有）：失败步骤、stderr 要点、已采取的排障动作

禁止：用「大概成功」、无报告路径、或编造指标。指标必须来自脚本输出或 JSON 报告。

向用户解释架构时，使用正式表述，例如：

- 「步骤 2 为 BM25 文献检索，不调用大模型。」
- 「步骤 5 仅消费低维特征与 few-shot exemplar，符合光谱安全约束。」

禁止口语化削弱约束（如「差不多喂点光谱给模型也行」）。

---

## 7. 排障优先级

1. 依赖 / 路径：确认在 `SKILL_ROOT`，`pip install -r requirements.txt`
2. 鉴权：检查 env 名称与 DeepSeek 兼容 base_url
3. 方法映射异常：加 `--skip-method-llm` 隔离步骤 3
4. 费用或超时：`--stop-after features` 分段
5. 检索命中差：核对实体 `research_object`；仅当用户确认新材料时追加 `extra_papers.json`（见 `knowledge_base/README.md`）
6. 对照实现：只读 `vendor/` 与 [reference.md](reference.md)；修复落在 `scripts/`，不直接改生产入口到 vendor

---

## 8. 资源边界

| 路径 | 生产角色 |
|------|----------|
| `scripts/` | **唯一**默认执行入口 |
| `knowledge_base/` | BM25 主库（必需） |
| `data/` | 内置光谱数据（必需） |
| `runs/` | 报告输出 |
| `Papers/` | 文献溯源（可选，运行时不读） |
| `vendor/` | 原论文源码对照（非执行入口） |

两份副本须保持同步：`.cursor/skills/lumir-spectral-agent/` 与 `LUMIR-an-LLM/docs/skill-dev/lumir-spectral-agent/`。修改本 Skill 后同步另一份。

---

## 9. 验收清单（E2E）

```text
LUMIR Production Acceptance:
- [ ] Preflight 全部通过
- [ ] run_e2e 对目标 dataset 退出码为 0
- [ ] runs/e2e_*.json 含约定阶段字段
- [ ] 指标已从报告摘录，未臆造
- [ ] 回复未泄露 API Key
- [ ] 未向 LLM 提交原始高维光谱
```
