# MSA-GCN · 分享卡片

## 60. MSA-GCN

**本地目录：** `2024_MSA-GCN/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类；可融合激光雷达。主要覆盖：Houston2013（城市精细地物（Houston 2013），共15类；2013 IEEE GRSS Data Fusion Contest）；Trento（城郊地物（常配合 LiDAR），共6类；多源 HSI+LiDAR）；MUUFL（校园/城市地物（常配合 LiDAR），共11类；多源 HSI+LiDAR…
- **模型来源：** Interactive Enhanced Network Based on Multihead Self-Attention and Graph Convolution for Classification of Hyperspectral and LiDAR Data
  - 原仓库路径：`2024/MSA-GCN`
- **模型作用：** 高光谱地物分类；可融合激光雷达
- **应用场景：** 多源联合调查；建筑道路植被分层；城市土地利用一张图；区分道路/建筑/绿地/停车场等；规划底图支撑；交通设施识别辅助；城郊/园区精细地物管理
- **能识别什么（摘要）：** Houston2013（城市精细地物（Houston 2013），共15类；2013 IEEE GRSS Data Fusion Contest）；Trento（城郊地物（常配合 LiDAR），共6类；多源 HSI+LiDAR）；MUUFL（校园/城市地物（常配合 LiDAR），共11类；多源 HSI+LiDAR）；另：可结合激光雷达

### 2. 数据输入示例

- [Houston2013] 城市精细地物（Houston 2013），15类；仓库真实超像素 `segmentmapshst.mat`；完整数据建议存 `_raw_datasets/Houston2013/`；[Trento] 城郊地物（常配合 LiDAR），6类；仓库未附带原始文件；请按模型 readme 下载到 `_raw_datasets/Trento/`；[MUUFL] 校园/城市地物（常配合 LiDAR），11类；仓库未附带原始文件；请按模型 readme 下载到 `_raw_datasets/MUUFL/`

### 3. 数据输出示例

- [Houston2013] 输出为同场景像素级分类图（15类着色）；[Trento] 输出为同场景像素级分类图（6类着色）；[MUUFL] 输出为同场景像素级分类图（11类着色）

### 4. 数据集介绍

- **Houston2013**：城市精细地物（常见 Houston 2013，15类）；本地：`datasets/Houston2013/`
- **Trento**：高光谱+LiDAR 城郊场景；本地：`datasets/Trento/`
- **MUUFL**：高光谱+LiDAR 校园场景；本地：`datasets/MUUFL/`

### 5. 部署条件

- **运行框架：** PyTorch
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** 仓库未提供链接

---
