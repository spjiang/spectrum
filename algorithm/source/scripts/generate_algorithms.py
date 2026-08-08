#!/usr/bin/env python3
"""（可选）重新生成骨架算法目录；已实现算法的 service.py 不会被覆盖。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.catalog import ALGORITHMS  # noqa: E402

ROUTER = '''"""HTTP 路由：{title}。"""
from __future__ import annotations

from common.routing import build_router

from . import service

router = build_router(service)
'''

SERVICE_STUB = '''"""骨架实现：{title}。"""
from __future__ import annotations

import json

from fastapi import UploadFile

from common.response import stub_response

ALGORITHM_ID = "{algo_id}"
TITLE = "{title}"
IMPLEMENTED = False
LEVEL = "{level}"


async def run(*, file: UploadFile, file2: UploadFile | None, params_json: str):
    """骨架：接收文件但不做真实计算。"""
    _ = await file.read()
    if file2 is not None:
        _ = await file2.read()
    try:
        json.loads(params_json or "{{}}")
    except json.JSONDecodeError:
        pass
    return stub_response(algorithm_id=ALGORITHM_ID, title=TITLE, level=LEVEL)
'''

README = '''# {title}

- **algorithm_id**: `{algo_id}`
- **层级**: {level}
- **实现状态**: {status_cn}

## 作用

{title}（对齐业界算法清单 #{num}）。

## 启动（整个算法服务）

```bash
cd algorithm/source
python run.py
```

## 调用示例

```bash
curl -X POST "http://127.0.0.1:28800/api/v1/{algo_id}/run" \\
  -F "file=@./data/examples/sample_cube.npy"
```

## 输入 / 输出

- **输入**: `multipart` 字段 `file`，可选 `file2`，`params`（JSON 字符串）
- **输出**: JSON；产物路径在 `files` 字段

当前为{status_cn}。
'''


def main() -> None:
    base = ROOT / "algorithms"
    base.mkdir(parents=True, exist_ok=True)
    (base / "__init__.py").write_text('"""算法模块包：一算法一目录。"""\n', encoding="utf-8")

    for i, meta in enumerate(ALGORITHMS, start=1):
        d = base / meta["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "__init__.py").write_text("", encoding="utf-8")
        (d / "router.py").write_text(ROUTER.format(title=meta["title"]), encoding="utf-8")

        svc = d / "service.py"
        # 已实现算法不覆盖业务代码
        if not meta["implemented"] or not svc.exists():
            if not meta["implemented"]:
                svc.write_text(
                    SERVICE_STUB.format(
                        algo_id=meta["id"],
                        title=meta["title"],
                        level=meta["level"],
                    ),
                    encoding="utf-8",
                )

        status_cn = "已实现（可运行）" if meta["implemented"] else "骨架（implemented=false）"
        (d / "README.md").write_text(
            README.format(
                title=meta["title"],
                algo_id=meta["id"],
                level=meta["level"],
                status_cn=status_cn,
                num=i,
            ),
            encoding="utf-8",
        )
        print("ensured", meta["id"])


if __name__ == "__main__":
    main()
