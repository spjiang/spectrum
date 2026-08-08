# SSMLP-RPL · 分享卡片

## 81. SSMLP-RPL

**本地目录：** `2022_SSMLP-RPL/`（`source/` · `docs/` · `datasets/`→共享数据）

### 1. 模型介绍

- **模型介绍：** 开放集识别（能标出未知类）。主要覆盖：Indian Pines（农田作物与植被（印第安纳松），共16类；145×145，常用200波段，光谱约0.4–2.5μm（400–2500nm））；Salinas（农业区蔬菜/葡萄园/裸土，共16类；512×217，常用204波段）；Pavia University（城市道路/建筑/植被，共9类；610×340…
- **模型来源：** Spectral–Spatial MLP-Like Network With Reciprocal Points Learning for Open-Set Hyperspectral Image Classification
  - 原仓库路径：`2022/SSMLP-RPL`
- **模型作用：** 开放集识别（能标出未知类）
- **应用场景：** 发现未知地物；异常告警；作物种植结构调查；田块地类一张图；区分玉米/大豆等细类；城市土地利用一张图；区分道路/建筑/绿地/停车场等
- **能识别什么（摘要）：** Indian Pines（农田作物与植被（印第安纳松），共16类；145×145，常用200波段，光谱约0.4–2.5μm（400–2500nm））；Salinas（农业区蔬菜/葡萄园/裸土，共16类；512×217，常用204波段）；Pavia University（城市道路/建筑/植被，共9类；610×340（常用），约103波段）；Pavia Centre（城市中心地物，共9类；约1096×715有效区，约102波段）；Kennedy Space Center (KSC)（海岸湿地植被与土地覆盖，共13类；常用176波段，400–2500nm）；Botswana（三角洲沼泽/林地，共14类；常用145波段，400–2500nm）；Houston（城市精细地物，共15类；IEEE GRSS 城市场景（常见 Houston 2013 设定））；另：可把训练未见过的“未知类”单独标出

### 2. 数据输入示例

- [Indian Pines] 农田作物与植被（印第安纳松），16类；仓库真实原始立方体 `HSI_data/Indian_pines_corrected.mat`（145×145×200）+ `Indian_pines_gt.mat`；[Salinas] 农业区蔬菜/葡萄园/裸土，16类；真实标签 `_raw_datasets/Salinas_gt.mat`（512×217）+ 超像素；影像请下载 `Salinas_corrected.mat`

### 3. 数据输出示例

- [Indian Pines] 输出为同场景像素级分类图（16类着色）；[Salinas] 输出为同场景像素级分类图（16类着色）

### 4. 数据集介绍

- **Indian Pines**：农田作物与植被（印第安纳松），145×145，常用200波段，16类；本地：`datasets/IndianPines/`
- **Salinas**：农业区蔬菜/葡萄园/裸土，512×217，常用204波段，16类；本地：`datasets/Salinas_corrected.mat + Salinas_gt.mat`
- **Pavia University**：城市道路/建筑/植被，610×340，约103波段，9类；本地：`datasets/PaviaU.mat + PaviaU_gt.mat`
- **Pavia Centre**：城市地物，1096×715，约102波段，9类；本地：`datasets/Pavia.mat + Pavia_gt.mat`
- **Kennedy Space Center (KSC)**：湿地/植被，512×614，176波段，13类；本地：`datasets/KSC.mat + KSC_gt.mat`
- **Botswana**：沼泽/植被，1476×256，145波段，14类；本地：`datasets/Botswana.mat + Botswana_gt.mat`
- **Houston**：城市精细地物（常见 Houston 2013，15类）；本地：`datasets/Houston2013/`

### 5. 部署条件

- **运行框架：** PyTorch
- **环境与硬件：** Python 3.8+；常见依赖：numpy / scipy / scikit-learn；`pip install torch torchvision scikit-learn spectral matplotlib`。依赖 CUDA/GPU（代码含 cuda）；无 GPU 时需改设备或走 CPU
- **数据准备：** 将 `datasets/` 中对应文件按该模型 `source/` 期望的路径/文件名软链或复制；文件名不一致时需改名或改加载代码。
- **建议验证：** 先用已就绪小数据（如 Indian Pines / PaviaU）冒烟，再切到论文主数据集。
- **源码/论文入口：** https://github.com/xuegeeker

---
