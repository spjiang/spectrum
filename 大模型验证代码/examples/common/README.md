# 通用示例脚本

本目录保存跨场景复用的数据处理脚本。

| 脚本 | 适用场景 | 说明 |
| --- | --- | --- |
| [`prepare_dataset.py`](prepare_dataset.py) | 农业/食品质检 | 将 ENVI 或演示标签数据转为千问 JSONL |

## 金属质量检查请用场景脚本

金属质检示例请使用：

[`../scenarios/metal-identification/prepare_metal_qc_dataset.py`](../scenarios/metal-identification/prepare_metal_qc_dataset.py)

它会读取金属质检示例光谱和标准模板，生成 `metal_sft_train.jsonl`。
