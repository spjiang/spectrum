"""路径与运行配置（单服务）。"""
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = SOURCE_ROOT / "data"
UPLOAD_DIR = DATA_ROOT / "uploads"
OUTPUT_DIR = DATA_ROOT / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

APP_HOST = "127.0.0.1"
APP_PORT = 28800
