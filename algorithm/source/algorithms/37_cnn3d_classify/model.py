"""HybridSN：3D-CNN + 2D-CNN 空谱分类（Roy et al. 2020 IEEE GRSL）。"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset


def pick_device() -> torch.device:
    """优先 Apple MPS，其次 CUDA，最后 CPU。"""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class HybridSN(nn.Module):
    """
    输入 (N, 1, B, P, P)。
    Conv3d(8, k=7) → Conv3d(16, k=5) → Conv3d(32, k=3) → reshape → Conv2d(64) → FC。
    核长随波段数裁剪，空间维 padding 保持 patch。
    """

    def __init__(self, bands: int, n_class: int, patch: int = 5):
        super().__init__()
        k1 = min(7, bands)
        d1 = bands - k1 + 1
        k2 = min(5, max(1, d1))
        d2 = d1 - k2 + 1
        k3 = min(3, max(1, d2))
        d3 = d2 - k3 + 1
        self.c1 = nn.Conv3d(1, 8, kernel_size=(k1, 3, 3), padding=(0, 1, 1))
        self.bn1 = nn.BatchNorm3d(8)
        self.c2 = nn.Conv3d(8, 16, kernel_size=(k2, 3, 3), padding=(0, 1, 1))
        self.bn2 = nn.BatchNorm3d(16)
        self.c3 = nn.Conv3d(16, 32, kernel_size=(k3, 3, 3), padding=(0, 1, 1))
        self.bn3 = nn.BatchNorm3d(32)
        self.c2d = nn.Conv2d(32 * d3, 64, kernel_size=3, padding=1)
        self.bn2d = nn.BatchNorm2d(64)
        self.drop = nn.Dropout(0.4)
        self.fc = nn.Linear(64, n_class)
        self.patch = patch
        self.bands = bands

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = torch.relu(self.bn1(self.c1(x)))
        h = torch.relu(self.bn2(self.c2(h)))
        h = torch.relu(self.bn3(self.c3(h)))
        n, c, d, p, q = h.shape
        h = h.reshape(n, c * d, p, q)
        h = torch.relu(self.bn2d(self.c2d(h)))
        h = torch.mean(h, dim=(2, 3))
        return self.fc(self.drop(h))


def apply_pca(cube: np.ndarray, n_components: int) -> np.ndarray:
    """对 H×W×B 做 PCA，返回 H×W×C。"""
    h, w, b = cube.shape
    n = min(n_components, b, h * w)
    flat = np.ascontiguousarray(cube.reshape(-1, b), dtype=np.float64)
    flat = (flat - flat.mean(axis=0, keepdims=True)) / (flat.std(axis=0, keepdims=True) + 1e-8)
    flat = PCA(n_components=n, whiten=True, svd_solver="full").fit_transform(flat)
    return flat.reshape(h, w, n).astype(np.float32)


def _pad(cube: np.ndarray, margin: int) -> np.ndarray:
    return np.pad(cube, ((margin, margin), (margin, margin), (0, 0)), mode="edge")


def extract_patches(
    cube: np.ndarray,
    gt: np.ndarray,
    patch_size: int,
    *,
    labeled_only: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """提取以每个像素为中心的 patch，返回 (N,P,P,B)、(N,)、(N,2)。"""
    margin = patch_size // 2
    padded = _pad(cube.astype(np.float32), margin)
    h, w = gt.shape
    patches, labels, coords = [], [], []
    for r in range(h):
        for c in range(w):
            lab = int(gt[r, c])
            if labeled_only and lab <= 0:
                continue
            patch = padded[r : r + patch_size, c : c + patch_size, :]
            patches.append(patch)
            labels.append(lab)
            coords.append((r, c))
    if not patches:
        return (
            np.zeros((0, patch_size, patch_size, cube.shape[2]), dtype=np.float32),
            np.zeros((0,), dtype=np.int64),
            np.zeros((0, 2), dtype=np.int64),
        )
    return (
        np.stack(patches, axis=0),
        np.asarray(labels, dtype=np.int64),
        np.asarray(coords, dtype=np.int64),
    )


def _to_ncbpp(patches: np.ndarray) -> np.ndarray:
    """(N,P,P,B) → (N,1,B,P,P)"""
    return np.moveaxis(patches, -1, 1)[:, None, ...].astype(np.float32)


def train_and_predict(
    cube: np.ndarray,
    gt: np.ndarray,
    *,
    patch_size: int = 5,
    pca_components: int = 8,
    epochs: int = 8,
    batch_size: int = 64,
    test_size: float = 0.3,
    lr: float = 1e-3,
    seed: int = 42,
) -> dict:
    """训练 HybridSN 并预测整幅分类图。"""
    torch.manual_seed(seed)
    cube_pca = apply_pca(cube, pca_components)
    mu = cube_pca.mean(axis=(0, 1), keepdims=True)
    sigma = cube_pca.std(axis=(0, 1), keepdims=True) + 1e-6
    cube_pca = (cube_pca - mu) / sigma

    patches, labels_raw, _ = extract_patches(cube_pca, gt, patch_size, labeled_only=True)
    if len(labels_raw) < 8:
        raise ValueError("有效标注像素过少，无法训练 HybridSN")

    classes = np.unique(labels_raw)
    class_to_idx = {int(c): i for i, c in enumerate(classes)}
    idx_to_class = {i: int(c) for c, i in class_to_idx.items()}
    y = np.asarray([class_to_idx[int(v)] for v in labels_raw], dtype=np.int64)
    x = _to_ncbpp(patches)

    strat = y if len(np.unique(y)) > 1 else None
    x_tr, x_te, y_tr, y_te = train_test_split(x, y, test_size=test_size, random_state=seed, stratify=strat)

    device = pick_device()
    model = HybridSN(bands=cube_pca.shape[2], n_class=len(classes), patch=patch_size).to(device)
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
        pred_te = model(torch.from_numpy(x_te).to(device)).argmax(dim=1).cpu().numpy()

    from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix

    oa = float(accuracy_score(y_te, pred_te))
    kappa = float(cohen_kappa_score(y_te, pred_te))
    cm = confusion_matrix(y_te, pred_te)
    with np.errstate(divide="ignore", invalid="ignore"):
        per = np.diag(cm) / cm.sum(axis=1)
    per = per[~np.isnan(per)]
    aa = float(per.mean()) if len(per) else 0.0

    all_patches, _, coords = extract_patches(cube_pca, np.ones_like(gt), patch_size, labeled_only=False)
    pred_map = np.zeros(gt.shape, dtype=np.int32)
    if len(all_patches):
        with torch.no_grad():
            xs = torch.from_numpy(_to_ncbpp(all_patches))
            outs = []
            bs = 256
            for i in range(0, len(xs), bs):
                outs.append(model(xs[i : i + bs].to(device)).argmax(dim=1).cpu().numpy())
            pred_idx = np.concatenate(outs)
        for (r, c), pi in zip(coords, pred_idx):
            pred_map[r, c] = idx_to_class[int(pi)]

    return {
        "oa": oa,
        "aa": aa,
        "kappa": kappa,
        "n_train": int(len(y_tr)),
        "n_test": int(len(y_te)),
        "classes": [int(c) for c in classes],
        "device": str(device),
        "bands_after_pca": int(cube_pca.shape[2]),
        "architecture": "HybridSN",
        "pred_map": pred_map,
    }
