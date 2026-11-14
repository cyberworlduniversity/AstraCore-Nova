import json
import tempfile
import unittest
from pathlib import Path
from nova_core.fact_memory import FactMemory

class FactMemoryPersistenceTests(unittest.TestCase):
    def test_round_trip_preserves_facts_sources_conflicts_and_counters(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "state" / "memory.json"
            memory = FactMemory(capacity=20, contradiction_pairs=(("enabled", "disabled"),))
            memory.add(("enabled", "service-1"), "audit-a")
            memory.add(("enabled", "service-1"), "audit-b")
            memory.add(("disabled", "service-1"), "audit-c")
            memory.add(("owns", "Maya", "Laptop"), "inventory")
            before = memory.report()
            memory.save(path)
            restored = FactMemory.load(path)
            self.assertEqual(restored.report(), before)
            self.assertEqual(restored.capacity, 20)
            self.assertEqual(restored.add(("new", "record"), "after-reload").evidence_id, 4)

    def test_saved_file_is_valid_versioned_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            memory = FactMemory()
            memory.add(("likes", "Arun", "Tea"), "source")
            memory.save(path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], FactMemory.SCHEMA)
            self.assertEqual(payload["version"], FactMemory.VERSION)

    def test_unknown_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            path.write_text(json.dumps({"schema": "wrong", "version": 1}), encoding="utf-8")
            with self.assertRaises(ValueError):
                FactMemory.load(path)

    def test_duplicate_fact_records_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            payload = {
                "schema": FactMemory.SCHEMA,
                "version": FactMemory.VERSION,
                "capacity": 5,
                "contradiction_pairs": [],
                "duplicates": 0,
                "next_id": 3,
                "records": [
                    {"evidence_id": 1, "fact": ["likes", "A", "Tea"], "sources": ["s1"]},
                    {"evidence_id": 2, "fact": ["likes", "A", "Tea"], "sources": ["s2"]}
                ]
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                FactMemory.load(path)

    def test_invalid_next_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            payload = {
                "schema": FactMemory.SCHEMA,
                "version": FactMemory.VERSION,
                "capacity": 5,
                "contradiction_pairs": [],
                "duplicates": 0,
                "next_id": 1,
                "records": [
                    {"evidence_id": 1, "fact": ["likes", "A", "Tea"], "sources": ["s1"]}
                ]
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                FactMemory.load(path)

if __name__ == "__main__":
    unittest.main()
