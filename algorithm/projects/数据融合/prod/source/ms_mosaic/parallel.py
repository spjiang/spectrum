"""按格网块并行的执行器。

密集匹配与正射都是「块之间完全独立」的计算，是典型的可并行结构。串行跑
4.5M 格网要 410 s，10 km 条带按面积外推约 2.2 小时，远超 30 分钟目标。

三个实现要点
------------
每个进程独立持有影像缓存
    影像是 numpy 数组，跨进程共享要么走共享内存（需要自己管生命周期），要么
    反复 pickle（比重新读盘还慢）。直接让每个 worker 自己读、自己缓存最简单，
    代价是同一张影像会被多个进程各读一次。

按空间邻近顺序分块
    相邻格网块看到的是同一批影像。若按块号轮转（worker i 拿第 i, i+n, i+2n 块），
    每个 worker 都要扫遍全部影像，缓存全部失效。改成把块按行带切成连续段，
    每段给一个 worker，缓存命中率就上来了。

限制每进程缓存张数
    668 张灰度影像约 2.1 GB。12 个进程各自缓存全量要 25 GB。按每进程
    limit 张封顶，既够用又不至于把内存吃光。
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any

Window = tuple[int, int, int, int]

# 每进程影像缓存张数上限。一个格网块最多用 max_views(10) 张，留几倍余量
# 让相邻块之间能复用，再多就只是占内存。
CACHE_PER_WORKER = 48


def default_workers() -> int:
    """默认进程数。留一个核给主进程写盘和系统，避免整机卡死。"""
    n = os.cpu_count() or 1
    return max(1, min(n - 1, 16))


def resolve_workers(requested: int | None) -> int:
    """requested 为 None 取默认值，<=1 表示串行（便于调试与测试）。"""
    if requested is None:
        return default_workers()
    return max(1, int(requested))


def spatial_chunks(windows: Sequence[Window], n_chunks: int) -> list[list[int]]:
    """把格网块按空间邻近切成 n_chunks 段，返回各段的块下标。

    先按 (行, 列) 排序再切连续段，使同一段内的块在地面上相邻，从而共用影像。
    """
    if n_chunks <= 1 or len(windows) <= 1:
        return [list(range(len(windows)))]
    order = sorted(range(len(windows)), key=lambda k: (windows[k][0], windows[k][1]))
    n_chunks = min(n_chunks, len(order))
    size, extra = divmod(len(order), n_chunks)
    chunks, start = [], 0
    for c in range(n_chunks):
        take = size + (1 if c < extra else 0)
        chunks.append(order[start : start + take])
        start += take
    return chunks


@dataclass
class TileJob:
    """一段连续格网块的任务。worker 收到它后按序算完再返回。"""

    indices: list[int]
    windows: list[Window]


_WORKER_STATE: dict[str, Any] = {}


def _init_worker(setup: Callable[[], Any]) -> None:
    """进程启动时建一次性的重型状态（影像缓存等）。"""
    # 每个 worker 都是独立进程，BLAS 再各开多线程会超订 CPU，反而变慢
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(var, "1")
    _WORKER_STATE["ctx"] = setup()


def _run_job(fn: Callable[[Any, Window], Any], job: TileJob) -> list[tuple[int, Any]]:
    ctx = _WORKER_STATE["ctx"]
    return [(k, fn(ctx, w)) for k, w in zip(job.indices, job.windows)]


def map_tiles(
    windows: Sequence[Window],
    setup: Callable[[], Any],
    fn: Callable[[Any, Window], Any],
    *,
    workers: int | None = None,
    log: Callable[[str], None] | None = None,
    label: str = "分块计算",
) -> Iterable[tuple[int, Window, Any]]:
    """并行遍历格网块，按完成顺序产出 (块下标, 窗口, 结果)。

    setup 与 fn 必须是模块级可 pickle 的对象（不能是 lambda 或闭包）。
    workers <= 1 时在当前进程直接跑，便于打断点调试。
    """
    windows = list(windows)
    n = resolve_workers(workers)
    total = len(windows)
    if not windows:
        return

    if n == 1:
        ctx = setup()
        for k, w in enumerate(windows):
            yield k, w, fn(ctx, w)
            if log is not None and (k + 1) % 10 == 0:
                log(f"{label} {k + 1}/{total} 块")
        return

    from concurrent.futures import ProcessPoolExecutor, as_completed

    chunks = spatial_chunks(windows, n * 2)  # 每进程分两段，缓解块间耗时不均
    jobs = [TileJob(c, [windows[k] for k in c]) for c in chunks]
    done = 0
    if log is not None:
        log(f"{label}：{total} 块 / {len(jobs)} 段 / {n} 进程")
    with ProcessPoolExecutor(max_workers=n, initializer=_init_worker, initargs=(setup,)) as pool:
        futures = [pool.submit(_run_job, fn, job) for job in jobs]
        for fut in as_completed(futures):
            for k, result in fut.result():
                yield k, windows[k], result
                done += 1
            if log is not None:
                log(f"{label} {done}/{total} 块")
