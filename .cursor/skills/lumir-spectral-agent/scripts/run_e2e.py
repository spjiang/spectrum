#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LUMIR 端到端测试入口（DeepSeek / OpenAI 兼容）。

五步流水线：
1. LLM 实体抽取
2. BM25 知识库检索
3. LLM 方法映射 + 多数投票（可跳过）
4. 本地预处理 + 特征提取
5. LLM few-shot 分类/回归（可选停在 features）
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import yaml
from openai import OpenAI
from rank_bm25 import BM25Okapi
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# 路径：Skill 目录自包含（可整包 zip 到其它 Agent 客户端）
# ---------------------------------------------------------------------------
SKILL_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_ROOT = SKILL_ROOT  # 数据/知识库均在 Skill 根下


def resolve_bundle_root() -> Path:
    """优先用 Skill 内嵌资源；兼容旧布局（仓库旁 LUMIR 源码）。"""
    local_kb = SKILL_ROOT / "knowledge_base" / "structured_papers1.json"
    local_data = SKILL_ROOT / "data"
    if local_kb.is_file() and local_data.is_dir():
        return SKILL_ROOT
    name = "LLM-Agent-for-Automated-Infrared-Spectral-Reasoning-main"
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3] / name,
        here.parents[4] / "LUMIR-an-LLM" / "docs" / name,
    ]
    for c in candidates:
        if c.is_dir() and (c / "structured_papers1.json").is_file():
            return c
    raise SystemExit(
        "找不到内嵌资源。请确认 Skill 目录含 knowledge_base/structured_papers1.json 与 data/。\n"
        f"  SKILL_ROOT={SKILL_ROOT}"
    )


LUMIR_ROOT = resolve_bundle_root()

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

DATASET_SPECS = {
    "chenpi": {
        "question": "I'm going to classify the following Citri Reticulatae Pericarpium spectral data.",
        "data": "Chenpi/chenpi.npy",
        "task": "classification",
        "object": "Citri Reticulatae Pericarpium",
        "method_key": "citri reticulatae pericarpium",
    },
    "milk": {
        "question": "I'm going to classify the following milk spectral data.",
        "data": "milk/milk_data.npy",
        "task": "classification",
        "object": "milk",
        "method_key": "milk",
    },
    "cn_medicine": {
        "question": "I'm going to classify the following chinese medicine spectral data.",
        "data": "CN_medicine/cnm.npy",
        "task": "classification",
        "object": "chinese medicine",
        "method_key": "chinese medicine",
    },
    "corn": {
        "question": "I'm going to predict the protein content in corn samples.",
        "data": "corn/corn_data.npy",
        "label": "corn/protein_label.npy",
        "task": "regression",
        "object": "corn",
        "method_key": "corn",
    },
    "tecator": {
        "question": "I'm going to predict the fat content in meat sample.",
        "data": "tecator/tecator_data.npy",
        "label": "tecator/tecator_label.npy",
        "task": "regression",
        "object": "tecator",
        "method_key": "tecator",
    },
}

ALL_PREPROCESS = [
    "baseline_correction_asls",
    "savitzky_golay_smoothing",
    "standard_normal_variate",
    "multiplicative_scatter_correction",
    "normalization_min_max",
    "detrend_spectrum",
    "snv_fd",
    "sg_fd",
    "msc_fd",
]
ALL_FEATURES = [
    "pca_feature_extraction",
    "nmf_feature_extraction",
    "cwt_feature_extraction",
    "spectral_derivative",
    "peak_feature_extraction",
    "statistical_feature_extraction",
    "lambert_pearson_feature_extraction",
    "Partial_Least_Squares",
]


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip("'\"")
        os.environ.setdefault(k, v)


def resolve_path(p: str, base: Path) -> Path:
    path = Path(p)
    if not path.is_absolute():
        path = (base / path).resolve()
    return path


def load_config(config_path: Optional[Path]) -> Dict[str, Any]:
    load_dotenv(SKILL_ROOT / ".env")
    cfg_path = config_path or (SKILL_ROOT / "config.yaml")
    if not cfg_path.is_file():
        cfg_path = SKILL_ROOT / "config.example.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg["_config_path"] = str(cfg_path)
    return cfg


