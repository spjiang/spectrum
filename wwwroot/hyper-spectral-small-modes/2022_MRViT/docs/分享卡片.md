# MRViT · 分享卡片

## 59. MRViT

**本地目录：** `2022_MRViT/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类；Transformer特征建模。主要覆盖：Salinas（农业区蔬菜/葡萄园/裸土，共16类；512×217，常用204波段）；Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Kennedy Space Center (KSC)（海岸湿地植被与土地覆盖，共13类；常用176波段，400–2500nm）
- **模型来源：** Mixed Convolutions with Vision Transformer in Hyperspectral Image Classification
  - 原仓库路径：`2022/MRViT`
- **模型作用：** 高光谱地物分类；Transformer特征建模
- **应用场景：** 作物种植结构调查；田块地类一张图；区分玉米/大豆等细类；城市土地利用一张图；区分道路/建筑/绿地/停车场等；规划底图支撑；湿地土地覆盖监测
- **能识别什么（摘要）：** Salinas（农业区蔬菜/葡萄园/裸土，共16类；512×217，常用204波段）；Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Kennedy Space Center (KSC)（海岸湿地植被与土地覆盖，共13类；常用176波段，400–2500nm）

### 2. 数据输入示例

- [Salinas] 农业区蔬菜/葡萄园/裸土，16类；真实标签 `_raw_datasets/Salinas_gt.mat`（512×217）+ 超像素；影像请下载 `Salinas_corrected.mat`；[Pavia University] 城市道路/建筑/植被，9类；仓库真实标签 `TRpaviaU.mat`/`TSpaviaU.mat`（610×340）+ 超像素 `segmentmapspaviau.mat`；完整立方体请下载到 `_raw_datasets/PaviaU.mat`

### 3. 数据输出示例

- [Salinas] 输出为同场景像素级分类图（16类着色）；[Pavia University] 输出为同场景像素级分类图（9类着色）

### 4. 数据集介绍

- **Salinas**：农业区蔬菜/葡萄园/裸土，512×217，常用204波段，16类；本地：`datasets/Salinas_corrected.mat + Salinas_gt.mat`
- **Pavia University**：城市道路/建筑/植被，610×340，约103波段，9类；本地：`datasets/PaviaU.mat + PaviaU_gt.mat`
- **Kennedy Space Center (KSC)**：湿地/植被，512×614，176波段，13类；本地：`datasets/KSC.mat + KSC_gt.mat`

### 5. 部署条件

- **运行框架：** PyTorch / Keras
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision keras scikit-learn spectral matplotlib`。建议 NVIDIA GPU；CPU 可冒烟但很慢
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** https://doi.org/10.1109/ICCT56141.2022.10073347

---
