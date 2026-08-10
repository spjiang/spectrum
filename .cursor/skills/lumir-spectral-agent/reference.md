# LUMIR 参考手册

## 流水线示意

```
自然语言问题 + 光谱数组
        │
        ▼
1. LLM 实体抽取 → research_object, task_type
        │
        ▼
2. BM25（structured_papers1.json ± extra_papers.json）
        │
        ▼
3. LLM 方法映射 + 多数投票（或 Table4 回退）
        │
        ▼
4. 本地 Preprocess + Feature → 低维特征
        │
        ▼
5. LLM few-shot → classification | regression | anomaly detection
```

## 工程配置

| 文件 | 作用 |
|------|------|
| `config.example.yaml` | 配置模板（DeepSeek、KB、pipeline） |
| `config.yaml` | 本地配置（gitignore，勿提交密钥） |
| `.env.example` | API Key / base_url / model 示例 |
| `knowledge_base/README.md` | 主库 + 追加库说明 |
| `scripts/run_e2e.py` | 端到端测试入口 |
| `scripts/demo_pipeline.py` | 离线冒烟 |
| `配置说明.md` | 配置手册 |
| `测试说明.md` | **演示文档**（讲解节奏、命令、话术） |
| `runs/` | E2E JSON 报告 |

DeepSeek 默认：

- `base_url`: `https://api.deepseek.com`
- `model`: `deepseek-chat`
- Key：`LUMIR_API_KEY` 或 `DEEPSEEK_API_KEY`

## 知识库

- **主库**：源码目录 `structured_papers1.json`（SDAAP 结构化文献，约 129 条）
- **追加**：`knowledge_base/extra_papers.json`（可选，同字段数组）
- 检索字段主要用 `paper_name` + `research_object`
- 方法字段：`preprocessing_method` / `feature_extracting_method`

测试牛奶/陈皮/中药材/Corn 等：**先用主库，不必自建。**

## 数据集（`data/`）

| 名称 | 文件 | 典型 shape | 任务 |
|------|------|------------|------|
| milk | `milk/milk_data.npy` | (9, 40, 601) | 分类 |
| chenpi (CRP) | `Chenpi/chenpi.npy` | (8, 30, 800) | 分类 |
| chinese medicine | `CN_medicine/cnm.npy` | (3, 40, 228) | 分类 |
| tecator | `tecator/*` | (215, 100) | 回归 |
| corn | `corn/*` | (80, 700) | 回归 |

## 文献引导方法表（Table 4）

| 材料 | 预处理 | 特征 |
|------|--------|------|
| Milk | SG | PCA |
| Chinese medicinal herbs | SNV+FD | PCA |
| CRP / chenpi | SNV | PCA |
| Wastewater | BC (AsLS) | Pearson |
| Tecator | SNV | PLS |
| Corn | SNV | PLS |

函数名映射：

- SG → `savitzky_golay_smoothing`
- SNV → `standard_normal_variate`
- SNV+FD → `snv_fd`
- BC → `baseline_correction_asls`
- PCA → `pca_feature_extraction`
- PLS → `Partial_Least_Squares`

## 常见问题

1. **没配 Key**：`run_e2e.py` 会提示设置 `LUMIR_API_KEY`。
2. **步骤3映射失败**：自动回退 Table4；或加 `--skip-method-llm`。
3. **新材料检索不准**：向 `extra_papers.json` 追加同结构条目。
4. **省费用**：`--stop-after features` 跳过 few-shot。
5. **路径**：原 notebook 的 Windows 反斜杠在 macOS/Linux 需改用 `pathlib`。
