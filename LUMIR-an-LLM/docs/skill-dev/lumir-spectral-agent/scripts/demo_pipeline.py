#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LUMIR 流水线演示：检索 → 预处理/特征 → 本地基线（可选 LLM 实体抽取）。

为避开本机部分原生库（nltk/regex、Pillow）架构冲突，默认走自包含离线路径；
仍读取 Skill 内嵌的 structured_papers1.json 与 data/（可整包分发）。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import train_test_split
from sklearn.cross_decomposition import PLSRegression

# ---------------------------------------------------------------------------
# 路径：Skill 目录自包含（可整包 zip）
# ---------------------------------------------------------------------------
SKILL_ROOT = Path(__file__).resolve().parents[1]


def _resolve_bundle_root() -> Path:
    local_kb = SKILL_ROOT / "knowledge_base" / "structured_papers1.json"
    if local_kb.is_file() and (SKILL_ROOT / "data").is_dir():
        return SKILL_ROOT
    name = "LLM-Agent-for-Automated-Infrared-Spectral-Reasoning-main"
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3] / name,
        here.parents[4] / "LUMIR-an-LLM" / "docs" / name,
    ]
    for c in candidates:
        if c.is_dir():
            return c
    raise SystemExit(
        "找不到内嵌资源。请确认 Skill 含 knowledge_base/structured_papers1.json 与 data/。\n"
        f"  SKILL_ROOT={SKILL_ROOT}"
    )


LUMIR_ROOT = _resolve_bundle_root()
DATA_ROOT = SKILL_ROOT / "data" if (SKILL_ROOT / "data").is_dir() else LUMIR_ROOT / "data"
KB_PRIMARY = (
    SKILL_ROOT / "knowledge_base" / "structured_papers1.json"
    if (SKILL_ROOT / "knowledge_base" / "structured_papers1.json").is_file()
    else LUMIR_ROOT / "structured_papers1.json"
)
# 文献 Table 4：材料 → (预处理, 特征)
LITERATURE_METHODS: Dict[str, Dict[str, List[str]]] = {
    "milk": {
        "preprocessing": ["savitzky_golay_smoothing"],
        "features": ["pca_feature_extraction"],
    },
    "chinese medicine": {
        "preprocessing": ["snv_fd"],
        "features": ["pca_feature_extraction"],
    },
    "citri reticulatae pericarpium": {
        "preprocessing": ["standard_normal_variate"],
        "features": ["pca_feature_extraction"],
    },
    "chenpi": {
        "preprocessing": ["standard_normal_variate"],
        "features": ["pca_feature_extraction"],
    },
    "waste water": {
        "preprocessing": ["baseline_correction_asls"],
        "features": ["lambert_pearson_feature_extraction"],
    },
    "tecator": {
        "preprocessing": ["standard_normal_variate"],
        "features": ["Partial_Least_Squares"],
    },
    "corn": {
        "preprocessing": ["standard_normal_variate"],
        "features": ["Partial_Least_Squares"],
    },
}

DATASET_SPECS = {
    "chenpi": {
        "question": "I'm going to classify the following Citri Reticulatae Pericarpium spectral data.",
        "data": DATA_ROOT / "Chenpi" / "chenpi.npy",
        "task": "classification",
        "object": "Citri Reticulatae Pericarpium",
        "method_key": "citri reticulatae pericarpium",
    },
    "milk": {
        "question": "I'm going to classify the following milk spectral data.",
        "data": DATA_ROOT / "milk" / "milk_data.npy",
        "task": "classification",
        "object": "milk",
        "method_key": "milk",
    },
    "cn_medicine": {
        "question": "I'm going to classify the following chinese medicine spectral data.",
        "data": DATA_ROOT / "CN_medicine" / "cnm.npy",
        "task": "classification",
        "object": "chinese medicine",
        "method_key": "chinese medicine",
    },
    "corn": {
        "question": "I'm going to predict the protein content in corn samples.",
        "data": DATA_ROOT / "corn" / "corn_data.npy",
        "label": DATA_ROOT / "corn" / "protein_label.npy",
        "task": "regression",
        "object": "corn",
        "method_key": "corn",
    },
    "tecator": {
        "question": "I'm going to predict the fat content in meat sample.",
        "data": DATA_ROOT / "tecator" / "tecator_data.npy",
        "label": DATA_ROOT / "tecator" / "tecator_label.npy",
        "task": "regression",
        "object": "tecator",
        "method_key": "tecator",
    },
}


def simple_tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def offline_extract(question: str, fallback_object: str, fallback_task: str) -> Dict[str, str]:
    q = question.lower()
    task = fallback_task
    if "anomaly" in q:
        task = "anomaly detection"
    elif any(w in q for w in ("predict", "regression", "content", "cod", "protein", "fat")):
        task = "regression"
    elif "classif" in q:
        task = "classification"

    obj = fallback_object
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
            obj = name
            break
    return {"research_object": obj, "task_type": task}


