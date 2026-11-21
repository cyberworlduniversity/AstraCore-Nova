from __future__ import annotations

from pathlib import Path
import torch


def load_text_bytes(directory: str) -> torch.Tensor:
    root = Path(directory)
    files = sorted(p for p in root.rglob("*.txt") if p.is_file())
    if not files:
        raise FileNotFoundError(f"No .txt training files found under {root}")
    data = b"\n".join(p.read_bytes() for p in files)
    if len(data) < 100:
        raise ValueError("Training corpus is too small; provide at least 100 bytes.")
    return torch.tensor(list(data), dtype=torch.long)


def split_data(data: torch.Tensor, train_fraction: float = 0.9):
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be between 0 and 1")
    split = int(len(data) * train_fraction)
    if split < 1 or split >= len(data):
        raise ValueError("Corpus is too small for train/validation split")
    return data[:split], data[split:]


def get_batch(source: torch.Tensor, batch_size: int, seq_len: int, device):
    if len(source) <= seq_len + 1:
        raise ValueError("Split must contain more bytes than seq_len + 1")
    starts = torch.randint(0, len(source) - seq_len - 1, (batch_size,))
    x = torch.stack([source[i:i + seq_len] for i in starts])
    y = torch.stack([source[i + 1:i + seq_len + 1] for i in starts])
    return x.to(device), y.to(device)
