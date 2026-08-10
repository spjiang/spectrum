# 2D/3D-CNN空谱分类

- **algorithm_id**: `37_cnn3d_classify`
- **层级**: L3
- **实现状态**: 已实现（PyTorch 轻量 3D-CNN，Apple MPS / CUDA / CPU）

## 作用

对高光谱 Cube 做 **空–谱邻域 patch + 3D-CNN** 像素级分类（思路对齐 `hyper-spectral-small-modes` 中 CNN3D / HybridSN 一类小模型：PCA 降维 → 提取空间立方体 → Softmax 分类）。

## 使用场景

地物分类制图、与 `34_svm_rf_classify` 对比基线、本地小模型能力接入 HTTP。

## 启动（整个算法服务）

```bash
cd algorithm/source
./scripts/start.sh
```

需已安装 `torch`（写入 `requirements.txt`）。本机 Apple Silicon 会自动用 MPS。

## 测试数据

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/37_cnn3d_classify/run" \
  -F "file=@./algorithms/37_cnn3d_classify/testdata/input.tif" \
  -F "file2=@./algorithms/37_cnn3d_classify/testdata/file2.tif" \
  -F 'params={"patch_size":5,"pca_components":4,"epochs":5}'
```

## 输入 / 输出

- **输入**: `file` 多波段 GeoTIFF；`file2` 单波段标签（0=背景）；`params`：`patch_size`(奇数)、`pca_components`、`epochs`、`test_size`、`batch_size`
- **输出**: JSON；`files.pred_map_tif` / `preview_png`；`data` 含 OA/AA/Kappa、device 等

## 本地 Indian Pines 冒烟（可选）

```bash
.venv/bin/python scripts/smoke_cnn3d_indian_pines.py
```
