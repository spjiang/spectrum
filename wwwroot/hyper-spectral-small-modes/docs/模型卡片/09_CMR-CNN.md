# CMR-CNN · 分享卡片

## 9. CMR-CNN

**本地目录：** `2022_CMR-CNN/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类。主要覆盖：Indian Pines（农田作物与植被（印第安纳松），共16类；145×145，常用200波段，光谱约0.4–2.5μm（400–2500nm））
- **模型来源：** Cross-Mixing Residual Network for Hyperspectral Image Classification
  - 原仓库路径：`2022/CMR-CNN`
- **模型作用：** 高光谱地物分类
- **应用场景：** 作物种植结构调查；田块地类一张图；区分玉米/大豆等细类
- **能识别什么（摘要）：** Indian Pines（农田作物与植被（印第安纳松），共16类；145×145，常用200波段，光谱约0.4–2.5μm（400–2500nm））

### 2. 数据输入示例

- [Indian Pines] 农田作物与植被（印第安纳松），16类；仓库真实原始立方体 `HSI_data/Indian_pines_corrected.mat`（145×145×200）+ `Indian_pines_gt.mat`

### 3. 数据输出示例

- [Indian Pines] 输出为同场景像素级分类图（16类着色）

### 4. 数据集介绍

- **Indian Pines**：农田作物与植被（印第安纳松），145×145，常用200波段，16类；本地：`datasets/IndianPines/`

### 5. 部署条件

- **运行框架：** PyTorch
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision scikit-learn spectral matplotlib`。建议 NVIDIA GPU；CPU 可冒烟但很慢
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** 仓库未提供链接

---
