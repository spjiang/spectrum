# MambaHSI · 分享卡片

## 51. MambaHSI

**本地目录：** `2024_MambaHSI/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类；Mamba高效建模；Transformer特征建模。主要覆盖：Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Houston（城市精细地物，共15类；IEEE GRSS 城市场景（常见 Houston 2013 设定））；WHU-Hi（无人机精细农业/地物，共若干类；WHU-Hi-HanChuan / HongHu /…
- **模型来源：** MambaHSI: Spatial-Spectral Mamba for Hyperspectral Image Classification
  - 原仓库路径：`2024/MambaHSI`
- **模型作用：** 高光谱地物分类；Mamba高效建模；Transformer特征建模
- **应用场景：** 作物种植结构调查；田块地类一张图；区分玉米/大豆等细类；城市土地利用一张图；区分道路/建筑/绿地/停车场等；规划底图支撑；交通设施识别辅助
- **能识别什么（摘要）：** Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Houston（城市精细地物，共15类；IEEE GRSS 城市场景（常见 Houston 2013 设定））；WHU-Hi（无人机精细农业/地物，共若干类；WHU-Hi-HanChuan / HongHu / LongKou 等子数据集类别不同）

### 2. 数据输入示例

- [Pavia University] 城市道路/建筑/植被，9类；仓库真实标签 `TRpaviaU.mat`/`TSpaviaU.mat`（610×340）+ 超像素 `segmentmapspaviau.mat`；完整立方体请下载到 `_raw_datasets/PaviaU.mat`；[Houston] 城市精细地物，15类；仓库真实超像素 `segmentmapshst.mat`；完整数据见 GRSS 官网，建议存 `_raw_datasets/Houston/`

### 3. 数据输出示例

- [Pavia University] 输出为同场景像素级分类图（9类着色）；[Houston] 输出为同场景像素级分类图（15类着色）

### 4. 数据集介绍

- **Pavia University**：城市道路/建筑/植被，610×340，约103波段，9类；本地：`datasets/PaviaU.mat + PaviaU_gt.mat`
- **Houston**：城市精细地物（常见 Houston 2013，15类）；本地：`datasets/Houston2013/`
- **WHU-Hi**：武汉高光谱农业场景（外部数据）；本地：`需自行下载 WHU-Hi`

### 5. 部署条件

- **运行框架：** PyTorch
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** https://doi.org/10.1109/TGRS.2024.3430985

---
