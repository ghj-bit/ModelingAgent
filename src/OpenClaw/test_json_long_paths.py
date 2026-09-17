"""Regression tests for JSON caches exceeding Windows MAX_PATH."""

import os
import tempfile
import unittest
from pathlib import Path

try:
    from . import run_evolution as evolution
    from . import run_interaction_rubric_evolution as interaction
except ImportError:
    import run_evolution as evolution
    import run_interaction_rubric_evolution as interaction


class JsonLongPathTests(unittest.TestCase):
    def test_deep_cache_roundtrip_and_overwrite(self):
        root = evolution._json_filesystem_path(Path(tempfile.gettempdir()))
        with tempfile.TemporaryDirectory(dir=root) as directory:
            # Pass ordinary paths to the public helpers, as the runner does.
            ordinary = directory.removeprefix("\\\\?\\") if os.name == "nt" else directory
            cache = (
                Path(ordinary)
                / ("experiment_" + "x" * 100)
                / "workflows/operator_evolution/after_round_12"
                / "interaction_report_change_summaries"
                / ("a" * 64 + ".json")
            )
            self.assertGreater(len(str(cache)), 260)
            self.assertIsNone(evolution.read_json(cache, None))
            evolution.write_json(cache, {"summary": "首次摘要", "max_chars": 50})
            self.assertEqual(evolution.read_json(cache, {}), {"summary": "首次摘要", "max_chars": 50})
            evolution.write_json(cache, {"summary": "更新摘要"})
            self.assertEqual(evolution.read_json(cache, {}), {"summary": "更新摘要"})
            temporary = cache.with_suffix(".json.tmp")
            self.assertFalse(evolution._json_filesystem_path(temporary).exists())

    def test_existing_short_path_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            fallback = {"missing": True}
            self.assertEqual(evolution.read_json(path, fallback), fallback)
            evolution.write_json(path, [{"utility": 0.8}])
            self.assertEqual(evolution.read_json(path, None), [{"utility": 0.8}])

    def test_atomic_interaction_json_supports_deep_cpe_path(self):
        root = evolution._json_filesystem_path(Path(tempfile.gettempdir()))
        with tempfile.TemporaryDirectory(dir=root) as directory:
            ordinary = directory.removeprefix("\\\\?\\") if os.name == "nt" else directory
            path = (
                Path(ordinary)
                / ("interaction_workflow_clean_baseline_refinement_" + "x" * 48)
                / "cpe_evaluations/round_4/train_parent_2/runs/round_4"
                / ("r1p2_" + "y" * 40)
                / "output/logs/operator_feedback/expert_request_1.json"
            )
            self.assertGreater(len(str(path)), 260)
            interaction.write_json_atomic(path, {"question": "test"})
            self.assertEqual(evolution.read_json(path, {}), {"question": "test"})
            interaction.write_json_atomic(path, {"question": "updated"})
            self.assertEqual(evolution.read_json(path, {}), {"question": "updated"})


if __name__ == "__main__":
    unittest.main()
