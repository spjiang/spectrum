#!/usr/bin/env bash
# 生产启动：绑定本机 28800，供 nginx 反代
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv"
cd "$ROOT"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
export MPLBACKEND=Agg
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"

SKLEARN_GOMP="$(find "$VENV" -path '*scikit_learn.libs/libgomp*' | head -1 || true)"
TORCHLIB="$VENV/lib/python3.12/site-packages/torch/lib"
PRELOAD_PARTS=()
if [[ -n "${SKLEARN_GOMP}" && -f "${SKLEARN_GOMP}" ]]; then
  PRELOAD_PARTS+=("${SKLEARN_GOMP}")
fi
if [[ -f "${TORCHLIB}/libgomp.so.1" ]]; then
  PRELOAD_PARTS+=("${TORCHLIB}/libgomp.so.1")
fi
if [[ -f "${TORCHLIB}/libc10.so" ]]; then
  PRELOAD_PARTS+=("${TORCHLIB}/libc10.so")
fi
if (( ${#PRELOAD_PARTS[@]} > 0 )); then
  IFS=:
  export LD_PRELOAD="${PRELOAD_PARTS[*]}${LD_PRELOAD:+:${LD_PRELOAD}}"
  unset IFS
fi

HOST="${ALGO_HOST:-127.0.0.1}"
PORT="${ALGO_PORT:-28800}"
echo "启动高光谱算法服务 http://${HOST}:${PORT}"
exec "$VENV/bin/uvicorn" app.main:app --host "$HOST" --port "$PORT" --workers 1
