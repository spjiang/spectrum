"""控制台 API：元数据、文件、预览、一键 testdata 运行。"""
from __future__ import annotations

import importlib
import io
import json
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from starlette.datastructures import Headers

from common.catalog import ALGORITHMS
from common.config import OUTPUT_DIR
from common.console_catalog import get_console_algorithm, list_console_algorithms
from common.console_params import get_service_params
from common.console_paths import (
    PRIMARY_NAMES,
    SECONDARY_NAMES,
    find_named,
    resolve_output,
    resolve_testdata,
    testdata_dir,
)
from common.console_preview import raster_meta, raster_png_bytes, spectrum_at

router = APIRouter(prefix="/api/v1/console", tags=["console"])

VALID_IDS = {a["id"] for a in ALGORITHMS}


def _need_id(algorithm_id: str) -> None:
    if algorithm_id not in VALID_IDS:
        raise HTTPException(404, f"未知算法 {algorithm_id}")


def _merge_console_params(
    algorithm_id: str,
    sample_params: dict,
    submitted_params: dict,
) -> dict:
    """合并示例默认值与表单覆盖值，并只保留服务真实读取的参数。"""
    allowed = set(get_service_params(algorithm_id))
    merged = {key: value for key, value in sample_params.items() if key in allowed}
    merged.update(
        {key: value for key, value in submitted_params.items() if key in allowed}
    )
    return merged


def _as_upload(path: Path) -> UploadFile:
    """把磁盘文件包装成 UploadFile，供 service.run 使用。"""
    data = path.read_bytes()
    return UploadFile(
        file=io.BytesIO(data),
        filename=path.name,
        headers=Headers({"content-type": "application/octet-stream"}),
    )


def _guess_preview_mode(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ("mask", "class", "pred", "label", "superpixel")):
        return "class"
    if any(k in n for k in ("ndvi", "ndre", "score", "lai", "cab", "inversion", "magnitude", "chi2", "abundance")):
        return "index"
    return "auto"


def files_to_http(files: dict[str, str]) -> dict[str, dict]:
    """把磁盘路径转成浏览器可访问的 URL。"""
    out: dict[str, dict] = {}
    root = OUTPUT_DIR.resolve()
    for key, abs_path in files.items():
        p = Path(abs_path).resolve()
        suffix = p.suffix.lower()
        job = p.parent.name
        name = p.name
        try:
            p.relative_to(root)
        except ValueError:
            out[key] = {"url": None, "vis": "none", "name": name, "error": "不在 outputs 白名单"}
            continue
        if suffix == ".png":
            url = f"/api/v1/console/outputs/{job}/{name}"
            vis = "png"
        elif suffix in {".tif", ".tiff"}:
            mode = _guess_preview_mode(name)
            url = f"/api/v1/console/preview/raster?src=outputs&job={job}&name={name}&mode={mode}"
            vis = {"class": "raster_class", "index": "raster_index"}.get(mode, "raster_falsecolor")
        elif suffix in {".geojson"}:
            url = f"/api/v1/console/file?src=outputs&job={job}&name={name}"
            vis = "geojson_map"
        elif suffix == ".csv":
            url = f"/api/v1/console/file?src=outputs&job={job}&name={name}"
            vis = "csv_track" if "pos" in name else "csv_table"
        elif suffix in {".json"}:
            url = f"/api/v1/console/file?src=outputs&job={job}&name={name}"
            vis = "geojson_map" if "geojson" in name else "json_table"
        else:
            url = f"/api/v1/console/file?src=outputs&job={job}&name={name}"
            vis = "none"
        out[key] = {"url": url, "vis": vis, "name": name, "job": job}
    return out


def testdata_http(algorithm_id: str, filename: str | None) -> dict | None:
    """testdata 文件的可视化 URL。"""
    if not filename:
        return None
    suffix = Path(filename).suffix.lower()
    if suffix in {".tif", ".tiff"}:
        url = (
            f"/api/v1/console/preview/raster?src=testdata&algorithm_id={algorithm_id}"
            f"&name={filename}&mode=auto"
        )
        vis = "raster_falsecolor"
    else:
        url = f"/api/v1/console/file?src=testdata&algorithm_id={algorithm_id}&name={filename}"
        vis = {
            ".geojson": "geojson_map",
            ".csv": "csv_track" if algorithm_id.startswith("03") else ("csv_spectrum" if algorithm_id in {"35_spectral_matching", "41_unmixing"} else "csv_table"),
            ".json": "json_table",
        }.get(suffix, "none")
    return {"url": url, "vis": vis, "name": filename}


@router.get("/algorithms")
def console_list():
    """左侧目录 + 首页用的算法列表。"""
    items = list_console_algorithms()
    for it in items:
        td = it.get("testdata") or {}
        it["testdata_http"] = {
            "file": testdata_http(it["id"], td.get("file")),
            "file2": testdata_http(it["id"], td.get("file2")),
        }
    return {"count": len(items), "algorithms": items}


@router.get("/algorithms/{algorithm_id}")
def console_one(algorithm_id: str):
    """单个算法详情（介绍、场景、字段）。"""
    _need_id(algorithm_id)
    item = get_console_algorithm(algorithm_id)
    if item is None:
        raise HTTPException(404, "未找到")
    td = item.get("testdata") or {}
    item["testdata_http"] = {
        "file": testdata_http(algorithm_id, td.get("file")),
        "file2": testdata_http(algorithm_id, td.get("file2")),
    }
    return item


