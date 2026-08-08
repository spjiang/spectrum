# 示例中心

本目录按应用场景整理示例数据、训练样本和数据生成脚本。

## 目录结构

| 目录 | 应用场景 | 说明 |
| --- | --- | --- |
| `scenarios/metal-identification/` | 金属质量检查 | 黄金、白银合格/待复检/不合格质检示例 |
| `scenarios/agriculture-quality/` | 农业/食品质检 | 苹果等农产品高光谱示例 |
| `common/` | 通用脚本 | 农业场景数据集生成脚本 |

## 金属质量检查示例

| 文件 | 说明 |
| --- | --- |
| [`scenarios/metal-identification/data/metal_sample_spectrum.json`](scenarios/metal-identification/data/metal_sample_spectrum.json) | 4 条质检样本：合格黄金、合格白银、待复检、不合格 |
| [`scenarios/metal-identification/data/labels.csv`](scenarios/metal-identification/data/labels.csv) | 质检标签表 |
| [`scenarios/metal-identification/data/qc_standards.json`](scenarios/metal-identification/data/qc_standards.json) | 黄金/白银合格标准模板 |
| [`scenarios/metal-identification/training/metal_sft_train.jsonl`](scenarios/metal-identification/training/metal_sft_train.jsonl) | 金属质检千问 SFT 训练样本 |
| [`scenarios/metal-identification/prepare_metal_qc_dataset.py`](scenarios/metal-identification/prepare_metal_qc_dataset.py) | 由示例光谱生成训练 JSONL |

### 快速开始（金属质检）

```bash
# 1. 查看质检示例光谱
cat examples/scenarios/metal-identification/data/metal_sample_spectrum.json

# 2. 由示例数据重新生成训练集
python examples/scenarios/metal-identification/prepare_metal_qc_dataset.py

# 3. 查看训练样本
cat examples/scenarios/metal-identification/training/metal_sft_train.jsonl
```

## 农业/食品质检示例

| 文件 | 说明 |
| --- | --- |
| [`scenarios/agriculture-quality/data/sample_spectrum.json`](scenarios/agriculture-quality/data/sample_spectrum.json) | 苹果样本高光谱示例 |
| [`scenarios/agriculture-quality/training/sft_train.jsonl`](scenarios/agriculture-quality/training/sft_train.jsonl) | 农产品质检训练样本 |
| [`common/prepare_dataset.py`](common/prepare_dataset.py) | 农业场景演示数据生成脚本 |

## 推荐入口

| 入口 | 说明 |
| --- | --- |
| [`scenarios/metal-identification/README.md`](scenarios/metal-identification/README.md) | 金属质量检查示例入口 |
| [`scenarios/agriculture-quality/README.md`](scenarios/agriculture-quality/README.md) | 农业/食品质检示例入口 |
