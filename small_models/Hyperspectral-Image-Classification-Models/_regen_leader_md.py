# -*- coding: utf-8 -*-
"""从备份稿重写领导精简版：突出作用、场景、输入输出数据结构。"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "高光谱分类小模型-领导精简版.备份-20260730.md"
OUT = ROOT / "高光谱分类小模型-领导精简版.md"

DATASET_IO = {
    "Indian Pines": {
        "scene": "农田作物与植被",
        "shape": "145×145×200",
        "classes": 16,
        "cube_file": "HSI_data/Indian_pines_corrected.mat",
        "cube_key": "indian_pines_corrected",
        "gt_file": "HSI_data/Indian_pines_gt.mat",
        "gt_key": "indian_pines_gt",
        "gt_shape": "145×145",
    },
    "Salinas": {
        "scene": "农业区蔬菜/葡萄园/裸土",
        "shape": "512×217×204",
        "classes": 16,
        "cube_file": "_raw_datasets/Salinas_corrected.mat",
        "cube_key": "salinas_corrected",
        "gt_file": "_raw_datasets/Salinas_gt.mat",
        "gt_key": "salinas_gt",
        "gt_shape": "512×217",
    },
    "Pavia University": {
        "scene": "城市道路/建筑/植被",
        "shape": "610×340×103",
        "classes": 9,
        "cube_file": "_raw_datasets/PaviaU.mat",
        "cube_key": "paviaU",
        "gt_file": "_raw_datasets/PaviaU_gt.mat",
        "gt_key": "paviaU_gt",
        "gt_shape": "610×340",
    },
    "Pavia Centre": {
        "scene": "城市中心地物",
        "shape": "约1096×715×102",
        "classes": 9,
        "cube_file": "_raw_datasets/Pavia.mat",
        "cube_key": "pavia",
        "gt_file": "_raw_datasets/Pavia_gt.mat",
        "gt_key": "pavia_gt",
        "gt_shape": "约1096×715",
    },
    "Kennedy Space Center (KSC)": {
        "scene": "海岸湿地植被与土地覆盖",
        "shape": "以实际文件为准（常用176波段）",
        "classes": 13,
        "cube_file": "_raw_datasets/KSC.mat",
        "cube_key": "KSC",
        "gt_file": "_raw_datasets/KSC_gt.mat",
        "gt_key": "KSC_gt",
        "gt_shape": "同影像高宽",
    },
    "Botswana": {
        "scene": "三角洲沼泽/林地",
        "shape": "以实际文件为准（常用145波段）",
        "classes": 14,
        "cube_file": "_raw_datasets/Botswana.mat",
        "cube_key": "Botswana",
        "gt_file": "_raw_datasets/Botswana_gt.mat",
        "gt_key": "Botswana_gt",
        "gt_shape": "同影像高宽",
    },
    "Houston": {
        "scene": "城市精细地物（常指 Houston 2013）",
        "shape": "常见约349×1905×144",
        "classes": 15,
        "cube_file": "_raw_datasets/Houston2013/",
        "cube_key": "（以数据包字段为准）",
        "gt_file": "_raw_datasets/Houston2013/",
        "gt_key": "（gt）",
        "gt_shape": "同影像高宽",
    },
    "Houston2013": {
        "scene": "城市精细地物（Houston 2013）",
        "shape": "约349×1905×144",
        "classes": 15,
        "cube_file": "_raw_datasets/Houston2013/",
        "cube_key": "（以数据包字段为准）",
        "gt_file": "_raw_datasets/Houston2013/",
        "gt_key": "（gt）",
        "gt_shape": "同影像高宽",
    },
    "Houston2018": {
        "scene": "城市精细地物（Houston 2018）",
        "shape": "601×2384×50",
        "classes": 20,
        "cube_file": "_raw_datasets/Houston2018/houstonU2018.mat",
        "cube_key": "houstonU",
        "gt_file": "同文件内 houstonU_gt",
        "gt_key": "houstonU_gt",
        "gt_shape": "601×2384",
    },
    "Trento": {
        "scene": "城郊地物（常配合 LiDAR）",
        "shape": "以实际 npy/mat 为准",
        "classes": 6,
        "cube_file": "模型目录 data/Trento/",
        "cube_key": "常见 trento_im / combinedData",
        "gt_file": "data/Trento/",
        "gt_key": "trento_raw_gt / label",
        "gt_shape": "同影像高宽",
    },
    "MUUFL": {
        "scene": "校园/城市地物（常配合 LiDAR）",
        "shape": "以实际文件为准",
        "classes": 11,
        "cube_file": "模型目录 data/Muufl/",
        "cube_key": "combinedData",
        "gt_file": "data/Muufl/",
        "gt_key": "label",
        "gt_shape": "同影像高宽",
    },
    "WHU-Hi": {
        "scene": "无人机精细农业/地物",
        "shape": "子数据集不同",
        "classes": "若干",
        "cube_file": "WHU-Hi 官方包",
        "cube_key": "（以子数据集字段为准）",
        "gt_file": "同数据包",
        "gt_key": "（gt）",
        "gt_shape": "同影像高宽",
    },
    "BigEarthNet": {
        "scene": "大范围多标签场景",
        "shape": "Sentinel-2 图块",
        "classes": 43,
        "cube_file": "BigEarthNet 官方包",
        "cube_key": "（多波段图块）",
        "gt_file": "多标签标注",
        "gt_key": "labels",
        "gt_shape": "每图块一组标签",
    },
}

CAP_TEMPLATES = {
    "高光谱地物分类": {
        "purpose": "把一张高光谱影像里的每个像素，自动判别成事先约定好的地物类别（如玉米、道路、水体），最终生成一张“地物分类彩图”。通俗说：看图自动告诉你这块地是什么。",
        "scenarios": [
            "农业：作物种植结构调查、田块地类一张图",
            "城市：道路/建筑/绿地/停车场等土地利用制图",
            "生态：湿地、林地、水体等土地覆盖本底调查",
            "业务底图：规划、执法巡查、资源清查的分类底图",
        ],
    },
    "少样本地物分类": {
        "purpose": "在每类只给很少标注样本（甚至几到几十个像素）的情况下，仍能完成地物分类出图。解决“新区域想制图，但人工标样本太贵太慢”的问题。",
        "scenarios": [
            "新测区冷启动：只有少量样点也能先出分类图",
            "应急制图：灾害后/突击调查，标注来不及做全",
            "降本：减少野外采样与人工标注成本",
        ],
    },
    "跨地区/跨场景迁移分类": {
        "purpose": "在已有地区训练好的模型，迁移到新地区/新传感器场景继续分类，减少“每换一块地就重新大量标注训练”的成本。",
        "scenarios": [
            "跨市县复用已有分类能力",
            "传感器/成像条件变化后的快速适配",
            "业务扩展到新测区时降低重复建设成本",
        ],
    },
    "开放集识别（能标出未知类）": {
        "purpose": "不仅识别训练时见过的地物类别，还能把“从来没见过/不在名录里”的像素标成未知类，避免硬塞进某个已知类造成误判。",
        "scenarios": [
            "异常地物发现与告警",
            "名录外目标筛查（如临时堆场、未知构筑物）",
            "开放环境下更稳健的地物制图",
        ],
    },
    "开放集识别（能标出未知类）；可融合激光雷达": {
        "purpose": "在高光谱基础上可融合激光雷达（高程/三维结构），既做已知地物分类，也能标出未知类，提高城市/城郊复杂场景的可靠性。",
        "scenarios": ["城市多源联合调查", "未知地物/异常目标发现", "建筑、道路、植被分层制图"],
    },
    "高光谱地物分类；可融合激光雷达": {
        "purpose": "同时利用高光谱（材质/光谱）和激光雷达（高度/结构）信息，做更准确的地物分类，尤其适合城市建筑、道路、植被分层。",
        "scenarios": ["城市多源联合地物调查", "建筑/道路/植被三维结构辅助分类", "规划与市政底图制作"],
    },
    "高光谱–多光谱融合 / 质量提升": {
        "purpose": "先把高光谱与多光谱等信息融合或提质（如超分辨），再服务后续精细分类。重点是“把输入影像做更好”，为分类铺路。",
        "scenarios": ["影像质量不足时先融合提质再分类", "多源卫星/航空数据协同利用", "精细分类前的数据预处理增强"],
    },
    "高光谱地物分类；大模型预训练后迁移": {
        "purpose": "先在大规模数据上预训练，再迁移到本地高光谱分类任务，提升少样本/新场景下的可用性。",
        "scenarios": ["预训练模型复用与迁移冷启动", "大范围土地覆盖识别", "本地业务数据不足时的能力补充"],
    },
    "高光谱地物分类；轻量化": {
        "purpose": "在保持可用分类效果的前提下，缩小模型、降低算力需求，便于边缘设备或快速演示部署。",
        "scenarios": ["算力受限环境部署", "现场快速出图演示", "批量测区低成本跑图"],
    },
    "高光谱地物分类；Mamba高效建模": {
        "purpose": "用 Mamba 等高效序列建模结构做高光谱地物分类，目标仍是像素级地物出图，侧重效率与长程依赖建模。",
        "scenarios": ["大规模影像高效分类出图", "农业/城市地物制图", "需要兼顾速度与精度的业务演示"],
    },
    "高光谱地物分类；Mamba高效建模；Transformer特征建模": {
        "purpose": "结合 Mamba/Transformer 等新架构做高光谱像素级地物分类，输出地物分类图，适合需要更强特征建模的场景。",
        "scenarios": ["农业/城市地物精细制图", "复杂光谱–空间特征场景", "方法对比与选型演示"],
    },
    "高光谱地物分类；Transformer特征建模": {
        "purpose": "用 Transformer 建模光谱–空间特征，完成像素级地物分类并输出分类彩图。",
        "scenarios": ["作物/城市/湿地等地物制图", "需要更强全局特征建模的测区", "技术方案对比与汇报演示"],
    },
    "少样本地物分类；Transformer特征建模": {
        "purpose": "在标注很少时，借助 Transformer 特征建模完成地物分类，降低新区域制图的标注门槛。",
        "scenarios": ["少标注新区域冷启动", "降本增效的快速制图", "样本稀缺条件下的业务试点"],
    },
    "方法综述与选型参考": {
        "purpose": "本身不是直接面向业务出图的“生产模型”，而是帮团队了解有哪些方法、怎么演进、如何选型。",
        "scenarios": ["技术调研与汇报底稿", "模型选型清单", "团队学习与知识沉淀"],
    },
    "经典基线分类（KNN / SVM / CNN）": {
        "purpose": "提供 KNN/SVM/CNN 等经典基线，用来对照“传统方法 vs 深度学习”效果，支撑教学与方案论证。",
        "scenarios": ["对照组实验", "教学演示", "汇报时说明方法进步幅度"],
    },
    "标签噪声下稳健训练": {
        "purpose": "在标注有噪声、不完全可靠时，仍尽量稳住分类效果，降低脏标签对制图结果的冲击。",
        "scenarios": ["标注质量参差不齐时的稳健训练", "降低返工成本", "业务试点中的容错分类"],
    },
}


def purpose_for(capability: str):
    if capability in CAP_TEMPLATES:
        t = CAP_TEMPLATES[capability]
        return t["purpose"], list(t["scenarios"])
    for key, t in CAP_TEMPLATES.items():
        if key in capability:
            return t["purpose"], list(t["scenarios"])
    if "开放集" in capability:
        t = CAP_TEMPLATES["开放集识别（能标出未知类）"]
    elif "少样本" in capability:
        t = CAP_TEMPLATES["少样本地物分类"]
    elif "跨地区" in capability or "跨场景" in capability:
        t = CAP_TEMPLATES["跨地区/跨场景迁移分类"]
    elif "激光雷达" in capability:
        t = CAP_TEMPLATES["高光谱地物分类；可融合激光雷达"]
    elif "融合" in capability or "多光谱" in capability:
        t = CAP_TEMPLATES["高光谱–多光谱融合 / 质量提升"]
    elif "综述" in capability:
        t = CAP_TEMPLATES["方法综述与选型参考"]
    elif "基线" in capability or "KNN" in capability:
        t = CAP_TEMPLATES["经典基线分类（KNN / SVM / CNN）"]
    elif "预训练" in capability or "大模型" in capability:
        t = CAP_TEMPLATES["高光谱地物分类；大模型预训练后迁移"]
    elif "噪声" in capability:
        t = CAP_TEMPLATES["标签噪声下稳健训练"]
    else:
        t = CAP_TEMPLATES["高光谱地物分类"]
    return t["purpose"], list(t["scenarios"])


def extract_field(block: str, name: str) -> str:
    m = re.search(rf"- \*\*{re.escape(name)}：\*\* (.+)", block)
    return m.group(1).strip() if m else ""


def extract_list(block: str, name: str):
    m = re.search(rf"- \*\*{re.escape(name)}：\*\*\s*\n((?:[ \t]*- .+\n)+)", block)
    if not m:
        return []
    return [x.strip() for x in re.findall(r"- (.+)", m.group(1))]


def parse_datasets(s: str):
    if not s or s.startswith("未明确"):
        return []
    out = []
    for p in s.split("、"):
        name = p.split("（")[0].strip()
        if name and name not in out and len(name) < 60:
            out.append(name)
    return out


def json_input_example(ds: str, info: dict) -> str:
    return (
        f"\n**接口化输入示例（以 {ds} 为例，字段来自真实 `.mat`）：**\n\n"
        "```json\n"
        "{\n"
        f'  "dataset": "{ds}",\n'
        '  "cube": {\n'
        f'    "file": "{info["cube_file"]}",\n'
        f'    "mat_key": "{info["cube_key"]}",\n'
        f'    "shape": "{info["shape"]}",\n'
        '    "dtype": "uint16",\n'
        '    "meaning": "每个像素一条光谱曲线（多波段反射/辐射值）"\n'
        "  },\n"
        '  "gt": {\n'
        f'    "file": "{info["gt_file"]}",\n'
        f'    "mat_key": "{info["gt_key"]}",\n'
        f'    "shape": "{info["gt_shape"]}",\n'
        '    "dtype": "uint8",\n'
        f'    "value_meaning": {{"0": "未标注/背景", "1_to_{info["classes"]}": "地物类别编号"}}\n'
        "  }\n"
        "}\n"
        "```\n"
    ).replace("{{", "{").replace("}}", "}")


def json_output_example(ds: str, info: dict) -> str:
    return (
        "\n**接口化输出示例（对照 HybridSN / MambaHSI / SGMAE 等源码常见产物）：**\n\n"
        "```json\n"
        "{\n"
        f'  "dataset": "{ds}",\n'
        '  "pred_map": {\n'
        f'    "shape": "{info["gt_shape"]}",\n'
        '    "dtype": "uint8",\n'
        f'    "classes": {info["classes"]},\n'
        '    "value_meaning": {"0": "背景或未预测", "k": "第 k 类地物"},\n'
        '    "files": ["predictions.npy", "predictions.jpg"]\n'
        "  },\n"
        '  "metrics_if_gt_available": {\n'
        '    "OA": "整体精度 Overall Accuracy",\n'
        '    "AA": "平均精度 Average Accuracy",\n'
        '    "Kappa": "Cohen Kappa",\n'
        '    "per_class_accuracy": {"1": "...", "2": "..."}\n'
        "  },\n"
        '  "note": "源码里通常先得到每像素类别号，再用配色表渲染成彩色分类图给人看"\n'
        "}\n"
        "```\n"
    )


def build_input_output(datasets, uses):
    if not datasets:
        inp = (
            "该模型源码未明确固定公开数据集。通用输入形态如下（与绝大多数分类模型一致）：\n\n"
            "1. **高光谱立方体**：三维数组 `H×W×B`（高×宽×波段），通常来自 `.mat` / `.npy`；\n"
            "2. **可选真值标签**：二维数组 `H×W`，`0=未标注/背景`，`1..C=地物类别`。\n\n"
            "若做成服务接口，请求体可约定为：\n\n"
            "```json\n"
            "{\n"
            '  "task": "hsi_classification",\n'
            '  "cube": {\n'
            '    "format": "mat_or_npy",\n'
            '    "path": "/data/xxx_corrected.mat",\n'
            '    "key": "cube_array_key",\n'
            '    "shape": [H, W, B],\n'
            '    "dtype": "uint16"\n'
            "  },\n"
            '  "gt_optional": {\n'
            '    "path": "/data/xxx_gt.mat",\n'
            '    "key": "gt_array_key",\n'
            '    "shape": [H, W],\n'
            '    "value_meaning": {"0": "未标注", "1_to_C": "地物类别编号"}\n'
            "  }\n"
            "}\n"
            "```\n"
        )
        out = (
            "通用输出形态（源码常见写法）：\n\n"
            "1. **分类图** `pred_map`：`H×W` 整型矩阵，每个像素一个类别号（常保存为 `.npy` / 着色后的 `.jpg/.png`）；\n"
            "2. **指标**（有真值时）：OA / AA / Kappa，以及每类精度。\n\n"
            "```json\n"
            "{\n"
            '  "pred_map": {\n'
            '    "shape": [H, W],\n'
            '    "dtype": "uint8",\n'
            '    "value_meaning": {"0": "背景或未预测", "1_to_C": "预测地物类别"},\n'
            '    "files": ["predictions.npy", "predictions.jpg"]\n'
            "  },\n"
            '  "metrics": {\n'
            '    "OA": 0.0,\n'
            '    "AA": 0.0,\n'
            '    "Kappa": 0.0,\n'
            '    "per_class_accuracy": {"1": 0.0, "2": 0.0}\n'
            "  }\n"
            "}\n"
            "```\n"
        )
        return inp, out

    lines_in = [
        "模型吃进去的是**高光谱影像立方体**（必要时再加真值标签），不是普通 RGB 照片。"
        "按本仓库源码与公开数据，对应关系如下：\n"
    ]
    lines_out = [
        "模型吐出来的是**每个像素一个类别号**的分类结果，再着色成地物分类彩图；"
        "有真值时还会给出精度指标。\n"
    ]
    for ds in datasets[:3]:
        info = DATASET_IO.get(ds)
        if not info:
            lines_in.append(f"- **{ds}**：请以下载后的 `.mat/.npy` 实际字段为准；类别明细见第 5 节。")
            lines_out.append(f"- **{ds}**：输出同尺寸分类图（类别数见第 5 节），并着色保存。")
            continue
        lines_in.append(
            f"- **{ds}**（{info['scene']}，{info['classes']}类）\n"
            f"  - 影像文件：`{info['cube_file']}`\n"
            f"  - `.mat` 字段名：`{info['cube_key']}`\n"
            f"  - 数组形状：`{info['shape']}`（高×宽×波段）\n"
            f"  - 标签文件：`{info['gt_file']}`，字段 `{info['gt_key']}`，形状 `{info['gt_shape']}`\n"
            f"  - 标签含义：`0=未标注`，`1..{info['classes']}=地物类`（类名见第 5 节）"
        )
        lines_out.append(
            f"- **{ds}**：输出 `pred_map`，形状与标签同为高×宽，取值 `0/1..{info['classes']}`；"
            f"再渲染成分类彩图（一种颜色一类地物）。"
        )

    primary = next(((ds, DATASET_IO[ds]) for ds in datasets if ds in DATASET_IO), None)
    if primary:
        ds, info = primary
        lines_in.append(json_input_example(ds, info))
        lines_out.append(json_output_example(ds, info))
    if uses:
        lines_out.append(
            "\n业务上可理解为：模型输出一张“地物名录上色图”，直接支撑："
            + "；".join(uses[:4])
            + "。"
        )
    return "\n".join(lines_in) + "\n", "\n".join(lines_out) + "\n"


def parse_models(detail: str):
    models = []
    cat_chunks = re.split(r"(?=^### .+（\d+ 个）\n)", detail, flags=re.M)
    for chunk in cat_chunks:
        chunk = chunk.strip()
        if not chunk.startswith("### "):
            continue
        first_nl = chunk.find("\n")
        cat_name = chunk[4:first_nl].strip()
        body = chunk[first_nl + 1 :]
        pieces = re.split(r"(?=^#### \d+\. )", body, flags=re.M)
        for piece in pieces:
            piece = piece.strip()
            if not piece.startswith("#### "):
                continue
            m = re.match(r"^#### (\d+)\. (.+?) —— (.+)\n([\s\S]*)$", piece)
            if not m:
                raise RuntimeError("无法解析: " + piece[:100])
            idx, name, cap, block = int(m.group(1)), m.group(2).strip(), m.group(3).strip(), m.group(4)
            code_ds = extract_field(block, "代码中的数据集")
            summary = extract_field(block, "能识别什么（摘要）")
            datasets = parse_datasets(code_ds)
            if not datasets:
                for dn in DATASET_IO:
                    if dn in summary and dn not in datasets:
                        datasets.append(dn)
            models.append(
                {
                    "cat": cat_name,
                    "idx": idx,
                    "name": name,
                    "cap": cap,
                    "path": extract_field(block, "仓库路径").strip("`"),
                    "paper": extract_field(block, "论文/题目"),
                    "datasets": datasets,
                    "uses": extract_list(block, "典型用途"),
                    "link": extract_field(block, "源码/论文入口"),
                    "in_imgs": re.findall(r"!\[([^\]]*)\]\((_demo_figs/real_in_[^)]+)\)", block),
                    "out_imgs": re.findall(r"!\[([^\]]*)\]\((_demo_figs/real_out_[^)]+)\)", block),
                    "in_ex": extract_field(block, "输入数据示例"),
                }
            )
    return models


def main():
    text = SRC.read_text(encoding="utf-8")
    download_section = re.search(r"## 2\. 人工下载地址与保存路径.*?(?=\n## 3\.)", text, re.S).group(0)
    class_section = re.search(r"## 3\. 公开数据集类别总表.*?(?=\n## 4\.)", text, re.S).group(0)
    overview_raw = re.search(r"## 4\. 模型总览表.*?(?=\n## 5\.)", text, re.S).group(0)
    detail = re.search(r"## 5\. 分模型详述\n(.*?)(?=\n## 6\. 附录)", text, re.S).group(1)

    models = parse_models(detail)
    assert len(models) == 87, len(models)

    year_map = {}
    for row in re.findall(
        r"^\| (\d+) \| (.+?) —— (.+?) \| (\d{4}|—) \| (.+?) \| (.+?) \|$",
        overview_raw,
        re.M,
    ):
        year_map[int(row[0])] = (row[3], row[4], row[5])

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = []

    parts.append(
        f"""# 高光谱分类小模型一览（领导精简版）

