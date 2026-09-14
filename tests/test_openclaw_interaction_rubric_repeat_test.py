import unittest
from pathlib import Path

from src.OpenClaw import run_interaction_rubric_repeat_test as repeat_test


class InteractionRubricRepeatTestTests(unittest.TestCase):
    def test_metric_statistics_reports_repeat_variation_and_source_delta(self):
        result = repeat_test.metric_statistics([0.7, 0.9], 0.75)

        self.assertAlmostEqual(result["mean"], 0.8)
        self.assertAlmostEqual(result["population_stddev"], 0.1)
        self.assertAlmostEqual(result["range"], 0.2)
        self.assertAlmostEqual(result["mean_delta_from_source_round"], 0.05)

    def test_default_experiment_round_four_is_available(self):
        source = repeat_test.load_source_round(
            Path(repeat_test.DEFAULT_EXPERIMENT), 4
        )

        self.assertEqual(source["round"], 4)
        self.assertEqual(
            source["rubric"]["rubric_id"], "interaction_a1e642d77811"
        )


if __name__ == "__main__":
    unittest.main()
