#!/usr/bin/env bash
# 启动单进程高光谱算法服务
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

if [[ -x "$ROOT/.venv/bin/uvicorn" ]]; then
  UV="$ROOT/.venv/bin/uvicorn"
  PY="$ROOT/.venv/bin/python"
else
  UV="uvicorn"
  PY="python3"
fi

PORT="$("$PY" -c 'from common.config import APP_PORT; print(APP_PORT)')"
HOST="$("$PY" -c 'from common.config import APP_HOST; print(APP_HOST)')"

echo "启动高光谱算法服务 http://${HOST}:${PORT}"
echo "文档: http://${HOST}:${PORT}/docs"
exec "$UV" app.main:app --host "$HOST" --port "$PORT"
