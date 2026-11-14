"""Bounded English fact memory with explicit contradiction policy."""
from __future__ import annotations
from dataclasses import dataclass

Fact = tuple[str, ...]

@dataclass(frozen=True)
class FactEvidence:
    evidence_id: int
    fact: Fact
    sources: tuple[str, ...]

@dataclass(frozen=True)
class FactConflict:
    left: FactEvidence
    right: FactEvidence
    reason: str

@dataclass(frozen=True)
class MemoryReport:
    facts: tuple[FactEvidence, ...]
    conflicts: tuple[FactConflict, ...]
    duplicates: int

class FactMemory:
    """Stores unique facts and source provenance; never silently resolves conflicts.

    contradiction_pairs contains explicitly declared opposing predicate pairs.
    A conflict is reported only when predicates are paired and all arguments match.
    """
    def __init__(self, capacity: int = 1000, contradiction_pairs=()):
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        pairs = set()
        for pair in contradiction_pairs:
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise ValueError("each contradiction pair must contain two predicates")
            left, right = pair
            if not all(isinstance(x, str) and x for x in (left, right)) or left == right:
                raise ValueError("contradiction predicates must be distinct non-empty strings")
            pairs.add(frozenset((left, right)))
        self.capacity = capacity
        self._pairs = frozenset(pairs)
        self._records = []
        self._by_fact = {}
        self._next_id = 1
        self._duplicates = 0

    @staticmethod
    def _validate_fact(fact):
        if not isinstance(fact, tuple) or len(fact) < 2:
            raise ValueError("fact must be a tuple with a predicate and at least one argument")
        if not all(isinstance(value, str) and value.strip() for value in fact):
            raise ValueError("fact fields must be non-empty strings")

    def add(self, fact: Fact, source: str) -> FactEvidence:
        self._validate_fact(fact)
        if not isinstance(source, str) or not source.strip():
            raise ValueError("source must be a non-empty string")
        source = source.strip()
        existing = self._by_fact.get(fact)
        if existing is not None:
            self._duplicates += 1
            sources = tuple(sorted(set(existing.sources) | {source}))
            updated = FactEvidence(existing.evidence_id, fact, sources)
            self._records[self._records.index(existing)] = updated
            self._by_fact[fact] = updated
            return updated
        if len(self._records) >= self.capacity:
            raise RuntimeError("fact memory capacity reached; no evidence was evicted")
        record = FactEvidence(self._next_id, fact, (source,))
        self._next_id += 1
        self._records.append(record)
        self._by_fact[fact] = record
        return record

    def conflicts(self):
        found = []
        records = sorted(self._records, key=lambda item: item.evidence_id)
        for index, left in enumerate(records):
            for right in records[index + 1:]:
                if (len(left.fact) == len(right.fact)
                    and left.fact[1:] == right.fact[1:]
                    and frozenset((left.fact[0], right.fact[0])) in self._pairs):
                    found.append(FactConflict(left, right, "configured_opposing_predicates"))
        return tuple(found)

    def report(self) -> MemoryReport:
        return MemoryReport(tuple(self._records), self.conflicts(), self._duplicates)

    def get(self, fact: Fact):
        self._validate_fact(fact)
        return self._by_fact.get(fact)

    def __len__(self):
        return len(self._records)

    @property
    def facts(self):
        return tuple(self._records)
