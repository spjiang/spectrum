from pathlib import Path

import pytest

from ms_mosaic.catalog import Shot, group_shots, parse_filename, scan_directory

REAL = Path(
    "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合"
    "/prod/docs/需求/测试正式数据/MAX_20251017/MAX_20251017_001"
)


def test_parse_color_jpg():
    rec = parse_filename(Path("MAX_0003_Color_D.jpg"))
    assert rec.index == 3
    assert rec.band == "Color"
    assert rec.role == "D"
    assert rec.kind == "rgb"


def test_parse_green_tif():
    rec = parse_filename(Path("MAX_0010_550nm_D.tif"))
    assert rec.index == 10
    assert rec.band == "550nm"
    assert rec.wavelength_nm == 550
    assert rec.role == "D"
    assert rec.kind == "ms"


def test_parse_white_panel():
    rec = parse_filename(Path("MAX_0002_450nm_W.tif"))
    assert rec.role == "W"
    assert rec.kind == "ms"


def test_parse_ignores_zip():
    assert parse_filename(Path("MAX_0010_Color_D.zip")) is None


def test_group_shots_binds_rgb_and_bands():
    files = [
        parse_filename(Path("MAX_0003_Color_D.jpg")),
        parse_filename(Path("MAX_0003_450nm_D.tif")),
        parse_filename(Path("MAX_0003_550nm_D.tif")),
        parse_filename(Path("MAX_0004_Color_D.jpg")),
    ]
    shots = group_shots(files)
    assert set(shots) == {3, 4}
    assert shots[3].rgb.path.name == "MAX_0003_Color_D.jpg"
    assert "550nm" in shots[3].ms
    assert shots[4].ms == {}


@pytest.mark.skipif(not REAL.exists(), reason="no MAX_20251017_001 dataset")
def test_scan_real_dir_reads_pos_and_uuid():
    shots = scan_directory(REAL, max_index=3)
    assert 1 in shots
    assert shots[1].rgb is not None
    assert shots[1].pos is not None
    assert shots[1].pos.lon > 100
    assert shots[1].pos.lat > 23
    shot3 = shots[3]
    assert shot3.pos is not None
    assert shot3.pos.agl_m > 50
    assert abs(shot3.pos.yaw_deg - 80.6) < 0.5
    assert "550nm" in shot3.ms
    assert shot3.capture_uuid
    assert shot3.ms["450nm"].capture_uuid == shot3.capture_uuid
