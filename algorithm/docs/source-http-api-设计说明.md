# 设计说明：高光谱算法 HTTP 服务（单进程）

> 日期：2026-08-08  
> 状态：已从「每算法一微服务」收敛为「单服务 + 按算法分目录」

## 目标

提供可学习、可对接的 HTTP API：文件输入、JSON 输出（含文件路径）；与业界 45 项算法清单一一对应。

面向阅读的简介见：[当前服务简单介绍.md](./当前服务简单介绍.md)。

## 架构

```text
Client ──► app.main (FastAPI :28800)
              ├── /api/v1/algorithms
              └── /api/v1/{algorithm_id}/run|health
                    └── algorithms/<id>/router.py
                          └── service.py
```

- **单进程**：运维简单，一个 OpenAPI 文档  
- **按算法分目录**：对照清单、独立实现与说明  
- **common.routing.build_router**：统一 `/run` 契约，避免 45 份重复样板  

## 接口约定

- `POST /api/v1/{algorithm_id}/run`
- 输入：`multipart` 字段 `file` / 可选 `file2` / `params`
- **业界格式**：栅格 **GeoTIFF**（可读 ENVI）；矢量 **GeoJSON**；轨迹/光谱库 **CSV**
- 输出：统一 JSON；栅格产物为 **`.tif`**，路径在 `files`
- `.npy` 仅兼容旧教学数据，非正式契约

详见 `业界文件格式介绍.md`。

## 第一批实现

12、20、21、22、23、27、28、34、40、42、45（见 `common/catalog.py` 中 `implemented: true`）

## 非目标

传感器 SDK、生产鉴权/队列、完整正射与大气业务级实现。
