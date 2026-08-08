# 文档中心

本文档目录按“应用场景”分类，方便从业务目标进入对应学习资料、示例数据和训练配置。

## 目录结构

| 目录 | 应用场景 | 说明 |
| --- | --- | --- |
| `scenarios/metal-identification/` | 金属质量检查 | 黄金、白银等金属材质符合性、表面状态、合格判定 |
| `scenarios/agriculture-quality/` | 农业/食品质检 | 苹果等农产品高光谱质检、分类、回归、报告生成 |
| `common/` | 通用流程 | 高光谱采集、预处理、特征提取、千问训练的共性流程 |
| `configs/` | 训练配置 | LLaMA-Factory、LoRA 等训练配置 |

## 推荐阅读顺序

1. 金属质检项目优先阅读：[`scenarios/metal-identification/README.md`](scenarios/metal-identification/README.md)
2. 想理解完整高光谱训练链路：[`common/高光谱训练流程.md`](common/高光谱训练流程.md)
3. 查阅 DN、ROI 等简称：[`common/高光谱术语缩写表.md`](common/高光谱术语缩写表.md)
4. 想参考农业/食品质检方案：[`scenarios/agriculture-quality/README.md`](scenarios/agriculture-quality/README.md)
5. 准备开始微调千问：[`configs/README.md`](configs/README.md)

## 当前重点场景

当前项目重点是 **金属质量检查**，尤其是黄金、白银等贵金属的合格判定、异常识别和质检报告生成。建议优先从金属质检学习指南开始：

[`scenarios/metal-identification/金属识别学习指南.md`](scenarios/metal-identification/金属识别学习指南.md)
