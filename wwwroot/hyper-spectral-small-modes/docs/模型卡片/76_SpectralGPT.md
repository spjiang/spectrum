# SpectralGPT · 分享卡片

## 76. SpectralGPT

**本地目录：** `2024_SpectralGPT/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类；大模型预训练后迁移。主要覆盖：BigEarthNet（大范围多标签场景，共43类；Sentinel-2 大规模场景（多标签））
- **模型来源：** SpectralGPT: Spectral Remote Sensing Foundation Model
  - 原仓库路径：`2024/SpectralGPT`
- **模型作用：** 高光谱地物分类；大模型预训练后迁移
- **应用场景：** 预训练复用；迁移冷启动
- **能识别什么（摘要）：** BigEarthNet（大范围多标签场景，共43类；Sentinel-2 大规模场景（多标签））

### 2. 数据输入示例

- [BigEarthNet] 大范围多标签场景，43类；仓库未附带原始文件；请按 SpectralGPT 说明获取
  > （原始立方体待下载后补图；当前不顶替）

### 3. 数据输出示例

- [BigEarthNet] 输出为同场景像素级分类图（43类着色）
  > （无对应输出示例图，见文字说明）

### 4. 数据集介绍

- **BigEarthNet**：大规模多光谱场景（外部数据）；本地：`需自行下载 BigEarthNet`

### 5. 部署条件

- **运行框架：** PyTorch
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** https://github.com/phelber/EuroSAT#eurosat-land-use-and-land-cover-classification-with-sentinel-2

---
