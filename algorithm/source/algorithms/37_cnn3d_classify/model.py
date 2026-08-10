"""轻量 3D-CNN：对齐小模型库空–谱 patch 分类思路（PCA + 邻域立方体）。"""
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


class Tiny3DCNN(nn.Module):
    """小型 3D-CNN：输入 (N,1,P,P,B) → 类别 logits。"""

    def __init__(self, bands: int, n_class: int, patch: int = 5):
        super().__init__()
        # 频谱核不宜超过波段数
        k_b1 = min(7, max(3, bands // 2))
        k_b2 = min(5, max(2, bands // 3))
        self.net = nn.Sequential(
            nn.Conv3d(1, 16, kernel_size=(3, 3, k_b1), padding=(1, 1, 0)),
            nn.BatchNorm3d(16),
            nn.ReLU(inplace=True),
            nn.Conv3d(16, 32, kernel_size=(3, 3, k_b2), padding=(1, 1, 0)),
            nn.BatchNorm3d(32),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool3d((1, 1, 1)),
            nn.Flatten(),
            nn.Linear(32, n_class),
        )
        self.patch = patch
        self.bands = bands

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def apply_pca(cube: np.ndarray, n_components: int) -> np.ndarray:
    """对 H×W×B 做 PCA，返回 H×W×C。"""
    h, w, b = cube.shape
    n = min(n_components, b, h * w)
    flat = np.ascontiguousarray(cube.reshape(-1, b), dtype=np.float64)
    # 先标准化，避免病态协方差触发 sklearn 数值告警
    flat = (flat - flat.mean(axis=0, keepdims=True)) / (flat.std(axis=0, keepdims=True) + 1e-8)
    flat = PCA(n_components=n, whiten=True, svd_solver="randomized").fit_transform(flat)
    return flat.reshape(h, w, n).astype(np.float32)


def _pad(cube: np.ndarray, margin: int) -> np.ndarray:
    h, w, b = cube.shape
    out = np.zeros((h + 2 * margin, w + 2 * margin, b), dtype=cube.dtype)
    out[margin : margin + h, margin : margin + w] = cube
    return out


def extract_patches(
    cube: np.ndarray,
    gt: np.ndarray,
    patch_size: int,
    *,
    labeled_only: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    提取以每个像素为中心的 patch。

    返回：
    - patches: (N, P, P, B)
    - labels: (N,) 原始标签（未减 1）
    - coords: (N, 2) 行列坐标
    """
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


def _to_nchwbd(patches: np.ndarray) -> np.ndarray:
    """(N,P,P,B) → (N,1,P,P,B)"""
    return patches[:, None, ...].astype(np.float32)


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
    """
    训练轻量 3D-CNN 并预测整幅分类图。

    gt: 0 为背景；正整数为类别 ID（不必从 1 连续，内部会映射）。
    """
    rng = np.random.RandomState(seed)
    torch.manual_seed(seed)

    cube_pca = apply_pca(cube, pca_components)
    # 标准化
    mu = cube_pca.mean(axis=(0, 1), keepdims=True)
    sigma = cube_pca.std(axis=(0, 1), keepdims=True) + 1e-6
    cube_pca = (cube_pca - mu) / sigma

    patches, labels_raw, _ = extract_patches(cube_pca, gt, patch_size, labeled_only=True)
    if len(labels_raw) < 8:
        raise ValueError("有效标注像素过少，无法训练 3D-CNN")

    classes = np.unique(labels_raw)
    class_to_idx = {int(c): i for i, c in enumerate(classes)}
    idx_to_class = {i: int(c) for c, i in class_to_idx.items()}
    y = np.asarray([class_to_idx[int(v)] for v in labels_raw], dtype=np.int64)
    x = _to_nchwbd(patches)

    strat = y if len(np.unique(y)) > 1 else None
    x_tr, x_te, y_tr, y_te = train_test_split(
        x, y, test_size=test_size, random_state=seed, stratify=strat
    )

    device = pick_device()
    model = Tiny3DCNN(bands=cube_pca.shape[2], n_class=len(classes), patch=patch_size).to(device)
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
            xb = xb.to(device)
            yb = yb.to(device)
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()

    model.eval()
    with torch.no_grad():
        logits = model(torch.from_numpy(x_te).to(device))
        pred_te = logits.argmax(dim=1).cpu().numpy()

    from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix

    oa = float(accuracy_score(y_te, pred_te))
    kappa = float(cohen_kappa_score(y_te, pred_te))
    cm = confusion_matrix(y_te, pred_te)
    with np.errstate(divide="ignore", invalid="ignore"):
        per = np.diag(cm) / cm.sum(axis=1)
    per = per[~np.isnan(per)]
    aa = float(per.mean()) if len(per) else 0.0

    # 整图推理（含背景像素，背景也给最近邻类；最终背景仍标 0）
    all_patches, _, coords = extract_patches(cube_pca, np.ones_like(gt), patch_size, labeled_only=False)
    pred_map = np.zeros(gt.shape, dtype=np.int32)
    if len(all_patches):
        with torch.no_grad():
            xs = torch.from_numpy(_to_nchwbd(all_patches))
            outs = []
            bs = 256
            for i in range(0, len(xs), bs):
                outs.append(model(xs[i : i + bs].to(device)).argmax(dim=1).cpu().numpy())
            pred_idx = np.concatenate(outs)
        for (r, c), pi in zip(coords, pred_idx):
            pred_map[r, c] = idx_to_class[int(pi)]
        # 无标注区可保留预测；也可把原背景强制为 0——业务上常保留全图预测
        # 这里：仅在有标签训练的场景输出全图预测图

    return {
        "oa": oa,
        "aa": aa,
        "kappa": kappa,
        "n_train": int(len(y_tr)),
        "n_test": int(len(y_te)),
        "classes": [int(c) for c in classes],
        "device": str(device),
        "bands_after_pca": int(cube_pca.shape[2]),
        "pred_map": pred_map,
        "rng_note": int(rng.randint(0, 1e6)),
    }
