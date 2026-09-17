import json
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from src.OpenClaw import baseline
from src.OpenClaw import run_mm_agent_baseline as runner


class MMAgentBaselineTests(unittest.TestCase):
    def test_judge_retries_after_process_level_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = root / "solution_report.md"
            report.write_text("# Report\n", encoding="utf-8")
            run_dir = root / "run-one"
            result_path = (
                root / "output_judge" / "OpenClaw" / "model" /
                run_dir.name / "problem.json"
            )
            calls = 0

            def fake_run(*_args, **_kwargs):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise subprocess.CalledProcessError(3221225477, ["judge"])
                result_path.parent.mkdir(parents=True, exist_ok=True)
                result_path.write_text('{"judgements": {}}', encoding="utf-8")

            with patch.object(baseline, "REPO_ROOT", root), \
                 patch.object(baseline, "JUDGER_DIR", root), \
                 patch.object(baseline, "JUDGE_RETRY_DELAY_SECONDS", 0), \
                 patch.object(baseline.subprocess, "run", side_effect=fake_run), \
                 patch.object(baseline, "calculate_average_score", return_value=0.5):
                actual = baseline.judge_final_report(
                    "problem", report, "model", run_dir
                )

            self.assertEqual(actual, result_path)
            self.assertEqual(calls, 2)

    def test_generated_skill_contains_complete_natural_language_workflow(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner.build_skill_bundle(root)
            skill = (root / runner.SKILL_NAME / "SKILL.md").read_text(encoding="utf-8")
            for step in range(1, 8):
                self.assertIn(f"## Step {step}:", skill)
            self.assertIn("ModelingBench", skill)
            self.assertIn("dependency order", skill)
            self.assertIn("final report", skill)
            for implementation_detail in (
                "MMAgent/", ".py", "HMML", "MethodScorer", "EmbeddingScorer",
                "top_method_num", "tasknum", "chart_num", "_round", "run_config",
            ):
                self.assertNotIn(implementation_detail, skill)

    def test_prepare_renders_current_problem_and_copies_attachments(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = root / "attachments"
            data.mkdir()
            (data / "measurements.csv").write_text("x,y\n1,2\n", encoding="utf-8")
            problem = {
                "title": "Current title",
                "question": "Use the supplied measurements.",
                "requirements": ["HIDDEN RUBRIC"],
                "eval_roles": ["HIDDEN ROLE"],
            }
            with patch.object(baseline, "load_problems", return_value={"current": problem}), \
                 patch.object(baseline, "find_openclaw_command", side_effect=AssertionError("CLI called")):
                runner.main([
                    "current", "--prepare-only", "--output-root", str(root / "runs"),
                    "--data-dir", str(data),
                ])
            summary = json.loads(next((root / "runs").glob("mm_agent_results_*.json")).read_text())
            record = summary["completed"][0]
            self.assertEqual(record["status"], "prepared")
            self.assertIsNone(record["final_report"])
            prompt = Path(record["prompt"]).read_text(encoding="utf-8")
            self.assertIn(problem["question"], prompt)
            self.assertNotIn("{{", prompt)
            self.assertNotIn("HIDDEN RUBRIC", prompt)
            self.assertNotIn("HIDDEN ROLE", prompt)
            skill = Path(record["run_dir"]) / "output/skills/mm-agent-pipeline"
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertEqual((skill / "data/measurements.csv").read_text(), "x,y\n1,2\n")

    def test_execution_judges_only_the_final_report_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw_judge = root / "judge.json"

            def solve(command, cwd, log_path, completion_artifact):
                completion_artifact.write_text("# Actual final report\n", encoding="utf-8")

            with patch.object(baseline, "load_problems", return_value={"current": {"question": "Solve."}}), \
                 patch.object(baseline, "find_openclaw_command", return_value="openclaw"), \
                 patch.object(baseline, "run_checked"), \
                 patch.object(baseline, "stream_command", side_effect=solve), \
                 patch.object(baseline, "judge_final_report", return_value=raw_judge) as judge, \
                 patch.object(baseline, "calculate_average_score", return_value=0.6), \
                 patch.object(baseline, "calculate_dimension_scores", return_value={}):
                runner.main(["current", "--output-root", str(root / "runs")])
            judge.assert_called_once()
            self.assertEqual(judge.call_args.args[0], "current")
            self.assertEqual(judge.call_args.args[1].name, "solution_report.md")

    def test_failed_solve_is_recorded_and_never_judged(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.object(baseline, "load_problems", return_value={"current": {}}), \
                 patch.object(baseline, "run_problem", side_effect=RuntimeError("solve failed")), \
                 patch.object(baseline, "judge_final_report") as judge:
                with self.assertRaisesRegex(RuntimeError, "1 problem"):
                    runner.main(["current", "--output-root", str(root / "runs")])
            judge.assert_not_called()
            summary = json.loads(next((root / "runs").glob("mm_agent_results_*.json")).read_text())
            self.assertEqual(summary["completed"], [])
            self.assertIn("solve failed", summary["failed"][0]["error"])

    def test_selected_problems_run_with_requested_concurrency(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            barrier = threading.Barrier(2)
            lock = threading.Lock()
            active = 0
            maximum_active = 0

            def fake_run(problem_id, problem, args):
                nonlocal active, maximum_active
                with lock:
                    active += 1
                    maximum_active = max(maximum_active, active)
                barrier.wait(timeout=3)
                with lock:
                    active -= 1
                return {
                    "run_dir": root / problem_id,
                    "prompt": root / problem_id / "prompt.md",
                    "final_report": root / problem_id / "solution_report.md",
                    "judge_result": None,
                    "average_score": None,
                }

            with patch.object(baseline, "load_problems", return_value={"one": {}, "two": {}}), \
                 patch.object(baseline, "run_problem", side_effect=fake_run):
                runner.main([
                    "one", "two", "--concurrency", "2", "--skip-judge",
                    "--output-root", str(root / "runs"),
                ])
            self.assertEqual(maximum_active, 2)
            summary = json.loads(next((root / "runs").glob("mm_agent_results_*.json")).read_text())
            self.assertEqual(summary["concurrency"], 2)
            self.assertEqual([item["problem_id"] for item in summary["completed"]], ["one", "two"])

    def test_attachments_require_exactly_one_problem(self):
        with self.assertRaises(SystemExit):
            runner.parse_args(["one", "two", "--data-dir", "."])


if __name__ == "__main__":
    unittest.main()
