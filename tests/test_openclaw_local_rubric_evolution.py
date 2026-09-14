import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.OpenClaw import baseline
from src.OpenClaw import run_local_rubric_evolution as local_evolution


class LocalRubricEvolutionTests(unittest.TestCase):
    def test_external_verifier_fallback_writes_feedback_and_overrides_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary) / "run"
            output = run / "output"
            role = output / "logs" / "operator_roles" / "react_verifier_modeling.md"
            role.parent.mkdir(parents=True)
            role.write_text(
                "Rubric criterion for this MCTS edge:\n- [candidate:test] check it\n",
                encoding="utf-8",
            )
            report = output / "results" / "parent_solution_report.md"
            report.parent.mkdir(parents=True)
            report.write_text("# Parent\n", encoding="utf-8")
            prompt = run / "prompt.md"
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text("# Original\n", encoding="utf-8")

            def fake_stream(*_args, **kwargs):
                feedback = Path(kwargs["completion_artifact"])
                feedback.parent.mkdir(parents=True, exist_ok=True)
                feedback.write_text("# Reviewed files\n- parent report\n", encoding="utf-8")

            with patch.object(baseline, "run_checked"), patch.object(
                baseline, "stream_command", side_effect=fake_stream
            ):
                feedback = local_evolution.run_external_verifier(
                    "openclaw",
                    output,
                    run,
                    prompt,
                    "agent",
                    "model",
                    "high",
                    60,
                )

            self.assertTrue(feedback.is_file())
            rendered = prompt.read_text(encoding="utf-8")
            self.assertIn("External Verifier Completion Override", rendered)
            self.assertIn("Do not launch another verifier", rendered)

    def test_experiment_path_is_repo_relative_from_openclaw_directory(self):
        original = Path.cwd()
        try:
            os.chdir(local_evolution.REPO_ROOT / "src" / "OpenClaw")
            resolved, exists = local_evolution.resolve_experiment(
                "openclaw_experiments/local_rubric_20260830_162443"
            )
        finally:
            os.chdir(original)
        self.assertTrue(exists)
        self.assertEqual(
            resolved,
            local_evolution.REPO_ROOT
            / "openclaw_experiments"
            / "local_rubric_20260830_162443",
        )

    def test_partial_run_with_inherited_receipt_is_not_recoverable(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary) / "model" / "problem_run"
            output = run / "output"
            feedback = output / "logs" / "operator_feedback" / "react_1.md"
            report = output / "results" / "solution_report.md"
            receipt = output / local_evolution.TRIAL_RECEIPT
            workflow_check = run / "meta" / "workflow_check.json"
            prompt = run / "prompt.md"
            for path in (feedback, report, receipt, workflow_check, prompt):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("content\n", encoding="utf-8")
            base = 1_700_000_000
            os.utime(receipt, (base - 10, base - 10))
            os.utime(prompt, (base, base))
            os.utime(feedback, (base + 1, base + 1))
            os.utime(report, (base + 2, base + 2))
            os.utime(workflow_check, (base + 3, base + 3))
            self.assertFalse(local_evolution.refinement_run_complete(report))
            os.utime(receipt, (base + 3, base + 3))
            self.assertTrue(local_evolution.refinement_outputs_ready(report))
            os.utime(workflow_check, (base + 4, base + 4))
            self.assertTrue(local_evolution.refinement_run_complete(report))

    def test_recover_branch_completes_missing_local_workflow_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run = root / "node" / "run"
            output = run / "output"
            prompt = run / "prompt.md"
            feedback = output / "logs" / "operator_feedback" / "react_1.md"
            report = output / "results" / "solution_report.md"
            receipt = output / local_evolution.TRIAL_RECEIPT
            for path in (prompt, feedback, report, receipt):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("content\n", encoding="utf-8")
            base = 1_700_000_000
            for offset, path in enumerate((prompt, feedback, report, receipt)):
                os.utime(path, (base + offset, base + offset))

            recovered = local_evolution.recover_branch(
                root, "problem", "model", skip_judge=True
            )

            self.assertEqual(recovered["final_report"], report)
            self.assertTrue((run / "meta" / "workflow_check.json").is_file())

    def test_incomplete_turn_log_is_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "model" / "run" / "meta" / "solve.log"
            log.parent.mkdir(parents=True)
            log.write_text(
                "[agent/embedded] incomplete turn detected: stopReason=toolUse\n",
                encoding="utf-8",
            )
            self.assertEqual(local_evolution.latest_incomplete_turn_log(root), log)

    def test_compaction_role_failure_log_is_retryable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "model" / "run" / "meta" / "solve.log"
            log.parent.mkdir(parents=True)
            log.write_text(
                "compaction retry aggregate timeout (60000ms)\n"
                'error="Error: Cannot continue from message role: assistant"\n',
                encoding="utf-8",
            )
            self.assertEqual(local_evolution.latest_incomplete_turn_log(root), log)

    def test_normal_failure_log_is_not_treated_as_session_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "model" / "run" / "meta" / "solve.log"
            log.parent.mkdir(parents=True)
            log.write_text("ordinary model failure\n", encoding="utf-8")
            self.assertIsNone(local_evolution.latest_incomplete_turn_log(root))

    def test_delayed_subagent_failure_from_an_old_agent_is_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "node" / "meta" / "solve.log"
            log.parent.mkdir(parents=True)
            log.write_text(
                '{"agentId": "current-agent"}\n'
                "[warn] Subagent announce give up (retry-limit) "
                "requester=agent:old-agent\n",
                encoding="utf-8",
            )
            self.assertFalse(local_evolution.has_subagent_delivery_failure(root))

    def test_subagent_failure_for_current_agent_is_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "node" / "meta" / "solve.log"
            log.parent.mkdir(parents=True)
            log.write_text(
                '{"agentId": "current-agent"}\n'
                "[warn] Subagent announce give up (retry-limit) "
                "requester=agent:current-agent\n",
                encoding="utf-8",
            )
            self.assertTrue(local_evolution.has_subagent_delivery_failure(root))

    def test_context_retry_prompt_uses_text_report_and_compact_packet(self):
        normal = "before\n\n## Local Rubric Trial Protocol\n\nafter\n"
        retry = local_evolution.context_retry_prompt(normal)
        self.assertEqual(normal.count("Context-Compaction Retry Protocol"), 0)
        self.assertIn("react_retry_parent_report.md", retry)
        self.assertIn("must not open, wrap", retry)
        self.assertIn("react_retry_evidence_packet.md", retry)
        self.assertIn("line range or JSON Pointer", retry)
        self.assertLess(
            retry.index("## Context-Compaction Retry Protocol"),
            retry.index("## Local Rubric Trial Protocol"),
        )
        self.assertEqual(local_evolution.context_retry_prompt(retry), retry)

    def test_context_retry_roles_are_separate_from_normal_roles(self):
        normal = {"modeling": "normal verifier\n"}
        retry = local_evolution.context_retry_role_prompts(normal)
        self.assertEqual(normal["modeling"], "normal verifier\n")
        self.assertIn("compact evidence packet", retry["modeling"])
        self.assertIn("Do not open either complete report", retry["modeling"])

    def test_context_retry_removes_full_stage_verifier_requirement(self):
        normal = (
            "All five stage summaries are mandatory inputs:\n"
            "Require the verifier to\n"
            "   inspect all five mandatory stage summaries and list their paths under a\n"
            "   `Reviewed files` heading in its feedback.\n\n"
            "## Local Rubric Trial Protocol\n\n"
            "- The verifier must inspect and acknowledge every mandatory stage summary; a\n"
            "  trial with an incomplete `Reviewed files` list is invalid.\n"
        )
        retry = local_evolution.context_retry_prompt(normal)
        self.assertNotIn("inspect all five mandatory stage summaries", retry)
        self.assertIn("read only the compact evidence packet", retry)
        self.assertIn("need not open every", retry)

    def test_refinement_prompt_requires_text_only_final_report(self):
        seed = local_evolution.DEFAULT_SEED_WORKFLOW.read_text(encoding="utf-8")
        prompt = local_evolution.local_refinement_template(
            seed,
            "modeling",
            {"rubric_id": "rubric_test"},
            "node_parent",
        )
        self.assertIn("final report must be text-only Markdown", prompt)
        self.assertIn("do not embed images", prompt)

    def test_compact_retry_report_removes_embedded_media(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            report = output / "results" / "parent_solution_report.md"
            report.parent.mkdir(parents=True)
            report.write_text(
                "# Report\nUseful claim.\n![plot](data:image/png;base64,"
                + "A" * 100_000
                + ")\n## Conclusion\nKeep this.\n",
                encoding="utf-8",
            )
            compact = local_evolution.create_compact_retry_report(output)
            text = compact.read_text(encoding="utf-8")
            self.assertIn("Useful claim", text)
            self.assertIn("Keep this", text)
            self.assertIn("embedded media payload omitted", text)
            self.assertLess(compact.stat().st_size, 1_000)

    def test_default_seed_root_is_reused_without_execution(self):
        seed = local_evolution.load_seed_root(local_evolution.DEFAULT_SEED_ROOT)
        self.assertTrue(seed["seed_reused"])
        self.assertEqual(seed["seed_source"], str(local_evolution.DEFAULT_SEED_ROOT))
        self.assertEqual(seed["offline_score"], 0.7208333333333333)
        self.assertTrue(Path(seed["selected_report"]).is_file())

    def test_initial_rubrics_are_empty(self):
        expected_counts = {stage: 0 for stage in local_evolution.STAGES}
        self.assertEqual(set(local_evolution.INITIAL_STAGE_RUBRICS), set(expected_counts))
        prompts = local_evolution.base_rubrics()
        for stage, count in expected_counts.items():
            criteria = local_evolution.INITIAL_STAGE_RUBRICS[stage]
            self.assertEqual(len(criteria), count)
            self.assertNotIn("Apply this rubric:", prompts[stage])

    def test_new_script_inherits_artifacts_without_completing_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent = root / "parent"
            for name in ("code", "data", "results"):
                (parent / name).mkdir(parents=True)
            (parent / "code" / "model.py").write_text("print(1)\n", encoding="utf-8")
            (parent / "data" / "input.csv").write_text("x\n1\n", encoding="utf-8")
            (parent / "results" / "solution_report.md").write_text(
                "# Parent\n", encoding="utf-8"
            )
            (parent / "results" / "numbers.json").write_text(
                "{}\n", encoding="utf-8"
            )
            template = root / "prompt.md"
            template.write_text(
                "{{PROBLEM_ID}} {{OUTPUT_DIR}} {{FINAL_REPORT}}\n",
                encoding="utf-8",
            )
            _run_dir, output, _prompt = local_evolution.prepare_inherited_run(
                "problem",
                {},
                root / "runs",
                "model",
                template,
                dict(baseline.REACT_VERIFIER_ROLE_PROMPTS),
                parent,
            )
            self.assertTrue(_run_dir.name.startswith("n_"))
            self.assertEqual(_run_dir.parent, root / "runs")
            self.assertTrue((output / "code" / "model.py").is_file())
            self.assertTrue((output / "data" / "input.csv").is_file())
            self.assertTrue((output / "results" / "numbers.json").is_file())
            self.assertTrue(
                (output / "results" / "parent_solution_report.md").is_file()
            )
            self.assertFalse((output / "results" / "solution_report.md").exists())
            manifest = json.loads(
                (output / "logs" / "inheritance_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertIn("results/parent_solution_report.md", manifest["files"])

    def test_inherited_legacy_fusion_bundle_uses_short_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent = root / "parent"
            legacy = (
                parent
                / "data"
                / "fusion_donor"
                / "donor_files"
                / "results"
                / "step_02_modeling_assumptions.md"
            )
            legacy.parent.mkdir(parents=True)
            legacy.write_text("# Donor\n", encoding="utf-8")
            template = root / "prompt.md"
            template.write_text(
                "{{PROBLEM_ID}} {{OUTPUT_DIR}} {{FINAL_REPORT}}\n",
                encoding="utf-8",
            )

            _run_dir, output, _prompt = local_evolution.prepare_inherited_run(
                "problem",
                {},
                root / "runs",
                "model",
                template,
                dict(baseline.REACT_VERIFIER_ROLE_PROMPTS),
                parent,
            )

            shortened = (
                output
                / "data"
                / "fusion_donor"
                / "d"
                / "results"
                / "step_02_modeling_assumptions.md"
            )
            self.assertTrue(shortened.is_file())
            self.assertFalse(
                (output / "data" / "fusion_donor" / "donor_files").exists()
            )

    def test_local_prompt_uses_inherited_refinement_without_judge_dimensions(self):
        seed = local_evolution.DEFAULT_SEED_WORKFLOW.read_text(encoding="utf-8")
        candidate = {
            "rubric_id": "rubric_test",
            "stage": "modeling",
            "criterion": "Check that the declared stochastic process matches the data.",
        }
        prompt = local_evolution.local_refinement_template(
            seed, "modeling", candidate, "node_r1_seed"
        )
        self.assertIn("parent_solution_report.md", prompt)
        self.assertIn("react_verifier_modeling.md", prompt)
        self.assertIn("rubric_trial_receipt.json", prompt)
        self.assertIn("direct child of `node_r1_seed`", prompt)
        self.assertNotIn("control and treatment", prompt.lower())
        self.assertIn("Preserve valid parent work", prompt)
        for path in local_evolution.REQUIRED_STAGE_SUMMARIES:
            self.assertIn(path, prompt)
        self.assertNotIn("## Strict Workflow Execution Protocol", prompt)
        self.assertNotIn("analysis_groundedness", prompt)
        self.assertNotIn("Judge feedback", prompt)

    def test_role_prompt_injects_only_current_edge_rubric(self):
        bank = local_evolution.new_rubric_bank()
        for index in range(4):
            bank["promoted"]["modeling"].append(
                {
                    "rubric_id": f"rubric_{index}",
                    "stage": "modeling",
                    "criterion": f"Criterion number {index} checks a distinct model risk.",
                    "verified_corrections": index,
                    "promoted_round": index + 2,
                }
            )
        candidate = {
            "rubric_id": "rubric_candidate",
            "stage": "modeling",
            "criterion": "Candidate criterion checks another distinct model risk.",
            "status": "candidate",
        }
        prompts = local_evolution.build_role_prompts(
            bank, "modeling", [], candidate
        )
        incremental = [
            line
            for line in prompts["modeling"].splitlines()
            if line.startswith("- [")
        ]
        self.assertEqual(len(incremental), 1)
        self.assertIn("rubric_candidate", incremental[0])
        self.assertNotIn("rubric_0", prompts["modeling"])

    def test_mcts_selects_a_branch_instead_of_following_last_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            seed_output = root / "seed"
            low_output = root / "low"
            high_output = root / "high"
            for output in (seed_output, low_output, high_output):
                output.mkdir()
                (output / "report.md").write_text("report\n", encoding="utf-8")
            seed = {
                "selected_run_dir": str(root),
                "selected_output_dir": str(seed_output),
                "selected_report": str(seed_output / "report.md"),
                "offline_score": 0.5,
                "offline_dimension_scores": {},
            }
            tree = local_evolution.new_mcts_tree(seed)
            parent = tree["nodes"][tree["root_id"]]
            local_evolution.mark_mcts_expansion(tree, parent["node_id"], 2)
            local_evolution.mark_mcts_expansion(tree, parent["node_id"], 3)
            for round_number, output, score in (
                (2, low_output, 0.4),
                (3, high_output, 0.8),
            ):
                node = {
                    "node_id": local_evolution.mcts_node_id(round_number),
                    "parent_id": parent["node_id"],
                    "children": [],
                    "expanded_rounds": [],
                    "round": round_number,
                    "rubric_id": f"rubric_{round_number}",
                    "rubric_lineage": [f"rubric_{round_number}"],
                    "stage": "modeling",
                    "run_dir": str(root),
                    "output_dir": str(output),
                    "report": str(output / "report.md"),
                    "score": score,
                    "dimension_scores": {},
                    "valid": True,
                    "patch": {"type": "verifier_feedback"},
                    "visits": 0,
                    "total_reward": 0.0,
                }
                local_evolution.register_mcts_node(tree, node)
            selected = local_evolution.select_mcts_parent(
                tree, exploration=0.0, max_expansions=2
            )
            self.assertEqual(selected["round"], 3)

    def test_mcts_child_keeps_lineage_but_does_not_reinject_it(self):
        parent = {
            "node_id": "parent",
            "rubric_lineage": ["rubric_old"],
        }
        candidate = {
            "rubric_id": "rubric_new",
            "stage": "implementation_analysis",
        }
        branch_result = {
            "run_dir": "run",
            "output_dir": "output",
            "final_report": "report.md",
            "offline_score": 0.7,
            "offline_dimension_scores": {},
        }
        validation = {"candidate_verified": True, "valid": True}
        node = local_evolution.make_mcts_node(
            branch_result,
            validation,
            {"type": "verifier_feedback"},
            candidate,
            parent,
            2,
        )
        self.assertEqual(node["rubric_lineage"], ["rubric_old", "rubric_new"])
        prompts = local_evolution.build_role_prompts(
            local_evolution.new_rubric_bank(),
            candidate["stage"],
            [],
            {**candidate, "criterion": "Verify one new executable correction."},
        )
        self.assertIn("rubric_new", prompts[candidate["stage"]])
        self.assertNotIn("rubric_old", prompts[candidate["stage"]])

    def test_parent_with_three_children_cannot_receive_a_fourth(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            seed_output = root / "seed"
            seed_output.mkdir()
            report = seed_output / "report.md"
            report.write_text("seed\n", encoding="utf-8")
            tree = local_evolution.new_mcts_tree(
                {
                    "selected_run_dir": str(root),
                    "selected_output_dir": str(seed_output),
                    "selected_report": str(report),
                    "offline_score": 0.5,
                    "offline_dimension_scores": {},
                }
            )
            root_node = tree["nodes"][tree["root_id"]]
            for round_number in range(2, 5):
                output = root / f"child_{round_number}"
                output.mkdir()
                child_report = output / "report.md"
                child_report.write_text("child\n", encoding="utf-8")
                local_evolution.register_mcts_node(
                    tree,
                    {
                        "node_id": local_evolution.mcts_node_id(round_number),
                        "parent_id": root_node["node_id"],
                        "children": [],
                        "expanded_rounds": [],
                        "round": round_number,
                        "rubric_id": f"rubric_{round_number}",
                        "rubric_lineage": [f"rubric_{round_number}"],
                        "stage": "modeling",
                        "run_dir": str(root),
                        "output_dir": str(output),
                        "report": str(child_report),
                        "score": 0.5,
                        "dimension_scores": {},
                        "valid": True,
                        "patch": {"type": "verifier_feedback"},
                        "visits": 0,
                        "total_reward": 0.0,
                    },
                )
            selected = local_evolution.select_mcts_parent(
                tree, exploration=1.414, max_expansions=3
            )
            self.assertNotEqual(selected["node_id"], root_node["node_id"])
            self.assertEqual(len(root_node["children"]), 3)

    def test_candidate_requires_verified_post_feedback_correction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent = root / "parent"
            output = root / "child"
            (parent / "results").mkdir(parents=True)
            (output / "results").mkdir(parents=True)
            (output / "data").mkdir(parents=True)
            (output / "logs" / "operator_feedback").mkdir(parents=True)
            (parent / "results" / "solution_report.md").write_text(
                "old report\n", encoding="utf-8"
            )
            for relative in local_evolution.REQUIRED_STAGE_SUMMARIES:
                summary = output / relative
                summary.parent.mkdir(parents=True, exist_ok=True)
                summary.write_text(f"summary for {relative}\n", encoding="utf-8")
            feedback = output / "logs" / "operator_feedback" / "react_1.md"
            feedback.write_text(
                "Reviewed files\n"
                + "\n".join(local_evolution.REQUIRED_STAGE_SUMMARIES)
                + "\n\nA concrete defect was found.\n",
                encoding="utf-8",
            )
            report = output / "results" / "solution_report.md"
            report.write_text("corrected report\n", encoding="utf-8")
            validation = output / "results" / "targeted_validation.json"
            validation.write_text('{"passed": true}\n', encoding="utf-8")
            receipt = output / local_evolution.TRIAL_RECEIPT
            receipt.write_text(
                json.dumps(
                    {
                        "parent_node_id": "node_parent",
                        "stage": "reporting",
                        "candidate_rubric_id": "rubric_test",
                        "candidate_applied": True,
                        "defect_found": True,
                        "finding": "The conclusion contradicted the result table.",
                        "modified_files": ["results/solution_report.md"],
                        "validation_files": ["results/targeted_validation.json"],
                        "validation_passed": True,
                        "report_regenerated": True,
                        "summary": "Corrected and checked.",
                    }
                ),
                encoding="utf-8",
            )
            base = 1_700_000_000
            os.utime(feedback, (base, base))
            os.utime(validation, (base + 1, base + 1))
            os.utime(report, (base + 2, base + 2))
            os.utime(receipt, (base + 3, base + 3))
            candidate = {"rubric_id": "rubric_test", "stage": "reporting"}
            result = {
                "output_dir": str(output),
                "run_dir": str(root),
            }
            checked = local_evolution.validate_node(
                result, parent, candidate, "node_parent"
            )
            self.assertTrue(checked["candidate_verified"], checked["errors"])
            report.write_text("changed too early\n", encoding="utf-8")
            os.utime(report, (base - 1, base - 1))
            checked = local_evolution.validate_node(
                result, parent, candidate, "node_parent"
            )
            self.assertFalse(checked["candidate_verified"])
            self.assertIn("final report predates ReAct feedback", checked["errors"])

    def test_inherited_validation_evidence_may_predate_feedback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent = root / "parent"
            output = root / "child"
            (parent / "results").mkdir(parents=True)
            (output / "results").mkdir(parents=True)
            (output / "data").mkdir(parents=True)
            (output / "logs" / "operator_feedback").mkdir(parents=True)
            (parent / "results" / "solution_report.md").write_text(
                "parent report\n", encoding="utf-8"
            )
            evidence_parent = parent / "results" / "evidence.json"
            evidence_child = output / "results" / "evidence.json"
            evidence_parent.write_text('{"passed": true}\n', encoding="utf-8")
            evidence_child.write_text('{"passed": true}\n', encoding="utf-8")
            for relative in local_evolution.REQUIRED_STAGE_SUMMARIES:
                summary = output / relative
                summary.parent.mkdir(parents=True, exist_ok=True)
                summary.write_text(f"summary for {relative}\n", encoding="utf-8")
            feedback = output / "logs" / "operator_feedback" / "react_1.md"
            feedback.write_text(
                "Reviewed files\n"
                + "\n".join(local_evolution.REQUIRED_STAGE_SUMMARIES)
                + "\n\nExisting evidence supports a report correction.\n",
                encoding="utf-8",
            )
            report = output / "results" / "solution_report.md"
            report.write_text("corrected report\n", encoding="utf-8")
            receipt = output / local_evolution.TRIAL_RECEIPT
            receipt.write_text(
                json.dumps(
                    {
                        "parent_node_id": "node_parent",
                        "stage": "reporting",
                        "candidate_rubric_id": "rubric_test",
                        "candidate_applied": True,
                        "defect_found": True,
                        "finding": "The report omitted the validation tolerance.",
                        "modified_files": ["results/solution_report.md"],
                        "validation_files": ["results/evidence.json"],
                        "validation_passed": True,
                        "report_regenerated": True,
                        "summary": "Added the tolerance backed by inherited evidence.",
                    }
                ),
                encoding="utf-8",
            )
            base = 1_700_000_000
            os.utime(evidence_parent, (base, base))
            os.utime(evidence_child, (base, base))
            os.utime(feedback, (base + 10, base + 10))
            os.utime(report, (base + 20, base + 20))
            os.utime(receipt, (base + 30, base + 30))
            candidate = {"rubric_id": "rubric_test", "stage": "reporting"}
            result = {"output_dir": str(output), "run_dir": str(root)}

            checked = local_evolution.validate_node(
                result, parent, candidate, "node_parent"
            )
            self.assertTrue(checked["candidate_verified"], checked["errors"])
            self.assertEqual(
                checked["inherited_validation_files"], ["results/evidence.json"]
            )
            self.assertEqual(checked["new_or_modified_validation_files"], [])

            evidence_child.write_text('{"passed": false}\n', encoding="utf-8")
            os.utime(evidence_child, (base, base))
            checked = local_evolution.validate_node(
                result, parent, candidate, "node_parent"
            )
            self.assertFalse(checked["candidate_verified"])
            self.assertIn(
                "validation predates ReAct feedback: evidence.json",
                checked["errors"],
            )

    def test_bank_uses_scores_only_for_candidate_prioritization(self):
        bank = local_evolution.new_rubric_bank()
        self.assertTrue(bank["judge_dimension_scores_used"])
        self.assertFalse(bank["judge_text_feedback_used"])
        self.assertEqual(
            bank["promotion_signal"], "internal_artifact_validation_only"
        )

    def test_start_prompt_matches_baseline_data_search_workflow(self):
        prompt = local_evolution.DEFAULT_SEED_WORKFLOW.read_text(encoding="utf-8")
        match = baseline.WORKFLOW_SECTION_PATTERN.search(prompt)
        self.assertIsNotNone(match)
        workflow = match.group(1)
        baseline_workflow = baseline.WORKFLOW_SECTION_PATTERN.search(
            baseline.BASELINE_PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
        ).group(1)
        self.assertEqual(workflow.strip(), baseline_workflow.strip())
        self.assertIn("at most 1-2 verifiable empirical data items", workflow)
        self.assertIn("6. Produce the final report", workflow)


if __name__ == "__main__":
    unittest.main()
