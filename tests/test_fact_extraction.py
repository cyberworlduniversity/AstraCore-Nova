import unittest
from nova_core.fact_extraction import MultilingualFactExtractor, verbalize_fact

class MultilingualFactExtractorTests(unittest.TestCase):
    def setUp(self):
        self.extractor = MultilingualFactExtractor()

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

    def test_tamil_father_pattern(self):
        result = self.extractor.extract("அருண் மாயாவின் தந்தை.")
        self.assertTrue(result.supported)
        self.assertEqual(result.facts, (("father", "அருண்", "மாயா"),))
        self.assertEqual(result.language, "ta")

    def test_tamil_mother_pattern(self):
        result = self.extractor.extract("மீனா ரவியின் தாய்")
        self.assertEqual(result.facts, (("mother", "மீனா", "ரவி"),))

    def test_unsupported_sentence_is_not_guessed(self):
        result = self.extractor.extract("இன்று வானிலை நன்றாக உள்ளது.")
        self.assertFalse(result.supported)
        self.assertEqual(result.facts, ())
        self.assertIsNone(result.language)

    def test_verbalizer_templates(self):
        self.assertEqual(verbalize_fact(("parent", "Arun", "Maya"), "en"),
                         "Arun is a parent of Maya.")
        self.assertIn("தந்தை", verbalize_fact(("father", "அருண்", "மாயா"), "ta"))

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):
            self.extractor.extract("   ")

if __name__ == "__main__":
    unittest.main()