@router.get("/health")
def console_health():
    """控制台依赖的算法服务是否可用。"""
    return {"status": "ok", "algorithms": len(VALID_IDS)}


def _resolve_src(src: str, algorithm_id: str | None, job: str | None, name: str) -> Path:
    if src == "testdata":
        if not algorithm_id:
            raise HTTPException(400, "testdata 需要 algorithm_id")
        _need_id(algorithm_id)
        try:
            return resolve_testdata(algorithm_id, name)
        except (ValueError, FileNotFoundError) as exc:
            raise HTTPException(400, str(exc)) from exc
    if src == "outputs":
        if not job:
            raise HTTPException(400, "outputs 需要 job")
        try:
            return resolve_output(job, name)
        except (ValueError, FileNotFoundError) as exc:
            raise HTTPException(400, str(exc)) from exc
    raise HTTPException(400, "src 只能是 testdata 或 outputs")


@router.get("/file")
def console_file(
    src: str = Query(...),
    name: str = Query(...),
    algorithm_id: str | None = None,
    job: str | None = None,
):
    """白名单内原样返回文件（JSON/CSV/GeoJSON/PNG）。"""
    path = _resolve_src(src, algorithm_id, job, name)
    media = {
        ".png": "image/png",
        ".json": "application/json",
        ".geojson": "application/geo+json",
        ".csv": "text/csv",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
        ".npz": "application/octet-stream",
    }.get(path.suffix.lower(), "application/octet-stream")
    return FileResponse(path, media_type=media, filename=path.name)


@router.get("/preview/raster")
def console_preview_raster(
    src: str = Query(...),
    name: str = Query(...),
    algorithm_id: str | None = None,
    job: str | None = None,
    mode: str = "auto",
):
    """GeoTIFF 渲染为 PNG。"""
    path = _resolve_src(src, algorithm_id, job, name)
    try:
        png, meta = raster_png_bytes(path, mode=mode)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, f"预览失败: {exc}") from exc
    headers = {
        "X-Raster-Height": str(meta["height"]),
        "X-Raster-Width": str(meta["width"]),
        "X-Raster-Bands": str(meta["bands"]),
        "X-Raster-Mode": str(meta["mode"]),
    }
    return Response(content=png, media_type="image/png", headers=headers)


@router.get("/preview/meta")
def console_preview_meta(
    src: str = Query(...),
    name: str = Query(...),
    algorithm_id: str | None = None,
    job: str | None = None,
):
    """栅格宽高波段。"""
    path = _resolve_src(src, algorithm_id, job, name)
    try:
        return raster_meta(path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, str(exc)) from exc


@router.get("/preview/spectrum")
def console_spectrum(
    src: str = Query(...),
    name: str = Query(...),
    row: int = Query(0),
    col: int = Query(0),
    algorithm_id: str | None = None,
    job: str | None = None,
):
    """点选像元光谱。"""
    path = _resolve_src(src, algorithm_id, job, name)
    try:
        return spectrum_at(path, row, col)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, str(exc)) from exc


@router.post("/run/{algorithm_id}")
async def console_run(
    algorithm_id: str,
    use_testdata: str = Form("false"),
    file: UploadFile | None = File(None),
    file2: UploadFile | None = File(None),
    params: str = Form("{}"),
):
    """控制台运行：testdata 一键或上传文件。"""
    _need_id(algorithm_id)
    try:
        submitted_params = json.loads(params or "{}")
        if not isinstance(submitted_params, dict):
            raise ValueError("params 必须是 JSON 对象")
    except (json.JSONDecodeError, ValueError):
        return JSONResponse(
            {
                "success": False,
                "algorithm_id": algorithm_id,
                "message": "params 不是合法 JSON 对象",
                "data": {},
                "files": {},
                "files_http": {},
            },
            status_code=400,
        )
    use_td = str(use_testdata).lower() in {"1", "true", "yes"}
    if use_td:
        folder = testdata_dir(algorithm_id)
        primary = find_named(folder, PRIMARY_NAMES)
        if primary is None:
            raise HTTPException(400, "缺少 testdata 主文件")
        file = _as_upload(primary)
        sec = find_named(folder, SECONDARY_NAMES)
        file2 = _as_upload(sec) if sec is not None else None
        pj = folder / "params.json"
        sample_params = (
            json.loads(pj.read_text(encoding="utf-8")) if pj.is_file() else {}
        )
        submitted_params = _merge_console_params(
            algorithm_id,
            sample_params,
            submitted_params,
        )
    else:
        submitted_params = _merge_console_params(
            algorithm_id,
            {},
            submitted_params,
        )
    params = json.dumps(submitted_params, ensure_ascii=False)
    if file is None:
        raise HTTPException(400, "需要 file 或 use_testdata=true")
    service = importlib.import_module(f"algorithms.{algorithm_id}.service")
    result = await service.run(file=file, file2=file2, params_json=params)
    if not isinstance(result, dict):
        raise HTTPException(500, "算法返回非 JSON")
    files = result.get("files") or {}
    result["files_http"] = files_to_http(files)
    if files:
        first = Path(next(iter(files.values())))
        result["job_id"] = first.parent.name
    else:
        result["job_id"] = None
    return result
