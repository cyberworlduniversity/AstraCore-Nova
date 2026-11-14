import unittest

from nova_core.fact_extraction import EnglishFactExtractor, verbalize_fact


class AdvancedEnglishGrammarTests(unittest.TestCase):
    def setUp(self):
        self.extractor = EnglishFactExtractor()

    def test_extended_relation_catalogue(self):
        cases = {
            "Arun is married to Meena.": ("spouse", "Arun", "Meena"),
            "Maya lives in Chennai.": ("lives_in", "Maya", "Chennai"),
            "Ravi resides in Vellore.": ("lives_in", "Ravi", "Vellore"),
            "CWU is located in India.": ("lives_in", "CWU", "India"),
            "Hemanathan works at CWU.": ("works_at", "Hemanathan", "CWU"),
            "Maya is employed at Acme Labs.": ("works_at", "Maya", "Acme Labs"),
            "Arun knows Ravi.": ("knows", "Arun", "Ravi"),
            "Maya owns a laptop.": ("owns", "Maya", "a laptop"),
            "Ravi likes science.": ("likes", "Ravi", "science"),
            "Meena loves music.": ("loves", "Meena", "music"),
        }
        for sentence, expected in cases.items():
            with self.subTest(sentence=sentence):
                result = self.extractor.extract(sentence)
                self.assertTrue(result.supported)
                self.assertEqual(result.facts, (expected,))
                self.assertEqual(result.language, "en")

    def test_case_insensitive_and_trailing_punctuation(self):
        result = self.extractor.extract("maya LIKES science!")
        self.assertEqual(result.facts, (("likes", "maya", "science"),))

    def test_same_entity_relation_is_rejected(self):
        result = self.extractor.extract("Maya knows maya.")
        self.assertFalse(result.supported)
        self.assertEqual(result.facts, ())

    def test_negative_or_uncertain_claim_is_not_guessed(self):
        for sentence in (
            "Maya does not like science.",
            "Maya might live in Chennai.",
            "I think Maya knows Ravi.",
        ):
            with self.subTest(sentence=sentence):
                result = self.extractor.extract(sentence)
                self.assertFalse(result.supported)
                self.assertEqual(result.facts, ())

    def test_extended_relations_verbalize(self):
        self.assertEqual(
            verbalize_fact(("lives_in", "Maya", "Chennai")),
            "Maya lives in Chennai.",
        )
        self.assertEqual(
            verbalize_fact(("spouse", "Arun", "Meena")),
            "Arun is married to Meena.",
        )


    def test_sentence_character_limit_is_enforced(self):
        sentence = "A" * (self.extractor.MAX_SENTENCE_CHARS + 1)
        with self.assertRaises(ValueError):
            self.extractor.extract(sentence)

    def test_control_characters_are_rejected(self):
        with self.assertRaises(ValueError):
            self.extractor.extract("Maya\x00 knows Ravi.")

    def test_total_text_limit_is_enforced(self):
        text = "A" * (self.extractor.MAX_TEXT_CHARS + 1)
        with self.assertRaises(ValueError):
            self.extractor.extract_many(text)

    def test_sentence_count_limit_is_enforced(self):
        text = " ".join(
            "Unsupported statement." for _ in range(self.extractor.MAX_SENTENCES + 1)
        )
        with self.assertRaises(ValueError):
            self.extractor.extract_many(text)

    def test_multi_sentence_extended_extraction(self):
        results = self.extractor.extract_many(
            "Maya lives in Chennai. Ravi likes science. The weather is pleasant."
        )
        self.assertEqual(len(results), 3)
        self.assertEqual(sum(item.supported for item in results), 2)
        self.assertEqual(results[2].facts, ())


if __name__ == "__main__":
    unittest.main()
