"""Offline regression tests for temporal dialogue-operator strategy evolution."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

try:
    from . import run_substantive_interaction_experiment as substantive
    from . import run_substantive_interaction_strategy_core as core
    from . import run_substantive_interaction_strategy_evolution as strategy
except ImportError:
    import run_substantive_interaction_experiment as substantive
    import run_substantive_interaction_strategy_core as core
    import run_substantive_interaction_strategy_evolution as strategy


class TemporalOperatorEvolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.old_operators = copy.deepcopy(core.INTERACTION_OPERATORS)
        core.INTERACTION_OPERATORS = copy.deepcopy(
            strategy.STRATEGY_INTERACTION_OPERATORS
        )

    def tearDown(self) -> None:
        core.INTERACTION_OPERATORS = self.old_operators

    def test_three_initial_strategies_bind_distinct_stage_operators(self) -> None:
        population = strategy.initial_execution_strategy_population()
        self.assertEqual(3, len(population))
        self.assertEqual(
            {
                "structure_assumption_discovery",
                "implemented_model_interpretation_audit",
                "validation_failure_signal_probe",
            },
            {item["seed_operator"] for item in population},
        )
        stages = set()
        for item in population:
            core.validate_workflow(item)
            core.validate_workflow_operator_bindings(
                item, strategy.STRATEGY_INTERACTION_OPERATORS, require=True
            )
            expert = next(
                action
                for action in item["actions"]
                if action["action_type"] == "expert_exchange"
            )
            stages.add(expert["stage"])
        self.assertEqual({"after_step_2", "after_step_5", "during_step_6"}, stages)
        self.assertIn("provisional_model_red_team", core.INTERACTION_OPERATORS)
        self.assertIn("sensitivity_evidence_calibration", core.INTERACTION_OPERATORS)

    def test_agent_render_resolves_operator_rule(self) -> None:
        seed = strategy.initial_execution_strategy_population()[1]
        rendered = strategy.render_strategy_with_operators(seed)
        self.assertIn("implemented_model_interpretation_audit", rendered)
        self.assertIn("[after_step_5] expert_exchange", rendered)
        self.assertIn("Operator rule:", rendered)
        prompt = strategy.build_end_to_end_prompt(seed)
        self.assertIn("## Expert Interaction Strategy", prompt)
        self.assertIn("implemented_model_interpretation_audit", prompt)
        self.assertIn("expert_request_N.json", prompt)

    def test_workflow_prompt_delegates_mutation_or_crossover_choice(self) -> None:
        population = strategy.initial_execution_strategy_population()
        primary = {"round": 1, "utility": 0.8, "workflow": population[0]}
        secondary = {"round": 2, "utility": 0.79, "workflow": population[1]}
        prompt = strategy.build_strategy_evolution_prompt(
            primary,
            secondary,
            [],
            "llm_selects_workflow_mutation_or_crossover",
            strategy.STRATEGY_INTERACTION_OPERATORS,
        )
        self.assertIn("You, the optimizer, must", prompt)
        self.assertIn("workflow_crossover_mutation", prompt)
        self.assertIn("operator_id referencing", prompt)
        self.assertIn("Do not invent an operator", prompt)

    def test_optimizer_can_choose_mutation_even_with_two_parents(self) -> None:
        population = strategy.initial_execution_strategy_population()
        results = [
            {
                "round": index,
                "utility": 0.82 - index * 0.01,
                "workflow": copy.deepcopy(item),
                "problem_results": [],
            }
            for index, item in enumerate(population, 1)
        ]
        candidate = {
            "evolution_operator": "workflow_mutation",
            "name": "Conditional interpretation consistency strategy",
            "purpose": "Use a late operational interpretation check only when the executable model contains unresolved semantic conflicts.",
            "entry_action": "audit_semantic_conflicts",
            "actions": [
                {
                    "action_id": "audit_semantic_conflicts",
                    "action_type": "agent_modeling",
                    "stage": "through_step_5",
                    "rule": "Complete the provisional model and identify contradictions among equations, outputs, and the operational process they represent.",
                },
                {
                    "action_id": "consult_if_unresolved",
                    "action_type": "expert_exchange",
                    "stage": "after_step_5",
                    "interaction_stage": 5,
                    "operator_id": "implemented_model_interpretation_audit",
                    "rule": "When an important operational interpretation remains unresolved, apply the registered interpretation-audit operator once.",
                },
                {
                    "action_id": "reconcile_and_validate",
                    "action_type": "agent_validation",
                    "stage": "steps_5_to_7",
                    "rule": "Reconcile affected definitions and outputs, run regression checks, and preserve complete coverage in the final report.",
                },
            ],
            "max_exchanges": 1,
            "stop_condition": "Stop after semantic conflicts are resolved and affected outputs pass regression checks.",
            "changed_components": ["trigger", "integration"],
            "mutation_rationale": "The consultation is now conditional on a concrete unresolved semantic conflict after implementation.",
            "crossover_rationale": "No crossover was selected because the mutation isolates the targeted behavioral change.",
        }
        args = SimpleNamespace(
            parent_similarity_threshold=0.999,
            candidate_similarity_threshold=0.999,
            optimizer_retries=1,
            opt_model="deepseek-v4-pro",
        )
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            core, "optimizer_evidence", return_value=[]
        ), patch.object(
            core.interaction.local, "optimizer_response", return_value=candidate
        ):
            round_dir = Path(temp_dir) / "round_4"
            round_dir.mkdir()
            child = core.propose_workflow(
                results, 4, round_dir, args, {}
            )
        self.assertEqual("workflow_mutation", child["evolution_operator"])
        self.assertEqual(1, len(child["parent_rounds"]))
        self.assertIsNone(child["secondary_parent_round"])

    def test_stagnation_starts_at_round_four_and_uses_point_001(self) -> None:
        population = strategy.initial_execution_strategy_population()

        def nodes(scores: list[float]) -> list[dict]:
            return [
                {
                    "round": index,
                    "utility": score,
                    "workflow": copy.deepcopy(population[(index - 1) % 3]),
                    "problem_results": [],
                }
                for index, score in enumerate(scores, 1)
            ]

        stagnant, best = core.stagnation_window(
            nodes([0.8, 0.79, 0.78, 0.8004, 0.8008, 0.8009, 0.8002, 0.799])
        )
        self.assertEqual([4, 5, 6, 7, 8], stagnant)
        self.assertEqual(0.8, best)
        stagnant, best = core.stagnation_window(
            nodes([0.8, 0.79, 0.78, 0.8004, 0.8008, 0.8009, 0.8002, 0.801])
        )
        self.assertEqual([], stagnant)
        self.assertEqual(0.801, best)

    def test_stagnation_event_generates_three_separate_operators(self) -> None:
        population = strategy.initial_execution_strategy_population()
        results = [
            {
                "round": index,
                "utility": 0.8 if index == 1 else 0.79,
                "workflow": copy.deepcopy(population[(index - 1) % 3]),
                "problem_results": [],
            }
            for index in range(1, 9)
        ]
        candidates = [
            {
                "name": "stakeholder_conflict_mapping",
                "stage": "after_step_1",
                "purpose": "Expose incompatible stakeholder interpretations before assumptions are fixed.",
                "rule": "Ask the expert to identify qualitatively incompatible stakeholder goals and explain which conflicts alter the decision framing.",
                "output": "A map of decision-relevant stakeholder conflicts and their qualitative consequences.",
                "mutation_rationale": "Existing operators do not elicit conflicts among stakeholder interpretations before decomposition.",
            },
            {
                "name": "implementation_feasibility_probe",
                "stage": "after_step_4",
                "purpose": "Test whether candidate policies can be implemented under real operational constraints.",
                "rule": "Ask the expert to identify operational obstacles, institutional dependencies, and adoption failures for candidate policies.",
                "output": "Qualitative implementation obstacles that the agent can translate into constraints or limits.",
                "mutation_rationale": "Existing operators do not isolate implementation feasibility before executable analysis begins.",
            },
            {
                "name": "communication_misuse_boundary",
                "stage": "after_step_6",
                "purpose": "Find ways a technically valid recommendation could be misunderstood or used outside its scope.",
                "rule": "Ask the expert to identify likely interpretation errors and scope violations that would make the recommendation unsafe to communicate.",
                "output": "Misuse boundaries that the agent can convert into qualified conclusions and decision guidance.",
                "mutation_rationale": "Existing operators do not target downstream interpretation and misuse immediately before reporting.",
            },
        ]
        args = SimpleNamespace(
            parent_similarity_threshold=0.98,
            optimizer_retries=1,
            opt_model="deepseek-v4-pro",
        )
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            core, "optimizer_evidence", return_value=[]
        ), patch.object(
            core.interaction.local, "optimizer_response", side_effect=candidates
        ) as optimizer:
            event = core.maybe_evolve_dialogue_operator(
                results, Path(temp_dir), args, {}
            )
            self.assertIsNotNone(event)
            self.assertEqual(3, len(event["operators"]))
            self.assertEqual(3, optimizer.call_count)
            event_dir = Path(temp_dir) / "operator_evolution" / "after_round_8"
            for index in range(1, 4):
                self.assertTrue((event_dir / f"operator_{index}_prompt.md").is_file())
                self.assertTrue((event_dir / f"operator_{index}.json").is_file())

    def test_bridge_uses_controller_authored_stages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            core.workflow_evolution.write_json(
                run_dir / "strategy.json",
                {
                    "actions": [
                        {
                            "action_type": "expert_exchange",
                            "interaction_stage": 5,
                        },
                        {
                            "action_type": "expert_exchange",
                            "interaction_stage": 6,
                        },
                    ]
                },
            )
            self.assertEqual(
                [5, 6], substantive.configured_interaction_stages({"run_dir": run_dir})
            )

    def test_optimizer_evidence_excludes_judge_role_feedback(self) -> None:
        node = {
            "round": 4,
            "utility": 0.81,
            "workflow": strategy.initial_execution_strategy_population()[0],
            "problem_results": [
                {
                    "problem_id": "sample_problem",
                    "run_dir": "unused",
                    "judge_result": "must_not_be_read.json",
                }
            ],
        }
        context = [
            {
                "problem_id": "sample_problem",
                "title": "Sample",
                "question": "Public task statement",
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            core.interaction, "optimizer_problem_context", return_value=context
        ), patch.object(
            core,
            "optimizer_parent_artifacts",
            return_value=[
                {"artifact_type": "expert_interaction", "content": "dialogue"}
            ],
        ):
            evidence = core.optimizer_evidence(
                [node], {}, Path(temp_dir), SimpleNamespace(opt_model="unused")
            )
        validation_run = evidence[0]["validation_runs"][0]
        self.assertNotIn("non_full_role_evaluations", validation_run)
        self.assertNotIn("overall_feedback", str(evidence))


if __name__ == "__main__":
    unittest.main()
