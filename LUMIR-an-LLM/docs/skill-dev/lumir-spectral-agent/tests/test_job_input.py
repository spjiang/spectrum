#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生产作业输入契约：必须用户路径，禁止内置数据集名。"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from job_input import (  # noqa: E402
    JobInputError,
    add_job_input_args,
    parse_job_input,
)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_job_input_args(p)
    return p


def test_missing_data_raises() -> None:
    try:
        parse_job_input(_parser().parse_args(["--task", "classification", "--object", "milk"]))
    except SystemExit as exc:
        msg = str(exc)
        assert "--data" in msg or "光谱" in msg
        return
    raise AssertionError("缺少 --data 必须失败")


def test_dataset_flag_rejected() -> None:
    try:
        parse_job_input(
            _parser().parse_args(
                ["--dataset", "chenpi", "--data", "/tmp/x.npy", "--task", "classification"]
            )
        )
    except (SystemExit, JobInputError) as exc:
        msg = str(exc)
        assert "dataset" in msg.lower() or "内置" in msg
        return
    raise AssertionError("--dataset 必须被拒绝")


def test_explicit_data_path_accepted() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "spectra.npy"
        np.save(path, np.zeros((2, 4, 8), dtype=float))
        job = parse_job_input(
            _parser().parse_args(
                ["--data", str(path), "--task", "classification", "--object", "milk"]
            )
        )
        assert job.data_path == path.resolve()
        assert job.task == "classification"
        assert job.research_object == "milk"
        assert job.label_path is None
        data, labels = job.load_xy()
        assert data.shape == (2, 4, 8)
        assert labels is None


def test_regression_requires_label() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "spectra.npy"
        np.save(path, np.zeros((1, 10, 20), dtype=float))
        try:
            parse_job_input(
                _parser().parse_args(
                    ["--data", str(path), "--task", "regression", "--object", "corn"]
                )
            )
        except (SystemExit, JobInputError) as exc:
            assert "label" in str(exc).lower() or "标签" in str(exc)
            return
        raise AssertionError("回归缺 --label 必须失败")


def test_cli_offline_without_data_nonzero() -> None:
    script = SKILL_ROOT / "scripts" / "run_offline.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--task", "classification", "--object", "milk"],
        cwd=str(SKILL_ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    blob = (proc.stderr or "") + (proc.stdout or "")
    assert "--data" in blob or "光谱" in blob
    assert "chenpi" not in blob.lower() or "禁止" in blob or "不要" in blob or "dataset" in blob.lower()


def main() -> None:
    test_missing_data_raises()
    print("PASS  缺少 --data 失败")
    test_dataset_flag_rejected()
    print("PASS  --dataset 被拒绝")
    test_explicit_data_path_accepted()
    print("PASS  显式 --data 可加载")
    test_regression_requires_label()
    print("PASS  回归缺标签失败")
    test_cli_offline_without_data_nonzero()
    print("PASS  run_offline 无 --data 非零退出")
    print("全部输入契约通过")


if __name__ == "__main__":
    main()
