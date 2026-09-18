#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
export RABBITMQ_URL="${RABBITMQ_URL:-amqp://mosaic:mosaic_secret@127.0.0.1:5672/}"
cd "$ROOT"
exec python -m ms_mosaic.worker_main
