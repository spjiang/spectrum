from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from app.config import Settings


def validate_paths(settings: Settings, input_dir: str, output_dir: str) -> tuple[Path, Path]:
    inp = Path(input_dir).expanduser().resolve()
    out = Path(output_dir).expanduser().resolve()
    if out == inp or inp in out.parents:
        raise HTTPException(400, "输出目录不能落在输入目录内")
    roots = [Path(r).expanduser().resolve() for r in settings.data_root_list()]
    if roots:

        def under(p: Path) -> bool:
            return any(p == r or r in p.parents for r in roots)

        if not under(inp) or not under(out):
            raise HTTPException(400, f"路径必须位于 DATA_ROOTS 下: {settings.data_roots}")
    return inp, out