def get_api_key(cfg: Dict[str, Any]) -> str:
    envs = cfg.get("llm", {}).get("api_key_env", ["LUMIR_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"])
    if isinstance(envs, str):
        envs = [envs]
    for name in envs:
        val = os.getenv(name)
        if val:
            return val
    raise SystemExit(
        "未找到 API Key。请设置环境变量，例如:\n"
        "  export LUMIR_API_KEY=sk-...\n"
        "或复制 .env.example 为 .env 后填写。"
    )


def resolve_kb_primary(cfg: Dict[str, Any]) -> Path:
    raw = (cfg.get("knowledge_base") or {}).get("primary", "auto")
    if raw in (None, "", "auto"):
        bundled = SKILL_ROOT / "knowledge_base" / "structured_papers1.json"
        if bundled.is_file():
            return bundled
        return LUMIR_ROOT / "structured_papers1.json"
    return resolve_path(str(raw), SKILL_ROOT)


# ---------------------------------------------------------------------------
# 步骤 1：实体抽取
# ---------------------------------------------------------------------------
def llm_extract_entities(client: OpenAI, model: str, temperature: float, question: str) -> Dict[str, str]:
    system = (
        "You extract research_object and task_type from a user question. "
        'task_type must be one of: "classification", "regression", "anomaly detection". '
        'Output ONLY JSON: {"research_object":"...","task_type":"..."}'
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ],
        temperature=temperature,
    )
    text = (resp.choices[0].message.content or "").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


# ---------------------------------------------------------------------------
# 步骤 2：知识库 BM25
# ---------------------------------------------------------------------------
def simple_tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def load_papers(primary: Path, extra: Optional[Path]) -> List[Dict[str, Any]]:
    if not primary.is_file():
        raise FileNotFoundError(f"主知识库不存在: {primary}")
    with open(primary, "r", encoding="utf-8") as f:
        papers = json.load(f)
    if not isinstance(papers, list):
        raise ValueError("知识库 JSON 必须是数组")
    if extra and extra.is_file():
        with open(extra, "r", encoding="utf-8") as f:
            more = json.load(f)
        if isinstance(more, list):
            papers = papers + more
    return papers


def retrieve_papers(papers: List[Dict[str, Any]], query: str, top_k: int) -> List[Dict[str, Any]]:
    tokenized = [
        simple_tokenize(f"{e.get('paper_name', '')} {e.get('research_object', '')}") for e in papers
    ]
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(simple_tokenize(query))
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    out = []
    for i in ranked:
        e = papers[i]
        out.append(
            {
                "paper_name": e.get("paper_name", ""),
                "research_object": e.get("research_object", ""),
                "preprocessing_method": e.get("preprocessing_method", ""),
                "feature_extracting_method": e.get("feature_extracting_method", ""),
                "score": float(scores[i]),
            }
        )
    return out


# ---------------------------------------------------------------------------
# 步骤 3：方法映射
# ---------------------------------------------------------------------------
def table4_methods(method_key: str, research_object: str) -> Dict[str, List[str]]:
    key = method_key.lower()
    if key in LITERATURE_METHODS:
        return dict(LITERATURE_METHODS[key])
    ro = research_object.lower()
    for k, v in LITERATURE_METHODS.items():
        if k in ro or ro in k:
            return dict(v)
    return {"preprocessing": ["standard_normal_variate"], "features": ["pca_feature_extraction"]}


def llm_map_methods(
    client: OpenAI, model: str, temperature: float, matched: List[Dict[str, Any]]
) -> Dict[str, Dict[str, List[str]]]:
    system = f"""You are a spectral analysis decision agent.
Map each paper's preprocessing_method and feature_extracting_method to function names.
Output ONLY JSON:
{{"paper_A": {{"preprocessing": [...], "features": [...]}}}}
Available preprocessing: {ALL_PREPROCESS}
Available features: {ALL_FEATURES}
Rules: use only names from the lists; empty lists allowed; no markdown.
"""
    papers_info = [
        {
            "paper_name": m["paper_name"],
            "preprocessing_method": m.get("preprocessing_method", ""),
            "feature_extracting_method": m.get("feature_extracting_method", ""),
        }
        for m in matched
    ]
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(papers_info, ensure_ascii=False, indent=2)},
        ],
        temperature=temperature,
    )
    text = (resp.choices[0].message.content or "").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise RuntimeError(f"方法映射无有效 JSON: {text[:500]}")
    return json.loads(text[start : end + 1])