def try_llm_extract(question: str) -> Optional[Dict[str, str]]:
    api_key = os.getenv("LUMIR_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    base_url = os.getenv("LUMIR_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    model = os.getenv("LUMIR_MODEL") or "gpt-4o-mini"
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url=base_url)
        system = (
            "Extract research_object and task_type "
            "(classification|regression|anomaly detection). "
            'Output ONLY JSON: {"research_object":"...","task_type":"..."}'
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": question},
            ],
            temperature=0.1,
        )
        text = resp.choices[0].message.content.strip()
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
        return json.loads(text)
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] LLM 实体抽取失败，回退离线规则: {exc}")
        return None


def resolve_methods(method_key: str, research_object: str) -> Dict[str, List[str]]:
    key = method_key.lower()
    if key in LITERATURE_METHODS:
        return LITERATURE_METHODS[key]
    ro = research_object.lower()
    for k, v in LITERATURE_METHODS.items():
        if k in ro or ro in k:
            return v
    return {"preprocessing": ["standard_normal_variate"], "features": ["pca_feature_extraction"]}


def load_xy(spec: Dict[str, Any]) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    data = np.load(spec["data"], allow_pickle=True)
    y = None
    if "label" in spec:
        y = np.load(spec["label"], allow_pickle=True)
    if data.ndim == 2:
        data = data.reshape(1, data.shape[0], data.shape[1])
    if y is not None:
        y = np.asarray(y).reshape(-1)
    return data, y


