# LUMIR Skill 便携包说明

本目录为**自包含** Skill：压缩整个 `lumir-spectral-agent/` 即可拷到其它 Agent 客户端使用，不再依赖仓库外的 `LUMIR-an-LLM/...` 路径。

目录职责与运行/对照分层详见 [整体说明.md](整体说明.md)。

## 目录结构

```text
lumir-spectral-agent/
├── SKILL.md                 # Agent 入口说明
├── 整体说明.md               # 总览 + 目录职责
├── 配置说明.md / 测试说明.md
├── config.example.yaml
├── .env.example
├── requirements.txt
├── knowledge_base/
│   ├── structured_papers1.json   # 主知识库（必需）
│   ├── extra_papers.example.json
│   └── README.md
├── data/                         # 演示光谱数据（必需）
├── Papers/                       # 文献溯源（可选，E2E 不读）
├── scripts/
│   ├── demo_pipeline.py          # 离线演示
│   └── run_e2e.py                # DeepSeek 端到端
├── vendor/                       # 原论文源码副本（对照用）
│   ├── README.md
│   └── LLM-Agent-for-Automated-Infrared-Spectral-Reasoning-main/
└── runs/                         # 运行报告输出
```

`vendor/` 含原 `Agent.py`、`Retrieval.py`、`main.ipynb` 等；`data/` / `Papers/` 只保留在 Skill 根，未再拷进 vendor（见 `vendor/README.md`）。日常运行仍用根目录 `scripts/`。

## 其它客户端使用步骤

1. 解压到客户端 Skills 目录（保持文件夹名 `lumir-spectral-agent`）
2. 安装依赖：`pip install -r requirements.txt`
3. 配置 Key：
   ```bash
   cp .env.example .env
   # 编辑 .env 填写 LUMIR_API_KEY
   cp config.example.yaml config.yaml
   ```
4. 运行：
   ```bash
   python scripts/demo_pipeline.py --dataset chenpi --offline
   python scripts/run_e2e.py --dataset chenpi
   ```
5. 在对话中 `@SKILL.md` 或提及 LUMIR，即可触发本 Skill

## 体积说明

约 50MB（含 `data/` ~5MB + `Papers/` ~44MB）。若只要跑流水线、不要文献溯源，可删除 `Papers/` 后再压缩（约 5–6MB）。

## 勿打包进分发 zip 的内容

- `.env`、`config.yaml`（含密钥）
- `runs/*.json`（本地报告，可选清空）
