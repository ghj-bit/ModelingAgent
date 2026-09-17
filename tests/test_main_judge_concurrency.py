import sys
import tempfile
import threading
import unittest
from pathlib import Path


JUDGER_DIR = Path(__file__).resolve().parents[1] / "src" / "judger"
sys.path.insert(0, str(JUDGER_DIR))

from main_judge import MainJudger  # noqa: E402


class MainJudgeConcurrencyTests(unittest.TestCase):
    def test_every_pending_judger_can_start_before_any_finishes(self):
        judger_count = 8
        names = [f"judge_{index}" for index in range(judger_count)]
        judger = MainJudger.__new__(MainJudger)
        judger.judgers = {name: object() for name in names}
        judger.role_based_judgers = set()

        start_barrier = threading.Barrier(judger_count, timeout=3.0)
        started = []
        started_lock = threading.Lock()

        def run_judger(name, writing, roles=None, grading_points=None):
            with started_lock:
                started.append(name)
            start_barrier.wait()
            return {"calculated_overall": 1.0}

        judger.run_judger = run_judger

        with tempfile.TemporaryDirectory() as output_dir:
            result = judger.judge(output_dir, "problem", "report", [])

        self.assertEqual(set(started), set(names))
        self.assertEqual(result["metadata"]["success_count"], judger_count)
        self.assertEqual(result["metadata"]["failed_count"], 0)


if __name__ == "__main__":
    unittest.main()
