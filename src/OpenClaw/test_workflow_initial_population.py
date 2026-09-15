"""Offline checks for population initialization and resume compatibility."""
import copy
import json
import math
import os
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import run_substantive_interaction_workflow_evolution as workflow
import run_substantive_interaction_strategy_clean_baseline as clean_baseline


class InitialPopulationTests(unittest.TestCase):
    @staticmethod
    def scored_nodes(scores):
        seeds = workflow.initial_strategy_population()
        return [
            {
                "round": index,
                "utility": score,
                "workflow": copy.deepcopy(seeds[(index - 1) % len(seeds)]),
            }
            for index, score in enumerate(scores, 1)
        ]

    def test_new_population_is_distinct_and_persists_on_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seeds = workflow.load_seed_population(root, False, None)
            self.assertEqual(len(seeds), 3)
            self.assertEqual({seed['max_exchanges'] for seed in seeds}, {2})
            self.assertEqual({seed['seed_operator'] for seed in seeds}, set(workflow.INTERACTION_OPERATORS))
            self.assertEqual(len({seed['workflow_id'] for seed in seeds}), 3)
            self.assertEqual(workflow.load_seed_population(root, True, None), seeds)

    def test_compact_population_persists_only_plural_seed_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seeds = workflow.load_seed_population(
                root, False, None, persist_legacy_file=False
            )
            self.assertEqual(len(seeds), 3)
            self.assertTrue((root / "initial_interaction_workflows.json").is_file())
            self.assertFalse((root / "initial_interaction_workflow.json").exists())

    def test_initial_workflows_bound_refinement_scope(self):
        for seed in workflow.initial_strategy_population():
            instructions = json.dumps(seed, ensure_ascii=False).lower()
            self.assertIn("at most two", instructions)
            self.assertIn("one proportionate independent check", instructions)
            self.assertIn("residual limitations", instructions)

    def test_legacy_resume_keeps_single_seed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = workflow.load_initial_workflow()
            workflow.workflow_evolution.write_json(root / 'initial_interaction_workflow.json', legacy)
            seeds = workflow.load_seed_population(root, True, None)
            self.assertEqual(len(seeds), 1)
            self.assertEqual(seeds[0]['workflow_id'], legacy['workflow_id'])

    def test_optimizer_excludes_requested_workflow_fields_without_mutation(self):
        seed = workflow.initial_strategy_population()[0]
        seed.update(
            changed_components=['actions'],
            mutation_rationale='old mutation rationale',
            crossover_rationale='retained crossover rationale',
        )
        compact = workflow.optimizer_workflow(seed)
        self.assertNotIn('purpose', compact)
        self.assertNotIn('changed_components', compact)
        self.assertNotIn('mutation_rationale', compact)
        self.assertIn('purpose', seed)
        self.assertIn('changed_components', seed)
        self.assertIn('mutation_rationale', seed)
        self.assertNotIn('crossover_rationale', compact)
        self.assertIn('crossover_rationale', seed)
        self.assertEqual(compact['actions'], seed['actions'])

    def test_agent_prompt_does_not_contain_interaction_rubric(self):
        rubric = workflow.load_fixed_rubric(workflow.DEFAULT_FIXED_RUBRIC_PATH)
        prompt = workflow.build_workflow_refinement_prompt(
            workflow.initial_strategy_population()[0]
        )
        self.assertNotIn('## Interaction Rubric', prompt)
        self.assertNotIn(rubric['name'], prompt)
        self.assertIn('## Expert Interaction Workflow', prompt)

    def test_clean_workspace_contains_only_task_directories(self):
        problem = {
            "title": "Offline test",
            "source": "test",
            "year": "2026",
            "question": "Build and validate a small mathematical model.",
        }
        with tempfile.TemporaryDirectory() as directory:
            _, output_dir, _ = workflow.baseline.prepare_run(
                "offline_problem",
                problem,
                Path(directory),
                "offline-model",
                flat_run_layout=True,
                prepare_interaction_artifacts=False,
            )
            names = {path.name for path in output_dir.iterdir()}
            self.assertEqual(names, {"code", "data", "results", "logs"})
            workflow.interaction.assert_clean_task_output_workspace(output_dir)

            (output_dir / "AGENTS.md").write_text("generated", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "AGENTS.md"):
                workflow.interaction.assert_clean_task_output_workspace(output_dir)

    def test_clean_baseline_uses_private_skip_bootstrap_config(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "openclaw.json"
            original = {
                "agents": {
                    "defaults": {"model": "provider/model"},
                    "list": [{"id": "existing"}],
                }
            }
            source.write_text(json.dumps(original), encoding="utf-8")
            with patch.dict(
                "os.environ", {"OPENCLAW_CONFIG_PATH": str(source)}, clear=False
            ):
                isolated, previous = clean_baseline.activate_clean_openclaw_config()
                try:
                    private = json.loads(isolated.read_text(encoding="utf-8"))
                    self.assertTrue(private["agents"]["defaults"]["skipBootstrap"])
                    self.assertEqual(private["agents"]["list"], [])
                    self.assertEqual(
                        json.loads(source.read_text(encoding="utf-8")), original
                    )
                finally:
                    clean_baseline.remove_clean_openclaw_config(
                        isolated, previous
                    )
                self.assertEqual(os.environ["OPENCLAW_CONFIG_PATH"], str(source))
                self.assertFalse(isolated.exists())

    def test_workflow_optimizer_prompt_is_not_operator_evolution_prompt(self):
        prompt = workflow.build_workflow_evolution_prompt([])
        self.assertIn("Evolve one executable multi-turn", prompt)
        self.assertNotIn("Evolve one new human-expert dialogue operator", prompt)
        self.assertNotIn("five consecutive", prompt)
        self.assertNotIn("historical_best_utility", prompt)
        self.assertNotIn("Primary parent", prompt)
        self.assertNotIn("Secondary parent", prompt)
        self.assertNotIn("Evolution operator:", prompt)

    def test_evidence_archive_keeps_only_seeds_and_global_champion(self):
        seeds = workflow.initial_strategy_population()
        nodes = [
            {
                "round": index,
                "utility": score,
                "evolution_operator": "initial_strategy",
                "workflow": copy.deepcopy(seeds[index - 1]),
            }
            for index, score in enumerate([0.70, 0.71, 0.69], 1)
        ]
        nodes.extend(
            [
                {
                    "round": 4,
                    "utility": 0.90,
                    "evolution_operator": "evidence_guided_workflow_evolution",
                    "workflow": copy.deepcopy(seeds[0]),
                },
                {
                    "round": 5,
                    "utility": 0.85,
                    "evolution_operator": "evidence_guided_workflow_evolution",
                    "workflow": copy.deepcopy(seeds[1]),
                },
            ]
        )
        selected = workflow.evolution_evidence_nodes(nodes)
        self.assertEqual([item["round"] for item in selected], [1, 2, 3, 4])
        self.assertEqual(
            selected[3]["parent_archive_roles"],
            [
                {
                    "role": "global_best_parent",
                    "scope": "historical",
                    "objective": "average_utility",
                }
            ],
        )
        self.assertNotIn("parent_archive_roles", nodes[3])
        self.assertNotIn("pareto", str(selected).lower())

    def test_evidence_archive_deduplicates_seed_that_is_global_best(self):
        nodes = self.scored_nodes([0.90, 0.80, 0.70])
        for node in nodes:
            node["evolution_operator"] = "initial_strategy"
        selected = workflow.evolution_evidence_nodes(nodes)
        self.assertEqual([item["round"] for item in selected], [1, 2, 3])
        self.assertEqual(
            [role["role"] for role in selected[0]["parent_archive_roles"]],
            ["initial_parent", "global_best_parent"],
        )

    def test_cpe_sampling_is_persisted_with_replacement_across_rounds(self):
        train = [f"train_{index}" for index in range(10)]
        validation = [f"val_{index}" for index in range(10)]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = workflow.load_or_create_cpe_state(
                root, train, validation, 3, 10, 12345
            )
            self.assertEqual(state["validation_problems"], validation)
            self.assertEqual(
                state["train_sampling"],
                "independent_batches_with_replacement_across_rounds",
            )
            batches = [
                workflow.reserve_cpe_train_batch(state, round_number)
                for round_number in range(4, 31)
            ]
            self.assertTrue(all(len(batch) == len(set(batch)) for batch in batches))
            sampled = [item for batch in batches for item in batch]
            self.assertLess(len(set(sampled)), len(sampled))
            workflow.workflow_evolution.write_json(
                workflow.cpe_state_path(root), state
            )
            resumed = workflow.load_or_create_cpe_state(
                root, train, validation, 3, 10, 12345
            )
            self.assertEqual(resumed["validation_problems"], state["validation_problems"])
            self.assertEqual(
                workflow.reserve_cpe_train_batch(resumed, 4), batches[0]
            )

    def test_cpe_selection_requires_strict_epsilon_improvement(self):
        self.assertTrue(workflow.cpe_accepts(0.81, 0.80, 0.0))
        self.assertFalse(workflow.cpe_accepts(0.80, 0.80, 0.0))
        self.assertFalse(workflow.cpe_accepts(0.805, 0.80, 0.01))

    def test_cpe_initial_training_parents_are_top_two_validation_seeds(self):
        seeds = workflow.initial_strategy_population()
        seed_results = [
            {
                "round": index,
                "workflow_id": seed["workflow_id"],
                "workflow": seed,
                "utility": utility,
            }
            for index, (seed, utility) in enumerate(
                zip(seeds, [0.04, 0.08, 0.06]), start=1
            )
        ]
        state = {}
        workflow.initialize_cpe_policies(state, seed_results)
        self.assertEqual(
            [item["workflow_id"] for item in state["training_elites"]],
            [seeds[1]["workflow_id"], seeds[2]["workflow_id"]],
        )
        self.assertEqual(
            state["best_policy"]["workflow_id"], seeds[1]["workflow_id"]
        )

    def test_cpe_train_accept_updates_working_policy_without_lowering_best(self):
        seeds = workflow.initial_strategy_population()
        candidate = copy.deepcopy(seeds[1])
        candidate["workflow_id"] = workflow.workflow_id(candidate)
        state = {
            "sampling_seed": 7,
            "train_pool": ["train_a", "train_b", "train_c"],
            "train_batch_size": 3,
            "validation_problems": [f"val_{index}" for index in range(10)],
            "rounds": {},
            "patch_history": [],
            "validation_stagnation_rounds": [],
            "current_policy": {
                "source_round": 1,
                "workflow_id": seeds[0]["workflow_id"],
                "workflow": seeds[0],
                "validation_utility": 0.90,
            },
            "training_elites": [
                {
                    "rank": 1,
                    "source_round": 1,
                    "source_phase": "initial_validation",
                    "workflow_id": seeds[0]["workflow_id"],
                    "workflow": seeds[0],
                    "selection_utility": 0.90,
                },
                {
                    "rank": 2,
                    "source_round": 3,
                    "source_phase": "initial_validation",
                    "workflow_id": seeds[2]["workflow_id"],
                    "workflow": seeds[2],
                    "selection_utility": 0.80,
                },
            ],
            "best_policy": {
                "source_round": 1,
                "workflow_id": seeds[0]["workflow_id"],
                "workflow": seeds[0],
                "validation_utility": 0.90,
            },
        }
        scores = {
            "train_parent_1": 0.70,
            "train_parent_2": 0.60,
            "train_candidate": 0.65,
            "validation": 0.85,
        }
        phases = []
        parent_barrier = threading.Barrier(2)

        def fake_evaluation(*call_args):
            phase = call_args[2]
            phases.append(phase)
            if phase.startswith("train_parent_"):
                parent_barrier.wait(timeout=2)
            active = call_args[5]
            return (
                {
                    "round": 4,
                    "utility": scores[phase],
                    "workflow": active,
                    "workflow_id": active["workflow_id"],
                    "problem_results": [],
                    "average_dimension_scores": {},
                },
                [],
            )

        args = SimpleNamespace(
            max_rounds=4,
            selection_epsilon=0.0,
            enforce_substantive_interaction_gate=False,
            baseline_report_root="unused",
        )
        run_args = SimpleNamespace(validation_repetitions=1, baseline_reports={})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflows = root / "workflows"
            workflows.mkdir()
            results_path = workflows / "results.json"
            workflow.workflow_evolution.write_json(results_path, [])
            with patch.object(
                workflow, "ensure_cpe_baseline_reports"
            ), patch.object(
                workflow, "ensure_cpe_original_report_scores", return_value={}
            ), patch.object(
                workflow, "execute_cpe_evaluation", side_effect=fake_evaluation
            ), patch.object(
                workflow, "propose_cpe_workflow", return_value=candidate
            ), patch.object(
                workflow,
                "persist_cpe_round_result",
                side_effect=lambda _path, result: [result],
            ):
                workflow.run_cpe_evolved_rounds(
                    root,
                    results_path,
                    [],
                    seeds,
                    {},
                    {},
                    run_args,
                    args,
                    state,
                    {},
                )
        self.assertEqual(set(phases[:2]), {"train_parent_1", "train_parent_2"})
        self.assertEqual(phases[2:], ["train_candidate", "validation"])
        self.assertEqual(
            state["current_policy"]["workflow_id"], seeds[0]["workflow_id"]
        )
        self.assertEqual(
            [item["workflow_id"] for item in state["training_elites"]],
            [seeds[0]["workflow_id"], candidate["workflow_id"]],
        )
        self.assertEqual(state["best_policy"]["workflow_id"], seeds[0]["workflow_id"])
        self.assertFalse(state["patch_history"][0]["validation_accepted"])

    def test_cpe_prompt_enforces_champion_information_boundaries(self):
        seeds = workflow.initial_strategy_population()
        training_parents = [
            {
                "parent_rank": rank,
                "workflow_id": seed["workflow_id"],
                "workflow": workflow.optimizer_workflow(seed),
                "net_utility_on_current_training_batch": 0.08 - rank * 0.01,
                "training_evidence": {
                    "round": 4,
                    "average_interaction_cost": 0.2,
                    "average_interaction_penalty": 0.002,
                    "interaction_cost_parameters": {"total_token_reference": 5000},
                    "training_runs": [
                        {
                            "problem_id": f"train_parent_{rank}_task",
                            "question": "public training question",
                            "artifacts": [{"artifact_type": "expert_interaction"}],
                        }
                    ],
                },
            }
            for rank, seed in enumerate(seeds[:2], start=1)
        ]
        validation_champion = {
            "workflow": workflow.optimizer_workflow(seeds[0]),
            "utility": 0.06,
        }
        history = [
            {
                "round": 4,
                "train_accepted": False,
                "validation_accepted": True,
                "validation_secret": "hidden_validation_trace",
            }
        ]
        prompt = workflow.build_cpe_workflow_evolution_prompt(
            training_parents, validation_champion, history
        )
        self.assertIn("same sampled training batch", prompt)
        self.assertIn("choose the evolution mode yourself", prompt)
        self.assertIn("evolution_mode must be exactly `crossover` or `mutation`", prompt)
        self.assertIn("use the other parent as comparative evidence", prompt)
        self.assertIn("train_parent_1_task", prompt)
        self.assertIn("train_parent_2_task", prompt)
        self.assertIn("train_accepted", prompt)
        self.assertIn("only its", prompt)
        self.assertNotIn("hidden_validation_trace", prompt)
        self.assertNotIn('"dimension_scores"', prompt)
        self.assertNotIn("judge_groundedness_weakness_summary", prompt)
        self.assertNotIn("validation_accepted", prompt)
        self.assertNotIn("pareto", prompt.lower())

        leaked = copy.deepcopy(training_parents)
        leaked[0]["training_evidence"]["training_runs"][0][
            "dimension_scores"
        ] = {"modeling_groundedness": 0.5}
        with self.assertRaisesRegex(ValueError, "leaks Judge fields"):
            workflow.build_cpe_workflow_evolution_prompt(
                leaked, validation_champion, history
            )

    def test_cpe_utility_is_quality_gain_minus_small_interaction_cost(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            problem_results = []
            for problem_id, score in (("a", 0.80), ("b", 0.70)):
                run_dir = root / problem_id
                feedback = run_dir / "output" / "logs" / "operator_feedback"
                feedback.mkdir(parents=True)
                workflow.workflow_evolution.write_json(
                    feedback / "expert_request_1.json", {"question": "q" * 400}
                )
                workflow.workflow_evolution.write_json(
                    feedback / "expert_reply_1.json",
                    {"ok": True, "answer": "a" * 200},
                )
                (feedback / "human_expert_dialogue.md").write_text(
                    "complete", encoding="utf-8"
                )
                meta = run_dir / "meta"
                meta.mkdir()
                (meta / "expert_bridge.log").write_text(
                    "completed exchange 1 reply (200 chars; 10.00s)",
                    encoding="utf-8",
                )
                problem_results.append(
                    {
                        "problem_id": problem_id,
                        "average_score": score,
                        "run_dir": str(run_dir),
                    }
                )
            result = {"utility": 0.90, "problem_results": problem_results}
            originals = {"a": {"utility": 0.60}, "b": {"utility": 0.65}}
            workflow.apply_cpe_net_utility(result, originals)

        expected_cost = (
            workflow.DEFAULT_CPE_TOKEN_COST_WEIGHT
            * math.log1p(150)
            / math.log1p(workflow.DEFAULT_CPE_TOTAL_TOKEN_REFERENCE)
            + workflow.DEFAULT_CPE_LATENCY_COST_WEIGHT
            * math.log1p(10)
            / math.log1p(
                workflow.DEFAULT_CPE_TOTAL_LATENCY_MAX_SECONDS
            )
        )
        self.assertAlmostEqual(result["absolute_utility"], 0.75)
        self.assertAlmostEqual(result["original_report_utility"], 0.625)
        self.assertAlmostEqual(result["quality_gain"], 0.125)
        self.assertAlmostEqual(result["interaction_cost"], expected_cost)
        self.assertAlmostEqual(
            result["utility"],
            0.125 - workflow.DEFAULT_CPE_COST_PENALTY_WEIGHT * expected_cost,
        )
        self.assertEqual(
            result["utility_basis"],
            "mean_quality_gain_minus_interaction_cost",
        )
        self.assertEqual(
            result["interaction_cost_parameters"]["total_token_reference"],
            5000,
        )

    def test_original_report_scores_use_the_same_objective_and_are_cached(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reports = {}
            for problem_id in ("a", "b"):
                report = root / f"{problem_id}.md"
                report.write_text("draft", encoding="utf-8")
                reports[problem_id] = str(report)

            def fake_judge(problem_id, *_args, **_kwargs):
                value = 0.4 if problem_id == "a" else 0.6
                return {
                    "average_scores": {
                        "round_original": {
                            "trial_count": 1,
                            "average_dimension_scores": {
                                dimension: value
                                for dimension in workflow.interaction.EVALUATION_DIMENSIONS
                            },
                        }
                    }
                }

            run_args = SimpleNamespace(
                baseline_reports=reports,
                judge_repeats=1,
                judge_concurrency=1,
                concurrency=2,
            )
            with patch.object(
                workflow.run_judge_stability,
                "evaluate_reports_repeated",
                side_effect=fake_judge,
            ):
                scores = workflow.ensure_cpe_original_report_scores(
                    root, ["a", "b"], run_args
                )
            self.assertAlmostEqual(scores["a"]["utility"], 0.4)
            self.assertAlmostEqual(scores["b"]["utility"], 0.6)
            cached = workflow.workflow_evolution.read_json(
                root / "workflows" / "cpe_original_report_scores.json", {}
            )
            self.assertEqual(set(cached), {"a", "b"})

    def test_validation_champion_signal_has_only_workflow_and_utility(self):
        seed = workflow.initial_strategy_population()[0]
        signal = workflow.cpe_validation_champion_signal(
            {
                "best_policy": {
                    "workflow": seed,
                    "validation_utility": 0.07,
                    "source_round": 3,
                    "validation_details": "must_not_escape",
                }
            }
        )
        self.assertEqual(set(signal), {"workflow", "utility"})
        self.assertEqual(signal["utility"], 0.07)

    def test_similarity_rejection_third_retry_triggers_operator_evolution(self):
        seeds = workflow.initial_strategy_population()
        duplicate = copy.deepcopy(seeds[0])
        duplicate["changed_components"] = ["stop_condition"]
        duplicate["evolution_mode"] = "mutation"
        novel = copy.deepcopy(seeds[1])
        novel["changed_components"] = ["entry_action", "actions"]
        novel["evolution_mode"] = "crossover"
        parents = [
            {
                "parent_rank": rank,
                "workflow_id": seed["workflow_id"],
                "workflow": workflow.optimizer_workflow(seed),
                "net_utility_on_current_training_batch": 0.1 - rank * 0.01,
                "training_evidence": {"training_runs": []},
            }
            for rank, seed in enumerate(seeds[:2], start=1)
        ]
        validation = {
            "workflow": workflow.optimizer_workflow(seeds[0]),
            "utility": 0.1,
        }
        previous = [
            {"round": 1, "utility": 0.1, "workflow": seeds[0]}
        ]
        operator_event = {
            "trigger_reason": "workflow_similarity_retry_limit",
            "operator": {"operator_id": "dialogue_operator_new"},
        }
        args = SimpleNamespace(
            optimizer_retries=4,
            opt_model="offline-test-model",
            candidate_similarity_threshold=0.90,
        )
        with tempfile.TemporaryDirectory() as directory, patch.object(
            workflow.interaction.local,
            "optimizer_response",
            side_effect=[duplicate, duplicate, duplicate, novel],
        ), patch.object(
            workflow,
            "evolve_cpe_dialogue_operator",
            return_value=operator_event,
        ) as evolve:
            root = Path(directory)
            (root / "round_4").mkdir()
            candidate = workflow.propose_cpe_workflow(
                parents, validation, previous, [], 4, root / "round_4", args
            )
        evolve.assert_called_once()
        self.assertEqual(
            candidate["operator_evolution_trigger"]["operator_id"],
            "dialogue_operator_new",
        )

    def test_cpe_validation_plateau_triggers_operator_after_five_rounds(self):
        state = {
            "validation_stagnation_rounds": [],
            "best_policy": {"validation_utility": 0.1},
        }
        event = {
            "trigger_reason": "validation_champion_stagnation",
            "operator": {"operator_id": "dialogue_operator_plateau"},
        }
        args = SimpleNamespace()
        with tempfile.TemporaryDirectory() as directory, patch.object(
            workflow, "evolve_cpe_dialogue_operator", return_value=event
        ) as evolve:
            root = Path(directory)
            for round_number in range(4, 8):
                self.assertIsNone(
                    workflow.maybe_evolve_cpe_operator_for_validation_stagnation(
                        state, root, args, [], round_number, False
                    )
                )
            actual = workflow.maybe_evolve_cpe_operator_for_validation_stagnation(
                state, root, args, [], 8, False
            )
        self.assertEqual(actual, event)
        evolve.assert_called_once()
        self.assertEqual(state["validation_stagnation_rounds"], [])

    def test_stagnation_requires_five_rounds_without_strict_global_improvement(self):
        nodes = self.scored_nodes(
            [0.80, 0.79, 0.80, 0.78, 0.77, 0.76, 0.75, 0.74]
        )
        stagnant, best = workflow.stagnation_window(nodes)
        self.assertEqual(stagnant, [4, 5, 6, 7, 8])
        self.assertEqual(best, 0.80)

        improved = self.scored_nodes(
            [0.80, 0.79, 0.78, 0.77, 0.76, 0.75, 0.74, 0.81]
        )
        stagnant, best = workflow.stagnation_window(improved)
        self.assertEqual(stagnant, [])
        self.assertEqual(best, 0.81)

    def test_operator_event_resets_plateau_count_and_extends_catalog(self):
        nodes = self.scored_nodes(
            [0.80, 0.79, 0.78, 0.77, 0.76, 0.75, 0.74, 0.73, 0.72]
        )
        stagnant, _ = workflow.stagnation_window(nodes, after_round=8)
        self.assertEqual(stagnant, [9])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            operator = {
                "name": "stakeholder_conflict",
                "purpose": "Elicit an unresolved conflict between affected actors.",
                "rule": "Ask which affected actor bears a hidden burden and how that conflict changes the decision boundary.",
                "output": "A qualitative stakeholder conflict for independent analysis.",
            }
            workflow.workflow_evolution.write_json(
                workflow.evolved_operator_registry_path(root),
                [{"trigger_after_round": 6, "operator": operator}],
            )
            catalog = workflow.available_dialogue_operators(root)
            self.assertEqual(
                set(catalog),
                set(workflow.INTERACTION_OPERATORS) | {"stakeholder_conflict"},
            )

    def test_five_round_plateau_evolves_and_persists_one_operator(self):
        nodes = self.scored_nodes(
            [0.80, 0.79, 0.78, 0.77, 0.76, 0.75, 0.74, 0.73]
        )
        candidate = {
            "name": "failure_recovery_probe",
            "purpose": "Elicit how affected actors would recognize and recover from a failed recommendation.",
            "rule": "Ask the expert to identify the earliest observable failure signal and the qualitative recovery choice it should trigger.",
            "output": "A failure signal and corresponding recovery decision for independent testing.",
            "mutation_rationale": "Existing operators address priorities, falsification, and feasibility, but not post-deployment recovery decisions.",
        }
        args = SimpleNamespace(
            parent_similarity_threshold=0.98,
            optimizer_retries=1,
            opt_model="offline-test-model",
        )
        problems = {
            problem_id: {"title": problem_id, "question": "offline test question"}
            for problem_id in workflow.interaction.VALIDATION_PROBLEMS
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(
                workflow.interaction.local,
                "optimizer_response",
                return_value=copy.deepcopy(candidate),
            ) as optimizer:
                event = workflow.maybe_evolve_dialogue_operator(
                    nodes, root, args, problems=problems
                )
            optimizer.assert_called_once()
            operator_prompt = optimizer.call_args.args[0]["messages"][1]["content"]
            self.assertIn(
                "Evolve one new human-expert dialogue operator", operator_prompt
            )
            self.assertNotIn("Evolve one executable multi-turn", operator_prompt)
            self.assertNotIn("five consecutive", operator_prompt)
            self.assertNotIn("historical_best_utility", operator_prompt)
            self.assertEqual(event["trigger_after_round"], 8)
            self.assertEqual(event["stagnant_rounds"], [4, 5, 6, 7, 8])
            self.assertIn(
                "failure_recovery_probe",
                workflow.available_dialogue_operators(root),
            )
            registry = workflow.load_evolved_operator_events(root)
            self.assertEqual(len(registry), 1)

            with patch.object(
                workflow.interaction.local, "optimizer_response"
            ) as optimizer:
                self.assertIsNone(
                    workflow.maybe_evolve_dialogue_operator(
                        nodes, root, args, problems=problems
                    )
                )
            optimizer.assert_not_called()


if __name__ == '__main__':
    unittest.main()
