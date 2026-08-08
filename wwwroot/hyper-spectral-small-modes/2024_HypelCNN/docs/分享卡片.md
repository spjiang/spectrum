# HypelCNN · 分享卡片

## 44. HypelCNN

**本地目录：** `2024_HypelCNN/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类；可融合激光雷达。主要覆盖：Houston（城市精细地物，共15类；IEEE GRSS 城市场景（常见 Houston 2013 设定））；另：可结合激光雷达
- **模型来源：** A Deep Learning Classification Framework with Spectral and Spatial Feature Fusion Layers for Hyperspectral and Lidar Sensor Data
  - 原仓库路径：`2024/HypelCNN`
- **模型作用：** 高光谱地物分类；可融合激光雷达
- **应用场景：** 多源联合调查；建筑道路植被分层；城市土地利用一张图；区分道路/建筑/绿地/停车场等；规划底图支撑；交通设施识别辅助
- **能识别什么（摘要）：** Houston（城市精细地物，共15类；IEEE GRSS 城市场景（常见 Houston 2013 设定））；另：可结合激光雷达

### 2. 数据输入示例

- [Houston] 城市精细地物，15类；仓库真实超像素 `segmentmapshst.mat`；完整数据见 GRSS 官网，建议存 `_raw_datasets/Houston/`

### 3. 数据输出示例

- [Houston] 输出为同场景像素级分类图（15类着色）

### 4. 数据集介绍

- **Houston**：城市精细地物（常见 Houston 2013，15类）；本地：`datasets/Houston2013/`

### 5. 部署条件

- **运行框架：** 未明确（请查看 source/）
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install scikit-learn spectral matplotlib`。建议 NVIDIA GPU；CPU 可冒烟但很慢
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** 仓库未提供链接

---
