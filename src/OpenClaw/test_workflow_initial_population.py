"""Offline checks for population initialization and resume compatibility."""
import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import run_substantive_interaction_workflow_evolution as workflow


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
            self.assertEqual({seed['max_exchanges'] for seed in seeds}, {1})
            self.assertEqual({seed['seed_operator'] for seed in seeds}, set(workflow.INTERACTION_OPERATORS))
            self.assertEqual(len({seed['workflow_id'] for seed in seeds}), 3)
            self.assertEqual(workflow.load_seed_population(root, True, None), seeds)

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

    def test_workflow_optimizer_prompt_is_not_operator_evolution_prompt(self):
        prompt = workflow.build_workflow_evolution_prompt([])
        self.assertIn("Evolve one executable multi-turn", prompt)
        self.assertNotIn("Evolve one new human-expert dialogue operator", prompt)
        self.assertNotIn("five consecutive", prompt)
        self.assertNotIn("historical_best_utility", prompt)
        self.assertNotIn("Primary parent", prompt)
        self.assertNotIn("Secondary parent", prompt)
        self.assertNotIn("Evolution operator:", prompt)

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
