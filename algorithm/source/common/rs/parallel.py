"""CPU 工人数与线程映射。大图分块用线程，避免 GDAL 多进程死锁。"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def worker_count(requested: int | None = 0) -> int:
    """requested<=0 时用 CPU 核数，上限 32。"""
    ncpu = os.cpu_count() or 1
    cap = max(1, min(int(ncpu), 32))
    if requested is None or int(requested) <= 0:
        return cap
    return max(1, min(int(requested), cap))


def map_threads(fn: Callable[[T], U], items: Iterable[T], workers: int) -> list[U]:
    """workers=1 或只有一项时顺序执行，保持结果可复现。"""
    seq = list(items)
    if not seq:
        return []
    n = max(1, int(workers))
    if n == 1 or len(seq) == 1:
        return [fn(item) for item in seq]
    with ThreadPoolExecutor(max_workers=n) as pool:
        return list(pool.map(fn, seq))