> 更新时间：{now}  
> 模型数：{len(models)}  
> 阅读目标：领导/业务同事 **3 分钟看懂模型做什么、用在哪、进出数据长什么样**；技术细节可再下钻源码。  
> 原则：类别明细集中放在第 5 节；各模型不重复罗列类名；输入输出按真实 `.mat` 字段与源码产物写清楚。

---

## 目录

1. [一句话看懂](#1-一句话看懂)
2. [模型作用（领导必读）](#2-模型作用领导必读)
3. [应用场景（领导必读）](#3-应用场景领导必读)
4. [输入输出数据说明（一看就懂）](#4-输入输出数据说明一看就懂)
5. [公开数据集类别总表](#5-公开数据集类别总表)
6. [模型总览表](#6-模型总览表)
7. [分模型详述](#7-分模型详述)
8. [数据下载与附录](#8-数据下载与附录)

---

## 1. 一句话看懂

这些小模型做同一件事：

> **输入**一张高光谱影像（每个像素不是 RGB 三通道，而是几十到上百个窄波段光谱值）  
> **输出**一张地物分类图（每个像素一个类别号，再上色给人看：玉米、道路、水体……）

仓库已有可演示真实数据：

- 输入：`HSI_data/Indian_pines_corrected.mat` → 字段 `indian_pines_corrected`，形状 **145×145×200**
- 标签：`HSI_data/Indian_pines_gt.mat` → 字段 `indian_pines_gt`，形状 **145×145**（0=未标注，1–16=地物）

![Indian Pines 输入示意](_demo_figs/real_in_indian_pines.png)

![Indian Pines 输出示意](_demo_figs/real_out_indian_pines.png)

---

## 2. 模型作用（领导必读）

### 2.1 核心作用

| 看什么 | 说明 |
|--------|------|
| 解决什么问题 | 人工看高光谱“光谱曲线”判地物又慢又难；模型自动把每个像素判成地物类别 |
| 产出什么成果 | **地物分类一张图**（可叠加到地图/影像上），不是检测框、不是文字问答 |
| 和普通遥感分类差别 | 普通光学常只有 RGB/少量波段；高光谱波段很密，更擅长区分“长得像但材质不同”的地物（如不同作物、不同路面材料） |
| 不做什么 | 默认不是目标检测（不画框找车），也不是生成式对话；主线是**像素级语义分类/制图** |

### 2.2 按能力类型理解“作用”

| 能力类型 | 作用一句话 |
|----------|------------|
| 通用地物分类 | 标注充足时，稳定输出地物分类图 |
| 少样本分类 | 每类只有很少样本也能出图，适合新区域冷启动 |
| 跨场景/跨域迁移 | 旧地区模型迁到新地区，减少重复标注 |
| 开放集识别 | 已知类照常识别，未知类单独标出，降低硬分错风险 |
| 高光谱+激光雷达 | 光谱+高程一起用，城市建筑/道路/植被更稳 |
| 融合/提质 | 先把影像融合或超分做好，再服务分类 |
| 预训练/大模型 | 大规模预训练后迁移到本地任务 |
| 综述与基线 | 用于选型、对照、学习，不直接当业务生产模型 |

---

## 3. 应用场景（领导必读）

### 3.1 业务场景总表

| 场景 | 典型问题 | 模型怎么帮 |
|------|----------|------------|
| 农业农村 | 这块地种了什么？玉米/大豆/小麦怎么分布？ | 输出田块级/像素级作物与植被分类图 |
| 城市国土 | 道路、建筑、绿地、停车场、水体怎么铺开？ | 输出城市土地利用/覆盖分类图 |
| 湿地生态 | 水体、沼泽、林地类型如何变化？ | 输出湿地土地覆盖分类图，支撑本底与监测 |
| 应急与扩展 | 新测区、少标注、要快速出图 | 选少样本/迁移类模型，先出可用底图 |
| 风险发现 | 有没有“名录外”异常地物？ | 选开放集模型，把未知类单独标出 |
| 多源增强 | 只有光谱不够，建筑高度也重要 | 选高光谱+LiDAR 融合模型 |
| 技术方案论证 | 领导要听清“为什么选这个模型” | 用综述/基线做对照说明 |

### 3.2 怎么选模型（不用懂算法）

1. **有较多样本、要常规出图** → 通用地物分类  
2. **样本很少/新区域** → 少样本；或预训练迁移  
3. **换了一个地方还想复用** → 跨场景迁移  
4. **怕把没见过的东西硬分错** → 开放集  
5. **城市且有激光雷达** → 高光谱+LiDAR  
6. **只要了解有哪些方法** → 综述与基线  

---

## 4. 输入输出数据说明（一看就懂）

> 依据仓库真实文件与典型源码（如 `2019/HybridSN_Exploring_3D_2D/main.py`、`2024/MambaHSI/utils/visual_predict.py`、`2025/SGMAE/get_cls_map.py`）整理。  
> 学术源码多数直接读 `.mat`；若要做系统对接，可包一层如下 JSON。

### 4.1 输入是什么

**本质：** 一个三维数组（高光谱立方体）+ 可选二维标签。

| 项目 | 内容 |
|------|------|
| 影像立方体 | 形状 `H×W×B`：H 行、W 列、B 个波段；每个像素是一条光谱 |
| 真值标签（训练/评测用） | 形状 `H×W`；`0` 未标注，`1..C` 为地物类 |
| 常见文件 | `.mat`（MATLAB）、部分模型用 `.npy` |
| 不是什么 | 不是一张普通 JPG；也不是纯 JSON 文本业务单 |

**真实数据例（Indian Pines，仓库已有）：**

```json
{{
  "dataset": "Indian Pines",
  "cube": {{
    "file": "HSI_data/Indian_pines_corrected.mat",
    "mat_key": "indian_pines_corrected",
    "shape": [145, 145, 200],
    "dtype": "uint16",
    "meaning": "145×145 个像素，每像素 200 个波段光谱值"
  }},
  "gt": {{
    "file": "HSI_data/Indian_pines_gt.mat",
    "mat_key": "indian_pines_gt",
    "shape": [145, 145],
    "dtype": "uint8",
    "value_meaning": {{
      "0": "未标注/背景",
      "1": "苜蓿 Alfalfa",
      "2": "玉米-非耕 Corn-notill",
      "16": "石钢塔 Stone-Steel-Towers",
      "note": "完整 1–16 类名见第 5 节"
    }}
  }}
}}
```

**再例（PaviaU，仓库已下载）：**

```json
{{
  "dataset": "Pavia University",
  "cube": {{
    "file": "_raw_datasets/PaviaU.mat",
    "mat_key": "paviaU",
    "shape": [610, 340, 103],
    "dtype": "uint16"
  }},
  "gt": {{
    "file": "_raw_datasets/PaviaU_gt.mat",
    "mat_key": "paviaU_gt",
    "shape": [610, 340],
    "dtype": "uint8",
    "value_meaning": {{"0": "未标注", "1_to_9": "沥青/草地/砾石/树木/…（见第 5 节）"}}
  }}
}}
```

**再例（Houston2018，单文件含影像+标签）：**

```json
{{
  "dataset": "Houston2018",
  "file": "_raw_datasets/Houston2018/houstonU2018.mat",
  "cube": {{"mat_key": "houstonU", "shape": [601, 2384, 50], "dtype": "uint16"}},
  "gt": {{"mat_key": "houstonU_gt", "shape": [601, 2384], "dtype": "uint8"}}
}}
```

### 4.2 输出是什么

**本质：** 一张与影像同高宽的“类别编号图”，再着色成彩图；有标签时附带精度。

源码常见流程：

1. 模型对每个像素（或每个邻域窗口中心像素）输出各类别概率 → `argmax` 得到类别号  
2. 拼成 `outputs[H][W]`（见 HybridSN `main.py`）  
3. `spectral.save_rgb(...)` / 自定义 colormap 存 `predictions.jpg`（见 MambaHSI `visual_predict.py`、SGMAE `get_cls_map.py`）  
4. 打印/返回 OA、AA、Kappa

**输出 JSON 约定示例：**

```json
{{
  "task": "hsi_classification",
  "pred_map": {{
    "shape": [145, 145],
    "dtype": "uint8",
    "value_meaning": {{
      "0": "背景或未预测",
      "1_to_C": "预测的地物类别编号（与训练集类名对齐）"
    }},
    "files": {{
      "array": "predictions.npy",
      "color_image": "predictions.jpg"
    }}
  }},
  "metrics": {{
    "OA": 0.985,
    "AA": 0.972,
    "Kappa": 0.981,
    "per_class_accuracy": {{
      "1": 0.99,
      "2": 0.96
    }}
  }},
  "human_readable": "一张地物分类彩图：一种颜色代表一类地物"
}}
```

> 说明：上面 `metrics` 数值仅为结构示例，**不是**本仓库实测承诺精度。

### 4.3 和“业务系统”怎么对接（概念）

```text
业务系统
  └─ 提交：高光谱 .mat/.npy（或对象存储路径）
        ↓
  分类小模型（本仓库之一）
        ↓
  返回：pred_map（数组）+ 着色图 URL +（可选）OA/AA/Kappa JSON
        ↓
业务系统叠图 / 统计面积 / 制专题图
```

---

"""
    )
    # 上面 header 里为了 f-string 用了双大括号，这里已经是 format 后的单大括号... 
    # 等等，f-string 会把 {{ 变成 {，所以 parts[-1] 已经是正确 JSON。

    class_section2 = class_section.replace(
        "## 3. 公开数据集类别总表（完整明细）", "## 5. 公开数据集类别总表"
    )
    parts.append(class_section2.strip() + "\n\n---\n\n")

    ov_lines = [
        "## 6. 模型总览表\n\n",
        "| 序号 | 模型 | 能力 | 年份 | 数据集 | 作用（一句话） | 典型场景 |\n",
        "|------|------|------|------|--------|----------------|----------|\n",
    ]
    by_idx = {m["idx"]: m for m in models}
    for idx in sorted(by_idx):
        m = by_idx[idx]
        year, ds, _ = year_map.get(
            idx, ("—", "、".join(m["datasets"]) or "未明确", "")
        )
        purpose, scenarios = purpose_for(m["cap"])
        purpose_short = purpose.split("。")[0] + "。"
        if len(purpose_short) > 42:
            purpose_short = purpose_short[:40] + "…"
        scen_short = "；".join(scenarios[:2]).replace("|", "/")
        purpose_short = purpose_short.replace("|", "/")
        ds_show = "、".join(m["datasets"]) if m["datasets"] else ds
        if len(ds_show) > 36:
            ds_show = ds_show[:34] + "…"
        ov_lines.append(
            f"| {idx} | {m['name']} | {m['cap']} | {year} | {ds_show} | {purpose_short} | {scen_short} |\n"
        )
    parts.append("".join(ov_lines) + "\n---\n\n")

    parts.append("## 7. 分模型详述\n\n")
    parts.append(
        "> 每个模型固定四块：**①作用 → ②场景 → ③输入 → ④输出**。"
        "类别名称不在此重复展开，统一见第 5 节。\n\n"
    )

    current_cat = None
    for m in models:
        if m["cat"] != current_cat:
            current_cat = m["cat"]
            parts.append(f"### {current_cat}\n\n")
        purpose, scenarios = purpose_for(m["cap"])
        scen = []
        for s in scenarios + m["uses"]:
            if s and s not in scen:
                scen.append(s)
        scen = scen[:6]
        inp, outp = build_input_output(m["datasets"], m["uses"])

        parts.append(f"#### {m['idx']}. {m['name']} —— {m['cap']}\n\n")
        parts.append(f"- **仓库路径：** `{m['path']}`\n")
        if m["paper"]:
            parts.append(f"- **论文/题目：** {m['paper']}\n")
        ds_txt = "、".join(m["datasets"]) if m["datasets"] else "源码未明确（下载数据后以标签文件为准）"
        parts.append(f"- **对应数据集：** {ds_txt}\n")
        if m["datasets"]:
            parts.append(
                f"- **能识别的地物：** 见第 5 节对应数据集类别明细（{'、'.join(m['datasets'][:4])}）\n"
            )
        parts.append("\n")
        parts.append(f"**① 模型作用**\n\n{purpose}\n\n")
        parts.append("**② 应用场景**\n\n")
        for s in scen:
            parts.append(f"- {s}\n")
        parts.append("\n**③ 输入数据（是什么）**\n\n")
        parts.append(inp)
        if m["in_imgs"]:
            parts.append("\n预览：\n\n")
            for alt, path in m["in_imgs"]:
                parts.append(f"![{alt or '输入预览'}]({path})\n\n")
        elif m["in_ex"] and "不展示替身" in m["in_ex"]:
            parts.append("> 原始立方体待数据就绪后补图；此处不顶替展示。\n\n")
        parts.append("**④ 输出数据（是什么）**\n\n")
        parts.append(outp)
        if m["out_imgs"]:
            parts.append("\n预览：\n\n")
            for alt, path in m["out_imgs"]:
                parts.append(f"![{alt or '输出预览'}]({path})\n\n")
        parts.append(f"- **源码/论文入口：** {m['link'] or '仓库未提供链接'}\n\n")
        parts.append("---\n\n")

    dl2 = download_section.replace(
        "## 2. 人工下载地址与保存路径（重要）",
        "## 8. 数据下载与附录\n\n### 8.1 人工下载地址与保存路径",
    )
    parts.append(dl2.strip() + "\n\n")
    parts.append(
        """### 8.2 名称对照

| 目录名 | 文档中名称 |
|--------|------------|
| DABAN | DADBN |
| HybridSN_Exploring_3D_2D | HybridSN |
| MambaHSI_Plus | MambaHSI+ |
| CDMLC | Model Description 未单列；题名取自 readme |

### 8.3 审阅说明

- 本文件供学习、汇报与修改；确认后再转 Word。
- **作用 / 场景 / 输入 / 输出** 是领导阅读主线；算法细节请直接看各模型源码。
- 输入输出 JSON 为对接约定示例，便于系统化封装；学术源码本身多直接读写 `.mat`/`.npy`。
- 图片相对路径基于本仓库根目录。
- 相关文件：`数据集人工下载清单.md`、`_demo_figs/`、`高光谱分类小模型-领导精简版.备份-20260730.md`（旧版备份）。
"""
    )

    out_text = "".join(parts)
    OUT.write_text(out_text, encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"lines={out_text.count(chr(10))+1} chars={len(out_text)} models={len(models)}")
    print("json blocks=", out_text.count("```json"))
    print("has #### 87.", "#### 87." in out_text)


if __name__ == "__main__":
    main()
