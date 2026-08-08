# 金属质量检查示例

本目录保存黄金、白银等金属**质量检查**相关示例，包括合格、待复检、不合格样本，以及质检标准模板和训练集生成脚本。

## 文件结构

```text
metal-identification/
├── data/
│   ├── metal_raw_spectrum.json          # 原始 DN 与白板/暗场参考
│   ├── metal_sample_spectrum.json       # 定标后反射率质检示例（4 条）
│   ├── metal_sample_spectrum_full.json  # 大规模合成光谱（800 条）
│   ├── labels.csv                       # 4 条示例标签
│   ├── labels_full.csv                  # 800 条合成标签
│   └── qc_standards.json                # 合格标准模板
├── training/
│   ├── metal_sft_train.jsonl            # 4 条演示训练样本
│   ├── metal_sft_train_full.jsonl       # 800 条完整训练数据
│   └── dataset_info.json                # LLaMA-Factory 数据集注册
├── llamafactory/
│   ├── train_metal_lora.yaml              # Qwen2.5-7B LoRA 训练配置
│   └── README.md                          # 训练与验证完整指南
├── prepare_metal_qc_dataset.py          # 4 条示例 → JSONL
├── generate_metal_qc_big_dataset.py     # 大规模合成数据生成器
└── evaluate_metal_qc_model.py           # LoRA 微调效果验证脚本
```

## 文件说明

| 文件 | 说明 |
| --- | --- |
| [`data/metal_raw_spectrum.json`](data/metal_raw_spectrum.json) | 原始 DN、白板/暗场参考，与定标后样本一一对应 |
| [`data/metal_sample_spectrum.json`](data/metal_sample_spectrum.json) | 合格黄金、合格白银、待复检、不合格 4 条样本 |
| [`data/labels.csv`](data/labels.csv) | 标称材质、质检结论、等级、缺陷、处置建议 |
| [`data/qc_standards.json`](data/qc_standards.json) | 黄金/白银红蓝比、近红外阈值等标准模板 |
| [`training/metal_sft_train.jsonl`](training/metal_sft_train.jsonl) | 4 条演示训练样本 |
| [`training/metal_sft_train_full.jsonl`](training/metal_sft_train_full.jsonl) | **800 条完整千问 SFT 训练数据** |
| [`training/dataset_info.json`](training/dataset_info.json) | LLaMA-Factory 数据集注册 |
| [`generate_metal_qc_big_dataset.py`](generate_metal_qc_big_dataset.py) | 大规模合成数据生成器 |
| [`evaluate_metal_qc_model.py`](evaluate_metal_qc_model.py) | LoRA 微调效果验证 |
| [`llamafactory/`](llamafactory/) | Qwen2.5-7B LoRA 训练配置与指南 |

## 样本类型

| 样本 | 标称材质 | 质检结论 | 处置 |
| --- | --- | --- | --- |
| `qc_gold_001_roi_center` | 黄金 | 合格 | 放行 |
| `qc_silver_001_roi_center` | 白银 | 合格 | 放行 |
| `qc_gold_003_roi_center` | 黄金 | 待复检 | 转人工复检 |
| `qc_silver_004_roi_center` | 白银 | 不合格 | 剔除 |

## 快速开始

```bash
# 1. 生成 800 条完整训练数据
python examples/scenarios/metal-identification/generate_metal_qc_big_dataset.py

# 2. 查看训练样本
head -n 2 examples/scenarios/metal-identification/training/metal_sft_train_full.jsonl

# 3. 在 LLaMA-Factory 中训练（详见 llamafactory/README.md）
llamafactory-cli train examples/scenarios/metal-identification/llamafactory/train_metal_lora.yaml

# 4. 验证微调效果
python examples/scenarios/metal-identification/evaluate_metal_qc_model.py \
    --lora-path saves/metal-qc-qwen7b-lora --num-samples 20
```

### 演示用小数据集（4 条）

```bash
python examples/scenarios/metal-identification/prepare_metal_qc_dataset.py
cat examples/scenarios/metal-identification/training/metal_sft_train.jsonl
```

## 对应文档

| 文档 | 说明 |
| --- | --- |
| [`../../../docs/scenarios/metal-identification/金属识别学习指南.md`](../../../docs/scenarios/metal-identification/金属识别学习指南.md) | 逐行解读金属质检数据和训练样本 |

## 学习顺序

1. 先看 `data/metal_raw_spectrum.json`，理解相机输出的原始 DN 和定标参考。
2. 再看 `data/metal_sample_spectrum.json`，理解标称材质、质检结论、缺陷和处置字段。
3. 再看 `data/qc_standards.json`，理解合格阈值如何定义。
4. 打开 `training/metal_sft_train.jsonl`，理解合格 / 待复检 / 不合格训练样本格式。
5. 运行 `prepare_metal_qc_dataset.py`，理解示例数据如何转成训练集。
