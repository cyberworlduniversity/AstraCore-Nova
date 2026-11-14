import unittest
from nova_core.fact_memory import FactMemory

class FactMemoryTests(unittest.TestCase):
    def test_add_fact_with_source(self):
        memory = FactMemory()
        record = memory.add(("owns", "Arun", "Car"), "email-1")
        self.assertEqual(record.evidence_id, 1)
        self.assertEqual(record.sources, ("email-1",))

    def test_duplicate_fact_merges_provenance(self):
        memory = FactMemory()
        first = memory.add(("owns", "Arun", "Car"), "email-1")
        second = memory.add(("owns", "Arun", "Car"), "meeting-2")
        self.assertEqual(first.evidence_id, second.evidence_id)
        self.assertEqual(second.sources, ("email-1", "meeting-2"))
        self.assertEqual(len(memory), 1)
        self.assertEqual(memory.report().duplicates, 1)

    def test_same_source_duplicate_is_idempotent(self):
        memory = FactMemory()
        memory.add(("owns", "Arun", "Car"), "source-a")
        memory.add(("owns", "Arun", "Car"), "source-a")
        self.assertEqual(memory.facts[0].sources, ("source-a",))
        self.assertEqual(memory.report().duplicates, 1)

    def test_configured_opposing_facts_are_reported(self):
        memory = FactMemory(contradiction_pairs=(("active", "inactive"),))
        memory.add(("active", "account-7"), "record-1")
        memory.add(("inactive", "account-7"), "record-2")
        report = memory.report()
        self.assertEqual(len(report.conflicts), 1)
        conflict = report.conflicts[0]
        self.assertEqual(conflict.left.fact, ("active", "account-7"))
        self.assertEqual(conflict.right.fact, ("inactive", "account-7"))
        self.assertEqual(conflict.reason, "configured_opposing_predicates")
        self.assertEqual(len(report.facts), 2)

    def test_unconfigured_different_predicates_are_not_conflicts(self):
        memory = FactMemory()
        memory.add(("father", "Arun", "Maya"), "source-1")
        memory.add(("mother", "Arun", "Maya"), "source-2")
        self.assertEqual(memory.conflicts(), ())

    def test_conflict_requires_same_arguments_and_arity(self):
        memory = FactMemory(contradiction_pairs=(("owns", "not_owns"),))
        memory.add(("owns", "Arun", "Car"), "source-1")
        memory.add(("not_owns", "Arun", "Bike"), "source-2")
        memory.add(("not_owns", "Arun", "Car", "today"), "source-3")
        self.assertEqual(memory.conflicts(), ())

    def test_capacity_does_not_silently_evict_evidence(self):
        memory = FactMemory(capacity=1)
        memory.add(("likes", "Arun", "Tea"), "source-1")
        with self.assertRaises(RuntimeError):
            memory.add(("likes", "Maya", "Coffee"), "source-2")
        self.assertEqual(len(memory), 1)

    def test_invalid_values(self):
        memory = FactMemory()
        with self.assertRaises(ValueError):
            memory.add(("owns", ""), "source")
        with self.assertRaises(ValueError):
            memory.add(("owns", "Arun"), "")
        with self.assertRaises(ValueError):
            FactMemory(contradiction_pairs=(("same", "same"),))

    def test_conflict_order_is_deterministic(self):
        def run():
            memory = FactMemory(contradiction_pairs=(("yes", "no"),))
            memory.add(("yes", "item"), "a")
            memory.add(("no", "item"), "b")
            return memory.report()
        self.assertEqual(run(), run())

if __name__ == "__main__":
    unittest.main()
