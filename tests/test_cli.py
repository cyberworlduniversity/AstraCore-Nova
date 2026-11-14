import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nova_core.__main__ import main
from nova_core.fact_memory import FactMemory

class NovaCliTests(unittest.TestCase):
    def test_cli_processes_statement_and_saves_on_exit(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            output = io.StringIO()
            with patch("builtins.input", side_effect=[
                "Arun is the father of Maya.",
                "Maya is the mother of Ravi.",
                ":quit",
            ]), contextlib.redirect_stdout(output):
                result = main(["--memory", str(path)])
            self.assertEqual(result, 0)
            self.assertTrue(path.exists())
            memory = FactMemory.load(path)
            self.assertTrue(any(item.fact == ("grandparent", "Arun", "Ravi")
                                for item in memory.facts))
            self.assertIn("Saved", output.getvalue())

    def test_cli_lists_facts(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            memory = FactMemory()
            memory.add(("father", "Arun", "Maya"), "seed")
            memory.save(path)
            output = io.StringIO()
            with patch("builtins.input", side_effect=[":facts", ":quit"]), contextlib.redirect_stdout(output):
                main(["--memory", str(path)])
            self.assertIn("Arun is the father of Maya.", output.getvalue())

    def test_cli_help_and_unknown_input(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            output = io.StringIO()
            with patch("builtins.input", side_effect=[":help", "The sky may be blue.", ":quit"]), contextlib.redirect_stdout(output):
                main(["--memory", str(path)])
            self.assertIn("Supported patterns", output.getvalue())
            self.assertIn("No supported English pattern matched", output.getvalue())

if __name__ == "__main__":
    unittest.main()
