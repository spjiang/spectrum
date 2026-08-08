# 金属质检千问 LoRA 微调指南

本目录提供 **Qwen2.5-7B-Instruct** 在金属高光谱质检场景下的完整 LoRA 微调方案。

## 文件说明

| 文件 | 说明 |
| --- | --- |
| [`train_metal_lora.yaml`](train_metal_lora.yaml) | LLaMA-Factory 训练配置 |
| [`dataset_info.json`](dataset_info.json) | 数据集注册（副本，主文件在 `../training/`） |

## 一、生成训练数据

```bash
cd /path/to/spectrum

# 生成 800 条合成训练数据（可调整 --num-samples）
python examples/scenarios/metal-identification/generate_metal_qc_big_dataset.py \
    --num-samples 800 \
    --seed 42
```

输出文件：

| 文件 | 说明 |
| --- | --- |
| `data/metal_sample_spectrum_full.json` | 800 条合成光谱 + 标签 |
| `data/labels_full.csv` | 标签汇总表 |
| `training/metal_sft_train_full.jsonl` | **LLaMA-Factory 训练用 JSONL** |

数据覆盖场景：

- 合格黄金 / 合格白银（A/B 级）
- 待复检（铜色替代、近红外边界、红蓝比边界）
- 不合格（氧化、污染、镀层风险、材质严重不符）

## 二、安装 LLaMA-Factory

```bash
conda create -n llamafactory python=3.10 -y
conda activate llamafactory

git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]"
```

## 三、配置数据集路径

LLaMA-Factory 要求 `dataset_dir` 目录下同时存在 `dataset_info.json` 和 JSONL 文件。

**方式 A（推荐）：修改 yaml 中的绝对路径**

编辑 `train_metal_lora.yaml`，将 `dataset_dir` 改为你本机的绝对路径：

```yaml
dataset_dir: /Users/jiangshengping/wwwroot/shenzhen/spectrum/examples/scenarios/metal-identification/training
```

**方式 B：复制到 LLaMA-Factory 默认 data 目录**

```bash
cp examples/scenarios/metal-identification/training/metal_sft_train_full.jsonl \
   LLaMA-Factory/data/

# 将 metal_qc_sft 条目追加到 LLaMA-Factory/data/dataset_info.json
```

## 四、启动 LoRA 训练

在 **LLaMA-Factory 根目录** 执行：

```bash
llamafactory-cli train \
  /Users/jiangshengping/wwwroot/shenzhen/spectrum/examples/scenarios/metal-identification/llamafactory/train_metal_lora.yaml
```

训练参数摘要：

| 参数 | 值 | 说明 |
| --- | --- | --- |
| 基座模型 | Qwen2.5-7B-Instruct | 千问 7B 指令模型 |
| 微调方式 | LoRA rank=16 | 约 50~150MB 权重 |
| 学习率 | 2e-4 | 标准 SFT 起步值 |
| 有效 batch | 2 × 8 = 16 | 单卡 24GB 可运行 |
| 验证集 | 10% 自动划分 | eval_steps=100 |

训练产物目录：`saves/metal-qc-qwen7b-lora/`

## 五、验证微调效果

### 方式 1：LLaMA-Factory 交互式对话（推荐）

```bash
llamafactory-cli chat \
  /path/to/spectrum/examples/scenarios/metal-identification/llamafactory/train_metal_lora.yaml
```

输入示例（从 JSONL 复制 user 内容）：

```text
样本编号：qc_gold_pass_0001。
标称材质：黄金。
采集范围：400-1000nm。
450nm 蓝光反射率：0.42。
550nm 绿光反射率：0.72。
650nm 红光反射率：0.88。
850nm 近红外反射率：0.93。
450-650nm 上升斜率：0.0023。
红蓝比：2.1。
800-1000nm 近红外均值：0.936。
表面状态：polished。
标准模板：红蓝比 1.9-2.3，近红外均值 > 0.9。
```

期望输出包含：`质检结论：合格。` `处置建议：放行。`

### 方式 2：Python 批量验证脚本

```bash
python examples/scenarios/metal-identification/evaluate_metal_qc_model.py \
    --lora-path saves/metal-qc-qwen7b-lora \
    --test-jsonl examples/scenarios/metal-identification/training/metal_sft_train_full.jsonl \
    --num-samples 20
```

### 方式 3：Web UI

```bash
llamafactory-cli webui
```

在界面中选择基座模型、LoRA 路径，加载后进行对话测试。

## 六、效果评估标准

| 指标 | 达标参考 |
| --- | --- |
| 质检结论准确率 | ≥ 90%（合格/待复检/不合格） |
| 处置建议准确率 | ≥ 85%（放行/复检/剔除/隔离） |
| train_loss | 从 ~1.5 降至 < 0.3 |
| eval_loss | 与 train_loss 差距 < 0.15，无持续回升 |

若 eval_loss 在 Epoch 2~3 回升，说明过拟合，应回退到较早 checkpoint 或减少 epoch。

## 七、显存参考

| 硬件 | Qwen2.5-7B LoRA |
| --- | --- |
| RTX 4090 24GB | batch=2，可训练 |
| A100 40GB | batch=4，充裕 |
| Mac MPS | 建议减小 batch 至 1，关闭 bf16 |
