#!/usr/bin/env python3
"""对 45 项算法 testdata 做 HTTP 冒烟：要求 200 + success + implemented + files。

通过 curl 访问本机服务，避免 Python HTTP 被代理拦截。
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST = "http://127.0.0.1:28800"
BASE = ROOT / "algorithms"
ns: dict = {}
exec((ROOT / "common" / "catalog.py").read_text(encoding="utf-8"), ns)
ALGORITHMS = ns["ALGORITHMS"]


def find_primary(d: Path) -> Path | None:
    for name in ("input.tif", "input.geojson", "input.csv", "input.json"):
        p = d / name
        if p.exists():
            return p
    return None


def find_secondary(d: Path) -> Path | None:
    for name in ("file2.tif", "file2.geojson", "file2.csv", "file2.json"):
        p = d / name
        if p.exists():
            return p
    return None


def main() -> int:
    rows = []
    ok_n = 0
    fail_n = 0
    tmp = Path("/tmp/algo_one.json")
    for meta in ALGORITHMS:
        aid = meta["id"]
        td = BASE / aid / "testdata"
        primary = find_primary(td)
        secondary = find_secondary(td)
        params = {}
        pj = td / "params.json"
        if pj.exists():
            params = json.loads(pj.read_text(encoding="utf-8"))
        if primary is None:
            rows.append({"id": aid, "ok": False, "message": "缺少 testdata"})
            fail_n += 1
            print(f"FAIL {aid} 缺少 testdata")
            continue
        cmd = [
            "curl",
            "-sS",
            "-o",
            str(tmp),
            "-w",
            "%{http_code}",
            "-X",
            "POST",
            f"{HOST}/api/v1/{aid}/run",
            "-F",
            f"file=@{primary}",
        ]
        if secondary is not None:
            cmd += ["-F", f"file2=@{secondary}"]
        cmd += ["-F", f"params={json.dumps(params, ensure_ascii=False)}"]
        code = subprocess.check_output(cmd, text=True).strip()
        try:
            body = json.loads(tmp.read_text(encoding="utf-8"))
        except Exception:
            body = {}
        success = bool(body.get("success"))
        implemented = bool(body.get("implemented"))
        files_out = body.get("files") or {}
        ok = code == "200" and success and implemented and bool(files_out)
        if ok:
            ok_n += 1
            print(f"OK   {aid} files={list(files_out)}")
        else:
            fail_n += 1
            print(
                f"FAIL {aid} http={code} success={success} implemented={implemented} "
                f"files={list(files_out)} msg={body.get('message', '')[:240]}"
            )
        rows.append(
            {
                "id": aid,
                "ok": ok,
                "http": code,
                "success": success,
                "implemented": implemented,
                "n_files": len(files_out),
                "message": body.get("message", ""),
            }
        )
    print(f"\n汇总 OK={ok_n} FAIL={fail_n} 时间={datetime.now().isoformat(timespec='seconds')}")
    out = ROOT / "data" / "logs"
    out.mkdir(parents=True, exist_ok=True)
    report = out / "smoke_all_implemented.json"
    report.write_text(json.dumps({"ok": ok_n, "fail": fail_n, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("report", report)
    return 0 if fail_n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
