# SSTN · 分享卡片

## 85. SSTN

**本地目录：** `2021_SSTN/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类；Transformer特征建模。主要覆盖：Indian Pines（农田作物与植被（印第安纳松），共16类；145×145，常用200波段，光谱约0.4–2.5μm（400–2500nm））；Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Kennedy Space Center (KSC)（海岸湿…
- **模型来源：** Spatial-Spectral Transformer for Hyperspectral Image Classification
  - 原仓库路径：`2021/SSTN`
- **模型作用：** 高光谱地物分类；Transformer特征建模
- **应用场景：** 作物种植结构调查；田块地类一张图；区分玉米/大豆等细类；城市土地利用一张图；区分道路/建筑/绿地/停车场等；规划底图支撑；湿地土地覆盖监测
- **能识别什么（摘要）：** Indian Pines（农田作物与植被（印第安纳松），共16类；145×145，常用200波段，光谱约0.4–2.5μm（400–2500nm））；Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Kennedy Space Center (KSC)（海岸湿地植被与土地覆盖，共13类；常用176波段，400–2500nm）

### 2. 数据输入示例

- [Indian Pines] 农田作物与植被（印第安纳松），16类；仓库真实原始立方体 `HSI_data/Indian_pines_corrected.mat`（145×145×200）+ `Indian_pines_gt.mat`；[Pavia University] 城市道路/建筑/植被，9类；仓库真实标签 `TRpaviaU.mat`/`TSpaviaU.mat`（610×340）+ 超像素 `segmentmapspaviau.mat`；完整立方体请下载到 `_raw_datasets/PaviaU.mat`

### 3. 数据输出示例

- [Indian Pines] 输出为同场景像素级分类图（16类着色）；[Pavia University] 输出为同场景像素级分类图（9类着色）

### 4. 数据集介绍

- **Indian Pines**：农田作物与植被（印第安纳松），145×145，常用200波段，16类；本地：`datasets/IndianPines/`
- **Pavia University**：城市道路/建筑/植被，610×340，约103波段，9类；本地：`datasets/PaviaU.mat + PaviaU_gt.mat`
- **Kennedy Space Center (KSC)**：湿地/植被，512×614，176波段，13类；本地：`datasets/KSC.mat + KSC_gt.mat`

### 5. 部署条件

- **运行框架：** PyTorch / Keras
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision keras scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** 仓库未提供链接

---
