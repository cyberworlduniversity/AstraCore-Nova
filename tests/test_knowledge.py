import unittest
from nova_core.knowledge import EnglishKnowledgeEngine

class EnglishKnowledgeEngineTests(unittest.TestCase):
    def test_end_to_end_multi_sentence_reasoning(self):
        engine = EnglishKnowledgeEngine()
        result = engine.process("Arun is the father of Maya. Maya is the mother of Ravi.", source="test-document-1")
        self.assertIn(("grandparent", "Arun", "Ravi"), result.reasoning.facts)
        self.assertTrue(result.reasoning.saturated)
        self.assertTrue(any(item.fact == ("father", "Arun", "Maya") for item in result.memory.facts))
        self.assertTrue(any(item.fact == ("grandparent", "Arun", "Ravi") for item in result.memory.facts))

    def test_duplicate_ingestion_merges_source_provenance(self):
        engine = EnglishKnowledgeEngine()
        engine.process("Arun is the father of Maya.", source="source-a")
        result = engine.process("Arun is the father of Maya.", source="source-b")
        record = next(item for item in result.memory.facts if item.fact == ("father", "Arun", "Maya"))
        self.assertEqual(record.sources, ("source-a", "source-b"))

    def test_unsupported_english_is_not_guessed(self):
        engine = EnglishKnowledgeEngine()
        result = engine.process("The weather might be pleasant tomorrow.")
        self.assertEqual(result.extraction[0].facts, ())
        self.assertEqual(result.reasoning.derived, ())

    def test_configured_conflicts_are_reported_not_resolved(self):
        engine = EnglishKnowledgeEngine(contradiction_pairs=(("active", "inactive"),))
        engine.memory.add(("active", "account-9"), "source-a")
        engine.memory.add(("inactive", "account-9"), "source-b")
        report = engine.process("Arun is a friend of Maya.").memory
        self.assertEqual(len(report.conflicts), 1)
        self.assertEqual(len(report.facts), 3)

    def test_empty_input_rejected(self):
        engine = EnglishKnowledgeEngine()
        with self.assertRaises(ValueError):
            engine.process("   ")

if __name__ == "__main__":
    unittest.main()
