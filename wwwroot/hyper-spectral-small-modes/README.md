# 高光谱分类小模型整理库

按「一模型一目录」整理，便于单独查阅、测试与交付。

## 目录结构

```text
hyper-spectral-small-modes/
├── README.md
├── datasets/                 # 统一测试数据集（一份，硬链自原下载目录）
├── docs/                     # 总文档（下载清单、领导精简版、模型清单等）
├── 2017_SSRN/
│   ├── source/               # 源代码
│   ├── docs/                 # 该模型文档/简介
│   └── datasets -> ../datasets
├── 2024_MSA-GCN/
│   ├── source/
│   ├── docs/
│   └── datasets -> ../datasets
└── ...（共 87 个模型）
```

每个模型目录固定三块：

| 子目录 | 内容 |
|--------|------|
| `source/` | 模型源代码（过滤了超大 `.mat/.pth` 等数据权重） |
| `docs/` | README、模型简介、目录说明 |
| `datasets/` | 软链到根目录 `datasets/`，避免每个模型重复拷贝数据 |

## 数据集现状（`datasets/`）

| 数据 | 状态 |
|------|------|
| Indian Pines | 有（`IndianPines/`） |
| PaviaU / Pavia Centre | 有 |
| Salinas | 有 |
| KSC | 有 |
| Botswana | 有 |
| Houston 2018 | 有（`Houston2018/houstonU2018.mat`） |
| Houston 2013 | 有（`Houston2013/houston13_*.mat`） |
| Trento | 有（HSI / LiDAR / GT） |
| MUUFL | 有（`MUUFL/muufl_*.mat`） |

详细下载说明见：[`docs/数据集人工下载清单.md`](docs/数据集人工下载清单.md)

## 使用方式

1. 打开某个模型，例如 `2025_SGMAE/`
2. 读 `docs/README.md` / `docs/模型简介.md`
3. 在 `source/` 中按原作者方式运行；数据路径指向本模型下的 `datasets/`（即根目录共享数据）

## 来源

整理自：`small_models/Hyperspectral-Image-Classification-Models`  
模型与论文对应关系见：`docs/Model_Description.txt`

## 分享清单

- 统一分享文档：[`docs/模型分享清单.md`](docs/模型分享清单.md)
- 单模型卡片目录：[`docs/模型卡片/`](docs/模型卡片/)
