# 原论文源码（vendor）

本目录为 LUMIR 论文仓库源码副本，便于对照与阅读，**不是** Skill 默认运行入口。

## 内容

`LLM-Agent-for-Automated-Infrared-Spectral-Reasoning-main/` 含：

- `Entity_extraction.py` / `Retrieval.py` / `Agent.py`
- `Preprocess_method.py` / `Feature_extract.py` / `Generate_single.py`
- `main.ipynb`、`dataset.py`、`other_models.py` 等
- 源码旁的 `structured_papers1.json`（与 Skill 根 `knowledge_base/` 同源）

## 与 Skill 根目录的关系

| 资源 | 位置 | 说明 |
|------|------|------|
| 演示光谱 `data/` | Skill 根 `data/` | 未再拷进 vendor，避免体积翻倍 |
| 文献溯源 `Papers/` | Skill 根 `Papers/` | 同上 |
| 主知识库 | Skill 根 `knowledge_base/` | 运行时以此为准 |
| 工程脚本 | Skill 根 `scripts/` | `demo_pipeline.py` / `run_e2e.py` |

若需在 vendor 内按原 notebook 相对路径找数据，可自行：

```bash
cd LLM-Agent-for-Automated-Infrared-Spectral-Reasoning-main
ln -s ../../data data
ln -s ../../Papers Papers
```

## 注意

原脚本依赖较重（nltk、matplotlib、部分路径写死等）。日常演示与 E2E 请用 Skill 根目录的 `scripts/`，勿直接把 vendor 当作默认入口。
