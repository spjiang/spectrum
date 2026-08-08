# HyLiOSR · 分享卡片

## 43. HyLiOSR

**本地目录：** `2025_HyLiOSR/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 开放集识别（能标出未知类）；可融合激光雷达。主要覆盖：Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Houston（城市精细地物，共15类；IEEE GRSS 城市场景（常见 Houston 2013 设定））；Trento（城郊地物（常配合 LiDAR），共6类；多源 HSI+LiDAR）；MUUFL（校园…
- **模型来源：** HyLiOSR: Staged Progressive Learning for Joint Open-Set Recognition of Hyperspectral and LiDAR Data
  - 原仓库路径：`2025/HyLiOSR`
- **模型作用：** 开放集识别（能标出未知类）；可融合激光雷达
- **应用场景：** 发现未知地物；异常告警；多源联合调查；建筑道路植被分层；城市土地利用一张图；区分道路/建筑/绿地/停车场等；规划底图支撑
- **能识别什么（摘要）：** Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Houston（城市精细地物，共15类；IEEE GRSS 城市场景（常见 Houston 2013 设定））；Trento（城郊地物（常配合 LiDAR），共6类；多源 HSI+LiDAR）；MUUFL（校园/城市地物（常配合 LiDAR），共11类；多源 HSI+LiDAR）；另：可把训练未见过的“未知类”单独标出；另：可结合激光雷达

### 2. 数据输入示例

- [Pavia University] 城市道路/建筑/植被，9类；仓库真实标签 `TRpaviaU.mat`/`TSpaviaU.mat`（610×340）+ 超像素 `segmentmapspaviau.mat`；完整立方体请下载到 `_raw_datasets/PaviaU.mat`；[Houston] 城市精细地物，15类；仓库真实超像素 `segmentmapshst.mat`；完整数据见 GRSS 官网，建议存 `_raw_datasets/Houston/`

### 3. 数据输出示例

- [Pavia University] 输出为同场景像素级分类图（9类着色）；[Houston] 输出为同场景像素级分类图（15类着色）

### 4. 数据集介绍

- **Pavia University**：城市道路/建筑/植被，610×340，约103波段，9类；本地：`datasets/PaviaU.mat + PaviaU_gt.mat`
- **Houston**：城市精细地物（常见 Houston 2013，15类）；本地：`datasets/Houston2013/`
- **Trento**：高光谱+LiDAR 城郊场景；本地：`datasets/Trento/`
- **MUUFL**：高光谱+LiDAR 校园场景；本地：`datasets/MUUFL/`

### 5. 部署条件

- **运行框架：** PyTorch / TensorFlow / Keras
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision tensorflow scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** http://doi.org/10.1109/TGRS.2025.3545926

---
