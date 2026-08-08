# algorithm

高光谱业务侧说明与算法落点梳理（相对 `wwwroot/hyper-spectral-small-modes` 等实现代码）。

## 文档

| 文档 | 说明 |
|------|------|
| [docs/业界高光谱数据处理流程.md](./docs/业界高光谱数据处理流程.md) | 业界 L0→L3 数据处理流程；含**架构图、流程图**；标出各环节是否使用算法及与本仓库模型的对应关系 |
| [docs/采集到算法-算法清单.md](./docs/采集到算法-算法清单.md) | **业界算法清单（45 项）**：先 L0–L4 架构图，再按层级列算法（作用/场景/输入/输出） |
| [docs/参考链接算法分析.md](./docs/参考链接算法分析.md) | 对 `dev.prompt.md` 两篇链接中算法的拆解（植被指数已分析；知乎文待补正文） |
| [docs/source-http-api-设计说明.md](./docs/source-http-api-设计说明.md) | `source/` 单进程 HTTP 服务设计说明 |
| [source/README.md](./source/README.md) | **算法 HTTP API（单服务）**：45 算法分目录，统一端口调用 |
| [dev.prompt.md](./dev.prompt.md) | 背景问题与参考链接 |

## 快速结论

- 业界主链路：**L0 原始 → L1 辐亮度 → L2 反射率正射立方体 → L3 分类/指数 → L4 报表告警**。
- 本仓库分类小模型主要落在 **L2 → L3（分类图）**；领导/客户最终看的多为 **L4**。
- 可运行教学 API：见 [`source/README.md`](./source/README.md)（单服务默认 `http://127.0.0.1:28800`）。
