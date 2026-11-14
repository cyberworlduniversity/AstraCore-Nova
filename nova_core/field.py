"""Relational Field State (RFS): deterministic raw-Unicode state encoding.

This is a hand-designed numerical transform, not a trained model.
"""
from __future__ import annotations
from math import cos, sin, sqrt

DEFAULT_WIDTH = 48

def _unit(values: list[float]) -> tuple[float, ...]:
    norm = sqrt(sum(v * v for v in values))
    if norm == 0.0:
        return tuple(values)
    return tuple(v / norm for v in values)

def encode_state(text: str, width: int = DEFAULT_WIDTH) -> tuple[float, ...]:
    """Encode every Unicode code point directly into a bounded state vector."""
    if width < 4:
        raise ValueError("width must be >= 4")
    state = [0.0] * width
    for pos, char in enumerate(text):
        scalar = ord(char) / 0x10FFFF
        phase = pos + 1
        drive = [sin((i + 1) * (scalar + .17) * phase * .013)
                 + cos((i + 1) * (scalar + .31) / (phase + 1))
                 for i in range(width)]
        drive = list(_unit(drive))
        nxt = [0.0] * width
        for i in range(width):
            mixed = .68 * state[i] + .16 * state[(i - 1) % width] + .16 * state[(i + 1) % width] + .22 * drive[i]
            nxt[i] = mixed / (1.0 + abs(mixed))
        state = nxt
    return _unit(state)

def field_similarity(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if len(a) != len(b):
        raise ValueError("field dimensions must match")
    return sum(x * y for x, y in zip(a, b))
