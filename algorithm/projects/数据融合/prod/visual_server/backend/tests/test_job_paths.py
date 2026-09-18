from pathlib import Path

import pytest
from fastapi import HTTPException

from app.config import Settings
from app.services.paths import validate_paths

STAGES = ["S0_io", "S1_catalog", "S2_at", "S3_dense", "S4_dsm", "S5_ortho", "S6_report"]


def test_stages_cover_pipeline():
    assert "S5_ortho" in STAGES
    assert STAGES[0] == "S0_io"


def test_validate_paths_rejects_nested_out(tmp_path: Path):
    settings = Settings(data_roots=str(tmp_path))
    inp = tmp_path / "in"
    out = inp / "out"
    inp.mkdir()
    out.mkdir()
    with pytest.raises(HTTPException):
        validate_paths(settings, str(inp), str(out))


def test_validate_paths_ok(tmp_path: Path):
    settings = Settings(data_roots=str(tmp_path))
    inp = tmp_path / "in"
    out = tmp_path / "out"
    inp.mkdir()
    out.mkdir()
    a, b = validate_paths(settings, str(inp), str(out))
    assert a == inp.resolve()
    assert b == out.resolve()
