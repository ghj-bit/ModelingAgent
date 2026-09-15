"""Verify Agent execution overlaps registration of later concurrent tasks."""

import json
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

try:
    from . import run_interaction_rubric_evolution as interaction
    from . import run_substantive_interaction_workflow_evolution_from_clean_baseline as refinement
except ImportError:
    import run_interaction_rubric_evolution as interaction
    import run_substantive_interaction_workflow_evolution_from_clean_baseline as refinement


class PipelinedAgentExecutionTests(unittest.TestCase):
    @staticmethod
    def write_clean_report(root: Path, run_name: str, problem_id: str) -> Path:
        run_dir = root / run_name
        report = run_dir / "output" / "results" / "solution_report.md"
        report.parent.mkdir(parents=True)
        report.write_text("draft", encoding="utf-8")
        metadata = run_dir / "meta" / "run.json"
        metadata.parent.mkdir(parents=True)
        metadata.write_text(
            json.dumps({"problem_id": problem_id}), encoding="utf-8"
        )
        return report

    def test_clean_baseline_refinement_enables_pipeline_mode(self):
        expected = SimpleNamespace()
        with patch.object(refinement, "_original_runtime_args", return_value=expected):
            actual = refinement.runtime_args_with_immediate_agent_start()
        self.assertIs(actual, expected)
        self.assertTrue(actual.pipeline_agent_start)
        self.assertTrue(actual.require_clean_task_workspace)

    def test_clean_baseline_refinement_uses_isolated_openclaw_config(self):
        isolated = Path("isolated-openclaw.json")
        with (
            patch.object(refinement.sys, "argv", ["runner"]),
            patch.object(
                refinement.clean_baseline,
                "activate_clean_openclaw_config",
                return_value=(isolated, "original-openclaw.json"),
            ) as activate,
            patch.object(
                refinement.clean_baseline, "remove_clean_openclaw_config"
            ) as remove,
            patch.object(refinement.workflow, "main") as workflow_main,
            patch.object(refinement, "record_initial_draft_config"),
        ):
            refinement.main()

        activate.assert_called_once_with()
        workflow_main.assert_called_once_with(
            cpe_mode=True, compact_experiment_inputs=True
        )
        remove.assert_called_once_with(isolated, "original-openclaw.json")

    def test_current_clean_pool_defaults_to_three_concurrent_tasks(self):
        parsed = SimpleNamespace(
            validation_size=10,
            train_batch_size=3,
            concurrency=1,
            retry_concurrency=1,
            judge_concurrency=1,
        )
        with (
            patch.object(refinement, "_original_parse_args", return_value=parsed),
            patch.object(refinement.sys, "argv", ["runner"]),
        ):
            actual = refinement.parse_args_with_current_pool_defaults()
        self.assertEqual(actual.validation_size, 3)
        self.assertEqual(actual.concurrency, 3)
        self.assertEqual(actual.retry_concurrency, 3)
        self.assertEqual(actual.judge_concurrency, 3)
        train, validation = refinement.load_current_clean_baseline_split(
            Path("unused")
        )
        self.assertEqual(len(train), 5)
        self.assertEqual(len(validation), 3)

    def test_default_concurrency_covers_larger_training_batch(self):
        parsed = SimpleNamespace(
            validation_size=10,
            train_batch_size=5,
            concurrency=1,
            retry_concurrency=1,
            judge_concurrency=1,
        )
        with (
            patch.object(refinement, "_original_parse_args", return_value=parsed),
            patch.object(refinement.sys, "argv", ["runner"]),
        ):
            actual = refinement.parse_args_with_current_pool_defaults()
        self.assertEqual(actual.concurrency, 5)
        self.assertEqual(actual.retry_concurrency, 5)
        self.assertEqual(actual.judge_concurrency, 5)

    def test_first_agent_runs_before_second_registration_finishes(self):
        first_agent_running = threading.Event()
        second_registration_observed_running_agent = threading.Event()

        def prepare(problem_id, *args):
            if problem_id == "second":
                if not first_agent_running.wait(timeout=2):
                    raise AssertionError(
                        "Second registration waited without the first Agent starting"
                    )
                second_registration_observed_running_agent.set()
            return {
                "problem_id": problem_id,
                "repetition": 1,
                "run_dir": Path(args[4]) / problem_id,
            }

        def run(prepared, *args):
            if prepared["problem_id"] == "first":
                first_agent_running.set()
                if not second_registration_observed_running_agent.wait(timeout=2):
                    raise AssertionError("Later Agent registration did not overlap execution")
            return {
                "problem_id": prepared["problem_id"],
                "repetition": 1,
                "run_dir": str(prepared["run_dir"]),
                "average_score": 0.8,
                "dimension_scores": {"quality": 0.8},
            }

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = SimpleNamespace(
                validation_repetitions=1,
                validation_attempts=1,
                validation_retry_delay=0,
                concurrency=2,
                retry_concurrency=2,
                pipeline_agent_start=True,
                evaluation_round_dir=root / "round_1",
                evaluation_problem_ids=("first", "second"),
            )
            with (
                patch.object(interaction, "VALIDATION_PROBLEMS", ("wrong",)),
                patch.object(interaction, "prepare_validation_problem", side_effect=prepare),
                patch.object(interaction, "run_validation_problem", side_effect=run),
            ):
                result = interaction.evaluate_round(
                    root,
                    1,
                    {"rubric_id": "test"},
                    {"first": {}, "second": {}},
                    root / "prompt.md",
                    args,
                )

        self.assertTrue(first_agent_running.is_set())
        self.assertTrue(second_registration_observed_running_agent.is_set())
        self.assertEqual(len(result["problem_results"]), 2)

    def test_clean_drafts_are_routed_by_train_validation_split(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            train_root = root / "train" / "runs" / "round_1"
            validation_root = root / "validation" / "runs" / "round_1"
            train_report = self.write_clean_report(
                train_root, "train_run", "train_problem"
            )
            validation_report = self.write_clean_report(
                validation_root, "validation_run", "validation_problem"
            )
            with (
                patch.object(
                    refinement, "TRAIN_PROBLEM_SET", frozenset({"train_problem"})
                ),
                patch.object(
                    refinement,
                    "VALIDATION_PROBLEM_SET",
                    frozenset({"validation_problem"}),
                ),
                patch.object(
                    refinement, "TRAIN_CLEAN_BASELINE_ROUND_ROOT", train_root
                ),
                patch.object(
                    refinement,
                    "VALIDATION_CLEAN_BASELINE_ROUND_ROOT",
                    validation_root,
                ),
            ):
                self.assertEqual(
                    refinement.resolve_clean_baseline_report(
                        "train_problem", root / "wrong"
                    ),
                    train_report,
                )
                self.assertEqual(
                    refinement.resolve_clean_baseline_report(
                        "validation_problem", root / "wrong"
                    ),
                    validation_report,
                )
                self.assertFalse(
                    refinement.clean_baseline_report_matches_problem(
                        "validation_problem", train_report
                    )
                )


if __name__ == "__main__":
    unittest.main()
