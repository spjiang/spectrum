from pathlib import Path

import pytest
import rasterio

from ms_mosaic.pipeline import run_mosaic

REAL = Path(
    "/Users/jiangshengping/wwwroot/shenzhen/spectrum/algorithm/projects/数据融合"
    "/prod/docs/需求/测试正式数据/MAX_20251017/MAX_20251017_001"
)


def test_refuses_to_write_into_input_dir(tmp_path: Path):
    inp = tmp_path / "MAX_20251017_001"
    inp.mkdir()
    with pytest.raises(ValueError, match="禁止写入输入目录"):
        run_mosaic(inp, inp)
    with pytest.raises(ValueError, match="禁止写入输入目录"):
        run_mosaic(inp, inp / "mosaics")


@pytest.mark.skipif(not REAL.exists(), reason="no MAX_20251017_001 dataset")
def test_run_mosaic_on_few_real_shots(tmp_path: Path):
    before = {p.name for p in REAL.iterdir()}
    result = run_mosaic(REAL, tmp_path, max_frames=3, max_index=20)
    after = {p.name for p in REAL.iterdir()}
    assert after == before
    rgb = Path(result["files"]["rgb"])
    assert rgb.exists()
    assert REAL not in rgb.resolve().parents
    with rasterio.open(rgb) as ds:
        assert ds.crs.to_string() == "EPSG:32647"
        assert ds.count == 3
        assert ds.width > 100
        assert ds.height > 100
        assert float(ds.read(1).max()) > 0
    report = Path(result["files"]["report_json"])
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "EPSG:32647" in text
    assert "n_shots" in text
    green = Path(result["files"]["bands"]["550nm"])
    assert green.exists()
    with rasterio.open(green) as ds:
        assert ds.count == 1
        assert ds.crs.to_string() == "EPSG:32647"
