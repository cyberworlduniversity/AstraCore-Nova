"""Bounded, transparent episodic memory for the Nova prototype."""
from __future__ import annotations
from dataclasses import dataclass
from .field import encode_state, field_similarity

@dataclass(frozen=True)
class Episode:
    text: str
    state: tuple[float, ...]
    tag: str = "example"

class EpisodicMemory:
    def __init__(self, capacity: int = 256, width: int = 48):
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self.capacity, self.width = capacity, width
        self._items: list[Episode] = []

    def remember(self, text: str, tag: str = "example") -> None:
        if not isinstance(text, str) or not text:
            raise ValueError("text must be a non-empty string")
        self._items.append(Episode(text, encode_state(text, self.width), tag))
        if len(self._items) > self.capacity:
            self._items.pop(0)

    def recall(self, query: str, limit: int = 3) -> list[tuple[float, Episode]]:
        if limit < 1:
            return []
        q = encode_state(query, self.width)
        ranked = [(field_similarity(q, item.state), item) for item in self._items]
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return ranked[:limit]

    def __len__(self) -> int:
        return len(self._items)
