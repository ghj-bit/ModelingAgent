import os
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.OpenClaw import run_mlevolve_rubric_evolution as evolution


def make_node(root: Path, node_id: str, parent_id: str | None, score: float, delta=None):
    output = root / node_id
    output.mkdir(parents=True, exist_ok=True)
    return {
        "node_id": node_id,
        "parent_id": parent_id,
        "children": [],
        "output_dir": str(output),
        "run_dir": str(output),
        "report": str(output / "report.md"),
        "score": score,
        "dimension_scores": {},
        "valid": True,
        "terminal": False,
        "visits": 1,
        "total_reward": delta or 0.0,
        "score_delta": delta,
        "patch": {"changed_files": []},
        "semantic_signature": {
            "stage": "modeling",
            "defect_family": node_id,
        },
    }


class MLEvolveRubricTests(unittest.TestCase):
    def test_seed_prompt_matches_baseline_and_keeps_stage_summaries(self):
        baseline_prompt = evolution.openclaw_baseline.BASELINE_PROMPT_TEMPLATE_PATH.read_text(
            encoding="utf-8"
        )
        seed_prompt = evolution.local.DEFAULT_SEED_WORKFLOW.read_text(
            encoding="utf-8"
        )
        baseline_workflow = evolution.openclaw_baseline.WORKFLOW_SECTION_PATTERN.search(
            baseline_prompt
        ).group(1).strip()
        seed_workflow = evolution.openclaw_baseline.WORKFLOW_SECTION_PATTERN.search(
            seed_prompt
        ).group(1).strip()
        self.assertEqual(seed_workflow, baseline_workflow)
        self.assertEqual(
            seed_prompt.split("## Required Workflow", 1)[0],
            baseline_prompt.split("## Required Workflow", 1)[0],
        )
        self.assertEqual(
            seed_prompt.split("## Final Report Contract", 1)[1],
            baseline_prompt.split("## Final Report Contract", 1)[1],
        )
        self.assertIn("## Workflow Summary Contract", seed_prompt)
        for relative in evolution.local.REQUIRED_STAGE_SUMMARIES:
            self.assertIn(Path(relative).name, seed_prompt)

    def test_default_experiment_and_seed_are_problem_scoped(self):
        with patch.object(
            sys,
            "argv",
            ["run", "--problem_id", "2025_Managing_Sustainable_Tourism"],
        ):
            args = evolution.parse_args()
        self.assertIsNone(args.seed_root)
        self.assertIn("2025_Managing_Sustainable_Tourism", args.exp)
        self.assertEqual(args.operators, list(evolution.RUBRIC_OPERATORS))
        self.assertEqual(args.judge_repeats, 3)
        self.assertEqual(args.judge_concurrency, 3)

    def test_repeated_judge_paths_are_json_serializable(self):
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            report = run_dir / "output" / "results" / "solution_report.md"
            report.parent.mkdir(parents=True)
            report.write_text("# Report\n", encoding="utf-8")
            raw_result = run_dir / "judge.json"
            payload = {
                "average_scores": {
                    "round_report": {
                        "average_overall_score": 0.75,
                        "average_dimension_scores": {"modeling_groundedness": 0.75},
                        "trial_count": 3,
                    }
                },
                "evaluations": {
                    "report": [{"raw_result": str(raw_result)}]
                },
            }
            artifacts = {
                "run_dir": str(run_dir),
                "final_report": str(report),
                "judge_result": None,
            }
            args = SimpleNamespace(
                skip_judge=False,
                judge_repeats=3,
                judge_concurrency=3,
                model="deepseek/deepseek-v4-flash",
            )
            with patch.object(
                evolution.judge_stability,
                "evaluate_reports_repeated",
                return_value=payload,
            ):
                result = evolution.attach_repeated_judge("problem", artifacts, args)
            self.assertIsInstance(result["judge_result"], str)
            self.assertIsInstance(result["judge_stability_result"], str)
            json.dumps(result)

    def test_external_seed_root_must_match_problem_id(self):
        with tempfile.TemporaryDirectory() as temporary:
            seed_root = Path(temporary) / "round_1"
            run_dir = seed_root / "model" / "2013_Bank_Service_Problem_run"
            report = run_dir / "output" / "results" / "solution_report.md"
            metadata = run_dir / "meta" / "run.json"
            report.parent.mkdir(parents=True)
            metadata.parent.mkdir(parents=True)
            report.write_text("# Report\n", encoding="utf-8")
            metadata.write_text(
                json.dumps({"problem_id": "2013_Bank_Service_Problem"}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Seed root problem mismatch"):
                evolution.validate_seed_root_problem(
                    seed_root, "2025_Managing_Sustainable_Tourism"
                )

    def test_automatic_seed_uses_problem_experiment_and_no_skills(self):
        with tempfile.TemporaryDirectory() as temporary:
            experiment = Path(temporary) / "experiment"
            workflows = experiment / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "round_1").mkdir()
            (workflows / "round_1" / "prompt.md").write_text(
                "{{QUESTION}}", encoding="utf-8"
            )
            run_dir = experiment / "runs" / "round_1" / "model" / "task_run"
            report = run_dir / "output" / "results" / "solution_report.md"
            judge = run_dir / "judge.json"
            report.parent.mkdir(parents=True)
            report.write_text("# Report\n", encoding="utf-8")
            judge.write_text("{}", encoding="utf-8")
            args = SimpleNamespace(
                problem_id="2025_Managing_Sustainable_Tourism",
                model="deepseek/deepseek-v4-flash",
                openclaw_command=None,
                agent=None,
                thinking="high",
                timeout=7200,
                skip_judge=False,
            )
            artifacts = {
                "run_dir": run_dir,
                "final_report": report,
                "judge_result": judge,
                "average_score": 0.5,
            }
            with patch.object(evolution.local, "recover_branch", return_value=None), patch.object(
                evolution.openclaw_baseline,
                "run_problem",
                return_value=artifacts,
            ) as mocked_run, patch.object(
                evolution.workflow_evolution,
                "judge_dimension_scores",
                return_value={"modeling_groundedness": 0.5},
            ):
                seed = evolution.execute_problem_seed_round(
                    experiment,
                    workflows / "results.json",
                    {"question": "Tourism task"},
                    args,
                )
            run_args = mocked_run.call_args.args[2]
            self.assertEqual(
                Path(run_args.output_root), experiment / "runs" / "round_1"
            )
            self.assertIsNone(run_args.skills_source)
            self.assertEqual(run_args.run_directory_prefix, "seed")
            self.assertEqual(seed["problem_id"], args.problem_id)
            self.assertEqual(seed["selected_output_dir"], str(run_dir / "output"))

    def test_semantic_duplicate_uses_canonical_family_and_targets(self):
        candidate = {"stage": "modeling", "criterion": "Compare pooled and separate teller queues."}
        signature = {
            "stage": "modeling",
            "defect_family": "queue_configuration_robustness",
            "target_claims": ["minimum teller count"],
            "intervention": "compare pooled and dedicated queues",
        }
        memory = evolution.new_semantic_memory()
        memory["entries"].append(
            {
                "rubric_id": "old",
                "criterion": "Test whether single-line assumptions alter staffing.",
                "signature": {
                    "stage": "modeling",
                    "defect_family": "queue_configuration_robustness",
                    "target_claims": ["minimum teller count"],
                    "intervention": "compare single line with dedicated lines",
                },
            }
        )
        duplicate, similarity = evolution.semantic_duplicate(candidate, signature, memory, 0.68)
        self.assertEqual(duplicate["rubric_id"], "old")
        self.assertGreaterEqual(similarity, 0.68)

    def test_family_cools_down_after_two_non_positive_results(self):
        signature = {"defect_family": "traceability"}
        memory = evolution.new_semantic_memory()
        for delta in (-0.01, 0.0):
            memory["entries"].append(
                {"signature": signature, "score_delta": delta}
            )
        self.assertTrue(evolution.family_is_cooled_down(signature, memory))

    def test_candidate_stage_plan_covers_all_stages_and_prioritizes_weakness(self):
        node = {
            "dimension_scores": {
                "data_groundedness": 0.2,
                "modeling_groundedness": 0.4,
                "analysis_groundedness": 0.6,
                "structural_coherency": 0.8,
            }
        }
        plan = evolution.candidate_stage_plan(node)
        self.assertEqual(plan[0], "problem_data")
        self.assertEqual(set(plan), set(evolution.local.STAGES))
        self.assertEqual(len(plan), len(set(plan)))

    def test_semantically_exhausted_nodes_are_not_expandable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            node = make_node(root, "root", None, 0.5)
            node["semantic_exhausted"] = True
            tree = {"root_id": "root", "nodes": {"root": node}}
            args = SimpleNamespace(max_children=3)
            self.assertEqual(evolution.expandable_nodes(tree, args), [])

    def test_duplicate_retry_forces_a_different_stage(self):
        duplicate_text = (
            "Require traceable source evidence for every external numeric input "
            "used by the solution."
        )

        def proposal(stage, criterion, family):
            return {
                "stage": stage,
                "risk": "A concrete inherited artifact risk is not checked.",
                "criterion": criterion,
                "failure_condition": "The required evidence is absent.",
                "evidence_required": ["artifact evidence"],
                "expected_outputs": ["updated stage artifact"],
                "rationale": "The correction is reusable across modeling tasks.",
                "semantic_signature": {
                    "stage": stage,
                    "defect_family": family,
                    "target_claims": ["reported decision"],
                    "intervention": "add verifiable evidence",
                    "evidence_type": ["artifact"],
                },
            }

        responses = [
            proposal("problem_data", duplicate_text, "source_traceability"),
            proposal(
                "modeling",
                "Require a dimensional consistency audit for every governing equation and derived decision threshold.",
                "dimensional_consistency",
            ),
        ]
        bank = {
            "promoted": {
                stage: (
                    [{"criterion": duplicate_text}]
                    if stage == "problem_data"
                    else []
                )
                for stage in evolution.local.STAGES
            },
            "trials": [],
        }
        parent = {
            "node_id": "parent",
            "dimension_scores": {
                "data_groundedness": 0.2,
                "modeling_groundedness": 0.4,
            },
        }
        args = SimpleNamespace(
            semantic_attempts=2,
            semantic_threshold=0.68,
            opt_model="optimizer",
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            report = output / "results" / "solution_report.md"
            report.parent.mkdir(parents=True)
            report.write_text("A modeling report.", encoding="utf-8")
            with patch.object(
                evolution.local, "optimizer_response", side_effect=responses
            ) as mocked:
                candidate, _ = evolution.propose_unique_candidate(
                    output,
                    parent,
                    bank,
                    evolution.new_semantic_memory(),
                    2,
                    args,
                )
        self.assertEqual(candidate["stage"], "modeling")
        self.assertEqual(candidate["operator_type"], "ask_expert")
        self.assertEqual(mocked.call_count, 2)
        retry_prompt = mocked.call_args_list[1].args[0]["messages"][1]["content"]
        self.assertIn(duplicate_text, retry_prompt)
        self.assertIn("MUST use stage `modeling`", retry_prompt)
        self.assertIn("operator_type `ask_expert`", retry_prompt)

    def test_operator_specific_refinement_prompts_use_distinct_feedback_files(self):
        seed = evolution.local.DEFAULT_SEED_WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "react": ("**ReAct:**", "react_1.md"),
            "ask_expert": ("**AskExpert:**", "ask_expert_1.md"),
            "counterexample": ("**Counterexample:**", "counterexample_1.md"),
        }
        for operator, (label, feedback) in expected.items():
            candidate = {
                "stage": "modeling",
                "operator_type": operator,
                "rubric_id": f"rubric_{operator}",
                "criterion": "Require one concrete, testable correction.",
            }
            prompt = evolution.refinement_prompt(
                seed, "modeling", candidate, "parent"
            )
            self.assertIn(label, prompt)
            self.assertIn(feedback, prompt)
            roles = evolution.local.build_role_prompts(
                evolution.local.new_rubric_bank(), "modeling", [], candidate
            )
            self.assertIn(
                evolution.local.RUBRIC_OPERATOR_SPECS[operator]["role"],
                roles["modeling"],
            )
            self.assertIn("Never use CMD-only `dir /s /b`", prompt)
            self.assertIn(
                "Never use CMD-only `dir /s /b`", roles["modeling"]
            )

    def test_cached_prompt_receives_windows_tool_protocol_once(self):
        original = "# Prompt\n\n## Local Rubric Trial Protocol\n\n- Existing.\n"
        upgraded = evolution.ensure_windows_tool_protocol(original)
        self.assertIn("## Windows Tool Protocol", upgraded)
        self.assertIn("Get-ChildItem -LiteralPath", upgraded)
        self.assertEqual(evolution.ensure_windows_tool_protocol(upgraded), upgraded)

    def test_progressive_widening_does_not_immediately_allow_three_children(self):
        self.assertEqual(evolution.progressive_child_limit({"visits": 1}, 3), 1)
        self.assertEqual(evolution.progressive_child_limit({"visits": 2}, 3), 2)
        self.assertEqual(evolution.progressive_child_limit({"visits": 4}, 3), 3)

    def test_exhausted_children_unlock_next_progressive_branch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent = make_node(root, "parent", None, 0.5)
            parent["visits"] = 3
            first = make_node(root, "first", "parent", 0.5)
            second = make_node(root, "second", "parent", 0.5)
            first["terminal"] = True
            second["valid"] = False
            parent["children"] = ["first", "second"]
            tree = {
                "root_id": "parent",
                "nodes": {node["node_id"]: node for node in (parent, first, second)},
            }
            self.assertEqual(evolution.effective_child_limit(tree, parent, 3), 3)

    def test_ordering_only_errors_are_warnings_when_causal_outputs_are_fresh(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            feedback = output / "logs" / "operator_feedback" / "react_1.md"
            stale = output / "logs" / "setup.txt"
            changed = output / "code" / "model.py"
            validation_file = output / "results" / "check.json"
            report = output / "results" / "solution_report.md"
            for path in (feedback, stale, changed, validation_file, report):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(path.name, encoding="utf-8")
            os.utime(stale, (10, 10))
            os.utime(feedback, (20, 20))
            for path in (changed, validation_file, report):
                os.utime(path, (30, 30))
            raw_validation = {
                "valid": False,
                "candidate_verified": False,
                "errors": [
                    "modified before ReAct feedback: setup.txt",
                    "validation predates ReAct feedback: old_check.py",
                ],
                "changed_files": ["logs/setup.txt", "code/model.py"],
                "new_or_modified_validation_files": ["results/check.json"],
            }
            with patch.object(
                evolution.local, "validate_node", return_value=raw_validation
            ):
                result = evolution.validate_search_node(
                    {"output_dir": str(output)},
                    output,
                    {"stage": "modeling", "rubric_id": "rubric"},
                    "parent",
                )
            self.assertTrue(result["candidate_verified"])
            self.assertEqual(len(result["ordering_warnings"]), 2)
            self.assertEqual(result["operational_changed_files"], ["logs/setup.txt"])
            self.assertNotIn("logs/setup.txt", result["changed_files"])

    def test_refinement_prompt_assigns_file_choice_to_modeling_agent(self):
        candidate = {
            "stage": "modeling",
            "rubric_id": "rubric_test",
            "criterion": "Require one concrete model correction with evidence.",
        }
        seed = """## Required Workflow

1. Existing workflow.

## Workspace

- Workspace root: `{{OUTPUT_DIR}}`
"""
        prompt = evolution.refinement_prompt(
            seed, "modeling", candidate, "parent"
        )
        self.assertIn("main modeling Agent", prompt)
        self.assertIn("preserved_files", prompt)
        self.assertIn("metadata_files", prompt)
        self.assertIn("dedicated fresh log", prompt)

    def test_top_k_selection_preserves_root_branch_diversity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root_node = make_node(root, "root", None, 0.5)
            a = make_node(root, "a", "root", 0.8, 0.1)
            a2 = make_node(root, "a2", "a", 0.9, 0.1)
            b = make_node(root, "b", "root", 0.7, 0.1)
            root_node["children"] = ["a", "b"]
            a["children"] = ["a2"]
            tree = {"root_id": "root", "nodes": {n["node_id"]: n for n in (root_node, a, a2, b)}}
            selected = evolution.select_top_k_diverse(tree, [a, a2, b], 2)
            self.assertEqual({evolution.root_branch_id(tree, n["node_id"]) for n in selected}, {"a", "b"})

    def test_fusion_pair_requires_positive_complementary_branches(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root_node = make_node(root, "root", None, 0.5)
            a = make_node(root, "a", "root", 0.7, 0.02)
            b = make_node(root, "b", "root", 0.72, 0.03)
            a["semantic_signature"]["defect_family"] = "model_robustness"
            b["semantic_signature"]["defect_family"] = "report_uncertainty"
            a["patch"]["changed_files"] = ["code/model.py"]
            b["patch"]["changed_files"] = ["results/report.md"]
            root_node["children"] = ["a", "b"]
            tree = {"root_id": "root", "nodes": {n["node_id"]: n for n in (root_node, a, b)}}
            args = SimpleNamespace(min_improvement=0.005, fusion_overlap_penalty=0.2)
            primary, donor = evolution.select_fusion_pair(tree, args)
            self.assertEqual(primary["node_id"], "b")
            self.assertEqual(donor["node_id"], "a")

    def test_fusion_bundle_contains_primary_donor_and_lca_versions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root_node = make_node(root, "root", None, 0.5)
            primary = make_node(root, "primary", "root", 0.7, 0.02)
            donor = make_node(root, "donor", "root", 0.71, 0.03)
            root_node["children"] = ["primary", "donor"]
            relative = Path("results") / "analysis.md"
            for node, text in (
                (root_node, "base"),
                (primary, "primary"),
                (donor, "donor"),
            ):
                path = Path(node["output_dir"]) / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            donor["patch"]["changed_files"] = [relative.as_posix()]
            tree = {
                "root_id": "root",
                "nodes": {
                    node["node_id"]: node
                    for node in (root_node, primary, donor)
                },
            }
            staging = evolution.prepare_fusion_parent(
                root / "round", tree, primary, donor
            )
            self.assertEqual(
                (staging / relative).read_text(encoding="utf-8"), "primary"
            )
            bundle = staging / "data" / "fusion_donor"
            self.assertEqual(
                (bundle / "d" / relative).read_text(encoding="utf-8"),
                "donor",
            )
            self.assertEqual(
                (bundle / "l" / relative).read_text(encoding="utf-8"),
                "base",
            )
            self.assertTrue((bundle / "manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
