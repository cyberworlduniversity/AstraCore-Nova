"""AstraCore Nova Field Dynamics (NFD), clean-room research prototype.

This is a deterministic field encoder and associative memory experiment.
It is deliberately not a language model and makes no claim of general
semantic understanding.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin, sqrt
from typing import Iterable


FIELD_WIDTH = 32


def _normalise(values: list[float]) -> list[float]:
    norm = sqrt(sum(value * value for value in values))
    if norm == 0.0:
        return values
    return [value / norm for value in values]


def _couple(field: list[float], drive: list[float]) -> list[float]:
    """One bounded local interaction step across the field."""
    width = len(field)
    updated = [0.0] * width
    for i in range(width):
        left = field[(i - 1) % width]
        right = field[(i + 1) % width]
        centre = field[i]
        updated[i] = (
            0.72 * centre
            + 0.13 * left
            + 0.13 * right
            + 0.18 * drive[i]
        )
        # Smooth bounded activation without external numerical libraries.
        updated[i] = updated[i] / (1.0 + abs(updated[i]))
    return updated


def encode_field(text: str, width: int = FIELD_WIDTH) -> tuple[float, ...]:
    """Map a raw Unicode stream into a fixed-size dynamic field.

    No vocabulary, token IDs, subword segmentation, or tokenizer is used.
    Python's Unicode code points are consumed in their original sequence.
    """
    if width < 4:
        raise ValueError("width must be at least 4")

    field = [0.0] * width
    if not text:
        return tuple(field)

    for position, character in enumerate(text):
        scalar = ord(character) / 0x10FFFF
        phase = position + 1
        drive = [
            sin((i + 1) * (scalar + 0.25) * phase * 0.017)
            + cos((i + 1) * (scalar + 0.5) / (phase + 1))
            for i in range(width)
        ]
        drive = _normalise(drive)
        field = _couple(field, drive)

    return tuple(_normalise(field))


def similarity(a: Iterable[float], b: Iterable[float]) -> float:
    left, right = tuple(a), tuple(b)
    if len(left) != len(right):
        raise ValueError("field dimensions must match")
    return sum(x * y for x, y in zip(left, right))


@dataclass(frozen=True)
class MemoryRecord:
    label: str
    content: str
    field: tuple[float, ...]


class NovaFieldMemory:
    """Small bounded associative store over NFD field signatures."""

    def __init__(self, capacity: int = 256, width: int = FIELD_WIDTH):
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.width = width
        self._records: list[MemoryRecord] = []

    def store(self, label: str, content: str) -> None:
        record = MemoryRecord(label, content, encode_field(content, self.width))
        self._records = [r for r in self._records if r.label != label]
        self._records.append(record)
        if len(self._records) > self.capacity:
            self._records.pop(0)

    def recall(self, query: str, limit: int = 3) -> list[tuple[float, MemoryRecord]]:
        if limit < 1:
            return []
        query_field = encode_field(query, self.width)
        ranked = [
            (similarity(query_field, record.field), record)
            for record in self._records
        ]
        ranked.sort(key=lambda item: item[0], reverse=True)
        return ranked[:limit]

    def __len__(self) -> int:
        return len(self._records)
