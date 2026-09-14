import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.OpenClaw import baseline
from src.OpenClaw import run_modelingbench_interaction_rubric_test as runner


def rubric(rubric_id: str) -> dict:
    return {
        "rubric_id": rubric_id,
        "name": "Focused expert consultation",
        "purpose": "Resolve one material modeling uncertainty with expert judgment.",
        "criteria": [
            {
                "name": "Ask a consequential question",
                "rule": "Ask one specific question whose answer changes a decision.",
                "positive_example": "Compare two assumptions using observable evidence.",
                "negative_example": "Ask for a broad and unstructured model review.",
            },
            {
                "name": "Use the answer traceably",
                "rule": "Adopt or reject advice and verify the downstream change.",
                "positive_example": "Update the model and run the named validation check.",
                "negative_example": "Copy the advice without applying or checking it.",
            },
        ],
        "attention_budget": "One expert session with up to three focused exchanges.",
        "success_test": "A material uncertainty is resolved and its use is validated.",
    }


class ModelingBenchInteractionRubricTestTests(unittest.TestCase):
    def test_test_judge_uses_only_evolution_objective_dimensions(self):
        self.assertEqual(
            set(runner.TEST_JUDGE_DIMENSIONS),
            {
                "analysis_groundedness",
                "modeling_groundedness",
                "scoring_decomposition",
                "structural_coherency",
            },
        )
        self.assertNotIn("innovativeness", runner.TEST_JUDGE_DIMENSIONS)
        self.assertNotIn("data_groundedness", runner.TEST_JUDGE_DIMENSIONS)

    def test_load_best_rubric_ignores_incomplete_higher_utility_node(self):
        validation = list(runner.interaction_evolution.VALIDATION_PROBLEMS)
        results = [
            {
                "round": 1,
                "rubric_id": "complete",
                "rubric": rubric("complete"),
                "utility": 0.8,
                "problem_results": [{"problem_id": value} for value in validation],
            },
            {
                "round": 2,
                "rubric_id": "incomplete",
                "rubric": rubric("incomplete"),
                "utility": 0.99,
                "problem_results": [{"problem_id": validation[0]}],
            },
        ]
        with tempfile.TemporaryDirectory() as temporary:
            experiment = Path(temporary)
            workflows = experiment / "workflows"
            workflows.mkdir()
            (workflows / "results.json").write_text(
                json.dumps(results), encoding="utf-8"
            )
            selected = runner.load_best_rubric(experiment)
        self.assertEqual(selected["rubric_id"], "complete")

    def test_materialized_prompt_contains_rubric_and_stage_outputs(self):
        validation = list(runner.interaction_evolution.VALIDATION_PROBLEMS)
        results = [
            {
                "round": 3,
                "rubric_id": "best",
                "rubric": rubric("best"),
                "utility": 0.9,
                "problem_results": [{"problem_id": value} for value in validation],
            }
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            experiment = root / "experiment"
            workflows = experiment / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "results.json").write_text(
                json.dumps(results), encoding="utf-8"
            )
            _, prompt_path, selection_path = runner.materialize_treatment_prompt(
                experiment, root / "output", baseline.BASELINE_PROMPT_TEMPLATE_PATH
            )
            prompt = prompt_path.read_text(encoding="utf-8")
            metadata = json.loads(selection_path.read_text(encoding="utf-8"))
        self.assertIn("## Human Expert Interaction", prompt)
        self.assertIn("step_01_problem_understanding.md", prompt)
        self.assertIn("step_05_validation_analysis.md", prompt)
        self.assertIn("interaction_receipt.json", prompt)
        self.assertEqual(metadata["rubric_id"], "best")

    def test_all_selects_test_set_and_excludes_validation(self):
        validation = runner.interaction_evolution.VALIDATION_PROBLEMS
        problems = {"test_a": {}, validation[0]: {}, validation[1]: {}}
        selected = runner.select_test_problems(problems, [], True)
        self.assertEqual(selected, [("test_a", {})])
        with self.assertRaises(ValueError):
            runner.select_test_problems(problems, [validation[0]], False)

    def test_historical_experiment_keeps_its_original_validation_set(self):
        with tempfile.TemporaryDirectory() as temporary:
            experiment = Path(temporary)
            (experiment / "config.json").write_text(
                json.dumps({"validation_problems": ["old_a", "old_b"]}),
                encoding="utf-8",
            )

            self.assertEqual(
                runner.experiment_validation_problems(experiment),
                ("old_a", "old_b"),
            )

    def test_validate_stage_outputs_requires_all_five_nonempty_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            for relative_path in runner.STAGE_OUTPUTS.values():
                path = run_dir / "output" / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("done", encoding="utf-8")
            stage_files = runner.validate_stage_outputs({"run_dir": run_dir})
            self.assertEqual(set(stage_files), set(runner.STAGE_OUTPUTS))

    def test_run_selected_applies_per_problem_short_directory_prefix(self):
        captured = {}

        def prepare_only(problem_id, _problem, args):
            captured[problem_id] = args.run_directory_prefix
            return {
                "run_dir": Path("run") / problem_id,
                "prompt": Path("prompt.md"),
                "final_report": Path("solution_report.md"),
                "judge_result": None,
                "average_score": None,
            }

        args = SimpleNamespace(
            concurrency=2,
            prepare_only=True,
            skip_judge=True,
            run_directory_prefixes={"problem_a": "p1", "problem_b": "p2"},
        )
        with patch.object(runner.baseline, "run_problem", side_effect=prepare_only):
            completed, failed = runner.run_selected(
                [("problem_a", {}), ("problem_b", {})], args, rubric("fixed")
            )

        self.assertEqual(captured, {"problem_a": "p1", "problem_b": "p2"})
        self.assertEqual(len(completed), 2)
        self.assertEqual(failed, [])


if __name__ == "__main__":
    unittest.main()
