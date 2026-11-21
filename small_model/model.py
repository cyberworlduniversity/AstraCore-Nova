from __future__ import annotations

import torch
from torch import nn


class NovaTiny(nn.Module):
    """Four-layer byte-level GRU language model."""

    def __init__(self, vocab_size: int = 256, embedding_dim: int = 64,
                 hidden_size: int = 128, num_layers: int = 4,
                 dropout: float = 0.1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.gru = nn.GRU(
            input_size=embedding_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.output = nn.Linear(hidden_size, vocab_size)

    def forward(self, tokens: torch.Tensor, hidden=None):
        x = self.embedding(tokens)
        x, hidden = self.gru(x, hidden)
        logits = self.output(x)
        return logits, hidden

    def parameter_count(self) -> int:
        return sum(p.numel() for p in self.parameters())
