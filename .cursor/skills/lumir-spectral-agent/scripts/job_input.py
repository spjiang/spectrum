#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生产作业输入：光谱必须来自用户上传文件或显式路径。"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Tuple

import numpy as np

MISSING_DATA_MSG = (
    "缺少光谱数据。生产作业必须提供用户数据，禁止回退到内置样本：\n"
    "  --data <光谱.npy>            必填（上传文件的绝对路径，或本机路径）\n"
    "  --label <标签.npy>           回归必填；分类若标签在独立文件中也请提供\n"
    "  --task classification|regression|anomaly_detection\n"
    "  --object <研究对象>          如 milk / corn / 用户材料名\n"
    "  --question <自然语言任务描述> 可选，覆盖默认问题"
)

DATASET_REJECTED_MSG = (
    "已取消 --dataset 内置数据集名。请改用 --data / --label 指向用户文件或上传路径。"
)

REGRESSION_LABEL_MSG = "回归任务必须提供 --label <标签.npy>。"
DATA_NOT_FOUND_MSG = "光谱文件不存在: {path}"
LABEL_NOT_FOUND_MSG = "标签文件不存在: {path}"
TASK_REQUIRED_MSG = "必须提供 --task 或 --question，以便确定 classification / regression。"


class JobInputError(SystemExit):
    """输入不合法时以非零退出，消息给操作者看。"""


@dataclass
class JobInput:
    data_path: Path
    label_path: Optional[Path]
    task: str
    research_object: str
    question: str
    job_id: str

    def load_xy(self) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """加载光谱与可选标签；2D 光谱升为 (1, n_samples, n_bands)。"""
        data = np.load(self.data_path, allow_pickle=True)
        y = None
        if self.label_path is not None:
            y = np.load(self.label_path, allow_pickle=True)
        if data.ndim == 2:
            data = data.reshape(1, data.shape[0], data.shape[1])
        if y is not None:
            y = np.asarray(y).reshape(-1)
        return data, y


def add_job_input_args(parser: argparse.ArgumentParser) -> None:
    """向入口脚本注册生产输入参数。"""
    parser.add_argument(
        "--data",
        default=None,
        help="光谱 .npy 路径（用户上传文件或本机绝对/相对路径，必填）",
    )
    parser.add_argument("--label", default=None, help="标签 .npy 路径（回归必填）")
    parser.add_argument(
        "--task",
        default=None,
        choices=["classification", "regression", "anomaly_detection"],
        help="任务类型",
    )
    parser.add_argument("--object", default=None, dest="research_object", help="研究对象名称")
    parser.add_argument("--question", default=None, help="自然语言任务描述")
    parser.add_argument("--job-id", default=None, help="报告文件名前缀，默认由研究对象生成")
    parser.add_argument(
        "--dataset",
        default=None,
        help=argparse.SUPPRESS,
    )


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", (text or "").strip()).strip("_").lower()
    return slug[:40] or "job"


def _infer_task(question: str, fallback: Optional[str]) -> Optional[str]:
    if fallback:
        return fallback
    q = (question or "").lower()
    if "anomaly" in q or "异常" in q:
        return "anomaly_detection"
    if any(w in q for w in ("predict", "regression", "content", "protein", "fat", "回归", "含量")):
        return "regression"
    if any(w in q for w in ("classif", "分类")):
        return "classification"
    return None


def _infer_object(question: str, fallback: Optional[str]) -> str:
    if fallback:
        return fallback
    q = question or ""
    rules = [
        (r"citri|chenpi|pericarpium|陈皮", "Citri Reticulatae Pericarpium"),
        (r"chinese medicine|medicinal herb|中药|金银花", "chinese medicine"),
        (r"\bmilk\b|牛奶", "milk"),
        (r"\bcorn\b|玉米", "corn"),
        (r"tecator|meat|fat content", "tecator"),
        (r"waste.?water|cod", "waste water"),
    ]
    for pat, name in rules:
        if re.search(pat, q, re.I):
            return name
    return "unknown material"


def _default_question(task: str, research_object: str) -> str:
    if task == "regression":
        return f"I'm going to predict a continuous target from the following {research_object} spectral data."
    if task == "anomaly_detection":
        return f"I'm going to detect anomalies in the following {research_object} spectral data."
    return f"I'm going to classify the following {research_object} spectral data."


def parse_job_input(args: Any) -> JobInput:
    """校验并解析生产作业输入。"""
    if getattr(args, "dataset", None):
        raise JobInputError(DATASET_REJECTED_MSG)
    data_raw = getattr(args, "data", None)
    if not data_raw:
        raise JobInputError(MISSING_DATA_MSG)
    data_path = Path(data_raw).expanduser().resolve()
    if not data_path.is_file():
        raise JobInputError(DATA_NOT_FOUND_MSG.format(path=data_path))

    question = (getattr(args, "question", None) or "").strip()
    task = _infer_task(question, getattr(args, "task", None))
    if not task:
        raise JobInputError(TASK_REQUIRED_MSG)
    # 脚本内部回归/分类用短名；anomaly 与知识库一致时可写 "anomaly detection"
    task_norm = "anomaly detection" if task == "anomaly_detection" else task

    research_object = _infer_object(question, getattr(args, "research_object", None))
    if not question:
        question = _default_question(task, research_object)

    label_raw = getattr(args, "label", None)
    label_path: Optional[Path] = None
    if label_raw:
        label_path = Path(label_raw).expanduser().resolve()
        if not label_path.is_file():
            raise JobInputError(LABEL_NOT_FOUND_MSG.format(path=label_path))
    if task == "regression" and label_path is None:
        raise JobInputError(REGRESSION_LABEL_MSG)

    job_id = getattr(args, "job_id", None) or _slug(research_object)
    return JobInput(
        data_path=data_path,
        label_path=label_path,
        task=task_norm,
        research_object=research_object,
        question=question,
        job_id=job_id,
    )


def data_cli_epilog() -> str:
    """argparse epilog，供入口 --help。"""
    return MISSING_DATA_MSG


def required_job_argv_example(data: Path, label: Optional[Path], task: str, obj: str) -> List[str]:
    """生成验收命令参数，避免脚本里写死数据集名。"""
    argv = ["--data", str(data), "--task", task, "--object", obj]
    if label is not None:
        argv.extend(["--label", str(label)])
    return argv
