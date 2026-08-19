"""SpectralFormer：邻域波段 token + 跨层残差（Hong et al. 2022 IEEE TGRS）。"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset


def pick_device() -> torch.device:
    """优先 MPS/CUDA，否则 CPU。"""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class SpectralFormer(nn.Module):
    """
    滑动窗口把相邻波段编成 token，两层 TransformerEncoder，
    输出加输入残差（论文跨层 skip）。
    输入 (N, B)。
    """

    def __init__(self, bands: int, n_class: int, d_model: int = 64, nhead: int = 4, group: int = 3):
        super().__init__()
        self.group = min(max(2, group), bands)
        self.embed = nn.Linear(self.group, d_model)
        layer_kw = dict(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 2,
            batch_first=True,
            activation="gelu",
            norm_first=True,
        )
        self.enc1 = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(**layer_kw), num_layers=1, enable_nested_tensor=False
        )
        self.enc2 = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(**layer_kw), num_layers=1, enable_nested_tensor=False
        )
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, n_class)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (N, B) → (N, n_token, group)
        tokens = x.unfold(dimension=1, size=self.group, step=1)
        h0 = self.embed(tokens)
        h1 = self.enc1(h0)
        h2 = self.enc2(h1)
        h = self.norm(h2 + h0)
        return self.head(h.mean(dim=1))


def train_and_predict(
    cube: np.ndarray,
    gt: np.ndarray,
    *,
    epochs: int = 6,
    batch_size: int = 64,
    test_size: float = 0.3,
    lr: float = 1e-3,
    seed: int = 42,
) -> dict:
    """训练 SpectralFormer 并预测整图。"""
    torch.manual_seed(seed)
    h, w, b = cube.shape
    x = cube.reshape(-1, b).astype(np.float32)
    ymap = gt.reshape(-1)
    mask = ymap > 0
    if mask.sum() < 8:
        raise ValueError("有效标注像素过少")
    classes = np.unique(ymap[mask])
    class_to_idx = {int(c): i for i, c in enumerate(classes)}
    idx_to_class = {i: int(c) for c, i in class_to_idx.items()}
    xl = x[mask]
    yl = np.asarray([class_to_idx[int(v)] for v in ymap[mask]], dtype=np.int64)
    mu, sd = xl.mean(0, keepdims=True), xl.std(0, keepdims=True) + 1e-6
    xl = (xl - mu) / sd
    x_all = (x - mu) / sd
    strat = yl if len(np.unique(yl)) > 1 else None
    x_tr, x_te, y_tr, y_te = train_test_split(xl, yl, test_size=test_size, random_state=seed, stratify=strat)

    device = pick_device()
    nhead = 4 if 64 % 4 == 0 else 2
    model = SpectralFormer(b, len(classes), d_model=64, nhead=nhead).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    loader = DataLoader(
        TensorDataset(torch.from_numpy(x_tr), torch.from_numpy(y_tr)),
        batch_size=min(batch_size, max(1, len(x_tr))),
        shuffle=True,
    )
    model.train()
    for _ in range(max(1, epochs)):
        for xb, yb in loader:
            opt.zero_grad()
            loss = loss_fn(model(xb.to(device)), yb.to(device))
            loss.backward()
            opt.step()
    model.eval()
    with torch.no_grad():
        pred_te = model(torch.from_numpy(x_te).to(device)).argmax(1).cpu().numpy()
        pred_all = model(torch.from_numpy(x_all).to(device)).argmax(1).cpu().numpy()
    from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix

    oa = float(accuracy_score(y_te, pred_te))
    kappa = float(cohen_kappa_score(y_te, pred_te))
    cm = confusion_matrix(y_te, pred_te)
    with np.errstate(divide="ignore", invalid="ignore"):
        per = np.diag(cm) / cm.sum(axis=1)
    per = per[~np.isnan(per)]
    aa = float(per.mean()) if len(per) else 0.0
    pred_map = np.asarray([idx_to_class[int(i)] for i in pred_all], dtype=np.int32).reshape(h, w)
    return {
        "oa": oa,
        "aa": aa,
        "kappa": kappa,
        "n_train": int(len(y_tr)),
        "n_test": int(len(y_te)),
        "classes": [int(c) for c in classes],
        "device": str(device),
        "architecture": "SpectralFormer",
        "pred_map": pred_map,
    }
