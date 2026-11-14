"""Bounded English fact memory with explicit contradiction policy and JSON persistence."""
from __future__ import annotations
from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile

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

    SCHEMA = "astracore-nova-fact-memory"
    VERSION = 1
    MAX_FILE_BYTES = 5 * 1024 * 1024

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

    def save(self, path: str | os.PathLike) -> None:
        """Atomically persist memory to a versioned JSON file."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": self.SCHEMA,
            "version": self.VERSION,
            "capacity": self.capacity,
            "contradiction_pairs": [
                sorted(pair) for pair in sorted(self._pairs, key=lambda p: tuple(sorted(p)))
            ],
            "duplicates": self._duplicates,
            "next_id": self._next_id,
            "records": [
                {
                    "evidence_id": item.evidence_id,
                    "fact": list(item.fact),
                    "sources": list(item.sources),
                }
                for item in self._records
            ],
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if len(encoded.encode("utf-8")) > self.MAX_FILE_BYTES:
            raise ValueError("serialized memory exceeds the file size limit")
        fd, temporary = tempfile.mkstemp(
            prefix=destination.name + ".", suffix=".tmp", dir=str(destination.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        except Exception:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise

    @classmethod
    def load(cls, path: str | os.PathLike) -> "FactMemory":
        """Load and strictly validate a versioned fact-memory JSON file."""
        source_path = Path(path)
        if source_path.stat().st_size > cls.MAX_FILE_BYTES:
            raise ValueError("memory file exceeds the file size limit")
        try:
            payload = json.loads(source_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("memory file is not valid UTF-8 JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("memory payload must be a JSON object")
        if payload.get("schema") != cls.SCHEMA or payload.get("version") != cls.VERSION:
            raise ValueError("unsupported memory schema or version")
        capacity = payload.get("capacity")
        pairs = payload.get("contradiction_pairs")
        records = payload.get("records")
        duplicates = payload.get("duplicates")
        next_id = payload.get("next_id")
        if not isinstance(pairs, list) or not isinstance(records, list):
            raise ValueError("memory pairs and records must be lists")
        if not isinstance(duplicates, int) or duplicates < 0:
            raise ValueError("duplicate count must be a non-negative integer")
        if not isinstance(next_id, int) or next_id < 1:
            raise ValueError("next evidence ID must be a positive integer")
        memory = cls(capacity=capacity, contradiction_pairs=pairs)
        if len(records) > memory.capacity:
            raise ValueError("stored records exceed declared memory capacity")
        seen_ids = set()
        for entry in records:
            if not isinstance(entry, dict):
                raise ValueError("each memory record must be an object")
            evidence_id = entry.get("evidence_id")
            fact_data = entry.get("fact")
            sources = entry.get("sources")
            if not isinstance(evidence_id, int) or evidence_id < 1 or evidence_id in seen_ids:
                raise ValueError("evidence IDs must be unique positive integers")
            if not isinstance(fact_data, list) or len(fact_data) < 2:
                raise ValueError("stored fact must be a list with at least two fields")
            if not all(isinstance(value, str) and value.strip() for value in fact_data):
                raise ValueError("stored fact fields must be non-empty strings")
            if not isinstance(sources, list) or not sources:
                raise ValueError("each fact must have at least one source")
            if not all(isinstance(value, str) and value.strip() for value in sources):
                raise ValueError("source labels must be non-empty strings")
            fact = tuple(fact_data)
            if fact in memory._by_fact:
                raise ValueError("duplicate facts are not valid serialized records")
            record = FactEvidence(evidence_id, fact, tuple(sorted(set(sources))))
            memory._records.append(record)
            memory._by_fact[fact] = record
            seen_ids.add(evidence_id)
        if next_id <= max(seen_ids, default=0):
            raise ValueError("next evidence ID must exceed all stored IDs")
        memory._next_id = next_id
        memory._duplicates = duplicates
        return memory

    def __len__(self):
        return len(self._records)

    @property
    def facts(self):
        return tuple(self._records)
