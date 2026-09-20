from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

NAME_RE = re.compile(
    r"^MAX_(\d+)_(Color|(?P<wl>\d+)nm)_(?P<role>[DWdw])\.(?P<ext>jpg|jpeg|tif|tiff)$",
    re.IGNORECASE,
)
XMP_RE = {
    "yaw": re.compile(r"<Camera:Yaw>([^<]+)</Camera:Yaw>"),
    "pitch": re.compile(r"<Camera:Pitch>([^<]+)</Camera:Pitch>"),
    "roll": re.compile(r"<Camera:Roll>([^<]+)</Camera:Roll>"),
    "agl": re.compile(r"<Camera:AboveGroundAltitude>([^<]+)</Camera:AboveGroundAltitude>"),
    "lat": re.compile(r"<Camera:PositionLatitudeFused>([^<]+)</Camera:PositionLatitudeFused>"),
    "lon": re.compile(r"<Camera:PositionLongitudeFused>([^<]+)</Camera:PositionLongitudeFused>"),
    "alt": re.compile(r"<Camera:PositionAltitudeFused>([^<]+)</Camera:PositionAltitudeFused>"),
    "uuid": re.compile(r"<Camera:CaptureUUID>([^<]+)</Camera:CaptureUUID>"),
    "focal": re.compile(r"<Camera:PerspectiveFocalLength>([^<]+)</Camera:PerspectiveFocalLength>"),
    "rtk": re.compile(r"<Camera:RtkUsage>([^<]+)</Camera:RtkUsage>"),
}


@dataclass
class Pos:
    lon: float
    lat: float
    alt_m: float
    yaw_deg: float
    pitch_deg: float
    roll_deg: float
    agl_m: float
    focal_mm: float = 5.0
    rtk: int = 0


@dataclass
class FileRecord:
    path: Path
    index: int
    band: str
    role: str
    kind: str
    wavelength_nm: int | None = None
    pos: Pos | None = None
    capture_uuid: str = ""


@dataclass
class Shot:
    index: int
    rgb: FileRecord | None = None
    ms: dict[str, FileRecord] = field(default_factory=dict)
    pos: Pos | None = None
    capture_uuid: str = ""
    role: str = "D"


def parse_filename(path: Path) -> FileRecord | None:
    m = NAME_RE.match(path.name)
    if not m:
        return None
    index = int(m.group(1))
    role = m.group("role").upper()
    wl = m.group("wl")
    if wl:
        return FileRecord(
            path=path,
            index=index,
            band=f"{int(wl)}nm",
            role=role,
            kind="ms",
            wavelength_nm=int(wl),
        )
    return FileRecord(
        path=path,
        index=index,
        band="Color",
        role=role,
        kind="rgb",
        wavelength_nm=None,
    )


def _dms_to_deg(values, ref: str) -> float:
    seq = list(values)
    if len(seq) == 6:
        d, m, s = seq[0] / seq[1], seq[2] / seq[3], seq[4] / seq[5]
    elif len(seq) == 3:
        d, m, s = (float(x) for x in seq)
    else:
        raise ValueError(f"unexpected GPS tuple {values!r}")
    deg = float(d) + float(m) / 60.0 + float(s) / 3600.0
    if str(ref).upper().startswith("S") or str(ref).upper().startswith("W"):
        deg = -deg
    return deg


def _xmp_blob(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".tif", ".tiff"}:
        import tifffile

        with tifffile.TiffFile(path) as tf:
            tag = tf.pages[0].tags.get(700)
            if tag is None:
                return ""
            raw = tag.value
            if isinstance(raw, (bytes, bytearray)):
                return bytes(raw).decode("utf-8", "replace")
            return str(raw)
    data = path.read_bytes()
    m = re.search(br"<x:xmpmeta[\s\S]*?</x:xmpmeta>", data)
    return m.group(0).decode("utf-8", "replace") if m else ""


