import unittest

from nova_core.validation import adaptation_report, ablation_report, benchmark


class NFDValidationTests(unittest.TestCase):
    def test_adaptation_changes_bias_and_state(self):
        result = adaptation_report(repeats=8)
        self.assertGreater(result["bias_l1"], 0.0)
        self.assertEqual(result["frozen_bias_l1"], 0.0)
        self.assertGreater(result["adapted_state_delta_l1"], 0.0)

    def test_trace_ablation_removes_trace_state(self):
        result = ablation_report()
        self.assertGreater(result["full"]["trace_l1"], 0.0)
        self.assertEqual(result["no_trace"]["trace_l1"], 0.0)

    def test_tension_ablation_removes_tension_state(self):
        result = ablation_report()
        self.assertGreater(result["full"]["tension_l1"], 0.0)
        self.assertEqual(result["no_tension"]["tension_l1"], 0.0)

    def test_adaptation_ablation_freezes_bias(self):
        result = ablation_report()
        self.assertGreater(result["full"]["bias_l1"], 0.0)
        self.assertEqual(result["no_adaptation"]["bias_l1"], 0.0)

    def test_benchmark_is_reproducible_in_shape(self):
        result = benchmark(repeats=1, width=8)
        self.assertEqual(result["events"], sum(len(x) for x in (
            "AstraCore Nova learns from repeated observations.",
            "English language processing uses explicit sentence patterns.",
            "prediction error and temporal memory",
        )))
        self.assertGreater(result["events_per_second"], 0.0)
        self.assertGreater(result["peak_traced_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
