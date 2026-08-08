# S4L-FSC · 分享卡片

## 71. S4L-FSC

**本地目录：** `2025_S4L-FSC/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 少样本地物分类。主要覆盖：（代码未明确数据集时，类别以实际标签文件为准）
- **模型来源：** Spectral-Spatial Self-Supervised Learning for Few-Shot Hyperspectral Image Classification
  - 原仓库路径：`2025/S4L-FSC`
- **模型作用：** 少样本地物分类
- **应用场景：** 少标注制图；新区域冷启动；应急测绘
- **能识别什么（摘要）：** （代码未明确数据集时，类别以实际标签文件为准）

### 2. 数据输入示例

- 未明确数据集且无原始文件，不展示替身数据
  > （原始立方体待下载后补图；当前不顶替）

### 3. 数据输出示例

- 一般为像素级分类图 + OA/AA/Kappa
  > （无对应输出示例图，见文字说明）

### 4. 数据集介绍

- 文档未明确主数据集；请查看 `source/` 与论文。

### 5. 部署条件

- **运行框架：** 未明确（请查看 source/）
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install scikit-learn spectral matplotlib`。建议 NVIDIA GPU；CPU 可冒烟但很慢
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** https://github.com/Li-ZK/DCFSL-2021

---
