# LMSS-NAS · 分享卡片

## 48. LMSS-NAS

**本地目录：** `2023_LMSS-NAS/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类；轻量化。主要覆盖：Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Pavia Centre（城市中心地物，共9类；约1096×715有效区，约102波段）；Kennedy Space Center (KSC)（海岸湿地植被与土地覆盖，共13类；常用176波段，400–2500…
- **模型来源：** Lightweight Multiscale Neural Architecture Search With Spectral–Spatial Attention for Hyperspectral Image Classification
  - 原仓库路径：`2023/LMSS-NAS`
- **模型作用：** 高光谱地物分类；轻量化
- **应用场景：** 算力受限环境部署；快速出图演示；城市土地利用一张图；区分道路/建筑/绿地/停车场等；规划底图支撑；交通设施识别辅助；湿地土地覆盖监测
- **能识别什么（摘要）：** Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Pavia Centre（城市中心地物，共9类；约1096×715有效区，约102波段）；Kennedy Space Center (KSC)（海岸湿地植被与土地覆盖，共13类；常用176波段，400–2500nm）；Houston（城市精细地物，共15类；IEEE GRSS 城市场景（常见 Houston 2013 设定））

### 2. 数据输入示例

- [Pavia University] 城市道路/建筑/植被，9类；仓库真实标签 `TRpaviaU.mat`/`TSpaviaU.mat`（610×340）+ 超像素 `segmentmapspaviau.mat`；完整立方体请下载到 `_raw_datasets/PaviaU.mat`；[Pavia Centre] 城市中心地物，9类；仓库真实超像素 `segmentmapspaviac.mat`；完整立方体请下载到 `_raw_datasets/Pavia.mat`

### 3. 数据输出示例

- [Pavia University] 输出为同场景像素级分类图（9类着色）；[Pavia Centre] 输出为同场景像素级分类图（9类着色）

### 4. 数据集介绍

- **Pavia University**：城市道路/建筑/植被，610×340，约103波段，9类；本地：`datasets/PaviaU.mat + PaviaU_gt.mat`
- **Pavia Centre**：城市地物，1096×715，约102波段，9类；本地：`datasets/Pavia.mat + Pavia_gt.mat`
- **Kennedy Space Center (KSC)**：湿地/植被，512×614，176波段，13类；本地：`datasets/KSC.mat + KSC_gt.mat`
- **Houston**：城市精细地物（常见 Houston 2013，15类）；本地：`datasets/Houston2013/`

### 5. 部署条件

- **运行框架：** PyTorch / TensorFlow
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision tensorflow scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** 仓库未提供链接

---
