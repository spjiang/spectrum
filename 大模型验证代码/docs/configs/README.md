# 训练配置

本目录用于保存模型训练配置文件。

| 文件 | 说明 |
| --- | --- |
| [`train_lora.yaml`](train_lora.yaml) | LLaMA-Factory 的 Qwen LoRA 微调配置 |

## 使用位置

当前配置适合用于高光谱特征文本化后的千问 SFT 微调。

示例命令：

```bash
llamafactory-cli train docs/configs/train_lora.yaml
```

## 与应用场景的关系

训练配置是通用的。金属识别、农业/食品质检等场景主要差异在训练数据集，而不是 LoRA 配置本身。

| 场景 | 数据文件示例 |
| --- | --- |
| 金属识别 | `examples/scenarios/metal-identification/training/metal_sft_train_full.jsonl`（800 条） |
| 农业/食品质检 | `examples/scenarios/agriculture-quality/training/sft_train.jsonl` |
