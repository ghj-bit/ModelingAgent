import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.OpenClaw import baseline
from src.OpenClaw import run_react_rubric_evolution as rubric_evolution


class ReactRubricEvolutionTests(unittest.TestCase):
    def setUp(self):
        self.seed = rubric_evolution.DEFAULT_SEED_WORKFLOW.read_text(
            encoding="utf-8"
        )

    def test_seed_workflow_is_relaxed_without_changing_operator_order(self):
        relaxed = rubric_evolution.remove_stage_check_protocol(self.seed)
        self.assertNotIn("## Strict Workflow Execution Protocol", relaxed)
        self.assertNotIn("## Workflow Evidence Contract", relaxed)
        self.assertNotIn("step_NN.json", relaxed)
        _, workflow, _ = rubric_evolution.workflow_evolution.split_required_workflow(
            relaxed
        )
        steps = rubric_evolution.workflow_evolution.parse_steps(workflow)
        operators = [
            rubric_evolution.workflow_evolution.step_operator(step)
            for step in steps
            if rubric_evolution.workflow_evolution.step_operator(step)
        ]
        self.assertEqual(operators, ["AskExpert", "ReAct"])
        self.assertEqual(len(steps), 8)

    def test_round_two_react_uses_implementation_analysis_rubric(self):
        relaxed = rubric_evolution.remove_stage_check_protocol(self.seed)
        self.assertEqual(
            rubric_evolution.active_react_stages(relaxed),
            ["implementation_analysis"],
        )

    def test_react_after_modeling_uses_modeling_rubric(self):
        prompt = """## Required Workflow
1. Understand the problem and data.
2. Construct the mathematical model and state assumptions.
3. **ReAct:** verify the preceding stage.
4. Produce the final report.

## Final Report Contract
Write the report.
"""
        self.assertEqual(
            rubric_evolution.active_react_stages(prompt), ["modeling"]
        )

    def test_incremental_criterion_is_written_to_role_prompt(self):
        bank = rubric_evolution.new_rubric_bank()
        addition = {
            "rubric_id": "rubric_test",
            "stage": "modeling",
            "criterion": "Verify dimensional consistency for every model equation.",
            "target_dimensions": ["modeling_groundedness"],
            "rationale": "Unit errors invalidate model conclusions.",
        }
        rubric_evolution.append_additions(
            bank, [addition], 2, {"round": 1, "score": 0.5}
        )
        prompts = rubric_evolution.build_role_prompts(bank)
        self.assertIn(addition["criterion"], prompts["modeling"])
        self.assertNotIn(addition["criterion"], prompts["problem_data"])

    def test_duplicate_criterion_detects_reworded_same_check(self):
        existing = [
            {
                "criterion": (
                    "Verify zero interarrival batch handling and test whether "
                    "queue metrics are sensitive to the batch generation method."
                )
            }
        ]
        duplicate = rubric_evolution.find_duplicate_criterion(
            "Test zero interarrival batch generation and quantify whether queue "
            "metrics are sensitive to that batch handling method.",
            existing,
        )
        self.assertIsNotNone(duplicate)

    def test_duplicate_criterion_allows_different_failure_mode(self):
        existing = [
            {"criterion": "Verify zero interarrival batch handling."}
        ]
        duplicate = rubric_evolution.find_duplicate_criterion(
            "Check bootstrap confidence interval coverage using preserved "
            "replication-level outputs.",
            existing,
        )
        self.assertIsNone(duplicate)

    def test_duplicate_criterion_rejects_batch_sensitivity_variant(self):
        existing = [
            {
                "criterion": (
                    "Verify that zero interarrival batch size generation is "
                    "geometric and quantify sensitivity to the generation method."
                )
            }
        ]
        duplicate = rubric_evolution.find_duplicate_criterion(
            "Verify zero interarrival batch generation and quantify sensitivity "
            "of queue results to that generation method.",
            existing,
        )
        self.assertIsNotNone(duplicate)

    def test_baseline_materializes_overridden_role_prompt(self):
        overrides = dict(baseline.REACT_VERIFIER_ROLE_PROMPTS)
        overrides["modeling"] = "custom modeling rubric\n"
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            baseline.create_operator_role_prompts(output, overrides)
            role_file = (
                output
                / "logs"
                / "operator_roles"
                / "react_verifier_modeling.md"
            )
            self.assertEqual(
                role_file.read_text(encoding="utf-8"),
                "custom modeling rubric\n",
            )

    def test_initialize_reuses_seed_result_as_round_one(self):
        args = SimpleNamespace(
            seed_workflow=rubric_evolution.DEFAULT_SEED_WORKFLOW,
            seed_result=rubric_evolution.DEFAULT_SEED_RESULT,
            problem_id="2013_Bank_Service_Problem",
            evolve_workflow=False,
            model="deepseek/deepseek-v4-flash",
            opt_model="deepseek-v4-flash",
            max_rounds=5,
            completion_grace=10.0,
        )
        with tempfile.TemporaryDirectory() as temporary:
            experiment = Path(temporary) / "experiment"
            rubric_evolution.initialize_experiment(experiment, args)
            results = rubric_evolution.workflow_evolution.read_json(
                experiment / "workflows" / "results.json", []
            )
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["round"], 1)
            self.assertTrue(results[0]["seed_reused"])
            self.assertTrue(Path(results[0]["report"]).is_file())
            self.assertTrue(Path(results[0]["judge_result"]).is_file())
            prompt = (
                experiment / "workflows" / "round_1" / "prompt.md"
            ).read_text(encoding="utf-8")
            self.assertIn("{{OUTPUT_DIR}}", prompt)
            self.assertNotIn("2013_Bank_Service_Problem_20260828_184448", prompt)


if __name__ == "__main__":
    unittest.main()
