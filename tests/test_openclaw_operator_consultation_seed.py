"""The Claude arm's seed is a repertoire of interaction operators, and stays evolvable.

The seed states the consultation as four operators -- resolve uncertainty,
challenge reasoning, inject knowledge, refine/correct -- each with its own
trigger (`When`) and execution rule (`How`).  The four is the seed's roster and
not a ceiling: a round may add an operator, which is why nothing the solver reads
may state a count.  A count written into a fixed section would survive every
round and contradict the first one that adds an operator.

Two properties make the experiment work, and both are mechanical rather than
editorial, so they are asserted here:

* the operators sit inside the policy's operator section (headed ``# 可选交互算子``),
  which is the only region ``assert_fixed_policy_sections_unchanged`` lets a round
  rewrite.  An operator that drifted outside it could not be evolved, and a round
  that rewrote the prohibition list outside it could weaken the ban on asking the
  expert for parameters, computation or code while still looking like a valid
  candidate.  The heading is what marks that boundary, so the engine accepts more
  than one wording and both are asserted to still parse: a policy whose heading
  stops matching loses the operator steps *and* silently loses the guard.
* each operator is one step of the derived action graph, which is what
  ``workflow_similarity`` compares.  A round that rewrites one operator of four
  scores 0.75 against its parent; if the operators were not steps, the round
  would score near 1.0 and be rejected as a duplicate before it ever ran.

The last case pins the ceiling: the engine allows at most eight actions, and at
eight operators a one-operator round still scores 0.875, below the 0.90 default.
Adding a ninth would turn every subsequent round into a rejected duplicate.
"""

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import interaction_policy
from src.OpenClaw import run_substantive_interaction_workflow_evolution as workflow
from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base,
)
from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch,
)

WORKFLOW_HEADING = "# 可选交互算子"
# The heading the other arms' seeds still use.  The engine accepts both, and the
# boundary guard depends on that: a wording it stops recognising is not an error
# anywhere, it is a policy with no mutable section and no fixed-section check.
LEGACY_WORKFLOW_HEADING = "# Interaction Workflow"

OPERATORS = [
    "Operator 1: Resolve uncertainty",
    "Operator 2: Challenge reasoning",
    "Operator 3: Inject knowledge",
    "Operator 4: Refine / correct",
]

# The prohibitions the rounds may not touch.  Each is a line of the fixed section.
PROHIBITIONS = (
    "- parameter values, ranges, estimates, initial conditions, or calibration targets;",
    "- computation, derivation, data processing, statistical analysis, or simulation;",
    "- code in any form: writing, reading, reviewing, debugging, or tool usage;",
    "- model validation, result checking, error analysis, or numerical comparison;",
    "- approval, confirmation, or review of a decision the agent has already made.",
)


def as_workflow(policy_text: str) -> dict:
    """The shape ``workflow_similarity`` reads a candidate through."""
    return {
        "policy_text": policy_text,
        "max_exchanges": 3,
        "stop_condition": "never exceed three expert replies",
    }