def select_by_majority(
    methods_map: Dict[str, Dict[str, List[str]]], paper_order: List[str]
) -> Dict[str, List[str]]:
    from collections import Counter

    pre_set, feat_set = set(ALL_PREPROCESS), set(ALL_FEATURES)
    pairs = []
    for name in paper_order:
        mm = methods_map.get(name) or {}
        # 允许 key 不完全等于 paper_name：模糊匹配
        if not mm:
            for k, v in methods_map.items():
                if k == name or name in k or k in name:
                    mm = v
                    break
        pre = [x for x in mm.get("preprocessing", []) if x in pre_set]
        feat = [x for x in mm.get("features", []) if x in feat_set]
        if pre and feat:
            pairs.append((tuple(pre), tuple(feat)))
    if not pairs:
        return {"preprocessing": [], "features": ["pca_feature_extraction"]}
    (pre_t, feat_t), _ = Counter(pairs).most_common(1)[0]
    return {"preprocessing": list(pre_t), "features": list(feat_t)}


# ---------------------------------------------------------------------------
# 步骤 4：预处理 / 特征（自包含，避开 matplotlib/PIL）
# ---------------------------------------------------------------------------
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


PRE_FUNCS = {
    "standard_normal_variate": standard_normal_variate,
    "savitzky_golay_smoothing": savitzky_golay_smoothing,
    "snv_fd": snv_fd,
}


def pca_feature_extraction(data: np.ndarray, n_components: int = 5) -> np.ndarray:
    n0, n1, nb = data.shape
    flat = data.reshape(-1, nb)
    n_components = min(n_components, flat.shape[0], flat.shape[1])
    return PCA(n_components=n_components).fit_transform(flat).reshape(n0, n1, n_components)


def pls_feature_extraction(data: np.ndarray, y: np.ndarray, n_components: int = 4) -> np.ndarray:
    x = data.reshape(-1, data.shape[-1])
    y = y.reshape(-1)
    n = min(len(x), len(y))
    x, y = x[:n], y[:n]
    n_components = min(n_components, x.shape[0] - 1, x.shape[1])
    scores = PLSRegression(n_components=n_components).fit_transform(x, y)[0]
    return scores.reshape(1, n, n_components)


def run_preprocess_feature(
    data: np.ndarray, selected: Dict[str, List[str]], labels: Optional[np.ndarray], task: str
) -> Tuple[np.ndarray, Dict[str, np.ndarray], Dict[str, List[str]]]:
    used = {"preprocessing": [], "features": []}
    processed = data.astype(float).copy()
    for fn in selected.get("preprocessing", []):
        if fn not in PRE_FUNCS:
            print(f"[warn] 未实现预处理 {fn}，跳过")
            continue
        processed = PRE_FUNCS[fn](processed)
        used["preprocessing"].append(fn)

    feats: Dict[str, np.ndarray] = {}
    feat_list = selected.get("features") or ["pca_feature_extraction"]
    for fn in feat_list:
        if fn == "Partial_Least_Squares" and labels is not None and task == "regression":
            feats[fn] = pls_feature_extraction(processed, labels)
            used["features"].append(fn)
        else:
            if fn != "pca_feature_extraction":
                print(f"[info] 特征 {fn} 使用 pca_feature_extraction 实现/降级")
            feats["pca_feature_extraction"] = pca_feature_extraction(processed)
            used["features"].append("pca_feature_extraction")
            break
    return processed, feats, used


def load_xy(spec: Dict[str, Any]) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    data_root = SKILL_ROOT / "data" if (SKILL_ROOT / "data").is_dir() else LUMIR_ROOT / "data"
    data_path = data_root / spec["data"]
    data = np.load(data_path, allow_pickle=True)
    y = None
    if "label" in spec:
        y = np.load(data_root / spec["label"], allow_pickle=True)
    if data.ndim == 2:
        data = data.reshape(1, data.shape[0], data.shape[1])
    if y is not None:
        y = np.asarray(y).reshape(-1)
    return data, y


