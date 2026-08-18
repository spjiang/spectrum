# LUMIR 参考手册

## 流水线示意

```
用户光谱路径 + 自然语言问题
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
| `scripts/job_input.py` | `--data` / `--label` 校验 |
| `scripts/run_e2e.py` | 端到端作业入口 |
| `scripts/run_offline.py` | 离线作业 |
| `配置说明.md` | 配置手册 |
| `测试说明.md` | 验收节奏与命令 |
| `runs/` | JSON 报告（含 `data_path`） |

DeepSeek 默认：

- `base_url`: `https://api.deepseek.com`
- `model`: `deepseek-chat`
- Key：`LUMIR_API_KEY` 或 `DEEPSEEK_API_KEY`

## 知识库

- **主库**：`knowledge_base/structured_papers1.json`（SDAAP 结构化文献，约 129 条）
- **追加**：`knowledge_base/extra_papers.json`（可选）
- 检索字段主要用 `paper_name` + `research_object`
- 方法字段：`preprocessing_method` / `feature_extracting_method`

## 作业数据

生产入口只接受用户文件：

```bash
--data /path/to/spectra.npy
--label /path/to/labels.npy   # 回归必填
--task classification|regression|anomaly_detection
--object "<研究对象>"
```

OpenClaw：使用用户上传文件的绝对路径作为 `--data`。未提供路径则停止询问，不得回退样本文件。

数组约定：`.npy`；2D 视为 `(n_samples, n_bands)`，自动升为 `(1, n_samples, n_bands)`；3D 分类常见 `(n_classes, n_per_class, n_bands)`。

## 文献引导方法表（Table 4）

| 材料 | 预处理 | 特征 |
|------|--------|------|
| Milk | SG | PCA |
| Chinese medicinal herbs | SNV+FD | PCA |
| CRP | SNV | PCA |
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
2. **没给数据**：`job_input` 以非零退出，要求 `--data`。
3. **步骤3映射失败**：自动回退 Table4；或加 `--skip-method-llm`。
4. **新材料检索不准**：向 `extra_papers.json` 追加同结构条目。
5. **省费用**：`--stop-after features` 跳过 few-shot。
