"""超像素：SLIC（Achanta 2012，业界面向对象分割标准实现）。"""
from __future__ import annotations

from fastapi import UploadFile
from skimage.segmentation import slic

from common.impl import parse_params
from common.io import as_cube, load_raster, new_job_dir, save_geotiff, save_preview_png, save_upload
from common.response import err_response, ok_response

ALGORITHM_ID = "25_superpixel"
TITLE = "超像素/对象分割"
IMPLEMENTED = True
LEVEL = "L2"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """在前三主成分（或前三波段）上运行 SLIC。"""
    _ = file2
    params, err = parse_params(params_json)
    if err:
        return err_response(algorithm_id=ALGORITHM_ID, algorithm=TITLE, message=err)
    n_seg = int(params.get("n_segments", 20))
    compactness = float(params.get("compactness", 10.0))
    job = new_job_dir(ALGORITHM_ID)
    path = await save_upload(file, job)
    arr, profile = load_raster(path)
    cube = as_cube(arr.astype(float))
    h, w, b = cube.shape
    rgb = cube[:, :, : min(3, b)]
    if rgb.shape[2] == 1:
        rgb = rgb.repeat(3, axis=2)
    elif rgb.shape[2] == 2:
        import numpy as np

        rgb = np.concatenate([rgb, rgb[:, :, :1]], axis=2)
    labels = slic(
        rgb,
        n_segments=max(2, n_seg),
        compactness=compactness,
        start_label=1,
        channel_axis=-1,
    ).astype("int32")
    tif = job / "superpixel_labels.tif"
    png = job / "superpixel_preview.png"
    save_geotiff(labels, tif, profile=profile)
    save_preview_png(labels.astype(float), png, title="SLIC")
    return ok_response(
        algorithm_id=ALGORITHM_ID,
        algorithm=TITLE,
        implemented=True,
        message=f"SLIC 超像素完成，对象数 {len(set(labels.ravel()))}",
        data={
            "method": "SLIC",
            "n_segments": n_seg,
            "compactness": compactness,
            "n_unique": int(len(set(labels.ravel()))),
            "shape": [h, w],
            "format": "GeoTIFF",
        },
        files={"labels_tif": str(tif.resolve()), "preview_png": str(png.resolve())},
    )