# ---------------------------------------------------------------------------
# 步骤 5：few-shot 推理
# ---------------------------------------------------------------------------
def vec_to_list(v: np.ndarray, ndigits: int = 4) -> List[float]:
    return [round(float(x), ndigits) for x in np.asarray(v).reshape(-1)]


def build_cls_examples(
    feat: np.ndarray, few_shot: int, test_ratio: float, max_test: int, seed: int
) -> Tuple[List[Dict], List[Dict], List[str]]:
    n_cls, n_per, _ = feat.shape
    X = feat.reshape(-1, feat.shape[-1])
    y = np.array([str(i + 1) for i in range(n_cls) for _ in range(n_per)])
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=test_ratio, random_state=seed, stratify=y
    )
    if len(Xte) > max_test:
        Xte, yte = Xte[:max_test], yte[:max_test]
    train = [
        {"name": f"tr{i}", "x": vec_to_list(Xtr[i]), "label": str(ytr[i])}
        for i in range(min(few_shot, len(Xtr)))
    ]
    # 补充：尽量覆盖各类别
    seen = {e["label"] for e in train}
    for i in range(len(Xtr)):
        if len(train) >= few_shot and len(seen) >= n_cls:
            break
        lab = str(ytr[i])
        if lab not in seen:
            train.append({"name": f"tr_c{lab}", "x": vec_to_list(Xtr[i]), "label": lab})
            seen.add(lab)
    test = [{"name": f"te{i}", "x": vec_to_list(Xte[i])} for i in range(len(Xte))]
    return train, test, [str(t) for t in yte]


def build_reg_examples(
    feat: np.ndarray, labels: np.ndarray, few_shot: int, test_ratio: float, max_test: int, seed: int
) -> Tuple[List[Dict], List[Dict], List[float]]:
    X = feat.reshape(-1, feat.shape[-1])
    y = labels.reshape(-1)
    n = min(len(X), len(y))
    X, y = X[:n], y[:n]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_ratio, random_state=seed)
    if len(Xte) > max_test:
        Xte, yte = Xte[:max_test], yte[:max_test]
    train = [
        {"name": f"tr{i}", "x": vec_to_list(Xtr[i]), "y": round(float(ytr[i]), 4)}
        for i in range(min(few_shot, len(Xtr)))
    ]
    test = [{"name": f"te{i}", "x": vec_to_list(Xte[i])} for i in range(len(Xte))]
    return train, test, [float(t) for t in yte]


def fewshot_classify(
    client: OpenAI, model: str, temperature: float, train: List[Dict], test: List[Dict]
) -> Tuple[List[str], str]:
    system = (
        "You are a spectral chemometrics expert. "
        "Given few-shot examples (x and label), classify test samples. "
        "Output MUST be a JSON array of labels with length exactly equal to test samples. "
        "No extra text."
    )
    few = "\n".join(f"{e['name']}: x={e['x']}, label={e['label']}" for e in train)
    xs = [e["x"] for e in test]
    user = f"Few-shot examples:\n{few}\n\nClassify these samples. Return ONLY a JSON array.\nSamples: {xs}"
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=temperature,
    )
    raw = (resp.choices[0].message.content or "").strip()
    arr = _parse_json_array(raw)
    preds = [str(x) for x in arr]
    if len(preds) < len(test):
        preds += ["UNKNOWN"] * (len(test) - len(preds))
    return preds[: len(test)], raw


def fewshot_regress(
    client: OpenAI, model: str, temperature: float, train: List[Dict], test: List[Dict]
) -> Tuple[List[float], str]:
    system = (
        "You are a spectral regression expert. "
        "Based on x→y examples, predict y for new x. "
        "Output ONLY a JSON array of numbers, length equal to test samples."
    )
    few = "\n".join(f"{e['name']}: x={e['x']}, y={e['y']}" for e in train)
    xs = [e["x"] for e in test]
    user = f"Examples:\n{few}\n\nPredict y for:\n{xs}\nReturn ONLY a JSON array of numbers."
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=temperature,
    )
    raw = (resp.choices[0].message.content or "").strip()
    arr = _parse_json_array(raw)
    preds = [float(x) for x in arr]
    if len(preds) < len(test):
        preds += [float("nan")] * (len(test) - len(preds))
    return preds[: len(test)], raw


