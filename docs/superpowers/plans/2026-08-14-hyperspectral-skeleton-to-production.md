# 33 项骨架→生产级 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按方案 C 分五波，将 33 个骨架算法全部升级为生产级可运行实现，最终 45/45 `implemented=true` 且产出 `files`。

**Architecture:** 每个算法仍为独立目录 `service.py` + `testdata`；复用 `common/io` / `common/response`；`IMPLEMENTED` 以 service 模块为准并同步 `common/catalog.py`；每波结束后用增强冒烟脚本验收并运行 `sync_api_test_checklist.py` 回写测试清单。

**Tech Stack:** FastAPI、numpy、scipy、scikit-learn、rasterio、torch、scikit-image（W1 SLIC 如需）

## Global Constraints

- 规格：`docs/superpowers/specs/2026-08-14-hyperspectral-skeleton-to-production-design.md`
- 每波直接生产级，不留骨架
- 波序固定：W1→W2→W3→W4→W5
- 成功标准：HTTP 200、`success=true`、`implemented=true`、`files` 非空且路径存在
- 不破坏现有 12 项行为
- 中文注释；未经用户要求不 git commit
- 诚实边界见规格 §3.1（大气/正射/SfM 等）

### 文件总览

| 路径 | 职责 |
|------|------|
| `algorithm/source/algorithms/{id}/service.py` | 生产实现，`IMPLEMENTED=True` |
| `algorithm/source/algorithms/{id}/README.md` | 方法/参数/产物/边界 |
| `algorithm/source/algorithms/{id}/testdata/*` | 可复现样例与 params |
| `algorithm/source/common/catalog.py` | 同步 `implemented` 标志 |
| `algorithm/source/scripts/verify_algorithms.py` | 严格验收（implemented+files） |
| `algorithm/docs/sync_api_test_checklist.py` | 回写测试清单 |
| `algorithm/docs/算法API测试清单.md` | 用户手测入口 |

---

### Task 0: 严格验收脚本

**Files:**
- Create: `algorithm/source/scripts/verify_algorithms.py`
- Modify: `algorithm/source/requirements.txt`（若缺 `scikit-image` 则追加 `scikit-image>=0.22.0`）

**Interfaces:**
- Produces: `verify(host: str, ids: list[str] | None) -> int`（失败数；0=全过）
- Consumes: `scripts/smoke_all_algorithms.sh` 同款 testdata 发现规则 + `common.catalog.ALGORITHMS`

- [ ] **Step 1: 编写验收脚本**

```python
#!/usr/bin/env python3
"""严格验收：HTTP200 + success + implemented + files 非空且存在。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.catalog import ALGORITHMS  # noqa: E402

HOST = "http://127.0.0.1:28800"


def discover(algo_id: str) -> tuple[Path | None, Path | None, str]:
    d = ROOT / "algorithms" / algo_id / "testdata"
    primary = None
    for name in ("input.tif", "input.geojson", "input.csv", "input.json"):
        if (d / name).exists():
            primary = d / name
            break
    secondary = None
    for name in ("file2.tif", "file2.geojson", "file2.csv", "file2.json"):
        if (d / name).exists():
            secondary = d / name
            break
    params = "{}"
    pj = d / "params.json"
    if pj.exists():
        params = pj.read_text(encoding="utf-8")
    return primary, secondary, params


def verify(host: str = HOST, ids: list[str] | None = None) -> int:
    fail = 0
    targets = [a["id"] for a in ALGORITHMS if ids is None or a["id"] in ids]
    with httpx.Client(timeout=120.0, trust_env=False) as client:
        for algo_id in targets:
            primary, secondary, params = discover(algo_id)
            if primary is None:
                print(f"FAIL {algo_id}: 缺少 testdata 主文件")
                fail += 1
                continue
            files = {"file": (primary.name, primary.read_bytes())}
            if secondary is not None:
                files["file2"] = (secondary.name, secondary.read_bytes())
            data = {"params": params}
            r = client.post(f"{host}/api/v1/{algo_id}/run", files=files, data=data)
            if r.status_code != 200:
                print(f"FAIL {algo_id}: HTTP {r.status_code}")
                fail += 1
                continue
            body = r.json()
            ok = body.get("success") is True and body.get("implemented") is True and bool(body.get("files"))
            missing = [p for p in (body.get("files") or {}).values() if not Path(p).exists()]
            if not ok or missing:
                print(f"FAIL {algo_id}: body={body.get('message')} missing={missing}")
                fail += 1
            else:
                print(f"PASS {algo_id}")
    return fail


if __name__ == "__main__":
    only = sys.argv[1:] or None
    raise SystemExit(verify(ids=only))
```

