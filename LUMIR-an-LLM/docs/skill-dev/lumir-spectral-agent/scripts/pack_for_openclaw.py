#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打包可导入 OpenClaw 的 Skill zip。默认精简包，排除密钥与文献全文。"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = SKILL_ROOT.parent / "lumir-spectral-agent-openclaw.zip"

EXCLUDE_ALWAYS = {
    ".env",
    "config.yaml",
    ".DS_Store",
}
EXCLUDE_DIR_NAMES = {"__pycache__", ".git"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def should_skip(rel: Path, include_papers: bool, include_vendor: bool, include_runs: bool) -> bool:
    """判断相对路径是否应排除出包。"""
    parts = set(rel.parts)
    if parts & EXCLUDE_DIR_NAMES:
        return True
    if rel.name in EXCLUDE_ALWAYS:
        return True
    if rel.suffix in EXCLUDE_SUFFIXES:
        return True
    if rel.name.startswith(".") and rel.name not in {".env.example", ".gitignore"}:
        return True
    if not include_papers and rel.parts[:1] == ("Papers",):
        return True
    if not include_vendor and rel.parts[:1] == ("vendor",):
        return True
    if not include_runs and rel.parts[:1] == ("runs",) and rel.name != ".gitkeep":
        return True
    return False


def pack(out: Path, include_papers: bool, include_vendor: bool) -> None:
    """写入 zip，根目录名为 lumir-spectral-agent。"""
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    count = 0
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in SKILL_ROOT.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(SKILL_ROOT)
            if should_skip(rel, include_papers, include_vendor, include_runs=False):
                continue
            zf.write(path, arcname=str(Path("lumir-spectral-agent") / rel))
            count += 1
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"wrote {out}")
    print(f"files={count}  size={size_mb:.2f} MB")
    print("excluded: .env, config.yaml, runs/*.json, Papers=" 
          f"{'kept' if include_papers else 'dropped'}, vendor={'kept' if include_vendor else 'dropped'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="打包 lumir-spectral-agent 供 OpenClaw")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--full", action="store_true", help="包含 Papers/ 与 vendor/")
    args = parser.parse_args()
    pack(args.out, include_papers=args.full, include_vendor=args.full)


if __name__ == "__main__":
    main()
