import contextlib
import io
import json
import sys
import unittest
from unittest.mock import patch

import english_demo


class EnglishDemoTests(unittest.TestCase):
    def run_demo(self, *args):
        output = io.StringIO()
        with patch.object(sys, "argv", ["english_demo.py", *args]):
            with contextlib.redirect_stdout(output):
                status = english_demo.main()
        return status, json.loads(output.getvalue())

    def test_default_demo_runs_end_to_end_and_emits_proof(self):
        status, payload = self.run_demo()
        self.assertEqual(status, 0)
        self.assertTrue(payload["ok"])
        self.assertIn(
            ["grandparent", "Arun", "Ravi"],
            payload["reasoning"]["derived"],
        )
        self.assertTrue(payload["reasoning"]["proof"])

    def test_unsupported_sentence_is_not_guessed(self):
        status, payload = self.run_demo("The weather might be pleasant tomorrow.")
        self.assertEqual(status, 0)
        self.assertEqual(payload["extraction"][0]["facts"], [])
        self.assertEqual(payload["reasoning"]["derived"], [])

    def test_invalid_capacity_returns_structured_error(self):
        status, payload = self.run_demo("--capacity", "0")
        self.assertEqual(status, 2)
        self.assertFalse(payload["ok"])
        self.assertIn("capacity", payload["error"])


if __name__ == "__main__":
    unittest.main()
