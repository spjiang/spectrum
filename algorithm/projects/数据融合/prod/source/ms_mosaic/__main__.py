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
    parser.add_argument("--dsm-gsd", type=float, default=None, help="DSM 地面分辨率（米），默认对齐商业 0.1077")
    parser.add_argument("--workers", type=int, default=None, help="密集匹配/正射进程数，默认 CPU-1")
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="特征缓存目录。复用上次空三的 features 可跳过提取",
    )
    parser.add_argument(
        "--bands",
        default=None,
        help="逗号分隔波段，默认全部。例: Color 或 Color,550nm",
    )
    parser.add_argument(
        "--reuse-dsm",
        type=Path,
        default=None,
        help="跳过密集匹配，复用已有 DSM.tif 并按足迹补北缘缺口",
    )
    args = parser.parse_args(argv)
    bands = None if not args.bands else tuple(s.strip() for s in args.bands.split(",") if s.strip())
    kwargs = dict(
        max_frames=args.max_frames,
        max_index=args.max_index,
        workers=args.workers,
        bands=bands,
        cache_dir=args.cache_dir,
        reuse_dsm=args.reuse_dsm,
    )
    if args.dsm_gsd is not None:
        kwargs["dsm_gsd"] = args.dsm_gsd
    result = run_mosaic(args.input, args.out, **kwargs)
    print(f"shots={result['n_shots']}  elapsed={result['elapsed_s']}s  crs={result['crs']}")
    print(f"mosaic={result['files'].get('mosaic_dir')}")
    print(f"rgb={result['files'].get('rgb')}")
    print(f"dsm={result['files'].get('dsm')}")
    print(f"report={result['files'].get('report_pdf') or result['files'].get('report_json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
