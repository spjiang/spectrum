# 农业/食品质检示例

本目录保存农业、食品、农产品质检相关示例。当前示例主要以苹果质检为主。

## 文件结构

| 文件 | 说明 |
| --- | --- |
| [`data/sample_spectrum.json`](data/sample_spectrum.json) | 苹果样本高光谱示例数据 |
| [`training/sft_train.jsonl`](training/sft_train.jsonl) | 农产品质检千问 SFT 训练样本 |
| [`training/train_samples.jsonl`](training/train_samples.jsonl) | 分类、回归、报告生成等综合训练样本 |

## 对应文档

| 文档 | 说明 |
| --- | --- |
| [`../../../docs/scenarios/agriculture-quality/训练方案.md`](../../../docs/scenarios/agriculture-quality/训练方案.md) | 农业/食品质检完整训练方案 |

## 说明

这些样本用于理解高光谱训练流程。当前项目重点是金属识别时，可把本目录作为通用流程参考，不建议直接复用苹果场景的波段规则。
