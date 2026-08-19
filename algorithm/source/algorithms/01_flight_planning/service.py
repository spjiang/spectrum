"""航线规划：摄影测量 GSD / 重叠覆盖。"""
from __future__ import annotations

from fastapi import UploadFile

from common.impl import parse_params, write_json
from common.io import load_text_or_json, new_job_dir, save_upload
from common.response import err_response, ok_response
from common.rs.photogrammetry import plan_lawnmower

ALGORITHM_ID = "01_flight_planning"
TITLE = "航线规划与覆盖优化"
IMPLEMENTED = True
LEVEL = "L0前"


def _extract(geo: dict):
    if geo.get("type") == "FeatureCollection":
        feats = geo.get("features") or []
        if not feats:
            return None
        return feats[0].get("geometry") or {}, feats[0].get("properties") or {}
    if geo.get("type") == "Feature":
        return geo.get("geometry") or {}, geo.get("properties") or {}
    if geo.get("type") in {"Polygon", "MultiPolygon"}:
        return geo, {}
    return None


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """GSD=H·像元/焦距；航带间距=幅宽·(1-旁向重叠)。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    geo = load_text_or_json(path)
    parsed = _extract(geo) if isinstance(geo, dict) else None
    if parsed is None:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="需要测区 GeoJSON（Polygon）")
    geom, props = parsed
    if geom.get("type") == "Polygon":
        ring = geom["coordinates"][0]
    elif geom.get("type") == "MultiPolygon":
        ring = geom["coordinates"][0][0]
    else:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message="几何类型须为 Polygon")
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    gsd_hint = float(props.get("gsd_m", 0.1))
    altitude = float(params.get("alt_m", props.get("alt_m", 120)))
    focal_mm = float(params.get("focal_mm", 8.0))
    pixel_um = float(params.get("pixel_um", 5.5))
    n_cols = int(params.get("n_cols", 1024))
    n_rows = int(params.get("n_rows", 1024))
    # 若未给相机而给了 GSD，反推等效焦距
    from common.rs.photogrammetry import gsd_m

    if abs(gsd_m(altitude, pixel_um, focal_mm) - gsd_hint) / max(gsd_hint, 1e-6) > 0.5 and gsd_hint > 0:
        # 用目标 GSD 反解焦距：f = H * pixel / GSD
        focal_mm = altitude * (pixel_um * 1e-3) / gsd_hint
    plan = plan_lawnmower(
        min(xs),
        min(ys),
        max(xs),
        max(ys),
        altitude_m=altitude,
        overlap=float(props.get("overlap", params.get("overlap", 0.7))),
        sidelap=float(props.get("sidelap", params.get("sidelap", 0.6))),
        focal_mm=focal_mm,
        pixel_um=pixel_um,
        n_cols=n_cols,
        n_rows=n_rows,
        cruise_speed_m_s=float(params.get("cruise_speed_m_s", 8.0)),
    )
    fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"seq": i, "line": wp["line"]},
                "geometry": {"type": "Point", "coordinates": [wp["lon"], wp["lat"]]},
            }
            for i, wp in enumerate(plan["waypoints"])
        ],
    }
    summary = {k: v for k, v in plan.items() if k != "waypoints"}
    mission_path = job / "mission.json"
    wp_path = job / "waypoints.geojson"
    write_json(mission_path, {**summary, "waypoints": plan["waypoints"]})
    write_json(wp_path, fc)
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"摄影测量航线：{plan['n_lines']} 带 / {plan['n_waypoints']} 航点，GSD={plan['gsd_m']:.4f} m",
        data=summary,
        files={"mission_json": str(mission_path.resolve()), "waypoints_geojson": str(wp_path.resolve())},
    )
