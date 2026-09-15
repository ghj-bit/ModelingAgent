"""Regression tests for JSON caches exceeding Windows MAX_PATH."""

import os
import tempfile
import unittest
from pathlib import Path

try:
    from . import run_evolution as evolution
except ImportError:
    import run_evolution as evolution


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


if __name__ == "__main__":
    unittest.main()
