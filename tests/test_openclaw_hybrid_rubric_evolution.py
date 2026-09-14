import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.OpenClaw import run_hybrid_rubric_evolution as hybrid


class HybridRubricEvolutionTests(unittest.TestCase):
    def test_five_dimension_score_excludes_innovativeness(self):
        dimensions = {name: 0.8 for name in hybrid.FIVE_DIMENSIONS}
        dimensions[hybrid.EXCLUDED_DIMENSION] = 0.0
        self.assertAlmostEqual(hybrid.five_dimension_score(dimensions), 0.8)

    def test_global_mode_is_default_when_incremental_is_disabled(self):
        mode, reason = hybrid.choose_mode(
            {"nodes": {}},
            2,
            SimpleNamespace(enable_incremental=False),
        )
        self.assertEqual(mode, "global")
        self.assertEqual(reason, "incremental_disabled")

    def test_source_round_filters_before_top_k_selection(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            round_one = source / "round_one_output"
            round_six = source / "round_six_output"
            round_one.mkdir()
            round_six.mkdir()
            low = {name: 0.6 for name in hybrid.FIVE_DIMENSIONS}
            high = {name: 0.9 for name in hybrid.FIVE_DIMENSIONS}
            hybrid.workflow_evolution.write_json(
                source / "workflows" / "search_graph.json",
                {
                    "nodes": {
                        "node_r1": {
                            "node_id": "node_r1",
                            "round": 1,
                            "valid": True,
                            "output_dir": str(round_one),
                            "dimension_scores": low,
                        },
                        "node_r6": {
                            "node_id": "node_r6",
                            "round": 6,
                            "valid": True,
                            "output_dir": str(round_six),
                            "dimension_scores": high,
                        },
                    }
                },
            )
            selected = hybrid.select_source_nodes(source, 1, source_round=1)
            self.assertEqual(selected[0]["node_id"], "node_r1")

    def test_global_acceptance_protects_analysis_and_saturated_dimensions(self):
        args = SimpleNamespace(
            skip_judge=False,
            dimension_regression_tolerance=0.025,
            global_min_improvement=0.005,
        )
        validation = {"candidate_verified": True}
        accepted = hybrid.global_accepted(
            validation,
            0.02,
            {
                "structural_coherency": 0.0,
                "scoring_decomposition": 0.0,
                "analysis_groundedness": 0.01,
            },
            args,
        )
        rejected = hybrid.global_accepted(
            validation,
            0.02,
            {
                "structural_coherency": 0.0,
                "scoring_decomposition": 0.0,
                "analysis_groundedness": -0.05,
            },
            args,
        )
        self.assertTrue(accepted)
        self.assertFalse(rejected)

    def test_global_validation_requires_transaction_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            validation = {
                "errors": [],
                "changed_files": [
                    "code/model.py",
                    "results/solution_report.md",
                ],
            }
            result = hybrid.validate_global_node(
                validation,
                {"output_dir": str(output)},
                {"criteria": []},
            )
            self.assertFalse(result["candidate_verified"])
            self.assertTrue(
                any("global refinement artifact" in error for error in result["errors"])
            )

    def test_global_proposal_rejects_reporting_disguised_as_full_refinement(self):
        proposal = {
            "headline_decision": "Preserve or revise the main recommendation",
            "decision_mechanism": "Use an observable signal to choose an action",
            "baseline_comparison": "Run inherited and revised rules on common inputs",
            "operational_constraints": ["Both rules obey the same resource limit"],
            "integration_plan": "Update verification and then copy it into the report",
            "regression_invariants": ["Existing result remains true"],
            "criteria": [
                {
                    "stage": "implementation_analysis",
                    "defect_family": "one_generator_check",
                    "change_type": "independent_validation",
                    "criterion": "Add one internal generator consistency check with an auditable result.",
                    "failure_condition": "The check is absent.",
                    "decision_link": "Claims to support the recommendation.",
                    "parent_gap_evidence": "The parent report has no independent check.",
                    "evidence_required": ["one result"],
                    "authoritative_artifacts": ["code/check.py"],
                },
                {
                    "stage": "reporting",
                    "defect_family": "copy_check_to_report",
                    "change_type": "reporting_sync",
                    "criterion": "Copy the internal consistency check into the final report text.",
                    "failure_condition": "The report omits it.",
                    "decision_link": "Mentions the recommendation.",
                    "parent_gap_evidence": "The parent report only states the result.",
                    "evidence_required": ["report text"],
                    "authoritative_artifacts": ["results/solution_report.md"],
                },
            ],
        }
        with self.assertRaisesRegex(ValueError, "problem_data or modeling"):
            hybrid.validate_global_proposal(proposal)

    def test_global_proposal_requires_and_accepts_decision_mechanism_chain(self):
        proposal = {
            "headline_decision": "Select an implementable action",
            "decision_mechanism": "Map observed state to one feasible action",
            "baseline_comparison": "Evaluate old and new rules on identical inputs",
            "operational_constraints": ["Respect a shared capacity limit"],
            "integration_plan": "Define the rule, execute both policies, and update conclusions",
            "regression_invariants": ["Preserve the verified input totals"],
            "criteria": [
                {
                    "stage": "modeling",
                    "defect_family": "missing_decision_rule",
                    "change_type": "decision_model",
                    "criterion": "Define a reproducible mapping from observable state to a feasible action.",
                    "failure_condition": "No action can be reproduced from the stated inputs.",
                    "decision_link": "It determines which action is recommended.",
                    "parent_gap_evidence": "The parent states a recommendation without an executable rule.",
                    "evidence_required": ["formal decision rule"],
                    "authoritative_artifacts": ["results/step_02_modeling_assumptions.md"],
                },
                {
                    "stage": "implementation_analysis",
                    "defect_family": "missing_policy_comparison",
                    "change_type": "policy_comparison",
                    "criterion": "Execute inherited and revised policies on common inputs and compare outcomes and resource use.",
                    "failure_condition": "The policies use incompatible evidence or omit feasibility effects.",
                    "decision_link": "It tests whether the revised action improves the decision.",
                    "parent_gap_evidence": "The parent does not compare its recommendation with an explicit baseline.",
                    "evidence_required": ["common-input comparison table"],
                    "authoritative_artifacts": ["code/policy_comparison.py", "results/step_05_validation_analysis.md"],
                },
            ],
        }
        criteria, substantive = hybrid.validate_global_proposal(proposal)
        self.assertEqual(len(criteria), 2)
        self.assertEqual(len(substantive), 2)

    def test_global_prompt_distinguishes_parent_and_child_reports(self):
        seed = hybrid.local.REFERENCE_SEED_WORKFLOW.read_text(encoding="utf-8")
        candidate = {
            "stage": "implementation_analysis",
            "rubric_id": "rubric_test",
            "criterion": "Verify a coordinated correction with executable evidence.",
            "status": "candidate",
        }
        prompt = hybrid.global_prompt(seed, candidate, {"node_id": "parent"})
        self.assertIn("parent_solution_report.md", prompt)
        self.assertIn("solution_report.md` is intentionally absent until step 6", prompt)
        self.assertIn("never to\n   read `solution_report.md`", prompt)
        self.assertIn("Data support audit", prompt)
        self.assertIn("one or two decision-critical empirical inputs", prompt)
        self.assertIn("Never\n   substitute a proxy", prompt)

    def test_global_verifier_receives_data_support_contract(self):
        candidate = {
            "stage": "implementation_analysis",
            "rubric_id": "rubric_test",
            "criterion": "Compare a decision mechanism with its inherited baseline.",
            "status": "candidate",
        }
        prompts = hybrid.global_role_prompts(
            hybrid.local.new_rubric_bank(), candidate
        )
        verifier = prompts["implementation_analysis"]
        self.assertIn("Data support audit", verifier)
        self.assertIn("Search decision", verifier)
        self.assertIn("private and unavailable", verifier)


if __name__ == "__main__":
    unittest.main()
