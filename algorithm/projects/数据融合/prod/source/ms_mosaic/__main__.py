from __future__ import annotations

import argparse
from pathlib import Path

from ms_mosaic.pipeline import run_mosaic


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MAX 多光谱目录 → 正射大图 + 质量报告")
    parser.add_argument("--input", required=True, type=Path, help="拍完后的 MAX_* 目录")
    parser.add_argument("--out", required=True, type=Path, help="输出目录")
    parser.add_argument("--max-frames", type=int, default=None, help="只用前 N 个可用曝光，便于调试")
    parser.add_argument("--max-index", type=int, default=None, help="只扫描编号不超过该值的文件")
    args = parser.parse_args(argv)
    result = run_mosaic(
        args.input,
        args.out,
        max_frames=args.max_frames,
        max_index=args.max_index,
    )
    print(f"shots={result['n_shots']}  elapsed={result['elapsed_s']}s  crs={result['crs']}")
    print(f"rgb={result['files'].get('rgb')}")
    print(f"report={result['files'].get('report_json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