class OperatorSeedTests(unittest.TestCase):
    def setUp(self):
        self.seed = base.fixed_initial_workflow()
        self.policy_text = self.seed["policy_text"]

    def test_seed_is_the_four_operators_in_order(self):
        steps = base._interaction_workflow_steps(self.policy_text)
        self.assertEqual([title for title, _ in steps], OPERATORS)

    def test_both_accepted_headings_parse_and_enforce(self):
        # Each accepted wording must yield the same steps and the same boundary,
        # or one arm silently runs unguarded.  The legacy wording is what the
        # OpenHands seed still carries.
        reference = base._interaction_workflow_steps(self.policy_text)
        for heading in (WORKFLOW_HEADING, LEGACY_WORKFLOW_HEADING):
            other = self.policy_text.replace(WORKFLOW_HEADING, heading)
            self.assertEqual(
                base._interaction_workflow_steps(other),
                reference,
                f"{heading!r} is no longer accepted as the operator section",
            )
            parent = [{"workflow": {"policy_text": other, "workflow_id": "seed"}}]
            rewritten_before = other.replace("The expert never does computation.", "x")
            with self.assertRaises(ValueError):
                workflow.assert_fixed_policy_sections_unchanged(
                    {"policy_text": rewritten_before}, parent
                )

    def test_a_reworded_heading_is_rejected_not_ignored(self):
        # The heading sits inside the mutable region, so a round can reach it.
        # Rewording it to something unrecognised must fail loudly: if it instead
        # parsed as "no section", the guard would return early and every later
        # round could edit the prohibitions freely.
        parent = [{"workflow": {"policy_text": self.policy_text, "workflow_id": "seed"}}]
        with self.assertRaises(ValueError) as caught:
            workflow.assert_fixed_policy_sections_unchanged(
                {"policy_text": self.policy_text.replace(WORKFLOW_HEADING, "# Workflow")},
                parent,
            )
        # The message has to name the accepted wordings: it is the only thing
        # telling the optimizer why its rewrite was refused.
        for heading in ("可选交互算子", "Interaction Workflow"):
            self.assertIn(heading, str(caught.exception))

    def test_policy_states_no_operator_count(self):
        # The four operators above are the seed's roster, not a limit: the
        # evolution prompt lets a round add one. A count is unrewritable when it
        # sits in a fixed section, so the first round that adds an operator would
        # leave the policy contradicting itself. Counts of other things (the
        # exchange budget, the options in operator 1) are pinned elsewhere and
        # are not covered by this.
        for count in ("two", "three", "four", "five", "six", "seven", "eight"):
            for noun in ("interaction operators", "operators"):
                self.assertNotIn(f"{count} {noun}", self.policy_text)
        self.assertNotRegex(self.policy_text, r"\b\d+\s+(interaction )?operators\b")

    def test_each_operator_states_when_and_how(self):
        for title, body in base._interaction_workflow_steps(self.policy_text):
            self.assertIn("**When.**", body, f"{title} states no trigger condition")
            self.assertIn("**How.**", body, f"{title} states no execution rule")

    def test_each_operator_carries_a_short_exchange(self):
        # The example is part of the operator, not decoration: the optimizer is
        # told to rewrite it alongside `When`/`How` rather than drop it. It is
        # written as an agent/expert exchange because the operators govern a
        # dialogue -- the reply shape is half of what the solver has to imitate --
        # and it stays short, since a long example costs the solver the attention
        # the concise wording was just trimmed to buy back.
        for title, body in base._interaction_workflow_steps(self.policy_text):
            self.assertIn("**Example.**", body, f"{title} carries no example")
            example = body.split("**Example.**", 1)[1].strip()
            self.assertTrue(example, f"{title} has an empty example")
            self.assertLess(len(example), 240, f"{title}'s example is not concise")
            for speaker in ("Agent:", "Expert:"):
                self.assertIn(speaker, example, f"{title}'s example is not an exchange")
            self.assertGreaterEqual(
                example.count('"'), 4, f"{title}'s example does not quote both turns"
            )

    def test_prohibitions_are_present_and_outside_the_mutable_section(self):
        for line in PROHIBITIONS:
            self.assertIn(line, self.policy_text)
        # The boundary the engine enforces: everything before the workflow
        # heading is fixed, so the prohibitions must sit there.
        preamble, _, _ = self.policy_text.partition(WORKFLOW_HEADING)
        for line in PROHIBITIONS:
            self.assertIn(line, preamble)

    def test_operator_edit_passes_and_a_weakening_edit_is_rejected(self):
        parent = [{"workflow": {"policy_text": self.policy_text, "workflow_id": "seed"}}]

        operator_edit = self.policy_text.replace(
            "**When.** The agent has committed to a load-bearing assumption",
            "**When.** The agent has committed to a load-bearing assumption or a\nmechanism it cannot defend",
        )
        workflow.assert_fixed_policy_sections_unchanged(
            {"policy_text": operator_edit}, parent
        )

        for weakened in (
            self.policy_text.replace(PROHIBITIONS[1], "- computation, if convenient;"),
            self.policy_text.replace(WORKFLOW_HEADING, "## Workflow"),
        ):
            with self.assertRaises(ValueError):
                workflow.assert_fixed_policy_sections_unchanged(
                    {"policy_text": weakened}, parent
                )

    def test_one_operator_round_clears_the_duplicate_threshold(self):
        # Anchor the mutation on the `**How.**` label rather than on the prose
        # under it: the wording of an operator is exactly what the seed is
        # expected to be edited and evolved through, and a test that quotes it
        # breaks on every such edit while proving nothing extra.
        parent = as_workflow(self.policy_text)
        mutated = self.policy_text.replace(
            "**How.** ", "**How.** Answer directly. ", 1
        )
        self.assertNotEqual(mutated, self.policy_text)
        similarity = workflow.workflow_similarity(as_workflow(mutated), parent)
        self.assertLess(similarity, workflow.DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD)
        self.assertEqual(similarity, 0.75)

    def test_the_eight_operator_ceiling_still_clears_the_threshold(self):
        # The engine rejects a ninth action; this is the worst case at eight.
        self.assertLess(
            7 / 8, workflow.DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD
        )

    def test_from_scratch_arm_mints_the_same_policy(self):
        # The seed names no plan, so strip_plan_references is a no-op and the two
        # Claude arms start from identical text.
        other = scratch.fixed_initial_workflow()
        self.assertEqual(other["policy_text"], self.policy_text)
        self.assertEqual(other["workflow_id"], self.seed["workflow_id"])

    def test_seed_budget_is_pinned_by_the_engine(self):
        self.assertEqual(self.seed["max_exchanges"], 3)
        self.assertEqual(workflow.MAX_WORKFLOW_EXCHANGES, 3)

    def test_evolution_prompt_teaches_the_operator_surface(self):
        prompt = base.build_initial_draft_cpe_workflow_evolution_prompt(
            [
                {
                    "parent_rank": rank,
                    "workflow_id": f"seed{rank}",
                    "workflow": dict(self.seed),
                    "net_utility_on_current_training_batch": 0.0,
                    "training_evidence": {},
                }
                for rank in (1, 2)
            ],
            {"workflow": dict(self.seed), "utility": 0.0},
            [],
        )
        for needle in (
            "operator repertoire",
            # All three parts of an operator are named as mutable, or a round
            # would not know it may rewrite the example.
            "its `Example` (the exchange that",
            "`When`, `How` or `Example` changed",
            # Adding an operator is allowed but gated behind sharpening first.
            "Prefer sharpening an existing operator to adding one",
            "as a last resort",
            "new `### Operator N: <name>`",
            "eight operators",
            # The ban survives in the prompt too, so the optimizer is told which
            # prohibitions it may not weaken.
            "parameter values, computation, derivation",
        ):
            self.assertIn(needle, prompt)

    def test_retired_operator_catalogue_is_not_reachable(self):
        # The old catalogue's names must not reappear in the seed the arm runs on.
        for retired in ("assumption_audit", "model_failure_mode", "data_parameter_boundary"):
            self.assertNotIn(retired, self.policy_text)
            self.assertFalse(hasattr(interaction_policy, retired))


if __name__ == "__main__":
    unittest.main()
