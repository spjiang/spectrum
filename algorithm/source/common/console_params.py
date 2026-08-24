"""从算法服务源码静态提取控制台参数。"""

from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path
from typing import Any

from common.config import SOURCE_ROOT


PARAM_TYPE_OVERRIDES: dict[tuple[str, str], str] = {
    ("01_flight_planning", "alt_m"): "float",
    ("04_flight_qc", "bit_depth"): "int",
    ("12_panel_reflectance", "panel_roi"): "list",
    ("13_atmospheric_correction", "wavelengths_nm"): "list",
    ("15_geo_locate", "gsd_m"): "float",
    ("20_bad_band_remove", "wavelengths_nm"): "list",
    ("33_physical_inversion", "wavelengths_nm"): "list",
}


class _ParamsGetVisitor(ast.NodeVisitor):
    """按源码出现顺序收集 params.get 调用。"""

    def __init__(self) -> None:
        self.parameters: dict[str, Any] = {}

    def visit_Call(self, node: ast.Call) -> None:
        function = node.func
        if (
            isinstance(function, ast.Attribute)
            and function.attr == "get"
            and isinstance(function.value, ast.Name)
            and function.value.id == "params"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            key = node.args[0].value
            if key not in self.parameters:
                self.parameters[key] = self._literal_default(node)
        self.generic_visit(node)

    @staticmethod
    def _literal_default(node: ast.Call) -> Any:
        """返回可静态求值的默认值；动态表达式保留为 None。"""
        if len(node.args) < 2:
            return None
        try:
            return ast.literal_eval(node.args[1])
        except (ValueError, TypeError):
            return None


@lru_cache(maxsize=None)
def _cached_service_params(algorithm_id: str) -> tuple[tuple[str, Any], ...]:
    service_path = SOURCE_ROOT / "algorithms" / algorithm_id / "service.py"
    if not service_path.is_file():
        return ()
    tree = ast.parse(service_path.read_text(encoding="utf-8"), filename=str(service_path))
    visitor = _ParamsGetVisitor()
    visitor.visit(tree)
    return tuple(visitor.parameters.items())


def get_service_params(algorithm_id: str) -> dict[str, Any]:
    """返回服务实际读取的参数键及可静态求值默认值。"""
    return dict(_cached_service_params(algorithm_id))


def get_service_param_type(algorithm_id: str, key: str, default: Any) -> str:
    """返回参数接口类型；动态默认值使用经服务实现核对的显式类型。"""
    if default is not None:
        return type(default).__name__
    return PARAM_TYPE_OVERRIDES.get((algorithm_id, key), "str")


@lru_cache(maxsize=None)
def service_requires_file2(algorithm_id: str) -> bool:
    """判断服务是否在缺少 file2 时直接返回错误。"""
    service_path = SOURCE_ROOT / "algorithms" / algorithm_id / "service.py"
    if not service_path.is_file():
        return False
    tree = ast.parse(service_path.read_text(encoding="utf-8"), filename=str(service_path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        is_missing_check = (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "file2"
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Is)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value is None
        )
        if is_missing_check and any(isinstance(stmt, ast.Return) for stmt in node.body):
            return True
    return False