def _parse_json_array(text: str) -> List[Any]:
    text = re.sub(r"^```(?:json|python)?|```$", "", text, flags=re.M).strip()
    m = re.search(r"\[[\s\S]*\]", text)
    if not m:
        raise RuntimeError(f"无法解析模型输出为数组: {text[:400]}")
    return json.loads(m.group(0))


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="LUMIR 端到端测试（DeepSeek）")
    parser.add_argument("--dataset", default=None, choices=sorted(DATASET_SPECS.keys()))
    parser.add_argument("--config", type=Path, default=None, help="config.yaml 路径")
    parser.add_argument("--skip-method-llm", action="store_true", help="步骤3改用 Table4")
    parser.add_argument(
        "--stop-after",
        choices=["entity", "retrieve", "methods", "features", "infer"],
        default="infer",
    )
    parser.add_argument("--question", default=None, help="覆盖默认自然语言问题")
    args = parser.parse_args()

    cfg = load_config(args.config)
    llm_cfg = cfg.get("llm", {})
    kb_cfg = cfg.get("knowledge_base", {})
    pipe = cfg.get("pipeline", {})

    dataset = args.dataset or (cfg.get("datasets") or {}).get("default", "chenpi")
    spec = DATASET_SPECS[dataset]
    question = args.question or spec["question"]
    skip_method_llm = args.skip_method_llm or bool(pipe.get("skip_method_llm", False))
    few_shot = int(pipe.get("few_shot", 8))
    test_ratio = float(pipe.get("test_ratio", 0.2))
    max_test = int(pipe.get("max_test_samples", 16))
    seed = int(pipe.get("random_seed", 42))
    top_k = int(kb_cfg.get("top_k", 2))

    api_key = get_api_key(cfg)
    base_url = os.getenv("LUMIR_BASE_URL") or llm_cfg.get("base_url") or "https://api.deepseek.com"
    model = os.getenv("LUMIR_MODEL") or llm_cfg.get("model") or "deepseek-chat"
    client = OpenAI(api_key=api_key, base_url=base_url)

    report: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "dataset": dataset,
        "config_path": cfg.get("_config_path"),
        "llm": {"base_url": base_url, "model": model},
        "question": question,
        "steps": {},
    }

    print("=" * 60)
    print("LUMIR E2E")
    print("=" * 60)
    print(f"dataset={dataset}  model={model}  stop_after={args.stop_after}")
    print(f"SKILL_ROOT={SKILL_ROOT}")
    print(f"BUNDLE_ROOT={LUMIR_ROOT}")

    # ---- 1 实体 ----
    print("\n[1] LLM 实体抽取")
    extracted = llm_extract_entities(
        client, model, float(llm_cfg.get("temperature_entity", 0.1)), question
    )
    research_object = extracted.get("research_object") or spec["object"]
    task_type = extracted.get("task_type") or spec["task"]
    report["steps"]["entity"] = {
        "research_object": research_object,
        "task_type": task_type,
        "raw": extracted,
    }
    print(f"    research_object={research_object}")
    print(f"    task_type={task_type}")
    if args.stop_after == "entity":
        return _save_and_exit(report)

    # ---- 2 检索 ----
    print("\n[2] BM25 知识库检索")
    primary = resolve_kb_primary(cfg)
    extra_raw = kb_cfg.get("extra")
    extra = resolve_path(str(extra_raw), SKILL_ROOT) if extra_raw else None
    papers = load_papers(primary, extra)
    matched = retrieve_papers(papers, research_object, top_k=top_k)
    report["steps"]["retrieve"] = {
        "primary": str(primary),
        "extra": str(extra) if extra and extra.is_file() else None,
        "n_papers": len(papers),
        "matched": matched,
    }
    for i, m in enumerate(matched, 1):
        print(f"    ({i}) score={m['score']:.3f} {m['paper_name'][:70]}")
        print(f"        pre={m['preprocessing_method']!r}")
        print(f"        feat={m['feature_extracting_method']!r}")
    if args.stop_after == "retrieve":
        return _save_and_exit(report)

    # ---- 3 方法 ----
    print("\n[3] 方法映射")
    method_source = "table4"
    selected = table4_methods(spec["method_key"], research_object)
    methods_map: Dict[str, Any] = {}
    if not skip_method_llm:
        try:
            methods_map = llm_map_methods(
                client, model, float(llm_cfg.get("temperature_method", 0.1)), matched
            )
            paper_order = [m["paper_name"] for m in matched]
            selected = select_by_majority(methods_map, paper_order)
            # 若投票结果空预处理，回退 Table4 预处理
            if not selected.get("preprocessing"):
                fb = table4_methods(spec["method_key"], research_object)
                selected["preprocessing"] = fb["preprocessing"]
            method_source = "llm_majority"
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] LLM 方法映射失败，回退 Table4: {exc}")
            selected = table4_methods(spec["method_key"], research_object)
            method_source = "table4_fallback"
    else:
        print("    --skip-method-llm / config: 使用 Table4")
    report["steps"]["methods"] = {
        "source": method_source,
        "methods_map": methods_map,
        "selected": selected,
    }
    print(f"    source={method_source}")
    print(f"    selected={json.dumps(selected, ensure_ascii=False)}")
    if args.stop_after == "methods":
        return _save_and_exit(report)

    # ---- 4 特征 ----
    print("\n[4] 本地预处理 + 特征提取")
    data, labels = load_xy(spec)
    processed, features, used = run_preprocess_feature(data, selected, labels, task_type)
    feat_shapes = {k: list(v.shape) for k, v in features.items()}
    report["steps"]["features"] = {
        "raw_shape": list(data.shape),
        "processed_shape": list(processed.shape),
        "used_methods": used,
        "feature_shapes": feat_shapes,
    }
    print(f"    raw={data.shape} processed={processed.shape} feats={feat_shapes}")
    if args.stop_after == "features":
        return _save_and_exit(report)

    # ---- 5 few-shot ----
    print("\n[5] LLM few-shot 推理")
    feat = next(iter(features.values()))
    temp_inf = float(llm_cfg.get("temperature_infer", 0.5))
    if task_type == "regression":
        if labels is None:
            raise SystemExit("回归任务缺少标签文件")
        train, test, y_true = build_reg_examples(feat, labels, few_shot, test_ratio, max_test, seed)
        preds, raw = fewshot_regress(client, model, temp_inf, train, test)
        # 对齐长度
        n = min(len(preds), len(y_true))
        preds_n, y_n = preds[:n], y_true[:n]
        # 过滤 nan
        mask = [i for i, p in enumerate(preds_n) if p == p]
        if len(mask) >= 2:
            r2 = float(r2_score([y_n[i] for i in mask], [preds_n[i] for i in mask]))
            rmse = float(mean_squared_error([y_n[i] for i in mask], [preds_n[i] for i in mask]) ** 0.5)
        else:
            r2, rmse = None, None
        metrics = {"r2": r2, "rmse": rmse, "n_test": n, "n_train_fewshot": len(train)}
        report["steps"]["infer"] = {
            "task": "regression",
            "metrics": metrics,
            "y_true": y_n,
            "y_pred": preds_n,
            "raw_output": raw[:2000],
        }
        print(f"    R2={r2} RMSE={rmse} n_test={n}")
    else:
        # classification / anomaly detection：本入口按分类评测标签
        train, test, y_true = build_cls_examples(feat, few_shot, test_ratio, max_test, seed)
        preds, raw = fewshot_classify(client, model, temp_inf, train, test)
        n = min(len(preds), len(y_true))
        acc = float(accuracy_score(y_true[:n], preds[:n]))
        metrics = {"accuracy": acc, "n_test": n, "n_train_fewshot": len(train)}
        report["steps"]["infer"] = {
            "task": task_type,
            "metrics": metrics,
            "y_true": y_true[:n],
            "y_pred": preds[:n],
            "raw_output": raw[:2000],
        }
        print(f"    Acc={acc:.4f} n_test={n}")

    _save_and_exit(report)


def _save_and_exit(report: Dict[str, Any]) -> None:
    runs = SKILL_ROOT / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ds = report.get("dataset", "run")
    path = runs / f"e2e_{ds}_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已写入: {path}")
    print("完成。")


if __name__ == "__main__":
    main()
