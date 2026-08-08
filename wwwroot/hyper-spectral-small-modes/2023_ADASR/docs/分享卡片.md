# ADASR · 分享卡片

## 3. ADASR

**本地目录：** `2023_ADASR/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱–多光谱融合 / 质量提升。主要覆盖：Houston（城市精细地物，共15类；IEEE GRSS 城市场景（常见 Houston 2013 设定））；另：高光谱与多光谱融合提质
- **模型来源：** An Adversarial Auto-Augmentation Framework for Hyperspectral and Multispectral Data Fusion
  - 原仓库路径：`2023/ADASR`
- **模型作用：** 高光谱–多光谱融合 / 质量提升
- **应用场景：** 融合提质；服务精细分类；城市土地利用一张图；区分道路/建筑/绿地/停车场等；规划底图支撑；交通设施识别辅助
- **能识别什么（摘要）：** Houston（城市精细地物，共15类；IEEE GRSS 城市场景（常见 Houston 2013 设定））；另：高光谱与多光谱融合提质

### 2. 数据输入示例

- [Houston] 城市精细地物，15类；仓库真实超像素 `segmentmapshst.mat`；完整数据见 GRSS 官网，建议存 `_raw_datasets/Houston/`

### 3. 数据输出示例

- [Houston] 输出为同场景像素级分类图（15类着色）

### 4. 数据集介绍

- **Houston**：城市精细地物（常见 Houston 2013，15类）；本地：`datasets/Houston2013/`

### 5. 部署条件

- **运行框架：** PyTorch
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** https://github.com/fangfang11-plog/ADASR

---
