# DBDA · 分享卡片

## 20. DBDA

**本地目录：** `2020_DBDA/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类。主要覆盖：Kennedy Space Center (KSC)（海岸湿地植被与土地覆盖，共13类；常用176波段，400–2500nm）
- **模型来源：** Double-Branch Dual-Attention Mechanism Network for Hyperspectral Image Classification
  - 原仓库路径：`2020/DBDA`
- **模型作用：** 高光谱地物分类
- **应用场景：** 湿地土地覆盖监测；水体/沼泽/林地区分
- **能识别什么（摘要）：** Kennedy Space Center (KSC)（海岸湿地植被与土地覆盖，共13类；常用176波段，400–2500nm）

### 2. 数据输入示例

- [Kennedy Space Center (KSC)] 海岸湿地植被与土地覆盖，13类；仓库真实超像素 `segmentmapsksc.mat`；完整数据请下载到 `_raw_datasets/`

### 3. 数据输出示例

- [Kennedy Space Center (KSC)] 输出为同场景像素级分类图（13类着色）

### 4. 数据集介绍

- **Kennedy Space Center (KSC)**：湿地/植被，512×614，176波段，13类；本地：`datasets/KSC.mat + KSC_gt.mat`

### 5. 部署条件

- **运行框架：** PyTorch
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** 仓库未提供链接

---
