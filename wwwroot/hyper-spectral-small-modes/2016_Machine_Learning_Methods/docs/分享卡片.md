# Machine_Learning_Methods · 分享卡片

## 49. Machine_Learning_Methods

**本地目录：** `2016_Machine_Learning_Methods/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 经典基线分类（KNN / SVM / CNN）。主要覆盖：Indian Pines（农田作物与植被（印第安纳松），共16类；145×145，常用200波段，光谱约0.4–2.5μm（400–2500nm））；Salinas（农业区蔬菜/葡萄园/裸土，共16类；512×217，常用204波段）；Pavia University（城市道路/建筑/植被，共9类；610×340…
- **模型来源：** No paper! The project uses the CNN models、the KNN method、the SVM method as classifier in hyperspectral image classification
  - 原仓库路径：`2016/Machine_Learning_Methods`
- **模型作用：** 经典基线分类（KNN / SVM / CNN）
- **应用场景：** 对照组；教学演示；数据验证
- **能识别什么（摘要）：** Indian Pines（农田作物与植被（印第安纳松），共16类；145×145，常用200波段，光谱约0.4–2.5μm（400–2500nm））；Salinas（农业区蔬菜/葡萄园/裸土，共16类；512×217，常用204波段）；Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）

### 2. 数据输入示例

- [Indian Pines] 农田作物与植被（印第安纳松），16类；仓库真实原始立方体 `HSI_data/Indian_pines_corrected.mat`（145×145×200）+ `Indian_pines_gt.mat`；[Salinas] 农业区蔬菜/葡萄园/裸土，16类；真实标签 `_raw_datasets/Salinas_gt.mat`（512×217）+ 超像素；影像请下载 `Salinas_corrected.mat`

### 3. 数据输出示例

- [Indian Pines] 输出为同场景像素级分类图（16类着色）；[Salinas] 输出为同场景像素级分类图（16类着色）

### 4. 数据集介绍

- **Indian Pines**：农田作物与植被（印第安纳松），145×145，常用200波段，16类；本地：`datasets/IndianPines/`
- **Salinas**：农业区蔬菜/葡萄园/裸土，512×217，常用204波段，16类；本地：`datasets/Salinas_corrected.mat + Salinas_gt.mat`
- **Pavia University**：城市道路/建筑/植被，610×340，约103波段，9类；本地：`datasets/PaviaU.mat + PaviaU_gt.mat`

### 5. 部署条件

- **运行框架：** TensorFlow / Keras
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install tensorflow scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** 仓库未提供链接

---
