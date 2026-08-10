"""供脚本导入：转发到 37_cnn3d_classify.model（包名以数字开头，需 shim）。"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_MODEL = Path(__file__).resolve().parent / "37_cnn3d_classify" / "model.py"
_spec = importlib.util.spec_from_file_location("cnn3d_model_37", _MODEL)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

train_and_predict = _mod.train_and_predict
pick_device = _mod.pick_device
Tiny3DCNN = _mod.Tiny3DCNN
