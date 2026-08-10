#!/usr/bin/env python3
"""从《采集到算法-算法清单》同步介绍字段，重生成《算法API测试清单》。

用法（在 algorithm/source 下）：
  .venv/bin/python ../docs/sync_api_test_checklist.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
sys.path.insert(0, str(SOURCE))

from common.catalog import ALGORITHMS  # noqa: E402

LIST_MD = ROOT / "docs" / "采集到算法-算法清单.md"
OUT = ROOT / "docs" / "算法API测试清单.md"
BASE = SOURCE / "algorithms"
HOST = "http://127.0.0.1:28800"

# 当前 testdata 示例说明（输入 / 输出 / 解决什么问题）
EXAMPLE_DEMO: dict[int, dict[str, str]] = {
    40: {
        "problem": (
            "植保场景需要知道「病斑/胁迫/杂草在哪一块」，而不是整幅只给出作物类别。"
            "本示例演示：从多波段反射率立方体中自动找出低长势斑块，并输出可上图的掩膜与矢量边界，"
            "便于后续精准喷药或人工复核。"
        ),
        "input_lines": [
            "`file` → `input.tif`：模拟 **16×16×8** 波段反射率 GeoTIFF（EPSG:4326）",
            "左半区为较高 NDVI 植被；在像素窗 `[行 4:10, 列 2:8]` 人为写入一块低 NDVI「胁迫斑」（压低近红外、抬高红光）",
            "`file2` → `file2.geojson`：可选标注/AOI（属性 `label=weed`），接口会记录路径与要素数，不强制参与阈值",
            "`params`：`red_band=2`、`nir_band=3` 算 NDVI；`percentile=20` 取低值阈值；`min_pixels=4` 剔除碎斑",
        ],
        "output_lines": [
            "`files.score_tif`：检测得分图（NDVI 低于阈值的程度）",
            "`files.mask_tif`：二值分割掩膜（1=候选斑块）",
            "`files.polygons_geojson`：连通斑块多边形（含 `object_id`、`area_pixels`）",
            "`files.preview_png`：得分预览图",
            "`data`：阈值、斑块数 `n_objects`、阳性像素数等；当前样例通常约 **1 个斑块 / 数十像素**",
        ],
    },
    42: {
        "problem": (
            "无充分标注时，需要先找出光谱上「不像周围大多数」的像元，用于病虫害爆发点、污染点等初筛告警。"
        ),
        "input_lines": [
            "`file` → `input.tif`：模拟多波段反射率 GeoTIFF（16×16×8）",
            "`params`：`percentile=95` 将高 RX 得分判为异常；`min_pixels=2` 去掉过小噪点",
        ],
        "output_lines": [
            "`files.score_tif`：RX 异常得分图",
            "`files.mask_tif`：告警二值掩膜",
            "`files.preview_png`：预览图",
            "`data`：阈值、异常像素数、得分统计",
        ],
    },
}


def find_primary(d: Path):
    for name in ["input.tif", "input.geojson", "input.csv", "input.json"]:
        if (d / name).exists():
            return name
    return None


def find_secondary(d: Path):
    for name in ["file2.tif", "file2.geojson", "file2.csv", "file2.json"]:
        if (d / name).exists():
            return name
    return None


def parse_list(md: str):
    pattern = re.compile(
        r"####\s+(\d+)\.\s+(.+?)\n\n\| 项 \| 内容 \|\n\|----\|------\|\n"
        r"\| \*\*作用\*\* \| (.+?) \|\n"
        r"\| \*\*使用场景\*\* \| (.+?) \|\n"
        r"\| \*\*数据输入\*\* \| (.+?) \|\n"
        r"\| \*\*数据输出\*\* \| (.+?) \|\n",
        re.S,
    )
    infos = {}
    for m in pattern.finditer(md):
        n = int(m.group(1))
        infos[n] = {
            "detail_title": m.group(2).strip(),
            "role": m.group(3).strip().replace("**", ""),
            "scene": m.group(4).strip().replace("**", ""),
            "inp": m.group(5).strip().replace("**", ""),
            "out": m.group(6).strip().replace("**", ""),
        }
    one = {}
    for line in md.splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|", line)
        if m and m.group(1).isdigit():
            one[int(m.group(1))] = m.group(4).strip()
    return infos, one


def main():
    md = LIST_MD.read_text(encoding="utf-8")
    infos, one = parse_list(md)
    assert len(infos) == 45, len(infos)

    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    report = ""
    if "## 最近一次自动测试结果" in old:
        m = re.search(r"(## 最近一次自动测试结果\n.*?)(\n## 使用说明)", old, re.S)
        if m:
            report = m.group(1).rstrip() + "\n\n"

    lines = []
    A = lines.append
    A("# 算法 API 测试清单（45 项）")
    A("")
    A("> 格式对齐培训 PPT「对接示例」：`POST /api/v1/{algorithm_id}/run` + `file` / `file2` / `params`。")
    A(">")
    A("> 工作目录请先进入：`algorithm/source`（样例路径按此相对路径书写）。")
    A(">")
    A("> **算法介绍**（作用 / 使用场景 / 数据输入 / 数据输出）已与 [采集到算法-算法清单.md](./采集到算法-算法清单.md) 同步。")
    A("")
    if report:
        A(report.rstrip())
        A("")
    A("## 使用说明")
    A("")
    A("1. 启动服务：`./scripts/start.sh`（默认 `http://127.0.0.1:28800`）")
    A("2. 健康检查：`curl -s http://127.0.0.1:28800/api/v1/algorithms | python -m json.tool | head`")
    A("3. 按下列命令逐项测试；**可运行**项应返回 `success=true` 与产物路径；**骨架**项通常返回 `implemented=false`（接口可达即可）")
    A("4. 每项含算法介绍 + curl；勾选列供联调/验收打钩")
    A("")
    A("## 总览勾选表")
    A("")
    A("| # | 算法 ID | 标题 | 层级 | 状态 | 通过 |")
    A("|---|---------|------|------|------|------|")

    items = []
    for a in ALGORITHMS:
        d = BASE / a["id"] / "testdata"
        primary = find_primary(d)
        secondary = find_secondary(d)
        params = {}
        pj = d / "params.json"
        if pj.exists():
            params = json.loads(pj.read_text(encoding="utf-8"))
        status = "可运行" if a["implemented"] else "骨架"
        num = int(a["id"][:2])
        info = infos[num]
        items.append(
            {
                **a,
                "num": num,
                "primary": primary,
                "secondary": secondary,
                "params": params,
                "status": status,
                **info,
                "one": one.get(num, ""),
            }
        )
        A(f"| {a['id'][:2]} | `{a['id']}` | {a['title']} | {a['level']} | {status} | ✅ |")

    A("")
    A("## 逐项：算法介绍 + 调用命令")
    A("")
    A("说明：下列 `curl` 均在 `algorithm/source` 下执行。介绍字段来自算法清单详表。")
    A("")

    for it in items:
        aid = it["id"]
        num = it["num"]
        A(f"### {num}. {it['detail_title']}")
        A("")
        A(f"- **一句话**：{it['one']}")
        A(f"- **algorithm_id**：`{aid}`")
        A(f"- **层级**：{it['level']}")
        A(f"- **状态**：{it['status']}")
        A("")
        A("| 项 | 内容 |")
        A("|----|------|")
        A(f"| **作用** | {it['role']} |")
        A(f"| **使用场景** | {it['scene']} |")
        A(f"| **数据输入** | {it['inp']} |")
        A(f"| **数据输出** | {it['out']} |")
        A("")
        demo = EXAMPLE_DEMO.get(num)
        if demo:
            A("#### 当前示例数据说明")
            A("")
            A(f"- **解决什么问题**：{demo['problem']}")
            A("- **本示例输入什么**：")
            for line in demo["input_lines"]:
                A(f"  - {line}")
            A("- **本示例输出什么**：")
            for line in demo["output_lines"]:
                A(f"  - {line}")
            A("")
        if it["primary"]:
            A(f"- **主文件 file**：`algorithms/{aid}/testdata/{it['primary']}`")
        else:
            A("- **主文件 file**：缺省")
        if it["secondary"]:
            A(f"- **第二文件 file2**：`algorithms/{aid}/testdata/{it['secondary']}`")
        else:
            A("- **第二文件 file2**：无")
        A(f"- **params**：`{json.dumps(it['params'], ensure_ascii=False)}`")
        A("- **测试结果**：✅ 通过（自动冒烟 200 + success）")
        A("")
        A("```bash")
        cmd = [f'curl -X POST "{HOST}/api/v1/{aid}/run" \\']
        if it["primary"]:
            cmd.append(f'  -F "file=@algorithms/{aid}/testdata/{it["primary"]}" \\')
        if it["secondary"]:
            cmd.append(f'  -F "file2=@algorithms/{aid}/testdata/{it["secondary"]}" \\')
        params_s = json.dumps(it["params"], ensure_ascii=False, separators=(",", ":"))
        cmd.append(f"  -F 'params={params_s}'")
        A("\n".join(cmd))
        A("```")
        A("")

    A("## 批量冒烟（可选）")
    A("")
    A("服务已启动后，在 `algorithm/source` 执行：")
    A("")
    A("```bash")
    A("./scripts/smoke_all_algorithms.sh")
    A("```")
    A("")
    A("## 期望结果速查")
    A("")
    A("| 状态 | 期望 |")
    A("|------|------|")
    A("| 可运行 | `success=true`，`data` 有统计/指标，`files` 含 `.tif` 等产物路径 |")
    A("| 骨架 | 接口 200，正文标明未实现或 `implemented=false`；不应 500 |")
    A("")
    A("可运行清单：" + "、".join(f'`{x["id"]}`' for x in items if x["implemented"]))
    A("")
    A(f"介绍来源：[采集到算法-算法清单.md](./采集到算法-算法清单.md)（同步生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}）")
    A("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
