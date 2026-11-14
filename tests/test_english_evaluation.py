import unittest
from evaluate_english import evaluate


class EnglishEvaluationTests(unittest.TestCase):
    def test_curated_corpus_has_exact_expected_facts(self):
        report = evaluate("evaluation/english_pattern_eval.json")
        self.assertEqual(report["examples"], 36)
        self.assertEqual(report["exact_sentence_matches"], 36)
        self.assertEqual(report["fact"]["true_positive"], 24)
        self.assertEqual(report["fact"]["false_positive"], 0)
        self.assertEqual(report["fact"]["false_negative"], 0)
        self.assertEqual(report["fact"]["f1"], 1.0)
        self.assertEqual(report["supported_classification"]["f1"], 1.0)
        self.assertIn("not a representative English benchmark", report["warning"])


if __name__ == "__main__":
    unittest.main()
