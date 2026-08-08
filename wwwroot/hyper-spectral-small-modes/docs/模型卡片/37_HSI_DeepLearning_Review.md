# HSI_DeepLearning_Review · 分享卡片

## 37. HSI_DeepLearning_Review

**本地目录：** `2016_HSI_DeepLearning_Review/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 对应论文 *Deep Feature Extraction and Classification of Hyperspectral Images Based on Convolutional Neural Networks* 的可运行实现与对比基线集合。`source/` 中不是纯文档综述，而是一组可独立训练/评测的高光谱地物分类脚本：光谱维 1D-CNN（`cnn1d.py`）、空间维 2D-CNN（`cnn2d.py`）、空–谱 3D-CNN（`cnn3d.py`），以及 MLP、RNN（`recurrent.py`）、SVM、随机森林、多项逻辑回归；另含跨数据集迁移（`transfer_learning.py`）与 ImageNet 预训练 CNN 迁移（`pretrain_imagenet_cnn.py`）。数据经 PCA/标准化后，按像素光谱或空间邻域 patch（`createImageCubes`）送入模型，输出地物类别。
- **模型来源：** Deep Feature Extraction and Classification of Hyperspectral Images Based on Convolutional Neural Networks（2016）
  - 原仓库路径：`2016/HSI_DeepLearning_Review`
  - 核心网络示例（3D-CNN）：`Conv3D(32,(5,5,24)) → Conv3D(64,(5,5,16)) → MaxPooling3D → Dense → Softmax`
- **模型作用：** 对高光谱影像做**像素级地物分类**；同一数据接口下对比传统机器学习与深度 CNN/RNN 的分类效果；支持固定划分与跨场景迁移实验。
- **应用场景：**
  - 农田作物/植被精细分类（Indian Pines、Salinas）
  - 城市道路/建筑/植被一张图（Pavia University）
  - 城市精细地物制图（Houston）
  - 少样本或固定训练区划分下的算法对比与基线复现
  - 跨数据集迁移学习试验（`--dataset1` / `--dataset2`）
- **能识别什么（摘要）：** 按数据集输出对应地物类别（代码中 `num_class`：IP/SV=16，UP=9，UH=15）。例如 Indian Pines 的玉米/大豆/牧草等 16 类，PaviaU 的沥青/草地/树木等 9 类，Houston 的草地/道路/居民区等 15 类。

### 2. 数据输入示例

- 加载入口：`auxil/mydata.py` → `loadData(name)`，默认相对路径 `../HSI-datasets/`（部署时请改为指向本仓库共享 `datasets/`）。
- 数据集代号：`IP`=Indian Pines（`indian_pines_corrected.mat` + `indian_pines_gt.mat`）；`UP`=PaviaU（`paviaU.mat` + `paviaU_gt.mat`）；`SV`=Salinas（`salinas_corrected.mat` + `salinas_gt.mat`）；`UH`=Houston（`houston.mat` + `houston_gt.mat`）；另有固定划分 `DIP`/`DUP`/`DIPr`/`DUPr`。
- 预处理：可选 PCA 降维（如 3D-CNN 默认 `components=40`）+ `standard`/`minmax` 标准化。
- 输入形态：
  - 光谱分类（`cnn1d` / `svm` / `mlp` 等）：每个有标签像素的光谱向量，形状约 `(B,)` 或 `(B,1)`
  - 空–谱 CNN（`cnn2d` / `cnn3d`）：以中心像素为中心的邻域立方体，默认窗宽约 `spatialsize=19`，形状 `(W,W,B)` / `(W,W,B,1)`
- 运行示例：`python cnn3d.py --dataset IP --tr_percent 0.15`

### 3. 数据输出示例

- 每个测试像素的类别预测（Softmax / SVM 等），经 `auxil/mymetrics.reports` 汇总。
- 指标：Overall Accuracy（OA）、Average Accuracy（AA）、Kappa，以及各类别精度；控制台打印形如 `[OA, AA, Kappa, class1, …]`（百分数）。
- 深度模型训练过程会把验证集最优权重存到 `/tmp/best_model.h5`，再对测试集推理。
- 业务侧可据此生成与真值同尺寸的像素级分类着色图（16/9/15 类）。

### 4. 数据集介绍

- **Indian Pines（IP）**：农田作物与植被，145×145，常用200波段，16类；本地：`datasets/IndianPines/`
- **Pavia University（UP）**：城市道路/建筑/植被，610×340，约103波段，9类；本地：`datasets/PaviaU.mat` + `PaviaU_gt.mat`
- **Salinas（SV）**：农业区蔬菜/葡萄园/裸土，512×217，常用204波段，16类；本地：`datasets/Salinas_corrected.mat` + `Salinas_gt.mat`
- **Houston（UH）**：城市精细地物，15类；本地优先：`datasets/Houston2013/`（需按代码键名整理为 `houston.mat` / `houston_gt.mat`）

### 5. 部署条件

- **运行框架：** Keras（TensorFlow 后端）+ scikit-learn（SVM/RF/MLR）
- **环境与硬件：** Python 3.8+（原代码偏 Keras 2.x API，如 `Adam(lr=…)`，新环境可能需小改）；`pip install tensorflow keras scikit-learn scipy numpy spectral matplotlib`。CNN/RNN 建议 NVIDIA GPU；SVM/RF 可 CPU。
- **数据准备：** 将共享 `datasets/` 中对应 `.mat` 放到代码期望的 `HSI-datasets/`（或改 `mydata.loadData` 路径/文件名）；注意大小写（如 `paviaU.mat` vs `PaviaU.mat`）。
- **建议验证：** 先跑 `python svm.py --dataset IP` 或 `python cnn1d.py --dataset IP` 冒烟，再试 `cnn3d.py`。
- **源码/论文入口：** 目录内 PDF：`Deep Feature Extraction and Classification of Hyperspectral Images Based on Convolutional Neural Networks.pdf`

---