- [ ] **Step 2: 安装依赖并冒烟旧 12 项仍可用（服务需已启动）**

```bash
cd algorithm/source
.venv/bin/pip install -q 'scikit-image>=0.22.0' httpx
.venv/bin/python scripts/verify_algorithms.py 27_ndvi 20_bad_band_remove
```

Expected: `PASS 27_ndvi` / `PASS 20_bad_band_remove`；exit 0

---

### Task 1: W1 — `24_band_select`

**Files:**
- Modify: `algorithm/source/algorithms/24_band_select/service.py`
- Modify: `algorithm/source/algorithms/24_band_select/README.md`
- Modify: `algorithm/source/algorithms/24_band_select/testdata/params.json`
- Modify: `algorithm/source/common/catalog.py`（该项 `implemented: True`）

**Interfaces:**
- Consumes: `common.io.load_raster/as_cube/save_geotiff/new_job_dir/save_upload`
- Produces: `files.cube_tif`；`data.method/selected_bands/shape`

- [ ] **Step 1: 实现 service（method=variance|indices|mutual_info）**

核心逻辑：
- `indices`：使用 `params.bands` 显式索引
- `variance`：按波段方差降序取 `top_k`（默认 8）
- `mutual_info`：若提供 `file2` 标签图，用 sklearn `mutual_info_classif` 选 `top_k`；否则回退 variance
- 输出子集立方体 GeoTIFF；`IMPLEMENTED=True`

- [ ] **Step 2: 更新 params.json 为 `{"method":"variance","top_k":4}`，更新 README**

- [ ] **Step 3: 验收**

```bash
.venv/bin/python scripts/verify_algorithms.py 24_band_select
```

Expected: `PASS 24_band_select`

---

### Task 2: W1 — `25_superpixel`

**Files:**
- Modify: `algorithm/source/algorithms/25_superpixel/service.py`
- Modify: `algorithm/source/algorithms/25_superpixel/README.md`
- Modify: `algorithm/source/algorithms/25_superpixel/testdata/params.json`
- Modify: `algorithm/source/common/catalog.py`

**Interfaces:**
- Produces: `files.label_tif`、`files.preview_png`；可选 `files.mean_spectra_csv`

- [ ] **Step 1: 实现 SLIC（skimage.segmentation.slic）**
  - 输入多波段反射率；取前 3 波段或 PCA3 做分割
  - params: `n_segments`（默认 50）、`compactness`（默认 10）
  - 输出标签图 + 预览；统计超像素个数

- [ ] **Step 2: 验收**

```bash
.venv/bin/python scripts/verify_algorithms.py 25_superpixel
```

Expected: `PASS 25_superpixel`

---

### Task 3: W1 — `26_patch_build`

**Files:**
- Modify: `algorithm/source/algorithms/26_patch_build/service.py`
- Modify: `algorithm/source/algorithms/26_patch_build/README.md`
- Modify: `algorithm/source/algorithms/26_patch_build/testdata/params.json`
- Modify: `algorithm/source/common/catalog.py`

**Interfaces:**
- Consumes: cube `file` + label `file2`（0=忽略）
- Produces: `files.patches_npz`（或 zip 内多 patch）、`files.manifest_json`

- [ ] **Step 1: 实现以标注像元为中心的 patch 提取**
  - params: `patch_size`（奇数，默认 5）、`max_per_class`（默认 200）
  - 边界反射填充；写出 `patches.npz`（X,y）+ `manifest.json`
  - 同时写一份 `preview` 样本分布说明到 data

- [ ] **Step 2: 确认 testdata 有 file2.tif；若无则从 34 的标签样例复制/生成**

- [ ] **Step 3: 验收**

```bash
.venv/bin/python scripts/verify_algorithms.py 26_patch_build
```

Expected: `PASS 26_patch_build`

---

### Task 4: W1 收口

**Files:**
- Modify: `algorithm/docs/算法API测试清单.md`（经 sync 脚本）
- Modify: `algorithm/source/common/catalog.py`（确认 24/25/26 均为 True）

- [ ] **Step 1: 波验收**

```bash
.venv/bin/python scripts/verify_algorithms.py 24_band_select 25_superpixel 26_patch_build
```

Expected: 3 PASS

