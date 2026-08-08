# DCN-T · 分享卡片

## 21. DCN-T

**本地目录：** `2023_DCN-T/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 高光谱地物分类；Transformer特征建模。主要覆盖：WHU-Hi（无人机精细农业/地物，共若干类；WHU-Hi-HanChuan / HongHu / LongKou 等子数据集类别不同）
- **模型来源：** Dual Context Network with Transformer for Hyperspectral Image Classification
  - 原仓库路径：`2023/DCN-T`
- **模型作用：** 高光谱地物分类；Transformer特征建模
- **应用场景：** 作物种植结构调查；田块地类一张图；区分玉米/大豆等细类
- **能识别什么（摘要）：** WHU-Hi（无人机精细农业/地物，共若干类；WHU-Hi-HanChuan / HongHu / LongKou 等子数据集类别不同）

### 2. 数据输入示例

- [WHU-Hi] 无人机精细农业/地物，若干类；仓库未附带原始文件；请下载到 `_raw_datasets/WHU-Hi/`
  > （原始立方体待下载后补图；当前不顶替）

### 3. 数据输出示例

- [WHU-Hi] 输出为同场景像素级分类图（若干类着色）
  > （无对应输出示例图，见文字说明）

### 4. 数据集介绍

- **WHU-Hi**：武汉高光谱农业场景（外部数据）；本地：`需自行下载 WHU-Hi`

### 5. 部署条件

- **运行框架：** PyTorch
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** https://github.com/DotWang/DCN-T.git

---
