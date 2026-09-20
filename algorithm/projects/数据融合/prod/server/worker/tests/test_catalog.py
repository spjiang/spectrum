from pathlib import Path

import pytest

from ms_mosaic.catalog import Shot, group_shots, parse_filename, scan_directory
from ms_mosaic.local_defaults import INPUT as REAL


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


def test_usable_shots_respects_agl_tilt_and_whiteboard():
    from ms_mosaic.catalog import Pos, Shot
    from ms_mosaic.scene import usable_shots

    def shot(idx, *, role="D", agl=100.0, pitch=-90.0, has_pos=True):
        pos = (
            Pos(lon=100.0, lat=24.0, alt_m=1800.0, yaw_deg=0.0, pitch_deg=pitch, roll_deg=0.0, agl_m=agl)
            if has_pos
            else None
        )
        return Shot(index=idx, pos=pos, role=role)

    shots = {
        1: shot(1, role="W"),
        2: shot(2, agl=1.0),
        3: shot(3, pitch=0.0),
        4: shot(4, has_pos=False),
        5: shot(5),
    }
    keep, reasons = usable_shots(shots)
    assert set(keep) == {5}
    assert reasons["white_panel"] == 1
    assert reasons["low_agl"] == 1
    assert reasons["high_tilt"] == 1
    assert reasons["no_pos"] == 1

    keep_w, _ = usable_shots(shots, drop_white_panel=False, min_agl_m=0.0, max_tilt_deg=180.0)
    assert 1 in keep_w
    assert 5 in keep_w
    assert 4 not in keep_w
