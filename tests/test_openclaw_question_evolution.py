import tempfile
import unittest
from pathlib import Path

from src.OpenClaw import baseline
from src.OpenClaw import run_evolution as evolution


def strategy(dimension: str, label: str) -> dict:
    return evolution.canonical_question_strategy(
        {
            "target_dimensions": [dimension],
            "expert_role": f"{label} specialist",
            "question_objective": (
                f"Identify a decision-changing {label} weakness and prescribe "
                "a concrete, verifiable refinement for the current stage."
            ),
            "required_outputs": [f"{label} diagnosis", "verification requirement"],
        }
    )


class OpenClawQuestionEvolutionTests(unittest.TestCase):
    def setUp(self):
        self.prompt = Path("src/OpenClaw/prompt.md").read_text(encoding="utf-8")

    def test_ask_expert_cannot_be_inserted_after_final_report(self):
        _, workflow, _ = evolution.split_required_workflow(self.prompt)
        steps = evolution.parse_steps(workflow)
        report_step = evolution.final_report_step_number(steps)
        positions = evolution.valid_insertion_positions(steps, "AskExpert")
        self.assertTrue(positions)
        self.assertTrue(all(position < report_step for position in positions))

    def test_seed_prompt_has_receipt_protocol_but_no_operator_contract(self):
        self.assertIn("## Strict Workflow Execution Protocol", self.prompt)
        self.assertIn("step_NN.json", self.prompt)
        self.assertNotIn("## Workflow Evidence Contract", self.prompt)

    def test_inherited_prompt_is_upgraded_to_current_protocol(self):
        legacy = evolution.STRICT_PROTOCOL_PATTERN.sub("", self.prompt, count=1)
        child = evolution.insert_operator(
            legacy,
            "AskExpert",
            1,
            strategy("modeling_groundedness", "model validation"),
        )
        self.assertIn("## Strict Workflow Execution Protocol", child)
        self.assertIn("## Workflow Evidence Contract", child)

    def test_three_distinct_strategies_are_embedded_and_renumbered(self):
        insertions = [
            {"operator": "AskExpert", "after_step": 1,
             "question_strategy": strategy("structural_coherency", "assumption")},
            {"operator": "AskExpert", "after_step": 3,
             "question_strategy": strategy("analysis_groundedness", "uncertainty")},
            {"operator": "AskExpert", "after_step": 5,
             "question_strategy": strategy("innovativeness", "innovation")},
        ]
        child = evolution.apply_operator_insertions(self.prompt, insertions)
        _, workflow, _ = evolution.split_required_workflow(child)
        steps = evolution.parse_steps(workflow)
        operator_positions = [
            index
            for index, step in enumerate(steps, start=1)
            if evolution.step_operator(step) == "AskExpert"
        ]
        self.assertEqual(operator_positions, [2, 4, 6])
        self.assertEqual(evolution.final_report_step_number(steps), 8)
        for index in operator_positions:
            self.assertIn(f"This numbered step {index} ", steps[index - 1])
            self.assertIsNotNone(
                evolution.step_question_strategy(steps[index - 1])
            )
        contract = child.split("## Workflow Evidence Contract", 1)[1].split(
            "## Final Report Contract", 1
        )[0]
        self.assertIn("`AskExpert`", contract)
        self.assertNotIn("`ScEnsemble`", contract)
        self.assertNotIn("`Review`", contract)
        evolution.assert_only_workflow_changed(self.prompt, child)

    def test_question_bank_is_incremental_and_rejects_duplicates(self):
        first = strategy("data_groundedness", "provenance")
        with tempfile.TemporaryDirectory() as temporary:
            workflows = Path(temporary) / "workflows"
            workflows.mkdir()
            evolution.append_question_strategies(workflows, [first], 2, 1)
            self.assertEqual(len(evolution.load_question_bank(workflows)), 1)
            with self.assertRaises(ValueError):
                evolution.append_question_strategies(workflows, [first], 3, 2)
            self.assertEqual(len(evolution.load_question_bank(workflows)), 1)

    def test_react_without_question_strategy_does_not_enter_question_bank(self):
        ask_strategy = strategy("analysis_groundedness", "validation")
        insertions = [
            {"operator": "ReAct", "after_step": 1, "question_strategy": None},
            {
                "operator": "AskExpert",
                "after_step": 3,
                "question_strategy": ask_strategy,
            },
        ]
        with tempfile.TemporaryDirectory() as temporary:
            workflows = Path(temporary) / "workflows"
            workflows.mkdir()
            evolution.append_question_strategies(
                workflows,
                [item["question_strategy"] for item in insertions],
                2,
                1,
            )
            bank = evolution.load_question_bank(workflows)
            self.assertEqual(len(bank), 1)
            self.assertEqual(bank[0]["strategy_id"], ask_strategy["strategy_id"])

    def test_innovation_is_limited_to_model_and_execution_barriers(self):
        _, workflow, _ = evolution.split_required_workflow(self.prompt)
        steps = evolution.parse_steps(workflow)
        self.assertEqual(evolution.innovation_insertion_positions(steps), [2, 3])

    def test_fourth_ask_expert_is_rejected(self):
        child = evolution.apply_operator_insertions(
            self.prompt,
            [
                {"operator": "AskExpert", "after_step": 1,
                 "question_strategy": strategy("data_groundedness", "data")},
                {"operator": "AskExpert", "after_step": 3,
                 "question_strategy": strategy("modeling_groundedness", "model")},
                {"operator": "AskExpert", "after_step": 5,
                 "question_strategy": strategy("analysis_groundedness", "analysis")},
            ],
        )
        with self.assertRaises(ValueError):
            evolution.insert_operator(
                child,
                "AskExpert",
                7,
                strategy("structural_coherency", "structure"),
            )

    def test_positive_innovation_requires_complete_artifact_chain(self):
        innovation = strategy("innovativeness", "dynamic staffing")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workflows = root / "workflows"
            workflows.mkdir()
            evolution.append_question_strategies(
                workflows, [innovation], 2, 1, parent_score=0.5
            )
            run_dir = root / "run"
            output = run_dir / "output"
            evidence = output / "logs" / "workflow_evidence"
            results = output / "results"
            evidence.mkdir(parents=True)
            results.mkdir(parents=True)
            refined_files = []
            for name in evolution.INNOVATION_ARTIFACTS:
                artifact = results / name
                artifact.write_text("evidence", encoding="utf-8")
                refined_files.append(f"results/{name}")
            (evidence / "ask_expert_1.json").write_text(
                __import__("json").dumps(
                    {
                        "question_strategy": innovation,
                        "refined_files": refined_files,
                        "innovation_artifacts": refined_files,
                    }
                ),
                encoding="utf-8",
            )
            parent_dimensions = {
                name: 0.5 for name in baseline.EXPECTED_JUDGERS
            }
            child_dimensions = dict(parent_dimensions)
            child_dimensions["innovativeness"] = 0.65
            parent = {
                "round": 1,
                "score": 0.5,
                "dimension_scores": parent_dimensions,
            }
            child = {
                "round": 2,
                "score": 0.55,
                "dimension_scores": child_dimensions,
                "run_dir": str(run_dir),
            }
            evolution.update_question_strategy_effects(
                workflows, 2, parent, child
            )
            bank = evolution.load_question_bank(workflows)
            self.assertEqual(bank[0]["status"], "beneficial")
            self.assertAlmostEqual(bank[0]["score_delta"], 0.05)
            self.assertEqual(len(bank[0]["actual_artifacts"]), 6)
            self.assertEqual(evolution.effective_question_bank(bank), bank)

    def test_prose_question_strategy_evidence_is_supported(self):
        self.assertEqual(
            evolution.evidence_strategy_id(
                "Reusable strategy qs_12518571b436 targeting data grounding"
            ),
            "qs_12518571b436",
        )
        self.assertEqual(
            evolution.evidence_strategy_id(
                '{"strategy_id":"qs_dac8b98d14f0"}'
            ),
            "qs_dac8b98d14f0",
        )

    def test_standard_step_receipts_form_a_valid_dependency_chain(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "output"
            evidence = output / "logs" / "workflow_evidence"
            results = output / "results"
            evidence.mkdir(parents=True)
            results.mkdir(parents=True)
            prompt = root / "prompt.md"
            prompt.write_text(
                "## Required Workflow\n\n"
                "1. Understand the problem.\n"
                "2. Produce the final report at the required path.\n\n"
                "## Final Report Contract\n",
                encoding="utf-8",
            )
            stage = results / "understanding.md"
            stage.write_text("understanding", encoding="utf-8")
            (evidence / "step_01.json").write_text(
                '{"step_number":1,"step_name":"Understand the problem",'
                '"status":"completed","input_files":[],'
                '"output_files":["results/understanding.md"],'
                '"authoritative_outputs":["results/understanding.md"],'
                '"summary":"Problem understood","next_step":2}',
                encoding="utf-8",
            )
            report = results / "solution_report.md"
            report.write_text("report", encoding="utf-8")
            (evidence / "step_02.json").write_text(
                '{"step_number":2,"step_name":"Produce the final report",'
                '"status":"completed",'
                '"input_files":["results/understanding.md"],'
                '"output_files":["results/solution_report.md"],'
                '"authoritative_outputs":["results/solution_report.md"],'
                '"summary":"Report produced","next_step":null}',
                encoding="utf-8",
            )
            check = root / "workflow_check.json"
            baseline.check_workflow_execution(prompt, output, check)
            self.assertTrue(evolution.read_json(check, {})["passed"])

    def test_legacy_descriptive_next_step_is_recognized(self):
        self.assertTrue(
            baseline._matches_descriptive_next_step(
                "Produce the final report and management letter",
                "Produce the final report at the required path.",
            )
        )
        self.assertFalse(
            baseline._matches_descriptive_next_step(
                "Run an unrelated task",
                "Produce the final report at the required path.",
            )
        )


if __name__ == "__main__":
    unittest.main()
