# 农业/食品质检场景

本目录用于整理农业、食品、农产品质检相关文档。当前保留了早期以苹果质检为示例的完整训练方案，可用于理解高光谱从采集到千问微调的全流程。

## 适用问题

- 农产品品质分级，例如健康、碰伤、腐烂
- 糖度、水分、蛋白质等成分回归预测
- 缺陷检测、异常区域报告生成
- 产线质检 API 和模型部署

## 文档

| 文档 | 说明 |
| --- | --- |
| [`训练方案.md`](训练方案.md) | 以农产品质检为例的完整高光谱 + 千问训练方案 |

## 示例数据

| 文件 | 说明 |
| --- | --- |
| [`../../../examples/scenarios/agriculture-quality/data/sample_spectrum.json`](../../../examples/scenarios/agriculture-quality/data/sample_spectrum.json) | 苹果样本高光谱示例 |
| [`../../../examples/scenarios/agriculture-quality/training/sft_train.jsonl`](../../../examples/scenarios/agriculture-quality/training/sft_train.jsonl) | 农产品质检 SFT 训练样本 |
| [`../../../examples/scenarios/agriculture-quality/training/train_samples.jsonl`](../../../examples/scenarios/agriculture-quality/training/train_samples.jsonl) | 分类、回归、报告生成样本 |
| [`../../../dataset/labels.csv`](../../../dataset/labels.csv) | 标签表示例 |

## 与金属识别的区别

| 对比项 | 农业/食品质检 | 金属识别 |
| --- | --- | --- |
| 主要信号 | 水分、组织结构、色素、成分吸收 | 表面反射率、颜色倾向、氧化/镀层状态 |
| 常见任务 | 分级、病害、糖度、水分 | 黄金/白银/铜/铝识别、表面状态识别 |
| 关键风险 | 样本新鲜度、采集批次、化学真值 | 镜面反射、表面粗糙度、镀层混淆 |
| 辅助检测 | 糖度计、实验室成分分析 | XRF、密度、导电率 |

## 使用建议

如果当前项目聚焦金属识别，建议把本文档作为“通用训练流程参考”，不要直接复用苹果波段规则。金属需要重新设计特征、标签和负样本。
