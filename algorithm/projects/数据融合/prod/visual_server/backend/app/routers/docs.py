from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from app.auth import require_roles
from app.config import Settings, get_settings
from app.models import User

router = APIRouter(prefix="/api/docs", tags=["docs"])


@router.get("/cli-guide", response_class=PlainTextResponse)
def cli_guide(
    settings: Settings = Depends(get_settings),
    _: User = Depends(require_roles("executor", "viewer", "admin", "configurator")),
) -> str:
    path = Path(settings.cli_guide_path) if settings.cli_guide_path else Path()
    # fallback to sibling source docs when running locally
    candidates = [
        path,
        Path(__file__).resolve().parents[4] / "source" / "docs" / "cli-usage.md",
        Path("/cli_docs/cli-usage.md"),
    ]
    for p in candidates:
        if p and p.is_file():
            return p.read_text(encoding="utf-8")
    raise HTTPException(404, "cli-usage.md 未找到，请先生成 source/docs/cli-usage.md")
