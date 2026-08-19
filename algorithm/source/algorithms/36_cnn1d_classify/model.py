"""Hu et al. 2015 1-D CNN 高光谱分类（IEEE JSTARS）。"""
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


class Hu2015CNN(nn.Module):
    """
    1-D CNN：Conv1d(20, k) → ReLU → MaxPool → FC(100) → Dropout → FC(C)。
    核长随波段数自适应，保持论文结构。
    """

    def __init__(self, bands: int, n_class: int):
        super().__init__()
        k = min(24, bands if bands % 2 == 1 else max(3, bands - 1))
        k = max(3, k)
        if k > bands:
            k = bands
        self.conv = nn.Conv1d(1, 20, kernel_size=k)
        length = bands - k + 1
        self.do_pool = length >= 4
        if self.do_pool:
            self.pool = nn.MaxPool1d(kernel_size=2)
            length = length // 2
        self.fc1 = nn.Linear(20 * length, 100)
        self.drop = nn.Dropout(0.5)
        self.fc2 = nn.Linear(100, n_class)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = torch.relu(self.conv(x))
        if self.do_pool:
            h = self.pool(h)
        h = torch.relu(self.fc1(torch.flatten(h, 1)))
        return self.fc2(self.drop(h))


def train_and_predict(
    cube: np.ndarray,
    gt: np.ndarray,
    *,
    epochs: int = 8,
    batch_size: int = 64,
    test_size: float = 0.3,
    lr: float = 1e-3,
    seed: int = 42,
) -> dict:
    """训练 Hu 2015 1-D CNN 并预测整图。"""
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
    model = Hu2015CNN(b, len(classes)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    loader = DataLoader(
        TensorDataset(torch.from_numpy(x_tr[:, None, :]), torch.from_numpy(y_tr)),
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
        pred_te = model(torch.from_numpy(x_te[:, None, :]).to(device)).argmax(1).cpu().numpy()
        pred_all = model(torch.from_numpy(x_all[:, None, :]).to(device)).argmax(1).cpu().numpy()
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
        "architecture": "Hu2015_1DCNN",
        "pred_map": pred_map,
    }
