import tempfile
import unittest
import io
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.OpenClaw import baseline
from src.OpenClaw import run_modelingbench_baseline as runner


class ModelingBenchBaselineTests(unittest.TestCase):
    def test_human_expert_prompt_enforces_a_short_bounded_reply(self):
        prompt = baseline.HUMAN_MODELING_EXPERT_ROLE_PROMPT
        normalized_prompt = " ".join(prompt.split())
        self.assertIn("under 160 words", prompt)
        self.assertIn("single highest-impact qualitative decision", normalized_prompt)
        self.assertIn("complete Authoritative Problem Statement", prompt)
        self.assertIn("Stay strictly within that qualitative advisory scope", normalized_prompt)
        self.assertNotIn("parent modeling agent alone is responsible", prompt)
        self.assertNotIn("numerical calculation", prompt)

    def test_prepare_run_injects_complete_problem_into_human_expert_prompt(self):
        with tempfile.TemporaryDirectory() as temporary:
            problem = {
                "title": "Example title",
                "source": "Example source",
                "year": 2026,
                "question": "Build a model and assess its limitations.",
            }
            _, output_dir, _ = baseline.prepare_run(
                "example_problem",
                problem,
                Path(temporary),
                "test-model",
            )
            expert_prompt = (
                output_dir / "logs/operator_roles/human_modeling_expert.md"
            ).read_text(encoding="utf-8")
            self.assertIn("## Authoritative Problem Statement", expert_prompt)
            self.assertIn("Problem ID: example_problem", expert_prompt)
            self.assertIn("Title: Example title", expert_prompt)
            self.assertIn("Source: Example source", expert_prompt)
            self.assertIn("Year: 2026", expert_prompt)
            self.assertIn(problem["question"], expert_prompt)

    def test_baseline_prompt_is_generic_and_has_no_step_receipts(self):
        prompt = baseline.BASELINE_PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertIn("Search for at most 1-2 verifiable empirical data items", prompt)
        self.assertNotIn("bank", prompt.lower())
        self.assertNotIn("queue", prompt.lower())
        self.assertNotIn("step_NN", prompt)
        self.assertNotIn("step_01", prompt)
        self.assertNotIn("Workflow Summary Contract", prompt)
        self.assertNotIn("Workspace skills", prompt)
        self.assertNotIn("SKILL.md", prompt)

    def test_prepare_run_uses_new_baseline_prompt_by_default(self):
        with tempfile.TemporaryDirectory() as temporary:
            problem = {
                "title": "Example",
                "source": "Test",
                "year": 2026,
                "question": "Build a model.",
            }
            run_dir, output_dir, rendered = baseline.prepare_run(
                "example_problem",
                problem,
                Path(temporary),
                "test-model",
            )
            text = rendered.read_text(encoding="utf-8")
            self.assertIn("Search for at most 1-2 verifiable empirical data items", text)
            self.assertNotIn("step_NN", text)
            self.assertNotIn("Workspace skills", text)
            self.assertFalse((output_dir / "skills").exists())
            metadata = (run_dir / "meta/run.json").read_text(encoding="utf-8")
            self.assertIn('"installed_skills": []', metadata)

    def test_prepare_run_sanitizes_only_the_filesystem_problem_id(self):
        with tempfile.TemporaryDirectory() as temporary:
            problem = {
                "title": "Cyber Strong",
                "source": "Test",
                "year": 2025,
                "question": "Build a model.",
            }
            run_dir, _, rendered = baseline.prepare_run(
                "2025_Cyber_Strong?",
                problem,
                Path(temporary),
                "test-model",
            )
            self.assertTrue(run_dir.name.startswith("2025_Cyber_Strong_"))
            self.assertIn("2025_Cyber_Strong?", rendered.read_text(encoding="utf-8"))

    def test_prepare_run_can_shorten_only_the_physical_directory_name(self):
        with tempfile.TemporaryDirectory() as temporary:
            problem = {
                "title": "Sustainable Tourism",
                "source": "Test",
                "year": 2025,
                "question": "Build a tourism model.",
            }
            run_dir, _, rendered = baseline.prepare_run(
                "2025_Managing_Sustainable_Tourism",
                problem,
                Path(temporary),
                "test-model",
                run_directory_prefix="seed",
            )
            self.assertTrue(run_dir.name.startswith("seed_"))
            self.assertIn(
                "2025_Managing_Sustainable_Tourism",
                rendered.read_text(encoding="utf-8"),
            )

    def test_prepare_run_supports_flat_layout_without_model_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            problem = {
                "title": "Example",
                "source": "Test",
                "year": 2026,
                "question": "Build a model.",
            }
            root = Path(temporary)
            run_dir, _, _ = baseline.prepare_run(
                "long_problem_identifier",
                problem,
                root,
                "provider/long-model-name",
                run_directory_prefix="r1p1",
                flat_run_layout=True,
            )

            self.assertEqual(run_dir.parent, root)
            self.assertTrue(run_dir.name.startswith("r1p1_"))
            metadata = json.loads(
                (run_dir / "meta/run.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["problem_id"], "long_problem_identifier")

    def test_aggregate_scores_includes_each_dimension(self):
        dimensions = {name: 0.5 for name in baseline.EXPECTED_JUDGERS}
        overall, averages = runner.aggregate_scores(
            [
                {"average_score": 0.5, "dimension_scores": dimensions},
                {
                    "average_score": 0.7,
                    "dimension_scores": {name: 0.7 for name in dimensions},
                },
            ]
        )
        self.assertAlmostEqual(overall, 0.6)
        self.assertEqual(set(averages), set(baseline.EXPECTED_JUDGERS))
        self.assertTrue(all(abs(value - 0.6) < 1e-9 for value in averages.values()))

    def test_repeated_judge_result_record_uses_average_scores(self):
        dimensions = {name: 0.6 for name in baseline.EXPECTED_JUDGERS}
        record = runner.result_record(
            "example",
            {
                "run_dir": Path("run"),
                "final_report": Path("run/report.md"),
                "judge_result": Path("run/raw.json"),
                "repeated_judge": True,
                "judge_stability_result": Path("run/judge_stability.json"),
                "judge_repeats": 3,
                "average_score": 0.6,
                "dimension_scores": dimensions,
            },
        )
        self.assertEqual(record["judge_repeats"], 3)
        self.assertEqual(record["average_score"], 0.6)
        self.assertEqual(record["dimension_scores"], dimensions)

    def test_console_output_does_not_fail_on_gbk(self):
        output = io.TextIOWrapper(io.BytesIO(), encoding="gbk")
        with patch("sys.stdout", output):
            baseline.print_console("Unicode minus: \u2212")
            output.flush()

    def test_prepare_run_installs_only_skill_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skills = root / "source_skills"
            skill = skills / "example-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: test\n---\n",
                encoding="utf-8",
            )
            (skills / "metadata.json").write_text("{}", encoding="utf-8")
            problem = {
                "title": "Example",
                "source": "Test",
                "year": 2026,
                "question": "Build a model.",
            }
            run_dir, output, _ = baseline.prepare_run(
                "example_problem",
                problem,
                root / "runs",
                "test-model",
                skills_source=skills,
            )
            self.assertTrue((output / "skills/example-skill/SKILL.md").is_file())
            self.assertFalse((output / "skills/metadata.json").exists())
            metadata = (run_dir / "meta/run.json").read_text(encoding="utf-8")
            self.assertIn('"installed_skills": [', metadata)
            self.assertIn('"example-skill"', metadata)

    def test_select_problems_supports_ids_and_all(self):
        problems = {"a": {"title": "A"}, "b": {"title": "B"}}
        self.assertEqual(runner.select_problems(problems, ["b"], False), [("b", problems["b"])])
        self.assertEqual(runner.select_problems(problems, [], True), list(problems.items()))
        with self.assertRaises(ValueError):
            runner.select_problems(problems, [], False)

    def test_run_selected_uses_requested_concurrency(self):
        selected = [("a", {}), ("b", {})]
        args = SimpleNamespace(concurrency=2, skip_judge=True, prepare_only=False)

        def fake_run(problem_id, problem, run_args):
            return {
                "run_dir": Path(problem_id),
                "final_report": Path(problem_id) / "report.md",
                "judge_result": None,
                "average_score": None,
            }

        with patch.object(runner.baseline, "run_problem", side_effect=fake_run):
            completed, failed = runner.run_selected(selected, args)
        self.assertEqual([item["problem_id"] for item in completed], ["a", "b"])
        self.assertEqual(failed, [])


if __name__ == "__main__":
    unittest.main()