- [ ] **Step 2: 回写清单**

```bash
cd algorithm/source && .venv/bin/python ../docs/sync_api_test_checklist.py
```

Expected: 清单中 #24/#25/#26 状态为「可运行」；汇总可运行数增加 3

- [ ] **Step 3: 向用户报告 W1 可测项与 curl**

---

### Task 5: W2 — 指数与反演（#29–#33）

**Files:**
- Modify: `algorithms/29_evi_savi/service.py` 等 5 个目录 + README + params + catalog

**Interfaces / 方法合约：**

| ID | 方法 | 主产物 |
|----|------|--------|
| 29 | EVI/SAVI/MSAVI（params.index） | `index_tif` + preview |
| 30 | NDMI/NDWI/MNDWI | `index_tif` + preview |
| 31 | 红边位置/斜率（多项式或最大一阶导） | `param_tif` 或 CSV |
| 32 | PLS/Ridge，file2=标签或训练 CSV | `pred_tif` + metrics |
| 33 | 简化经验物理模型（可参数化 Beer-Lambert/线性） | `pred_tif` |

- [ ] 逐项实现 → `verify_algorithms.py` 五项全 PASS → sync 清单 → 报告用户可测

---

### Task 6: W3 — 分类/检测缺口（#35 #36 #38 #39 #41 #43 #44）

| ID | 方法 | 主产物 |
|----|------|--------|
| 35 | SAM（光谱库 CSV=file2） | `class_tif` |
| 36 | 轻量 1D-CNN（torch，少 epoch） | `pred_tif` + OA |
| 38 | 轻量光谱 Transformer | `pred_tif` + OA |
| 39 | 原型网络少样本 | `pred_tif` |
| 41 | N-FINDR/VCA + NNLS/FCLS | `abundance_tif` |
| 43 | 影像差分/CVA（file2=T2） | `change_tif` |
| 44 | 众数滤波 + 小斑剔除 | `smooth_tif` |

- [ ] 逐项实现 → 七项 PASS → sync → 报告

---

### Task 7: W4 — L0→L1（#01–#11）

按现有 testdata 类型实现（geojson/csv/json/tif）：

| ID | 方法 | 主产物 |
|----|------|--------|
| 01 | AOI 航迹规划 | `waypoints.geojson` + CSV |
| 02 | 时间戳最近邻对齐 | `aligned.json` |
| 03 | GPS+IMU 互补滤波轨迹 | `pose.csv` |
| 04 | 过曝/欠曝/丢帧质检 | `qc_report.json` + mask |
| 05 | 云影掩膜 | `mask_tif` |
| 06 | 暗帧减除 | `corrected_tif` |
| 07 | 坏像元检测修复 | `corrected_tif` |
| 08 | 列统计去条带 | `destripe_tif` |
| 09 | smile/keystone 多项式校正 | `corrected_tif` |
| 10 | gain/offset 辐射定标 | `radiance_tif` |
| 11 | 相对辐射/直方图匹配 | `normalized_tif` |

- [ ] 十一项 PASS → sync → 报告

---

### Task 8: W5 — L1→L2 几何辐射（#13–#19）

| ID | 方法 | 主产物 |
|----|------|--------|
| 13 | DOS 大气校正 | `reflectance_tif` |
| 14 | 余弦/简易 BRDF | `corrected_tif` |
| 15 | 写仿射/CRS 粗定位 | `georef_tif` |
| 16 | rasterio/GDAL warp + DEM(file2) | `ortho_tif` |
| 17 | 重叠融合镶嵌 | `mosaic_tif` |
| 18 | 直方图匀色 | `balanced_tif` |
| 19 | 互相关仿射配准 | `registered_tif` + transform.json |

- [ ] 七项 PASS → sync → 报告

---

### Task 9: 全量收口

- [ ] `verify_algorithms.py`（无参数）期望 45 PASS
- [ ] 回归抽检原 12 项
- [ ] `sync_api_test_checklist.py`：汇总 **可运行且产出 files = 45/45**，无骨架行
- [ ] 向用户交付最终验收说明

---

## Spec Coverage Check

| 规格项 | 任务 |
|--------|------|
| W1–W5 分波 | Task 1–8 |
| 生产级验收 | Task 0 + 各波 verify |
| catalog/清单同步 | Task 4/5/6/7/8/9 |
| 诚实边界 | 写入各 service message/README |
| 不破坏旧 12 项 | Task 0 抽检 + Task 9 回归 |
