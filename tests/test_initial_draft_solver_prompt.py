import unittest

from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_from_initial_draft as launcher,
)


class InitialDraftSolverPromptTests(unittest.TestCase):
    def test_initial_population_contains_the_two_current_policies(self):
        policies = launcher.initial_planning_workflows()

        self.assertEqual(len(policies), 2)
        self.assertEqual(
            [policy["policy_text"] for policy in policies],
            [
                launcher.INITIAL_STRATEGIC_UNCERTAINTY_POLICY,
                launcher.INITIAL_STRATEGIC_CHECKPOINT_POLICY,
            ],
        )
        self.assertEqual([policy["max_exchanges"] for policy in policies], [1, 1])
        self.assertIn("only when ALL conditions hold", policies[0]["policy_text"])
        self.assertIn("**Required**", policies[0]["policy_text"])
        self.assertIn("**Optional**", policies[0]["policy_text"])
        self.assertIn("predefined strategic checkpoints", policies[1]["policy_text"])
        self.assertIn("**Confirmation**", policies[1]["policy_text"])
        self.assertIn("**Correction**", policies[1]["policy_text"])
        self.assertIn("**Suggestion**", policies[1]["policy_text"])

    def test_prompt_forbids_generated_images(self):
        workflow = launcher.initial_planning_workflows()[0]
        prompt = launcher.build_interactive_solver_prompt(workflow)

        self.assertIn("Do not generate or include images.", prompt)


if __name__ == "__main__":
    unittest.main()
