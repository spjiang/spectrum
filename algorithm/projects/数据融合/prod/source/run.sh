#!/usr/bin/env bash
# MAX 多光谱拼图。输入目录只读，成果写到 --out。
#
# 用法（在 prod/source 下，或给脚本绝对路径）：
#   ./run.sh                      # 全目录，输出到 ../runs/manual_时间戳
#   ./run.sh --max-frames 12      # 先跑 12 帧看中途文件
#   ./run.sh --out ../runs/my_run
#   ./run.sh --input /path/to/MAX_xxx --out /path/to/out
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PROD="$(cd "$ROOT/.." && pwd)"
PY="${MS_MOSAIC_PYTHON:-$ROOT/../../../../source/.venv/bin/python}"
INPUT_DEFAULT="$PROD/docs/需求/测试正式数据/MAX_20251017/MAX_20251017_001"

has_input=0
has_out=0
args=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input)
      has_input=1
      args+=(--input "$2")
      shift 2
      ;;
    --out)
      has_out=1
      args+=(--out "$2")
      shift 2
      ;;
    --help|-h)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done

if [[ $has_input -eq 0 ]]; then
  args+=(--input "$INPUT_DEFAULT")
fi
if [[ $has_out -eq 0 ]]; then
  stamp="$(date +%Y%m%d_%H%M%S)"
  args+=(--out "$PROD/runs/manual_$stamp")
fi

if [[ ! -x "$PY" ]]; then
  echo "找不到 Python: $PY" >&2
  echo "请先准备 algorithm/source/.venv，或设置 MS_MOSAIC_PYTHON" >&2
  exit 1
fi

echo "python  $PY"
echo "workdir $ROOT"
printf 'run     '
printf '%q ' "$PY" -m ms_mosaic "${args[@]}"
echo
cd "$ROOT"
exec "$PY" -m ms_mosaic "${args[@]}"
