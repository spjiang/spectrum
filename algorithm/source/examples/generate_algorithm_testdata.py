#!/usr/bin/env python3
"""为每个算法目录生成业界格式 testdata（GeoTIFF / GeoJSON / CSV）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.catalog import ALGORITHMS  # noqa: E402
from common.io import save_geotiff  # noqa: E402

RNG = np.random.default_rng(42)
H, W, B = 16, 16, 8


def make_reflectance_cube() -> np.ndarray:
    cube = RNG.uniform(0.05, 0.25, size=(H, W, B)).astype(np.float32)
    cube[:, : W // 2, 3] = RNG.uniform(0.40, 0.70, size=(H, W // 2))
    cube[:, : W // 2, 2] = RNG.uniform(0.05, 0.15, size=(H, W // 2))
    cube[:, : W // 2, 4] = RNG.uniform(0.20, 0.35, size=(H, W // 2))
    cube[:, : W // 2, 1] = RNG.uniform(0.08, 0.18, size=(H, W // 2))
    cube[:, : W // 2, 0] = RNG.uniform(0.04, 0.10, size=(H, W // 2))
    return cube


def make_detect_cube(cube: np.ndarray) -> np.ndarray:
    """在植被半区写入低 NDVI 斑块，供检测算法演示。"""
    c = cube.copy()
    c[4:10, 2:8, 3] = 0.08  # 压低 NIR
    c[4:10, 2:8, 2] = 0.22  # 抬高 RED → NDVI 变低
    return c


def make_dn_cube(cube: np.ndarray) -> np.ndarray:
    return (cube * 1000.0).astype(np.float32)


def make_gt() -> np.ndarray:
    gt = np.zeros((H, W), dtype=np.int32)
    gt[:, : W // 2] = 1
    gt[:, W // 2 :] = 2
    return gt


def make_index_map(cube: np.ndarray) -> np.ndarray:
    red, nir = cube[:, :, 2], cube[:, :, 3]
    return ((nir - red) / (nir + red + 1e-12)).astype(np.float32)


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_files(outdir: Path, files: dict) -> list[str]:
    names: list[str] = []
    for name, value in files.items():
        path = outdir / name
        if isinstance(value, np.ndarray):
            if not name.endswith((".tif", ".tiff")):
                raise ValueError(f"栅格请用 .tif: {name}")
            save_geotiff(value, path)
        elif isinstance(value, (dict, list)):
            if not name.endswith((".json", ".geojson")):
                raise ValueError(f"对象请用 .json/.geojson: {name}")
            write_json(path, value)
        elif isinstance(value, str):
            path.write_text(value, encoding="utf-8")
        else:
            raise TypeError(type(value))
        names.append(name)
    return names


def fixture_spec(algo_id: str, cube, dn, gt, index) -> dict:
    aoi = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "demo_field", "gsd_m": 0.1, "overlap": 0.7, "sidelap": 0.6},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[114.06, 22.54], [114.061, 22.54], [114.061, 22.541], [114.06, 22.541], [114.06, 22.54]]],
                },
            }
        ],
    }
    base = {
        "files": {"input.tif": cube},
        "params": {},
        "note": "主输入 input.tif 为模拟反射率 GeoTIFF（多波段）。",
        "curl_extra": "",
    }
    specs = {
        "01_flight_planning": {
            "files": {"input.geojson": aoi},
            "params": {"cruise_speed_m_s": 8},
            "note": "测区 GeoJSON（业界常用矢量交换格式）。",
        },
        "02_sync_timestamp": {
            "files": {
                "input.json": {
                    "hsi_frames": [{"id": 1, "ts": 1000.01}, {"id": 2, "ts": 1000.05}],
                    "rgb_frames": [{"id": "a", "ts": 1000.02}],
                    "pos": [{"ts": 1000.00, "lat": 22.5, "lon": 114.0}],
                }
            },
            "params": {},
            "note": "多传感器时间戳 JSON（工程元数据）。",
        },
        "03_pos_solution": {
            "files": {
                "input.csv": (
                    "time,lat,lon,alt,roll,pitch,yaw\n"
                    "0.0,22.5401,114.0601,120.0,0.1,-0.2,90.0\n"
                    "0.1,22.5402,114.0602,120.1,0.1,-0.2,90.1\n"
                )
            },
            "params": {},
            "note": "GPS/IMU 轨迹 CSV（POS 常用落盘形态之一）。",
        },
        "04_flight_qc": {"files": {"input.tif": dn}, "params": {"max_saturated_ratio": 0.01}, "note": "原始 DN GeoTIFF。"},
        "05_cloud_shadow": {"files": {"input.tif": cube}, "params": {}, "note": "反射率 GeoTIFF。"},
        "06_dark_current": {
            "files": {"input.tif": dn, "file2.tif": RNG.uniform(0, 5, size=(H, W, B)).astype(np.float32)},
            "params": {},
            "note": "input=DN GeoTIFF；file2=暗电流参考 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "07_bad_pixel": {
            "files": {
                "input.tif": dn,
                "file2.json": {"bad_cols": [2, 7], "bad_pixels": [[1, 1], [3, 5]]},
            },
            "params": {},
            "note": "input=DN GeoTIFF；file2=坏像元表 JSON。",
            "curl_extra": ' -F "file2=@./testdata/file2.json"',
        },
        "08_destriping": {"files": {"input.tif": dn}, "params": {}, "note": "DN GeoTIFF。"},
        "09_smile_keystone": {"files": {"input.tif": dn}, "params": {}, "note": "DN/辐亮度 GeoTIFF。"},
        "10_radiance_calibration": {
            "files": {"input.tif": dn},
            "params": {"gain": 0.01, "offset": 0.0},
            "note": "DN GeoTIFF。",
        },
        "11_relative_radiometric": {
            "files": {"input.tif": cube, "file2.tif": np.clip(cube * 1.1, 0, 1).astype(np.float32)},
            "params": {},
            "note": "两景反射率 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "12_panel_reflectance": {
            "files": {"input.tif": dn},
            "params": {"scale": 0.001},
            "note": "DN GeoTIFF；输出反射率 GeoTIFF。",
        },
        "13_atmospheric_correction": {"files": {"input.tif": dn}, "params": {}, "note": "辐亮度/DN GeoTIFF。"},
        "14_brdf_correction": {
            "files": {"input.tif": cube},
            "params": {"solar_zenith": 30, "view_zenith": 10},
            "note": "反射率 GeoTIFF。",
        },
        "15_geo_locate": {
            "files": {
                "input.tif": cube,
                "file2.json": {"pos": {"lat": 22.54, "lon": 114.06, "alt": 120, "yaw": 90}},
            },
            "params": {},
            "note": "影像 GeoTIFF + POS JSON。",
            "curl_extra": ' -F "file2=@./testdata/file2.json"',
        },
        "16_orthorectify": {
            "files": {"input.tif": cube, "file2.tif": RNG.uniform(10, 50, size=(H, W)).astype(np.float32)},
            "params": {},
            "note": "input=影像 GeoTIFF；file2=DEM GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "17_mosaic": {
            "files": {
                "input.tif": cube[:, : W // 2 + 1, :],
                "file2.tif": cube[:, W // 2 - 1 :, :],
            },
            "params": {},
            "note": "两条航带 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "18_color_balance": {"files": {"input.tif": cube}, "params": {}, "note": "镶嵌 GeoTIFF。"},
        "19_multi_source_register": {
            "files": {
                "input.tif": cube,
                "file2.tif": np.stack([cube[:, :, 2], cube[:, :, 1], cube[:, :, 0]], axis=-1),
            },
            "params": {},
            "note": "input=HSI GeoTIFF；file2=RGB GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "20_bad_band_remove": {
            "files": {"input.tif": cube},
            "params": {"drop_bands": [0, 5]},
            "note": "反射率 GeoTIFF。",
        },
        "21_savgol_smooth": {
            "files": {"input.tif": cube},
            "params": {"window_length": 5, "polyorder": 2},
            "note": "反射率 GeoTIFF。",
        },
        "22_normalize": {
            "files": {"input.tif": cube},
            "params": {"method": "zscore"},
            "note": "反射率 GeoTIFF。",
        },
        "23_pca": {
            "files": {"input.tif": cube},
            "params": {"n_components": 3},
            "note": "反射率 GeoTIFF。",
        },
        "24_band_select": {
            "files": {"input.tif": cube, "file2.tif": gt},
            "params": {},
            "note": "Cube + 标签 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "25_superpixel": {"files": {"input.tif": cube}, "params": {"n_segments": 20}, "note": "反射率 GeoTIFF。"},
        "26_patch_build": {
            "files": {"input.tif": cube, "file2.tif": gt},
            "params": {"patch_size": 5},
            "note": "Cube + 标签 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "27_ndvi": {
            "files": {"input.tif": cube},
            "params": {"red_band": 2, "nir_band": 3},
            "note": "反射率 GeoTIFF；输出 NDVI GeoTIFF。",
        },
        "28_ndre": {
            "files": {"input.tif": cube},
            "params": {"re_band": 4, "nir_band": 3},
            "note": "反射率 GeoTIFF；输出 NDRE GeoTIFF。",
        },
        "29_evi_savi": {
            "files": {"input.tif": cube},
            "params": {"blue_band": 0, "red_band": 2, "nir_band": 3},
            "note": "反射率 GeoTIFF。",
        },
        "30_ndmi_ndwi": {
            "files": {"input.tif": cube},
            "params": {"green_band": 1, "nir_band": 3, "swir_band": 5},
            "note": "反射率 GeoTIFF。",
        },
        "31_red_edge_params": {"files": {"input.tif": cube}, "params": {}, "note": "反射率 GeoTIFF。"},
        "32_regression_inversion": {
            "files": {
                "input.tif": cube,
                "file2.tif": RNG.uniform(20, 60, size=(H, W)).astype(np.float32),
            },
            "params": {},
            "note": "光谱 GeoTIFF + 真值 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "33_physical_inversion": {"files": {"input.tif": cube}, "params": {}, "note": "反射率 GeoTIFF。"},
        "34_svm_rf_classify": {
            "files": {"input.tif": cube, "file2.tif": gt},
            "params": {"test_size": 0.3, "kernel": "rbf"},
            "note": "Cube GeoTIFF + 标签 GeoTIFF；输出分类 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "35_spectral_matching": {
            "files": {
                "input.tif": cube,
                "file2.csv": (
                    "band," + ",".join(f"e{i}" for i in range(2)) + "\n"
                    + "\n".join(
                        f"{b}," + ",".join(f"{float(cube[0, 0 if i == 0 else W - 1, b]):.6f}" for i in range(2))
                        for b in range(B)
                    )
                    + "\n"
                ),
            },
            "params": {},
            "note": "Cube GeoTIFF；file2 为端元光谱库 CSV（业界常见）。",
            "curl_extra": ' -F "file2=@./testdata/file2.csv"',
        },
        "36_cnn1d_classify": {
            "files": {"input.tif": cube, "file2.tif": gt},
            "params": {},
            "note": "Cube + 标签 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "37_cnn3d_classify": {
            "files": {"input.tif": cube, "file2.tif": gt},
            "params": {"patch_size": 5},
            "note": "Cube + 标签 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "38_transformer_classify": {
            "files": {"input.tif": cube, "file2.tif": gt},
            "params": {},
            "note": "Cube + 标签 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "39_few_shot_classify": {
            "files": {"input.tif": cube, "file2.tif": gt},
            "params": {"shots": 5},
            "note": "Cube + 标签 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "40_detect_segment": {
            "files": {
                "input.tif": make_detect_cube(cube),
                "file2.geojson": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {"label": "weed"},
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [[[114.0602, 22.5402], [114.0604, 22.5402], [114.0604, 22.5404], [114.0602, 22.5404], [114.0602, 22.5402]]],
                            },
                        }
                    ],
                },
            },
            "params": {"red_band": 2, "nir_band": 3, "percentile": 20, "min_pixels": 4},
            "note": "影像 GeoTIFF（含低 NDVI 斑块）+ 标注 GeoJSON。",
            "curl_extra": ' -F "file2=@./testdata/file2.geojson"',
        },
        "41_unmixing": {
            "files": {
                "input.tif": cube,
                "file2.csv": (
                    "band,endmember0,endmember1,endmember2\n"
                    + "\n".join(
                        f"{b},{float(cube.mean(axis=(0,1))[b]):.6f},{float(cube[0,0,b]):.6f},{float(cube[-1,-1,b]):.6f}"
                        for b in range(B)
                    )
                    + "\n"
                ),
            },
            "params": {},
            "note": "混合像元 GeoTIFF + 端元光谱 CSV。",
            "curl_extra": ' -F "file2=@./testdata/file2.csv"',
        },
        "42_anomaly_detect": {"files": {"input.tif": cube}, "params": {}, "note": "单时相 GeoTIFF。"},
        "43_change_detect": {
            "files": {
                "input.tif": cube,
                "file2.tif": np.clip(cube * 0.85 + 0.05, 0, 1).astype(np.float32),
            },
            "params": {},
            "note": "T1/T2 两景 GeoTIFF。",
            "curl_extra": ' -F "file2=@./testdata/file2.tif"',
        },
        "44_postprocess_smooth": {
            "files": {"input.tif": gt},
            "params": {"min_pixels": 4},
            "note": "分类标签 GeoTIFF。",
        },
        "45_parcel_zonal_stats": {
            "files": {
                "input.tif": index,
                "file2.geojson": aoi,
            },
            "params": {"mode": "continuous", "roi": [0, H // 2, 0, W // 2]},
            "note": "指数 GeoTIFF + 地块 GeoJSON。",
            "curl_extra": ' -F "file2=@./testdata/file2.geojson"',
        },
    }
    return specs.get(algo_id, base)


def update_algo_readme(algo_id: str, primary: str, curl_extra: str, params: dict) -> None:
    algo_readme = ROOT / "algorithms" / algo_id / "README.md"
    if not algo_readme.exists():
        return
    orig = algo_readme.read_text(encoding="utf-8")
    params_part = f" -F 'params={json.dumps(params, ensure_ascii=False)}'" if params else ""
    curl_file = f'-F "file=@./testdata/{primary}"'
    block = (
        f"## 测试数据\n\n"
        f"本目录 `testdata/` 使用**业界常用格式**（GeoTIFF / GeoJSON / CSV），说明见 `testdata/README.md`。\n\n"
        f"```bash\n"
        f"curl -X POST \"http://127.0.0.1:28800/api/v1/{algo_id}/run\" \\\n"
        f"  {curl_file}{curl_extra}{params_part}\n"
        f"```\n"
    )
    head = orig
    for marker in ("## 测试数据", "## 调用示例", "## 启动"):
        if marker in head:
            head = head.split(marker)[0]
    head = head.rstrip() + "\n\n"
    start = (
        "## 启动（整个算法服务）\n\n"
        "```bash\n"
        "cd algorithm/source\n"
        "python run.py\n"
        "```\n\n"
    )
    if "## 输入 / 输出" in orig:
        tail = "\n" + "## 输入 / 输出" + orig.split("## 输入 / 输出", 1)[1]
    else:
        tail = (
            "\n## 输入 / 输出\n\n"
            "- **输入**: 业界格式文件（优先 GeoTIFF）；`params` 为 JSON 字符串\n"
            "- **输出**: JSON；栅格产物为 GeoTIFF，路径在 `files`\n"
        )
    algo_readme.write_text(head + start + block + tail, encoding="utf-8")


def main() -> None:
    cube = make_reflectance_cube()
    dn = make_dn_cube(cube)
    gt = make_gt()
    index = make_index_map(cube)

    for meta in ALGORITHMS:
        algo_id = meta["id"]
        outdir = ROOT / "algorithms" / algo_id / "testdata"
        outdir.mkdir(parents=True, exist_ok=True)
        for p in outdir.iterdir():
            if p.is_file():
                p.unlink()

        spec = fixture_spec(algo_id, cube, dn, gt, index)
        names = save_files(outdir, spec["files"])
        params = spec.get("params") or {}
        write_json(outdir / "params.json", params)

        primary = names[0]
        for cand in ("input.tif", "input.geojson", "input.json", "input.csv"):
            if cand in names:
                primary = cand
                break

        curl_extra = spec.get("curl_extra", "")
        rows = [f"| `{primary}` | 主输入（API 字段 `file`） |"]
        for n in names:
            if n == primary:
                continue
            field = "file2" if n.startswith("file2") else "辅助"
            rows.append(f"| `{n}` | 附加输入（字段 `{field}`） |")
        rows.append("| `params.json` | 推荐请求参数 |")

        readme = (
            f"# testdata · {meta['title']}\n\n"
            f"{spec.get('note', '')}\n\n"
            f"**格式说明**：栅格为 GeoTIFF（`.tif`）；地块/AOI 为 GeoJSON；POS 为 CSV。\n\n"
            f"## 文件\n\n| 文件 | 说明 |\n|------|------|\n"
            + "\n".join(rows)
            + "\n\n## 调用示例\n\n```bash\n"
            f"curl -X POST \"http://127.0.0.1:28800/api/v1/{algo_id}/run\" \\\n"
            f"  -F \"file=@./testdata/{primary}\"{curl_extra}"
            + (f" -F 'params={json.dumps(params, ensure_ascii=False)}'" if params else "")
            + "\n```\n"
        )
        (outdir / "README.md").write_text(readme, encoding="utf-8")
        update_algo_readme(algo_id, primary, curl_extra, params)
        print("testdata ->", algo_id, names)


if __name__ == "__main__":
    main()
