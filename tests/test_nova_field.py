import unittest
from nova_field import NovaFieldMemory, encode_field, similarity

class NovaFieldTests(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(encode_field("Nova"), encode_field("Nova"))

    def test_fixed_width_and_normalised(self):
        field = encode_field("English language")
        self.assertEqual(len(field), 32)
        self.assertAlmostEqual(sum(x * x for x in field), 1.0, places=6)

    def test_empty_input(self):
        self.assertEqual(set(encode_field("")), {0.0})

    def test_different_inputs_produce_signatures(self):
        self.assertNotEqual(encode_field("alpha"), encode_field("bravo"))

    def test_similarity_self(self):
        field = encode_field("AstraCore Nova")
        self.assertAlmostEqual(similarity(field, field), 1.0, places=6)

    def test_memory_store_and_recall(self):
        memory = NovaFieldMemory(capacity=2)
        memory.store("one", "English language example")
        memory.store("two", "English coding example")
        self.assertEqual(len(memory), 2)
        results = memory.recall("English language example")
        self.assertEqual(results[0][1].label, "one")

    def test_capacity_is_bounded(self):
        memory = NovaFieldMemory(capacity=1)
        memory.store("one", "first")
        memory.store("two", "second")
        self.assertEqual(len(memory), 1)
        self.assertEqual(memory.recall("second")[0][1].label, "two")

if __name__ == "__main__":
    unittest.main()
