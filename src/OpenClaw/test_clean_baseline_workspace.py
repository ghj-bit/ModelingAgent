"""Offline checks for preparing clean workspaces without interaction artifacts."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import run_clean_baseline_train as launcher

try:
    from . import run_substantive_interaction_strategy_clean_baseline as clean
except ImportError:
    import run_substantive_interaction_strategy_clean_baseline as clean


class CleanBaselineWorkspaceTests(unittest.TestCase):
    def test_launcher_resumes_only_an_explicit_experiment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / "data/modeling_data_train.json"
            dataset.parent.mkdir()
            dataset.write_text(json.dumps({"task": {}}), encoding="utf-8")
            existing = root / "openclaw_experiments/existing"
            config = existing / "runs/config.json"
            config.parent.mkdir(parents=True)
            config.write_text(
                json.dumps(
                    {
                        "experiment_type": "substantive_interaction_strategy_clean_baseline",
                        "validation_problems": ["task"],
                        "validation_repetitions": 1,
                        "model": "deepseek/deepseek-v4-flash",
                    }
                ),
                encoding="utf-8",
            )
            completed = launcher.subprocess.CompletedProcess([], 0)
            with (
                patch.object(launcher, "REPO_ROOT", root),
                patch.object(launcher.subprocess, "run", return_value=completed) as run,
                patch.object(sys, "argv", ["launcher", "--num-problems", "1"]),
            ):
                self.assertEqual(launcher.main(), 0)
            generated_command = run.call_args.args[0]
            generated = Path(
                generated_command[generated_command.index("--exp") + 1]
            )
            self.assertNotEqual(generated, existing.resolve())
            self.assertTrue(generated.name.startswith(launcher.EXPERIMENT_PREFIX))

            with (
                patch.object(launcher, "REPO_ROOT", root),
                patch.object(launcher.subprocess, "run", return_value=completed) as run,
                patch.object(
                    sys,
                    "argv",
                    ["launcher", "--num-problems", "1", "--experiment", str(existing)],
                ),
            ):
                self.assertEqual(launcher.main(), 0)
            resumed_command = run.call_args.args[0]
            resumed = Path(resumed_command[resumed_command.index("--exp") + 1])
            self.assertEqual(resumed, existing.resolve())

    def test_reference_prompt_is_packaged_with_source(self):
        reference = clean.strategy.REFERENCE_BASELINE_PROMPT_PATH
        self.assertEqual(reference.parent.name, "prompts")
        self.assertTrue(reference.is_file())
        self.assertNotIn("openclaw_experiments", reference.parts)
        self.assertIn(
            "Search only for external evidence necessary",
            clean.strategy.reference_baseline_prompt_template(),
        )

    def test_clean_workspace_recovers_nonempty_report_without_interaction(self):
        interaction = clean.strategy.interaction
        with tempfile.TemporaryDirectory() as directory:
            experiment = Path(directory)
            run = experiment / "runs/round_1/r1p1_existing"
            report = run / "output/results/solution_report.md"
            report.parent.mkdir(parents=True)
            report.write_text("Completed report", encoding="utf-8")
            metadata = run / "meta/run.json"
            metadata.parent.mkdir()
            metadata.write_text(json.dumps({"problem_id": "task"}), encoding="utf-8")
            with patch.object(sys, "argv", ["runner", "--problem-id", "task"]):
                args = clean.runtime_args(clean.parse_args())
            with (
                patch.object(interaction, "VALIDATION_PROBLEMS", ("task",)),
                patch.object(
                    interaction.baseline,
                    "find_openclaw_command",
                    side_effect=AssertionError("Recovered runs must not register an Agent"),
                ),
            ):
                prepared = clean.strategy.PREPARE_FRESH_PROBLEM(
                    "task", {}, experiment / "prompt.md", 1, 1, experiment, args
                )
            self.assertTrue(prepared["recovered"])
            self.assertEqual(prepared["final_report"], report)

    def test_runs_only_layout_execution_and_resume(self):
        interaction = clean.strategy.interaction
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            experiment = root / "experiment"
            argv = ["runner", "--problem-id", "task", "--exp", str(experiment)]

            def solve(prepared, *args):
                output = prepared["output_dir"]
                self.assertEqual(list((output / "logs").iterdir()), [])
                self.assertEqual(list((output / "code").iterdir()), [])
                prepared["final_report"].write_text("Solved", encoding="utf-8")

            with (
                patch.object(sys, "argv", argv + ["--initialize-only"]),
                patch.object(clean.strategy.baseline, "load_problems", return_value={"task": {}}),
            ):
                clean.main()
            self.assertEqual([path.name for path in experiment.iterdir()], ["runs"])
            prompt = experiment / "runs/round_1/prompt.md"
            self.assertEqual(prompt.read_text(encoding="utf-8"), clean.build_clean_baseline_prompt({}))

            with (
                patch.object(sys, "argv", argv),
                patch.object(clean.strategy.baseline, "load_problems", return_value={"task": {}}),
                patch.object(clean.strategy.baseline, "find_openclaw_command", return_value="openclaw"),
                patch.object(clean.strategy.baseline, "run_checked"),
                patch.object(clean.atexit, "register"),
                patch.object(interaction, "VALIDATION_PROBLEMS", ("task",)),
                patch.object(interaction, "prepare_validation_problem", interaction.prepare_validation_problem),
                patch.object(interaction, "run_validation_problem", interaction.run_validation_problem),
                patch.object(interaction, "judge_report", return_value={"average_score": 0.8, "dimension_scores": {"quality": 0.8}}),
                patch.object(clean.strategy, "run_end_to_end_modeling_phase", side_effect=solve) as agent,
                patch.object(clean.strategy, "main", side_effect=AssertionError("No strategy evolution")),
            ):
                clean.main()
                clean.main()
                agent.assert_called_once()
            self.assertEqual([path.name for path in experiment.iterdir()], ["runs"])
            self.assertFalse(list(experiment.rglob("workflow.json")))
            self.assertFalse(list(experiment.rglob("strategy.json")))
            result = json.loads((experiment / "runs/round_1/result.json").read_text(encoding="utf-8"))
            report = Path(result["problem_results"][0]["final_report"])
            self.assertEqual(report.read_text(encoding="utf-8"), "Solved")
            self.assertTrue((report.parents[2] / "meta/run.json").is_file())
            self.assertTrue((experiment / "runs/round_1/evaluation_checkpoint.json").is_file())

    def prepare(self, root, clean_mode):
        with patch.object(sys, "argv", ["runner", "--problem-id", "task"]):
            args = clean.parse_args()
        run_args = clean.runtime_args(args) if clean_mode else clean._ORIGINAL_RUNTIME_ARGS(args)
        prompt = root / "template.md"
        prompt.write_text(clean.build_clean_baseline_prompt({}), encoding="utf-8")
        interaction = clean.strategy.interaction

        def register(command, run_dir, log_path):
            output = Path(run_dir) / "output"
            if clean_mode:
                self.assertEqual(list((output / "logs").iterdir()), [])
                self.assertEqual(list((output / "code").iterdir()), [])

        with (
            patch.object(interaction, "VALIDATION_PROBLEMS", ("task",)),
            patch.object(interaction.baseline, "find_openclaw_command", return_value="openclaw"),
            patch.object(interaction.baseline, "run_checked", side_effect=register),
        ):
            return interaction.prepare_validation_problem(
                "task", {"question": "Solve the task"}, prompt, 1, 1, root, run_args
            )

    def test_clean_workspace_never_creates_interaction_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(clean.strategy.baseline, "create_operator_role_prompts") as roles,
                patch.object(clean.strategy.interaction.shutil, "copy2") as copy,
                patch.object(Path, "unlink", side_effect=AssertionError("No runtime deletion")),
                patch.object(clean.strategy.interaction.shutil, "rmtree", side_effect=AssertionError("No runtime deletion")),
            ):
                prepared = self.prepare(Path(directory), True)
                roles.assert_not_called()
                copy.assert_not_called()
            output = prepared["output_dir"]
            self.assertTrue((output / "logs").is_dir())
            self.assertEqual(list((output / "logs").iterdir()), [])
            self.assertFalse((output / "code/wait_for_expert_reply.py").exists())

    def test_interaction_runner_keeps_default_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            prepared = self.prepare(Path(directory), False)
            output = prepared["output_dir"]
            for name in ("operator_roles", "operator_feedback", "workflow_evidence"):
                self.assertTrue((output / "logs" / name).is_dir())
            self.assertTrue((output / "code/wait_for_expert_reply.py").is_file())


if __name__ == "__main__":
    unittest.main()
