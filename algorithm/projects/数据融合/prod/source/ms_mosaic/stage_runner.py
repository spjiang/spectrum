"""按阶段编排 run_mosaic，支持起止阶段与 awaiting_continue。"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Sequence

from ms_mosaic.control import ControlState
from ms_mosaic.pipeline import run_mosaic
from ms_mosaic.progress import STAGES, NullReporter, ProgressReporter, global_percent_for, stage_index


def _should_run(stage: str, start: str, stop: str | None) -> bool:
    i = stage_index(stage)
    if i < stage_index(start):
        return False
    if stop is not None and i > stage_index(stop):
        return False
    return True


def run_stages(
    input_dir: Path,
    out_dir: Path,
    *,
    params: dict[str, Any] | None = None,
    reporter: ProgressReporter | None = None,
    control: ControlState | None = None,
) -> dict[str, Any]:
    """执行管线。

    返回 dict 含 status: succeeded | awaiting_continue | failed | cancelled
    以及 pipeline 原有字段（若已跑完相关阶段）。
    """
    params = dict(params or {})
    reporter = reporter or NullReporter()
    control = control or ControlState()
    start = params.get("start_stage") or "S0_io"
    run_mode = params.get("run_mode") or "full"
    stop = params.get("stop_after_stage")
    if run_mode == "step":
        stop = start
        params["stop_after_stage"] = stop
        run_mode = "until_stage"
    if run_mode == "full":
        stop = "S6_report"

    bands = params.get("bands")
    if isinstance(bands, str):
        bands = tuple(s.strip() for s in bands.split(",") if s.strip())
    elif isinstance(bands, list):
        bands = tuple(bands)

    # S0
    if _should_run("S0_io", start, stop):
        t0 = time.time()
        reporter.stage_start("S0_io", "校验输入输出路径")
        reporter.progress("S0_io", 50, global_percent_for("S0_io", 50), "检查路径")
        inp = Path(params.get("input_dir") or input_dir).expanduser().resolve()
        out = Path(params.get("output_dir") or out_dir).expanduser().resolve()
        if out == inp or inp in out.parents:
            reporter.event("failed", error="输出目录不能落在输入目录内", stage_id="S0_io")
            return {"status": "failed", "error": "输出目录不能落在输入目录内"}
        out.mkdir(parents=True, exist_ok=True)
        (out / "log").mkdir(parents=True, exist_ok=True)
        barrier = control.checkpoint_barrier()
        if barrier == "cancel":
            reporter.event("cancelled", stage_id="S0_io")
            return {"status": "cancelled"}
        reporter.stage_done("S0_io", time.time() - t0)
        if stop == "S0_io":
            reporter.event("awaiting_continue", stage_id="S0_io", message="S0 完成，等待继续")
            return {"status": "awaiting_continue", "completed_stage": "S0_io"}

    # 其余阶段：当前通过增强后的 run_mosaic 一次跑完 start..stop
    # （pipeline 内部按 stop_after 裁剪；若尚未接线则全量跑并在外层用 stop 语义近似）
    t0 = time.time()
    # map start to pipeline: if start after S0, still call run_mosaic which handles reuse
    try:
        reporter.stage_start(start if start != "S0_io" else "S1_catalog", "进入主计算")
        result = run_mosaic(
            Path(params.get("input_dir") or input_dir),
            Path(params.get("output_dir") or out_dir),
            max_frames=params.get("max_frames"),
            max_index=params.get("max_index"),
            dsm_gsd=params.get("dsm_gsd") or 0.107747293,
            workers=params.get("workers_dense") or params.get("workers_at") or params.get("workers"),
            bands=bands,
            cache_dir=Path(params["cache_dir"]) if params.get("cache_dir") else None,
            reuse_dsm=Path(params["reuse_dsm"]) if params.get("reuse_dsm") else None,
            reporter=reporter,
            control=control,
            start_stage=start,
            stop_after_stage=stop if run_mode == "until_stage" else None,
        )
    except Exception as exc:  # noqa: BLE001
        reporter.event("failed", error=str(exc))
        return {"status": "failed", "error": str(exc)}

    status = result.get("status") or "succeeded"
    if status == "awaiting_continue":
        reporter.event(
            "awaiting_continue",
            stage_id=result.get("completed_stage"),
            message=result.get("message") or "阶段完成，等待继续",
        )
    elif status == "cancelled":
        reporter.event("cancelled")
    elif status == "succeeded":
        reporter.event("succeeded", message="全流程完成", n_shots=result.get("n_shots"))
    result.setdefault("elapsed_s", time.time() - t0)
    return result
