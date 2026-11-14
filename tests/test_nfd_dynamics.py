import unittest
from nova_core.nfd_dynamics import NFDDynamics

class NFDDynamicsTests(unittest.TestCase):
    def test_same_stream_is_deterministic(self):
        self.assertEqual(NFDDynamics().observe("AstraCore Nova"),
                         NFDDynamics().observe("AstraCore Nova"))

    def test_ascii_events_are_consumed_as_codepoints(self):
        text = "English"
        frame = NFDDynamics().observe(text)
        self.assertEqual(frame.step, len(text))
        self.assertEqual(len(frame.activation), 32)

    def test_order_changes_state(self):
        a = NFDDynamics().observe("English")
        b = NFDDynamics().observe("gnilhsnE")
        self.assertNotEqual(a.activation, b.activation)

    def test_all_ledgers_are_bounded(self):
        frame = NFDDynamics().observe("A" * 1000)
        for ledger in (frame.activation, frame.trace, frame.tension):
            self.assertTrue(all(-1.0 <= value <= 1.0 for value in ledger))

    def test_adaptation_is_stateful_and_resettable(self):
        engine = NFDDynamics()
        engine.observe("repeated English pattern " * 20)
        self.assertEqual(len(engine.bias), engine.width)
        engine.reset()
        self.assertEqual(engine.steps, 0)
        self.assertEqual(engine.bias, [0.0] * engine.width)

    def test_invalid_event_is_rejected(self):
        with self.assertRaises(ValueError):
            NFDDynamics().step("two")

if __name__ == "__main__":
    unittest.main()
