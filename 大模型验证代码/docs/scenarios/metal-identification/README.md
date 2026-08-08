# 金属质量检查场景

本目录用于整理**金属质量检查**相关文档，重点面向黄金、白银等贵金属的产线质检、入库检验、材质符合性检查和表面状态判定。

## 适用问题

- 标称黄金/白银是否与实测表面光谱一致
- 样品是否合格，等级是 A / B / C 哪一档
- 是否存在氧化、污染、镀层风险、替代材料风险
- 不合格品如何处置：放行 / 复检 / 隔离 / 剔除
- 如何将高光谱质检数据转成千问 SFT 训练样本
- 如何让模型输出“质检结论 + 判断依据 + 处置建议”

## 文档

| 文档 | 说明 |
| --- | --- |
| [`金属识别学习指南.md`](金属识别学习指南.md) | 从零学习高光谱金属质检，包含原始 DN、定标后反射率、训练数据逐行说明 |
| [`../../common/高光谱术语缩写表.md`](../../common/高光谱术语缩写表.md) | DN、ROI 等简称中英文对照与速查 |

## 示例数据

| 文件 | 说明 |
| --- | --- |
| [`../../../examples/scenarios/metal-identification/data/metal_raw_spectrum.json`](../../../examples/scenarios/metal-identification/data/metal_raw_spectrum.json) | 原始 DN 值、白板/暗场参考（定标前） |
| [`../../../examples/scenarios/metal-identification/data/metal_sample_spectrum.json`](../../../examples/scenarios/metal-identification/data/metal_sample_spectrum.json) | 定标后反射率：合格黄金、合格白银、待复检、不合格样本 |
| [`../../../examples/scenarios/metal-identification/data/labels.csv`](../../../examples/scenarios/metal-identification/data/labels.csv) | 质检标签表 |
| [`../../../examples/scenarios/metal-identification/data/qc_standards.json`](../../../examples/scenarios/metal-identification/data/qc_standards.json) | 黄金/白银合格标准模板 |
| [`../../../examples/scenarios/metal-identification/training/metal_sft_train.jsonl`](../../../examples/scenarios/metal-identification/training/metal_sft_train.jsonl) | 金属质检千问 SFT 训练样本 |
| [`../../../examples/scenarios/metal-identification/prepare_metal_qc_dataset.py`](../../../examples/scenarios/metal-identification/prepare_metal_qc_dataset.py) | 示例数据转训练 JSONL |

## 学习路线

1. 先读 `金属识别学习指南.md` 的「一、二、三」章节，理解质检目标、原始 DN 和定标后反射率样本。
2. 打开 `metal_raw_spectrum.json`，对照文档理解 `raw_dn`、白板/暗场和定标公式。
3. 打开 `metal_sample_spectrum.json`，对照文档逐行理解标称材质、质检结论、缺陷和处置字段。
4. 打开 `metal_sft_train.jsonl`，理解千问训练数据如何表达「合格 / 待复检 / 不合格」。
5. 再回到通用流程文档，理解采集、定标、ROI、特征提取和训练部署。

## 重要提醒

高光谱质检主要检查的是**表面光谱是否符合标准**。若业务目标是判断黄金纯度、银饰成色、镀层厚度，建议结合 XRF、密度、导电率等检测方式，不要只依赖可见光-近红外高光谱。
