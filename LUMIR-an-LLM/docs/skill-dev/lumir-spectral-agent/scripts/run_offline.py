#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LUMIR 离线流水线：检索 → 预处理/特征 → 本地基线（不调用 LLM）。

生产输入必须是用户上传文件或 --data / --label 路径。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# job_input 与本文件同目录
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import train_test_split

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
from job_input import add_job_input_args, parse_job_input  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parents[1]


def _resolve_bundle_root() -> Path:
    local_kb = SKILL_ROOT / "knowledge_base" / "structured_papers1.json"
    if local_kb.is_file():
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
        "找不到知识库。请确认 Skill 含 knowledge_base/structured_papers1.json。\n"
        f"  SKILL_ROOT={SKILL_ROOT}"
    )


LUMIR_ROOT = _resolve_bundle_root()
KB_PRIMARY = (
    SKILL_ROOT / "knowledge_base" / "structured_papers1.json"
    if (SKILL_ROOT / "knowledge_base" / "structured_papers1.json").is_file()
    else LUMIR_ROOT / "structured_papers1.json"
)

LITERATURE_METHODS: Dict[str, Dict[str, List[str]]] = {
    "milk": {"preprocessing": ["savitzky_golay_smoothing"], "features": ["pca_feature_extraction"]},
    "chinese medicine": {"preprocessing": ["snv_fd"], "features": ["pca_feature_extraction"]},
    "citri reticulatae pericarpium": {
        "preprocessing": ["standard_normal_variate"],
        "features": ["pca_feature_extraction"],
    },
    "chenpi": {"preprocessing": ["standard_normal_variate"], "features": ["pca_feature_extraction"]},
    "waste water": {
        "preprocessing": ["baseline_correction_asls"],
        "features": ["lambert_pearson_feature_extraction"],
    },
    "tecator": {"preprocessing": ["standard_normal_variate"], "features": ["Partial_Least_Squares"]},
    "corn": {"preprocessing": ["standard_normal_variate"], "features": ["Partial_Least_Squares"]},
}


def simple_tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


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
        text = (resp.choices[0].message.content or "").strip()
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
        return json.loads(text)
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] LLM 实体抽取失败，回退规则抽取: {exc}")
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


def retrieve(research_object: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """读取文献库并用分词 + BM25 检索。"""
    with open(KB_PRIMARY, "r", encoding="utf-8") as f:
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
            print(f"[warn] 未实现预处理 {fn}，跳过")
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
    return {"mode": "skipped", "reason": f"未覆盖任务: {task}"}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LUMIR 离线流水线（本地基线，不调用 LLM）",
    )
    add_job_input_args(parser)
    parser.add_argument("--offline", action="store_true", help="强制不调用 LLM（默认即离线）")
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument(
        "--json-out",
        default="",
        help="结构化报告 JSON 路径（默认 runs/offline_<job>_<timestamp>.json）",
    )
    args = parser.parse_args()
    job = parse_job_input(args)

    print("=" * 60)
    print("LUMIR 离线作业")
    print("=" * 60)
    print(f"SKILL_ROOT: {SKILL_ROOT}")
    print(f"data={job.data_path}")
    if job.label_path:
        print(f"label={job.label_path}")
    print(f"问题: {job.question}")

    extracted = None if args.offline else try_llm_extract(job.question)
    mode = "llm" if extracted else "offline"
    research_object = (extracted or {}).get("research_object") or job.research_object
    task_type = (extracted or {}).get("task_type") or job.task
    print(f"\n[1] 实体抽取 ({mode})")
    print(f"    research_object = {research_object}")
    print(f"    task_type       = {task_type}")

    matched = retrieve(research_object, top_k=args.top_k)
    print(f"\n[2] BM25 文献检索 top-{args.top_k}")
    for i, m in enumerate(matched, 1):
        print(f"    ({i}) score={m.get('score', 0):.3f}  {m.get('paper_name', '')[:80]}")
        print(f"        preprocess={m.get('preprocessing_method')!r}")
        print(f"        feature   ={m.get('feature_extracting_method')!r}")

    selected = resolve_methods(research_object, research_object)
    print("\n[3] 选定方法 (literature Table 4)")
    print(f"    {json.dumps(selected, ensure_ascii=False)}")

    data, labels = job.load_xy()
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

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "job_id": job.job_id,
        "data_path": str(job.data_path),
        "label_path": str(job.label_path) if job.label_path else None,
        "mode": mode,
        "question": job.question,
        "steps": {
            "entity": {"research_object": research_object, "task_type": task_type, "source": mode},
            "retrieve": {"matched": matched, "n": len(matched)},
            "methods": selected,
            "features": {
                "raw_shape": list(data.shape),
                "processed_shape": list(processed.shape),
                "feature_shapes": {k: list(v.shape) for k, v in features.items()},
            },
            "infer": metrics,
        },
    }
    out_path = Path(args.json_out) if args.json_out else (
        SKILL_ROOT / "runs" / f"offline_{job.job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n完成。报告：{out_path}")
    print("完整 LLM few-shot 请用 scripts/run_e2e.py（需 LUMIR_API_KEY）。")


if __name__ == "__main__":
    main()
