import unittest

from nova_core.fact_extraction import EnglishFactExtractor, verbalize_fact


class EnglishFactExtractorTests(unittest.TestCase):
    def setUp(self):
        self.extractor = EnglishFactExtractor()

    def test_english_father_pattern_and_parent_inference(self):
        extracted, result = self.extractor.reason("Arun is the father of Maya.")
        self.assertTrue(extracted.supported)
        self.assertEqual(extracted.facts, (("father", "Arun", "Maya"),))
        self.assertIn(("parent", "Arun", "Maya"), result.facts)
        self.assertTrue(any(p.rule_name == "parent_from_father" for p in result.proof))

    def test_english_mother_pattern(self):
        result = self.extractor.extract("Meena is the mother of Ravi")
        self.assertEqual(result.facts, (("mother", "Meena", "Ravi"),))
        self.assertEqual(result.language, "en")

    def test_english_friend_pattern(self):
        result = self.extractor.extract("Maya is a friend of Arun.")
        self.assertEqual(result.facts, (("friend", "Maya", "Arun"),))

    def test_english_parent_pattern(self):
        result = self.extractor.extract("Arun is a parent of Maya.")
        self.assertEqual(result.facts, (("parent", "Arun", "Maya"),))

    def test_unsupported_sentence_is_not_guessed(self):
        result = self.extractor.extract("The weather is pleasant today.")
        self.assertFalse(result.supported)
        self.assertEqual(result.facts, ())
        self.assertIsNone(result.language)

    def test_unsupported_non_english_input_is_not_guessed(self):
        result = self.extractor.extract("Bonjour tout le monde.")
        self.assertFalse(result.supported)
        self.assertEqual(result.facts, ())

    def test_english_verbalizer_templates(self):
        self.assertEqual(
            verbalize_fact(("parent", "Arun", "Maya"), "en"),
            "Arun is a parent of Maya.",
        )
        with self.assertRaises(ValueError):
            verbalize_fact(("father", "Arun", "Maya"), "fr")

    def test_multi_sentence_english_reasoning(self):
        text = "Arun is the father of Maya. Maya is the mother of Ravi."
        extracted, result = self.extractor.reason_many(text)
        self.assertEqual(len(extracted), 2)
        self.assertTrue(all(item.supported for item in extracted))
        self.assertIn(("grandparent", "Arun", "Ravi"), result.facts)
        self.assertTrue(any(
            step.rule_name == "grandparent_transitive" for step in result.proof
        ))

    def test_mixed_supported_and_unsupported_sentences_are_separated(self):
        text = (
            "Arun is the father of Maya. "
            "The weather is pleasant today."
        )
        extracted, result = self.extractor.reason_many(text)
        self.assertTrue(extracted[0].supported)
        self.assertFalse(extracted[1].supported)
        self.assertNotIn(("weather", "pleasant"), result.facts)

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):
            self.extractor.extract("   ")


if __name__ == "__main__":
    unittest.main()
