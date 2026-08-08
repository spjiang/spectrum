# SGMAE · 分享卡片

## 73. SGMAE

**本地目录：** `2025_SGMAE/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类。主要覆盖：Houston2018（城市精细地物（Houston 2018），共20类；2018 IEEE GRSS Data Fusion Contest（以官方说明为准））
- **模型来源：** SGMAE:Self-Supervised Graph Masked Autoencoders for Hyperspectral Image Classification
  - 原仓库路径：`2025/SGMAE`
- **模型作用：** 高光谱地物分类
- **应用场景：** 城市土地利用一张图；区分道路/建筑/绿地/停车场等；规划底图支撑；交通设施识别辅助
- **能识别什么（摘要）：** Houston2018（城市精细地物（Houston 2018），共20类；2018 IEEE GRSS Data Fusion Contest（以官方说明为准））

### 2. 数据输入示例

- [Houston2018] 城市精细地物（Houston 2018），20类；仓库真实超像素 `segmentmapshstu.mat`；完整数据建议存 `_raw_datasets/Houston2018/`

### 3. 数据输出示例

- [Houston2018] 输出为同场景像素级分类图（20类着色）

### 4. 数据集介绍

- **Houston2018**：城市精细地物（常见 Houston 2013，15类）；本地：`datasets/Houston2013/`

### 5. 部署条件

- **运行框架：** PyTorch
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** https://github.com/copawloroous/SGMAE

---
