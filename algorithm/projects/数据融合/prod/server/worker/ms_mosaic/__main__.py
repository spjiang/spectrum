from __future__ import annotations

import argparse
from pathlib import Path

from ms_mosaic.local_defaults import INPUT as LOCAL_INPUT
from ms_mosaic.local_defaults import available as local_input_ready
from ms_mosaic.run_paths import stamp_run_output_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="多光谱/RGB 航摄目录 → 正射大图 + 质量报告")
    parser.add_argument(
        "--input",
        required=not local_input_ready,
        default=LOCAL_INPUT if local_input_ready else None,
        type=Path,
        help="拍完后的任务目录（如 MAX_*）。本机有默认测区时可省略",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="输出根目录；会在其下新建 YYYYMMDD_HHMMSS 子目录（与可视化任务相同）",
    )
    parser.add_argument("--max-frames", type=int, default=None, help="只用前 N 个可用曝光，便于调试")
    parser.add_argument("--max-index", type=int, default=None, help="只扫描编号不超过该值的文件")
    parser.add_argument(
        "--dsm-gsd",
        type=float,
        default=None,
        help="DSM 地面分辨率（米）。默认按中位航高/焦距估计，正射为其一半",
    )
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
        help="逗号分隔波段，默认全部。例: Color（仅 RGB）或 Color,550nm",
    )
    parser.add_argument(
        "--reuse-dsm",
        type=Path,
        default=None,
        help="跳过密集匹配，复用已有 DSM.tif 并按足迹补覆盖缺口",
    )
    parser.add_argument(
        "--benchmark-dir",
        type=Path,
        default=None,
        help="可选：对照该目录写比对报告。不改出图格网、覆盖、颜色",
    )
    parser.add_argument(
        "--match-reference-color",
        action="store_true",
        help="调试用：用参考正射套色。合格主路径不要开，出图不应依赖它",
    )
    parser.add_argument(
        "--run-mode",
        choices=("full", "until_stage", "step"),
        default="full",
        help="full 全流程；until_stage 跑到 --stop-after-stage 后停；step 只跑 --start-stage 一阶段",
    )
    parser.add_argument("--start-stage", default="S0_io", help="起始阶段，如 S2_at / S5_ortho")
    parser.add_argument(
        "--stop-after-stage",
        default=None,
        help="until_stage 时在该阶段结束后停止并返回 awaiting_continue",
    )
    args = parser.parse_args(argv)
    out = stamp_run_output_dir(args.out)
    print(f"out={out}", flush=True)
    bands = None if not args.bands else [s.strip() for s in args.bands.split(",") if s.strip()]
    params = {
        "input_dir": str(args.input),
        "output_dir": str(out),
        "max_frames": args.max_frames,
        "max_index": args.max_index,
        "workers": args.workers,
        "bands": bands,
        "cache_dir": str(args.cache_dir) if args.cache_dir else None,
        "reuse_dsm": str(args.reuse_dsm) if args.reuse_dsm else None,
        "run_mode": args.run_mode,
        "start_stage": args.start_stage,
        "stop_after_stage": args.stop_after_stage,
    }
    if args.dsm_gsd is not None:
        params["dsm_gsd"] = args.dsm_gsd
    if args.benchmark_dir is not None:
        params["benchmark_dir"] = str(args.benchmark_dir)
    if args.match_reference_color:
        params["match_reference_color"] = True
    from ms_mosaic.stage_runner import run_stages

    result = run_stages(args.input, out, params=params)
    status = result.get("status", "succeeded")
    print(f"status={status}")
    if result.get("completed_stage"):
        print(f"completed_stage={result['completed_stage']}")
    if status == "failed":
        print(f"error={result.get('error')}")
        return 2
    if status == "awaiting_continue":
        print("阶段完成，可用相同 --out 并设置 --start-stage 为下一阶段继续")
        return 10
    if status == "cancelled":
        return 130
    files = result.get("files") or {}
    print(f"shots={result.get('n_shots')}  elapsed={result.get('elapsed_s')}s  crs={result.get('crs')}")
    print(f"mosaic={files.get('mosaic_dir')}")
    print(f"rgb={files.get('rgb')}")
    print(f"dsm={files.get('dsm')}")
    print(f"report={files.get('report_pdf') or files.get('report_json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
