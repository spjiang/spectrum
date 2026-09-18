"""质量报告数据组装：GPS 分箱、航线切割、连通序列。"""

import numpy as np

from ms_mosaic.qa import (
    connected_sequences,
    crs_label,
    format_gps_extrema_line,
    gps_extrema,
    gps_histogram,
    split_strips,
    truncate_rows,
)


def test_crs_label_matches_limapper():
    assert crs_label("EPSG:32650") == "[EPSG::32650] UTM 50N (WGS84), egm_none"
    assert crs_label("EPSG:32647") == "[EPSG::32647] UTM 47N (WGS84), egm_none"


def test_gps_histogram_percentages_sum_to_100():
    rows = [
        {"error": 1.0, "dx": 0.5, "dy": -0.5, "dz": 5.0},
        {"error": 3.0, "dx": 2.5, "dy": 0.2, "dz": 11.0},
        {"error": 15.0, "dx": 0.1, "dy": -1.5, "dz": 14.5},
        {"error": 0.4, "dx": -0.2, "dy": 0.1, "dz": 0.3},
    ]
    hist = gps_histogram(rows)
    assert hist[0]["label"].startswith("[-6")
    for key in ("error", "dx", "dy", "dz"):
        total = sum(b[key] for b in hist)
        assert abs(total - 100.0) < 1e-6


def test_gps_extrema_picks_min_abs_axis_and_max_3d():
    rows = [
        {"index": 1, "name": "a.tif", "gps0": [0, 0, 0], "gps1": [0.01, 2.0, 3.0],
         "error": 3.606, "dx": 0.01, "dy": 2.0, "dz": 3.0},
        {"index": 2, "name": "b.tif", "gps0": [0, 0, 0], "gps1": [5.0, 0.02, 1.0],
         "error": 5.099, "dx": 5.0, "dy": 0.02, "dz": 1.0},
        {"index": 3, "name": "c.tif", "gps0": [0, 0, 0], "gps1": [1.0, 1.0, 0.01],
         "error": 1.415, "dx": 1.0, "dy": 1.0, "dz": 0.01},
    ]
    ext = gps_extrema(rows)
    assert ext["min_x"]["index"] == 1
    assert ext["min_y"]["index"] == 2
    assert ext["min_z"]["index"] == 3
    assert ext["min_err"]["index"] == 3
    assert ext["max_x"]["index"] == 2
    assert ext["max_err"]["index"] == 2
    line = format_gps_extrema_line(ext["min_x"])
    assert "序号 = 1" in line and "a.tif" in line and "dx =" in line


def test_split_strips_breaks_on_turn_and_gap():
    # 两条平行航线，各 4 点，中间大转向 + 大间距
    xs = [0, 10, 20, 30, 30, 20, 10, 0]
    ys = [0, 0, 0, 0, 80, 80, 80, 80]
    yaws = [90, 90, 90, 90, -90, -90, -90, -90]
    centers = np.column_stack([xs, ys, np.zeros(8)])
    strips = split_strips(list(range(8)), centers, np.array(yaws, float))
    assert len(strips) == 2
    assert strips[0] == [0, 1, 2, 3]
    assert strips[1] == [4, 5, 6, 7]


def test_connected_sequences_orders_large_component_first():
    from ms_mosaic.matching import PairMatches

    matches = [
        PairMatches(0, 1, np.array([[0, 0]]), "essential"),
        PairMatches(1, 2, np.array([[0, 0]]), "essential"),
        PairMatches(4, 5, np.array([[0, 0]]), "essential"),
    ]
    seqs = connected_sequences(matches, [0, 1, 2, 3, 4, 5])
    assert seqs[0] == [0, 1, 2]
    assert [3] in seqs
    assert [4, 5] in seqs or seqs[1] == [4, 5]


def test_truncate_rows_keeps_head_and_tail():
    rows = list(range(40))
    out = truncate_rows(rows, head=5, tail=3)
    assert out[0] == 0 and out[4] == 4
    assert out[5] is None
    assert out[-3:] == [37, 38, 39]
