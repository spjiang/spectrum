#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill 打包前结构与离线流水线验收。不读取、不打印任何 API Key。"""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_IN_ZIP = {".env", "config.yaml"}
REQUIRED_FILES = [
    "SKILL.md",
    "PORTABLE.md",
    "整体说明.md",
    "配置说明.md",
    "测试说明.md",
    "config.example.yaml",
    ".env.example",
    "requirements.txt",
    "knowledge_base/structured_papers1.json",
    "scripts/job_input.py",
    "scripts/run_offline.py",
    "scripts/run_e2e.py",
]
# 仅作验收夹具：生产作业不得把这些路径当成默认数据集名
FIXTURE_CLS = {
    "data": SKILL_ROOT / "data" / "Chenpi" / "chenpi.npy",
    "task": "classification",
    "object": "Citri Reticulatae Pericarpium",
    "report": SKILL_ROOT / "runs" / "verify_cls.json",
}
FIXTURE_REG = {
    "data": SKILL_ROOT / "data" / "corn" / "corn_data.npy",
    "label": SKILL_ROOT / "data" / "corn" / "protein_label.npy",
    "task": "regression",
    "object": "corn",
    "report": SKILL_ROOT / "runs" / "verify_reg.json",
}


def _fail(msg: str) -> None:
    print(f"FAIL  {msg}")
    raise SystemExit(1)


def check_structure() -> None:
    """检查分发必需文件与 frontmatter。"""
    missing = [rel for rel in REQUIRED_FILES if not (SKILL_ROOT / rel).is_file()]
    if missing:
        _fail("缺少必需文件: " + ", ".join(missing))
    if (SKILL_ROOT / "scripts" / "demo_pipeline.py").is_file():
        _fail("不得保留 scripts/demo_pipeline.py")
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---"):
        _fail("SKILL.md 缺少 YAML frontmatter")
    if "name: lumir-spectral-agent" not in text:
        _fail("SKILL.md name 必须为 lumir-spectral-agent")
    if "Use when" not in text.split("---", 2)[1]:
        _fail("description 必须包含 Use when 触发条件")
    lowered = text.lower()
    if "demo" in lowered:
        _fail("SKILL.md 不得出现 demo 一词")
    if "--dataset chenpi" in text or "--dataset milk" in text or "datasets.default" in text:
        _fail("SKILL.md 不得再把内置数据集名作为生产入口")
    if "--data" not in text:
        _fail("SKILL.md 必须要求 --data")
    papers = json.loads((SKILL_ROOT / "knowledge_base/structured_papers1.json").read_text(encoding="utf-8"))
    if not isinstance(papers, list) or len(papers) < 100:
        _fail(f"知识库条数异常: {0 if not isinstance(papers, list) else len(papers)}")
    print(f"PASS  结构检查（知识库 {len(papers)} 条）")


def check_no_secret_files_committed_to_examples() -> None:
    """example 文件不得含真实密钥形态。"""
    for rel in (".env.example", "config.example.yaml"):
        raw = (SKILL_ROOT / rel).read_text(encoding="utf-8")
        if "sk-" in raw and "your-deepseek-key" not in raw and "sk-your" not in raw:
            for token in raw.split():
                if token.startswith("sk-") and "your" not in token.lower():
                    _fail(f"{rel} 疑似含真实密钥")
    example = (SKILL_ROOT / "config.example.yaml").read_text(encoding="utf-8")
    if "datasets:" in example or "chenpi" in example:
        _fail("config.example.yaml 不得再声明默认数据集")
    print("PASS  example 配置无真实密钥、无默认数据集")


def run_offline_job(fx: dict) -> Path:
    """用显式 --data 跑离线作业并返回 JSON 报告路径。"""
    out = fx["report"]
    cmd = [
        sys.executable,
        str(SKILL_ROOT / "scripts/run_offline.py"),
        "--data",
        str(fx["data"]),
        "--task",
        fx["task"],
        "--object",
        fx["object"],
        "--offline",
        "--json-out",
        str(out),
    ]
    if fx.get("label"):
        cmd.extend(["--label", str(fx["label"])])
    proc = subprocess.run(cmd, cwd=str(SKILL_ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        _fail(f"{fx['object']} 离线失败: {proc.stderr[-800:] or proc.stdout[-800:]}")
    if not out.is_file():
        _fail(f"{fx['object']} 未写出报告 {out}")
    return out


def check_report(path: Path, name: str, expect_task: str) -> None:
    """断言离线报告含五步字段且指标存在。"""
    report = json.loads(path.read_text(encoding="utf-8"))
    if not report.get("data_path"):
        _fail(f"{name} 报告缺 data_path")
    steps = report.get("steps") or {}
    for key in ("entity", "retrieve", "methods", "features", "infer"):
        if key not in steps:
            _fail(f"{name} 报告缺步骤 {key}")
    entity = steps["entity"]
    if not entity.get("research_object"):
        _fail(f"{name} 实体抽取为空")
    if entity.get("task_type") != expect_task:
        _fail(f"{name} task_type={entity.get('task_type')} 期望 {expect_task}")
    if not steps["retrieve"].get("matched"):
        _fail(f"{name} BM25 无命中")
    methods = steps["methods"]
    if not methods.get("preprocessing") or not methods.get("features"):
        _fail(f"{name} 方法选择为空")
    infer = steps["infer"]
    if expect_task == "classification":
        acc = infer.get("accuracy")
        if acc is None:
            _fail(f"{name} 缺 accuracy")
        print(f"PASS  {name} 离线分类 accuracy={acc:.4f}")
    else:
        r2 = infer.get("r2")
        if r2 is None:
            _fail(f"{name} 缺 r2")
        print(f"PASS  {name} 离线回归 r2={r2:.4f}")


def check_zip(zip_path: Path) -> None:
    """检查分发 zip 不含密钥文件。"""
    if not zip_path.is_file():
        print(f"SKIP  尚未生成 zip: {zip_path}")
        return
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        for bad in FORBIDDEN_IN_ZIP:
            if any(n.endswith("/" + bad) or n == bad or n.endswith(bad) for n in names):
                _fail(f"zip 含禁止文件 {bad}")
        if not any(n.endswith("SKILL.md") for n in names):
            _fail("zip 缺少 SKILL.md")
        if not any("structured_papers1.json" in n for n in names):
            _fail("zip 缺少知识库")
        if any(n.endswith("scripts/demo_pipeline.py") for n in names):
            _fail("zip 不得包含 demo_pipeline.py")
    print(f"PASS  zip 检查 {zip_path.name}（无 .env / config.yaml）")


def main() -> None:
    check_structure()
    check_no_secret_files_committed_to_examples()
    if not FIXTURE_CLS["data"].is_file() or not FIXTURE_REG["data"].is_file():
        _fail("验收夹具缺失：需要 data/ 下的光谱文件供 --data 显式引用（不是默认数据集）")
    check_report(run_offline_job(FIXTURE_CLS), "classification_fixture", "classification")
    check_report(run_offline_job(FIXTURE_REG), "regression_fixture", "regression")
    zip_path = SKILL_ROOT.parent / "lumir-spectral-agent-openclaw.zip"
    check_zip(zip_path)
    print("全部验收通过")


if __name__ == "__main__":
    main()
