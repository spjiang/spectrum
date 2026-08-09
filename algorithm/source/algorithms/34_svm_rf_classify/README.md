# SVM / 随机森林分类（本期实现 SVM）

- **algorithm_id**: `34_svm_rf_classify`
- **层级**: L3
- **实现状态**: 已实现（可运行）

## 作用

基于像素光谱训练 SVM，输出全图预测；在测试集上计算 **OA / AA / Kappa**。

## 使用场景

作物/地物像素分类教学；理解「Cube + 标签 → 分类图 + 精度」。

## 启动（整个算法服务）

```bash
cd algorithm/source
python run.py
```

## 测试数据

本目录 `testdata/` 使用**业界常用格式**（GeoTIFF / GeoJSON / CSV），说明见 `testdata/README.md`。

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/34_svm_rf_classify/run" \
  -F "file=@./testdata/input.tif" -F "file2=@./testdata/file2.tif" -F 'params={"test_size": 0.3, "kernel": "rbf"}'
```

## 输入 / 输出

- **输入**: `file` Cube；`file2` 标签图（0=忽略）
- **输出**: `data.oa/aa/kappa`；`files.pred_map_npy`、`preview_png`
