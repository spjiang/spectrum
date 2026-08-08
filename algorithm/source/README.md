# 高光谱算法 HTTP 服务（单进程）

一个 FastAPI 进程聚合 **45** 个算法模块；**目录仍按算法拆分**，便于对照业界清单学习与扩展。

设计说明：[`../docs/source-http-api-设计说明.md`](../docs/source-http-api-设计说明.md)

## 目录结构

```text
source/
  run.py                 # 启动入口
  app/
    main.py              # 单服务：注册全部算法路由
  common/                # 共享：IO、响应、路由工厂、目录元数据
  algorithms/
    27_ndvi/
      router.py          # 薄 HTTP 层
      service.py         # 业务实现
      README.md          # 本算法使用说明
    …（共 45 个）
  scripts/start.sh       # 一键启动
  examples/              # 示例数据生成
  data/uploads|outputs|examples
```

## 快速开始

```bash
cd algorithm/source
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python examples/generate_sample_cube.py
chmod +x scripts/start.sh
./scripts/start.sh
# 或: python run.py
```

- 文档：http://127.0.0.1:28800/docs  
- 算法列表：http://127.0.0.1:28800/api/v1/algorithms  
- 端口可在 `common/config.py` 的 `APP_PORT` 修改  

## 接口约定

| 项 | 说明 |
|----|------|
| 运行 | `POST /api/v1/{algorithm_id}/run` |
| 健康 | `GET /api/v1/{algorithm_id}/health` |
| 输入 | `multipart`：`file` 必填；`file2` 可选；`params` JSON 字符串 |
| 输出 | JSON；需要落盘时路径在 `files` |

```json
{
  "success": true,
  "algorithm_id": "27_ndvi",
  "implemented": true,
  "message": "...",
  "data": {},
  "files": { "ndvi_npy": "...", "preview_png": "..." }
}
```

## 已实现（可运行）

`12_panel_reflectance` · `20_bad_band_remove` · `21_savgol_smooth` · `22_normalize` · `23_pca` · `27_ndvi` · `28_ndre` · `34_svm_rf_classify` · `45_parcel_zonal_stats`

其余为骨架（`implemented: false`），接口形状一致，可在对应目录补 `service.py`。

## 调用示例

```bash
# NDVI
curl -X POST "http://127.0.0.1:28800/api/v1/27_ndvi/run" \
  -F "file=@data/examples/sample_cube.npy" \
  -F 'params={"red_band":2,"nir_band":3}'

# SVM 分类（Cube + 标签）
curl -X POST "http://127.0.0.1:28800/api/v1/34_svm_rf_classify/run" \
  -F "file=@data/examples/sample_cube.npy" \
  -F "file2=@data/examples/sample_gt.npy"
```

## 如何新增/补全算法

1. 在 `common/catalog.py` 登记（或使用已有 id）  
2. `algorithms/<id>/service.py` 实现 `async def run(...)`  
3. 保留 `router.py`（一般不用改，走 `common.routing.build_router`）  
4. 更新本目录 `README.md`  
