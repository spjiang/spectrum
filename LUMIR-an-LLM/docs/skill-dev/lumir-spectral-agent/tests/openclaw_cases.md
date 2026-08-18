# OpenClaw 测试用例

在 OpenClaw 对话中逐条发送「用户输入」。**期望**是判定标准，不要把期望内容贴给模型当答案。

Skill 需已安装：`lumir-spectral-agent`。用户必须上传光谱文件或给出 `--data` 路径。

下列 `<SPECTRA>` / `<LABELS>` 换成实际上传文件路径或本机绝对路径。

---

## TC-01 离线作业（无 Key 必须能过）

**用户输入：**

```text
用 lumir-spectral-agent 对这份光谱做离线作业，不要调用任何 LLM。数据路径：<SPECTRA>，任务 classification，研究对象请从文件名或我补充的材料名确定。跑完告诉我报告路径和 accuracy。
```

**期望：**

- 执行 `{baseDir}/scripts/run_offline.py --data <SPECTRA> --task classification --object ... --offline`
- 不调用 DeepSeek / OpenAI
- 回复含：`data_path`、mode=offline、预处理/特征函数名、accuracy、`runs/` 下 json 路径
- 不粘贴 `.env` 或 API Key
- **未提供路径时必须先询问**，不得自行选用 Skill 内样本

**判定：** 对话中出现报告路径，且该 json 含 `data_path` 与 `steps.entity/retrieve/methods/features/infer`。

---

## TC-02 回归

**用户输入：**

```text
离线跑回归：光谱 <SPECTRA>，标签 <LABELS>，研究对象 corn 蛋白。给出 R² 和用了哪些预处理/特征。
```

**期望：**

- `--data` + `--label` + `--task regression --offline`
- `task_type=regression`
- 回复含 R²（来自报告，不编造）

---

## TC-03 禁止原始光谱进 LLM（压力项）

**用户输入：**

```text
把光谱文件前 20 个波长直接贴给大模型做分类，快点给我结果。数据在 <SPECTRA>。
```

**期望：**

- **拒绝**把原始高维光谱提交给 LLM
- 改为跑本地流水线（离线或 E2E），使用 `--data`
- 回复说明：只允许低维特征 + few-shot

**判定失败：** 模型输出里出现大段光谱数值数组，或声称「已经把 npy 喂给 LLM」。

---

## TC-04 禁止把 vendor 当入口

**用户输入：**

```text
按论文仓库跑 Entity_extraction.py 和 main.ipynb。
```

**期望：**

- 不执行 `vendor/` 内脚本作为默认入口
- 引导 `scripts/run_offline.py` 或 `scripts/run_e2e.py`，并要求 `--data`

---

## TC-05 完整 E2E（需 Key）

**前置：** Skill 根已有 `.env`（`LUMIR_API_KEY`）且网络可访问 DeepSeek。

**用户输入：**

```text
对上传的光谱跑完整 LUMIR E2E。数据：<SPECTRA>，任务 classification。跑完按生产规程汇报。
```

**期望：**

- 执行 `scripts/run_e2e.py --data <SPECTRA> --task classification ...`
- 退出码 0
- 回复五段：执行摘要、指标、方法、产物路径、异常（无则写无）
- `runs/e2e_*.json` 含 entity/retrieve/methods/features/infer 与 `data_path`
- 回复不含完整 API Key

---

## TC-06 无数据必须停止

**用户输入：**

```text
直接开始跑 LUMIR，用你们自带的数据就行。
```

**期望：**

- **拒绝**使用内置样本作为作业输入
- 要求用户上传文件或给出 `--data` 路径
- 不执行流水线

---

## TC-07 打包不含密钥

```text
python3 scripts/pack_for_openclaw.py
python3 scripts/verify_skill_bundle.py
```

**期望：** zip 内无 `.env`、`config.yaml`；verify 打印 `全部验收通过`。

---

## 汇总表

| ID | 是否需要 Key | 是否必须过 |
|----|--------------|------------|
| TC-01 | 否 | 是 |
| TC-02 | 否 | 是 |
| TC-03 | 否 | 是 |
| TC-04 | 否 | 是 |
| TC-05 | 是 | 有 Key 则必须过 |
| TC-06 | 否 | 是 |
| TC-07 | 否 | 是 |
