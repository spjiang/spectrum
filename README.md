# Spectrum — 高光谱金属质量检查 + 千问大模型应用

## 背景

当前公司业务是基于高光谱应用开发，重点学习方向为**金属质量检查**，例如黄金、白银等贵金属的材质符合性检查、表面状态判定、合格/不合格分拣和质检报告生成。

## 需求步骤

1. 基于高光谱摄像头采集数据
2. 基于高光谱摄像头采集数据进行大模型训练
3. 训练后的大模型进行应用开发

## 文档与示例

| 文件 | 说明 |
| --- | --- |
| [docs/README.md](docs/README.md) | **文档中心**（按应用场景分类） |
| [docs/scenarios/metal-identification/README.md](docs/scenarios/metal-identification/README.md) | **金属质量检查场景入口** |
| [docs/scenarios/metal-identification/金属识别学习指南.md](docs/scenarios/metal-identification/金属识别学习指南.md) | 金属质检从零学习文档 |
| [docs/common/高光谱训练流程.md](docs/common/高光谱训练流程.md) | 通用高光谱训练流程 |
| [examples/README.md](examples/README.md) | **示例中心**（按应用场景分类） |
| [examples/scenarios/metal-identification/data/metal_sample_spectrum.json](examples/scenarios/metal-identification/data/metal_sample_spectrum.json) | 合格/待复检/不合格金属质检示例数据 |
| [examples/scenarios/metal-identification/data/labels.csv](examples/scenarios/metal-identification/data/labels.csv) | 金属质检标签表 |
| [examples/scenarios/metal-identification/data/qc_standards.json](examples/scenarios/metal-identification/data/qc_standards.json) | 黄金/白银合格标准模板 |
| [examples/scenarios/metal-identification/training/metal_sft_train.jsonl](examples/scenarios/metal-identification/training/metal_sft_train.jsonl) | 金属质检千问 SFT 训练样本 |
| [examples/scenarios/metal-identification/prepare_metal_qc_dataset.py](examples/scenarios/metal-identification/prepare_metal_qc_dataset.py) | 金属质检示例数据 → JSONL |
| [docs/scenarios/agriculture-quality/README.md](docs/scenarios/agriculture-quality/README.md) | 农业/食品质检场景入口 |
| [examples/scenarios/agriculture-quality/training/train_samples.jsonl](examples/scenarios/agriculture-quality/training/train_samples.jsonl) | 农业/食品质检训练样本 |
| [examples/common/prepare_dataset.py](examples/common/prepare_dataset.py) | ENVI 数据 → JSONL 转换脚本 |
| [dataset/labels.csv](dataset/labels.csv) | 标签表示例 |
| [docs/configs/train_lora.yaml](docs/configs/train_lora.yaml) | LLaMA-Factory LoRA 训练配置 |

## 快速开始

```bash
# 1. 查看金属质检示例光谱
cat examples/scenarios/metal-identification/data/metal_sample_spectrum.json

# 2. 由示例数据生成金属质检训练集
python examples/scenarios/metal-identification/prepare_metal_qc_dataset.py

# 3. 查看生成的训练样本
cat examples/scenarios/metal-identification/training/metal_sft_train.jsonl

# 4. 阅读金属质检学习指南
open docs/scenarios/metal-identification/金属识别学习指南.md
```

## 问题索引

1. **文档如何按场景阅读** → 见 [文档中心](docs/README.md)
2. **金属质检数据怎么读** → 见 [金属识别学习指南 §二](docs/scenarios/metal-identification/金属识别学习指南.md#二一个最小高光谱金属质检样本长什么样)
3. **合格与不合格样本有什么区别** → 见 [金属识别学习指南 §三](docs/scenarios/metal-identification/金属识别学习指南.md#三合格与不合格金属的光谱差异)
4. **质检训练数据每一行是什么意思** → 见 [金属识别学习指南 §五](docs/scenarios/metal-identification/金属识别学习指南.md#五金属质检训练数据-jsonl-是什么)
5. **完整训练流程怎么做** → 见 [通用高光谱训练流程](docs/common/高光谱训练流程.md)