def retrieve(research_object: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """读取 LUMIR 文献库并用简易分词 + BM25 检索（不 import Retrieval/nltk）。"""
    json_path = KB_PRIMARY
    with open(json_path, "r", encoding="utf-8") as f:
        papers = json.load(f)
    tokenized = [
        simple_tokenize(f"{e.get('paper_name', '')} {e.get('research_object', '')}")
        for e in papers
    ]
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(simple_tokenize(research_object))
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    out = []
    for i in ranked:
        e = papers[i]
        out.append(
            {
                "paper_name": e.get("paper_name", ""),
                "preprocessing_method": e.get("preprocessing_method", ""),
                "feature_extracting_method": e.get("feature_extracting_method", ""),
                "score": float(scores[i]),
            }
        )
    return out


# -------------------- 与源码等价的核心预处理/特征（避免 matplotlib/PIL） --------------------

def standard_normal_variate(data: np.ndarray) -> np.ndarray:
    out = np.zeros_like(data, dtype=float)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            s = data[i, j].astype(float)
            std = s.std()
            out[i, j] = (s - s.mean()) / std if std > 0 else s - s.mean()
    return out


def savitzky_golay_smoothing(data: np.ndarray, window_length: int = 11, polyorder: int = 2) -> np.ndarray:
    from scipy.signal import savgol_filter

    out = np.zeros_like(data, dtype=float)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            out[i, j] = savgol_filter(data[i, j].astype(float), window_length, polyorder)
    return out


def snv_fd(data: np.ndarray) -> np.ndarray:
    snv = standard_normal_variate(data)
    # 一阶差分近似一阶导
    out = np.zeros_like(snv)
    out[..., 1:-1] = (snv[..., 2:] - snv[..., :-2]) / 2.0
    out[..., 0] = snv[..., 1] - snv[..., 0]
    out[..., -1] = snv[..., -1] - snv[..., -2]
    return out


def pca_feature_extraction(data: np.ndarray, n_components: int = 5) -> np.ndarray:
    n0, n1, nb = data.shape
    flat = data.reshape(-1, nb)
    n_components = min(n_components, flat.shape[0], flat.shape[1])
    transformed = PCA(n_components=n_components).fit_transform(flat)
    return transformed.reshape(n0, n1, n_components)


def pls_feature_extraction(data: np.ndarray, y: np.ndarray, n_components: int = 4) -> np.ndarray:
    # data: (1, n, bands)
    x = data.reshape(-1, data.shape[-1])
    y = y.reshape(-1)
    n = min(len(x), len(y))
    x, y = x[:n], y[:n]
    n_components = min(n_components, x.shape[0] - 1, x.shape[1])
    pls = PLSRegression(n_components=n_components)
    scores = pls.fit_transform(x, y)[0]
    return scores.reshape(1, n, n_components)


PRE_FUNCS = {
    "standard_normal_variate": standard_normal_variate,
    "savitzky_golay_smoothing": savitzky_golay_smoothing,
    "snv_fd": snv_fd,
}


def run_preprocess_feature(
    data: np.ndarray, selected: Dict[str, List[str]], regression_label: Optional[np.ndarray]
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    processed = data.astype(float).copy()
    for fn in selected.get("preprocessing", []):
        if fn not in PRE_FUNCS:
            print(f"[warn] 演示未实现预处理 {fn}，跳过")
            continue
        processed = PRE_FUNCS[fn](processed)

    feats: Dict[str, np.ndarray] = {}
    for fn in selected.get("features", []) or ["pca_feature_extraction"]:
        if fn == "Partial_Least_Squares" and regression_label is not None:
            feats[fn] = pls_feature_extraction(processed, regression_label)
        elif fn == "pca_feature_extraction" or regression_label is None:
            if fn != "pca_feature_extraction":
                print(f"[info] 特征 {fn} 降级为 pca_feature_extraction")
            feats["pca_feature_extraction"] = pca_feature_extraction(processed)
        else:
            feats["pca_feature_extraction"] = pca_feature_extraction(processed)
    return processed, feats


def local_baseline(
    task: str, features: Dict[str, np.ndarray], labels: Optional[np.ndarray]
) -> Dict[str, Any]:
    feat_name, feat = next(iter(features.items()))
    if task == "classification":
        n_cls, n_per, d = feat.shape
        X = feat.reshape(-1, d)
        y = np.repeat(np.arange(n_cls), n_per)
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(Xtr, ytr)
        pred = clf.predict(Xte)
        return {
            "mode": "sklearn_rf_classification",
            "feature": feat_name,
            "feature_shape": list(feat.shape),
            "accuracy": float(accuracy_score(yte, pred)),
            "n_train": int(len(ytr)),
            "n_test": int(len(yte)),
        }
    if task == "regression":
        if labels is None:
            return {"mode": "skipped", "reason": "无标签"}
        X = feat.reshape(-1, feat.shape[-1])
        y = labels.reshape(-1)
        n = min(len(X), len(y))
        X, y = X[:n], y[:n]
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
        reg = RandomForestRegressor(n_estimators=100, random_state=42)
        reg.fit(Xtr, ytr)
        pred = reg.predict(Xte)
        return {
            "mode": "sklearn_rf_regression",
            "feature": feat_name,
            "feature_shape": list(feat.shape),
            "r2": float(r2_score(yte, pred)),
            "n_train": int(len(ytr)),
            "n_test": int(len(yte)),
        }
    return {"mode": "skipped", "reason": f"演示未覆盖任务: {task}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="LUMIR 流水线演示")
    parser.add_argument("--dataset", default="chenpi", choices=sorted(DATASET_SPECS.keys()))
    parser.add_argument("--task", default=None)
    parser.add_argument("--offline", action="store_true", help="强制离线（不调 LLM）")
    parser.add_argument("--top-k", type=int, default=2)
    args = parser.parse_args()

    spec = DATASET_SPECS[args.dataset]
    question = spec["question"]
    task = args.task or spec["task"]

    print("=" * 60)
    print("LUMIR Demo")
    print("=" * 60)
    print(f"SKILL_ROOT: {SKILL_ROOT}")
    print(f"数据/知识库: {LUMIR_ROOT}")
    print(f"问题: {question}")

    extracted = None if args.offline else try_llm_extract(question)
    mode = "llm" if extracted else "offline"
    if extracted is None:
        extracted = offline_extract(question, spec["object"], task)
    research_object = extracted["research_object"]
    task_type = extracted.get("task_type") or task
    print(f"\n[1] 实体抽取 ({mode})")
    print(f"    research_object = {research_object}")
    print(f"    task_type       = {task_type}")

    matched = retrieve(research_object, top_k=args.top_k)
    print(f"\n[2] BM25 文献检索 top-{args.top_k}")
    for i, m in enumerate(matched, 1):
        print(f"    ({i}) score={m.get('score', 0):.3f}  {m.get('paper_name', '')[:80]}")
        print(f"        preprocess={m.get('preprocessing_method')!r}")
        print(f"        feature   ={m.get('feature_extracting_method')!r}")

    selected = resolve_methods(spec["method_key"], research_object)
    print("\n[3] 选定方法 (literature Table 4)")
    print(f"    {json.dumps(selected, ensure_ascii=False)}")

    data, labels = load_xy(spec)
    print(f"\n[4] 原始光谱 shape = {data.shape}")
    processed, features = run_preprocess_feature(
        data, selected, labels if task_type == "regression" else None
    )
    print(f"    预处理后 shape = {processed.shape}")
    for name, arr in features.items():
        print(f"    特征 {name} shape = {arr.shape}")

    metrics = local_baseline(task_type, features, labels)
    print("\n[5] 本地基线（sklearn 对照，非论文 LLM few-shot）")
    print(f"    {json.dumps(metrics, ensure_ascii=False, indent=2)}")
    print("\n完成。完整 LLM few-shot 见 main.ipynb（需配置 API）。")


if __name__ == "__main__":
    main()
