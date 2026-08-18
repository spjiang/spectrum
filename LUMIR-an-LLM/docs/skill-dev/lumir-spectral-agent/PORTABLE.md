# LUMIR Skill 便携包说明

本目录为**自包含** Skill：压缩整个 `lumir-spectral-agent/` 即可拷到其它 Agent 客户端。光谱作业数据由用户上传或 `--data` 路径提供，不依赖仓库外代码路径。

目录职责详见 [整体说明.md](整体说明.md)。

## 目录结构

```text
lumir-spectral-agent/
├── SKILL.md
├── 整体说明.md / 配置说明.md / 测试说明.md
├── config.example.yaml
├── .env.example
├── requirements.txt
├── knowledge_base/
│   ├── structured_papers1.json   # 主知识库（必需）
│   └── extra_papers.example.json
├── scripts/
│   ├── job_input.py              # 用户数据路径校验
│   ├── run_offline.py            # 离线作业
│   └── run_e2e.py                # DeepSeek 端到端
├── Papers/                       # 文献溯源（可选）
├── vendor/                       # 原论文源码副本（对照用）
└── runs/                         # 运行报告输出
```

## OpenClaw 导入

```bash
python3 scripts/pack_for_openclaw.py
# 生成：../lumir-spectral-agent-openclaw.zip
openclaw skills install ./lumir-spectral-agent --as lumir-spectral-agent
```

对话用例见 [tests/openclaw_cases.md](tests/openclaw_cases.md)。

## 其它客户端

1. 解压到 Skills 目录（文件夹名 `lumir-spectral-agent`）
2. `pip install -r requirements.txt`
3. 配置 Key：

```bash
cp .env.example .env
cp config.example.yaml config.yaml
```

4. 运行（替换为用户文件路径）：

```bash
python scripts/run_offline.py --data /path/to/spectra.npy --task classification --object "<材料>" --offline
python scripts/run_e2e.py --data /path/to/spectra.npy --task classification --object "<材料>"
```

5. 对话中 `@SKILL.md` 或提及 LUMIR

## 勿打包

- `.env`、`config.yaml`
- `runs/*.json`