def _pos_from_xmp(xmp: str) -> tuple[Pos | None, str]:
    if not xmp:
        return None, ""
    got = {k: rx.search(xmp) for k, rx in XMP_RE.items()}
    uuid = got["uuid"].group(1) if got["uuid"] else ""
    if not got["lat"] or not got["lon"]:
        return None, uuid
    pos = Pos(
        lon=float(got["lon"].group(1)),
        lat=float(got["lat"].group(1)),
        alt_m=float(got["alt"].group(1)) if got["alt"] else 0.0,
        yaw_deg=float(got["yaw"].group(1)) if got["yaw"] else 0.0,
        pitch_deg=float(got["pitch"].group(1)) if got["pitch"] else -90.0,
        roll_deg=float(got["roll"].group(1)) if got["roll"] else 0.0,
        agl_m=float(got["agl"].group(1)) if got["agl"] else 0.0,
        focal_mm=float(got["focal"].group(1)) if got["focal"] else 5.0,
        rtk=int(float(got["rtk"].group(1))) if got["rtk"] else 0,
    )
    return pos, uuid


def _pos_from_exif_gps(path: Path) -> Pos | None:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        from PIL import Image
        from PIL.ExifTags import GPSTAGS

        with Image.open(path) as im:
            exif = im.getexif()
            if not exif:
                return None
            gps = exif.get_ifd(0x8825)
            if not gps:
                return None
            gpsn = {GPSTAGS.get(k, str(k)): gps[k] for k in gps}
        if "GPSLatitude" not in gpsn:
            return None
        lat = _dms_to_deg(gpsn["GPSLatitude"], gpsn.get("GPSLatitudeRef", "N"))
        lon = _dms_to_deg(gpsn["GPSLongitude"], gpsn.get("GPSLongitudeRef", "E"))
        alt = float(gpsn.get("GPSAltitude") or 0)
        return Pos(lon=lon, lat=lat, alt_m=alt, yaw_deg=0.0, pitch_deg=-90.0, roll_deg=0.0, agl_m=0.0)
    if suffix in {".tif", ".tiff"}:
        import tifffile

        with tifffile.TiffFile(path) as tf:
            gps = tf.pages[0].tags.get(34853)
            if gps is None:
                return None
            g = gps.value
        if "GPSLatitude" not in g:
            return None
        lat = _dms_to_deg(g["GPSLatitude"], g.get("GPSLatitudeRef", "N"))
        lon = _dms_to_deg(g["GPSLongitude"], g.get("GPSLongitudeRef", "E"))
        alt_raw = g.get("GPSAltitude", 0)
        if isinstance(alt_raw, tuple) and len(alt_raw) == 2:
            alt = float(alt_raw[0]) / float(alt_raw[1])
        else:
            alt = float(alt_raw or 0)
        return Pos(lon=lon, lat=lat, alt_m=alt, yaw_deg=0.0, pitch_deg=-90.0, roll_deg=0.0, agl_m=0.0)
    return None


def read_sidecar(path: Path) -> tuple[Pos | None, str]:
    xmp = _xmp_blob(path)
    pos, uuid = _pos_from_xmp(xmp)
    if pos is None:
        pos = _pos_from_exif_gps(path)
    return pos, uuid


def group_shots(records: list[FileRecord | None]) -> dict[int, Shot]:
    shots: dict[int, Shot] = {}
    for rec in records:
        if rec is None:
            continue
        shot = shots.get(rec.index)
        if shot is None:
            shot = Shot(index=rec.index)
            shots[rec.index] = shot
        if rec.kind == "rgb":
            shot.rgb = rec
        else:
            shot.ms[rec.band] = rec
        if rec.capture_uuid and not shot.capture_uuid:
            shot.capture_uuid = rec.capture_uuid
        if rec.pos is not None and shot.pos is None:
            shot.pos = rec.pos
    for shot in shots.values():
        if shot.pos is None:
            src = shot.rgb or (next(iter(shot.ms.values())) if shot.ms else None)
            if src is not None:
                shot.pos = src.pos
                if src.capture_uuid:
                    shot.capture_uuid = src.capture_uuid
        ms_roles = {r.role for r in shot.ms.values()}
        if ms_roles and ms_roles <= {"W"}:
            shot.role = "W"
        else:
            shot.role = "D"
    return shots


def scan_directory(root: Path, max_index: int | None = None) -> dict[int, Shot]:
    records: list[FileRecord] = []
    for path in sorted(root.iterdir()):
        rec = parse_filename(path)
        if rec is None:
            continue
        if max_index is not None and rec.index > max_index:
            continue
        pos, uuid = read_sidecar(path)
        rec.pos = pos
        rec.capture_uuid = uuid
        records.append(rec)
    return group_shots(records)
