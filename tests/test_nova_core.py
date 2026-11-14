import unittest
from nova_core import NovaAgent, EpisodicMemory, encode_state, field_similarity

class NovaCoreTests(unittest.TestCase):
    def test_deterministic_encoding(self):
        self.assertEqual(encode_state("English"), encode_state("English"))

    def test_width_and_normalization(self):
        v = encode_state("English + Python")
        self.assertEqual(len(v), 48)
        self.assertAlmostEqual(sum(x*x for x in v), 1.0, places=6)

    def test_empty_input_is_zero_state(self):
        self.assertEqual(set(encode_state("")), {0.0})

    def test_similarity_self(self):
        v = encode_state("Nova")
        self.assertAlmostEqual(field_similarity(v, v), 1.0, places=6)

    def test_memory_capacity(self):
        m = EpisodicMemory(capacity=1)
        m.remember("first")
        m.remember("second")
        self.assertEqual(len(m), 1)
        self.assertEqual(m.recall("second")[0][1].text, "second")

    def test_agent_reports_unknown_without_evidence(self):
        a = NovaAgent(threshold=1.0)
        reply = a.respond("What is quantum computing?")
        self.assertEqual(reply.mode, "unknown")
        self.assertEqual(reply.evidence, ())

    def test_agent_retrieves_exact_example(self):
        a = NovaAgent(threshold=0.99)
        a.observe("AstraCore Nova is an experimental project.")
        reply = a.respond("AstraCore Nova is an experimental project.")
        self.assertEqual(reply.mode, "memory_retrieval")
        self.assertTrue(reply.evidence)

if __name__ == "__main__":
    unittest.main()
