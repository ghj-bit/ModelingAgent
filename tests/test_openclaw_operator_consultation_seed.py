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

import inspect
import json
import sys
import time
import unittest
import unittest.mock
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
# The list bars parameter *tuning*, not parameter *plausibility*: asking the
# expert whether a constant the agent assumed itself is of a sensible order of
# magnitude is permitted, and Operator 3 says so.  PROHIBITIONS[3] is the
# computation line the weakening case below rewrites.
PROHIBITIONS = (
    "- coding, debugging, or implementation issues;",
    "- parameter tuning or optimization details;",
    "- standard mathematical derivations;",
    "- computation, data processing, or routine validation.",
)


def as_workflow(policy_text: str) -> dict:
    """The shape ``workflow_similarity`` reads a candidate through."""
    return {
        "policy_text": policy_text,
        "max_exchanges": 3,
        "stop_condition": "never exceed three expert replies",
    }


def base_prompt_for(seed: dict) -> str:
    """The Claude arm's evolution prompt for one seed, as the optimizer reads it."""
    return base.build_initial_draft_cpe_workflow_evolution_prompt(
        [
            {
                "parent_rank": rank,
                "workflow_id": f"seed{rank}",
                "workflow": dict(seed),
                "net_utility_on_current_training_batch": 0.0,
                "training_evidence": {},
            }
            for rank in (1, 2)
        ],
        {"workflow": dict(seed), "utility": 0.0},
        [],
    )


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
            self.policy_text.replace(PROHIBITIONS[3], "- computation, if convenient;"),
            self.policy_text.replace(WORKFLOW_HEADING, "## Workflow"),
        ):
            with self.assertRaises(ValueError):
                workflow.assert_fixed_policy_sections_unchanged(
                    {"policy_text": weakened}, parent
                )

    def operator_regime(self):
        """Similarity with the repertoire open, as it was before the freeze."""
        return unittest.mock.patch.object(
            workflow, "POLICY_PATCH_OPERATOR_LIMIT", None
        )

    def frozen_regime(self):
        return unittest.mock.patch.object(workflow, "POLICY_PATCH_OPERATOR_LIMIT", 0)

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
        with self.operator_regime():
            similarity = workflow.workflow_similarity(as_workflow(mutated), parent)
            self.assertLess(
                similarity, workflow.DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD
            )
            # The denominator is the units similarity is judged on: the operators
            # plus the mutable rule section, which a round may also rewrite.
            # Pinned rather than written as a literal so adding a unit cannot
            # leave the number here describing a policy that no longer exists.
            units = len(workflow.workflow_behavior(parent)["steps"])
            self.assertEqual(similarity, (units - 1) / units)

    def test_a_rule_only_round_clears_the_duplicate_threshold(self):
        # The repertoire is frozen, so the rule is the only thing a round can
        # move.  Judged on the operators alone every such candidate would score
        # 1.0 against its parent and be rejected as a duplicate before it ran.
        parent = as_workflow(self.policy_text)
        start = self.policy_text.index("Before each exchange:")
        end = self.policy_text.index("## Prohibited Requests")
        rewritten = (
            self.policy_text[:start]
            + "Treat the three exchanges as one consultation, not three questions.\n"
            "Read the state once, before the first question, into the single\n"
            "decision that most constrains what the model can conclude. Each\n"
            "later question must be one the previous reply opened: name what it\n"
            "settled and what it left standing, and ask only about the latter.\n\n"
            + self.policy_text[end:]
        )
        self.assertNotEqual(rewritten, self.policy_text)
        with self.frozen_regime():
            similarity = workflow.workflow_similarity(as_workflow(rewritten), parent)
            self.assertLess(
                similarity, workflow.DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD
            )

    def test_a_cosmetic_rule_edit_is_a_duplicate_while_frozen(self):
        # The point of measuring the rule's text rather than counting it as one
        # unit: a rewritten rule has to clear the gate, a reworded one must not.
        # On the step count every edit scored the same 0.80 and the gate could
        # tell neither from the other.
        parent = as_workflow(self.policy_text)
        reworded = self.policy_text.replace(
            "Ask exactly one focused question.",
            "Ask exactly one focused question, and make it answerable.",
            1,
        )
        self.assertNotEqual(reworded, self.policy_text)
        with self.frozen_regime():
            self.assertGreaterEqual(
                workflow.workflow_similarity(as_workflow(reworded), parent),
                workflow.DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD,
            )
            self.assertEqual(
                workflow.workflow_similarity(as_workflow(self.policy_text), parent),
                1.0,
            )

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
        prompt = base_prompt_for(self.seed)
        for needle in (
            # The surface is two sections, and both are named: a round that is
            # told only about the repertoire rewrites the repertoire every time.
            "Change the consultation, not the contract.",
            "You patch one or more of these\n  sections",
            "`## Interaction Operators`",
            # All three parts of an operator are still named, so the shape is
            # stated even while the sections themselves are frozen -- the first
            # round that reopens one needs to know what it is editing.
            "`**When.**`, `**How.**` and `**Example.**` paragraphs",
            # What a round evolves is the consultation as a sequence, not a
            # single turn -- and the strategy section is the one it is pointed
            # at first.
            "Evolve the consultation, not the exchanges.",
            "Read the recorded dialogue as a sequence",
            "This is the section a round is expected to\n    move",
            # The repertoire may be restructured, bounded by the engine's ceiling.
            "The repertoire is yours to restructure.",
            "`### Operator N: <name>`",
            "no more than eight",
            # The answer is a patch, and the prompt has to say so where the
            # deliverable is defined -- §1, §2, §3 and §5 all name it, because a
            # schema the model reads once is not what it re-reads on a retry.
            "`policy_patch` is the whole deliverable",
            "the engine splices them into the parent",
            "`policy_patch` comes first because it is the deliverable",
            "no heading of any level may appear inside it",
            "fixed and are carried over from the parent",
            # The frozen sections are named, so the optimizer knows where the
            # boundary is without having to infer it from a rejected round --
            # and the ban survives in the prompt too, so it is told which
            # prohibitions it may not weaken.  Parameter *plausibility* is not
            # among them, or it would never propose such a question.
            # Single-line needles: the prompt is line-wrapped, so a phrase
            # spanning a wrap point would break on a harmless reflow.
            "the autonomy default in `## Principle`",
            "`## Prohibited Requests`",
            "`# Interaction Limits`",
            "*tuning* or optimization details",
            "sensible order of magnitude is permitted",
        ):
            self.assertIn(needle, prompt)

    def test_prompt_and_guard_agree_on_the_mutable_surface(self):
        # The prompt lives in the Claude arm and the spans in the shared engine,
        # so nothing but this test keeps them in step.  A prompt that offers more
        # than the guard allows wastes a rejected round per attempt; a guard that
        # allows more than the prompt offers is worse, because a round is then
        # told the prohibitions are fixed while something that rewrites them runs.
        parent = [{"workflow": {"policy_text": self.policy_text, "workflow_id": "seed"}}]

        def accepted(text: str) -> bool:
            try:
                workflow.assert_fixed_policy_sections_unchanged(
                    {"policy_text": text}, parent
                )
                return True
            except ValueError:
                return False

        def edited(heading: str) -> str:
            # Appended inside the section rather than rewriting the heading: the
            # heading itself is the boundary, and rewording it is a separate case.
            return self.policy_text.replace(
                heading, heading + "\n\nA sentence the parent never stated.", 1
            )

        mutable = [
            heading
            for heading in workflow.MUTABLE_POLICY_HEADINGS
            if heading in self.policy_text
        ]
        self.assertTrue(mutable, "the seed states no mutable section at all")
        for heading in mutable:
            with self.subTest(mutable=heading):
                self.assertIn(heading, base_prompt_for(self.seed))
                self.assertTrue(
                    accepted(edited(heading)),
                    f"the prompt offers {heading!r} as mutable but the guard refuses it",
                )
        for heading in ("## Principle", "## Prohibited Requests", "# Interaction Limits"):
            with self.subTest(fixed=heading):
                self.assertFalse(
                    accepted(edited(heading)),
                    f"the prompt calls {heading!r} fixed but the guard lets a round rewrite it",
                )

    def test_retired_operator_catalogue_is_not_reachable(self):
        # The old catalogue's names must not reappear in the seed the arm runs on.
        for retired in ("assumption_audit", "model_failure_mode", "data_parameter_boundary"):
            self.assertNotIn(retired, self.policy_text)
            self.assertFalse(hasattr(interaction_policy, retired))


class PolicyPatchTests(unittest.TestCase):
    """The round returns a patch; the engine splices it into the parent."""

    OPERATOR_BODY = (
        '**When.** a\n\n**How.** b\n\n**Example.** Agent: "x" Expert: "y"'
    )

    def setUp(self):
        self.seed = base.fixed_initial_workflow()
        self.arm_limit = workflow.POLICY_PATCH_OPERATOR_LIMIT
        workflow.POLICY_PATCH_OPERATOR_LIMIT = 1
        self.addCleanup(
            setattr, workflow, "POLICY_PATCH_OPERATOR_LIMIT", self.arm_limit
        )

    def splice(self, patch, parent=None, allowed=None):
        # The shape a round's response actually has: the patch, plus the two
        # labels the schema still asks for.  The budget and the stop condition
        # are deliberately absent -- the engine carries those from the parent.
        candidate = workflow.apply_policy_patch(
            {
                "policy_patch": patch,
                "name": "A patched consultation policy",
                "purpose": "Spend the fixed expert budget where the state says it matters.",
            },
            parent if parent is not None else self.seed,
            allowed,
        )
        # validate_workflow is what synthesises the action graph, and it is the
        # engine's own translation step -- everything downstream reads its output.
        base.validate_workflow_with_inferred_start(candidate)
        return candidate

    @staticmethod
    def evidence(*headings):
        """Training parents whose dialogue is headed with ``headings``."""
        dialogue = "\n\n".join(
            f"## Exchange {i}\n\n**Modeling Agent question**\n\n"
            f"# Expert Question {i} ({heading})\n\nbody\n"
            for i, heading in enumerate(headings, start=1)
        )
        return [
            {
                "parent_rank": 1,
                "workflow": {},
                "training_evidence": {
                    "training_runs": [
                        {
                            "problem_id": "2017_A",
                            "artifacts": [
                                {"artifact_type": "expert_interaction", "content": dialogue}
                            ],
                        }
                    ]
                },
            }
        ]

    def test_rule_alone_splices_and_keeps_the_repertoire(self):
        candidate = self.splice(
            [{"section": "## Interaction Operators", "body": "Read the state first."}]
        )
        self.assertIn("Read the state first.", candidate["policy_text"])
        self.assertEqual(len(candidate["actions"]), 4)
        self.assertIn(
            "Operator 4: Refine / correct", candidate["policy_text"]
        )

    def test_one_operator_alongside_the_rule_is_allowed(self):
        candidate = self.splice(
            [
                {"section": "## Interaction Operators", "body": "Read the state first."},
                {"section": "### Operator 4: Refine / correct", "body": self.OPERATOR_BODY},
            ]
        )
        self.assertIn(self.OPERATOR_BODY, candidate["policy_text"])

    def test_two_operators_are_rejected(self):
        with self.assertRaises(ValueError) as caught:
            self.splice(
                [
                    {"section": "### Operator 4: Refine / correct", "body": self.OPERATOR_BODY},
                    {"section": "### Operator 2: Challenge reasoning", "body": self.OPERATOR_BODY},
                ]
            )
        # The message has to name the limit: it is the whole retry hint.
        self.assertIn("at most 1", str(caught.exception))
        self.assertIn("## Interaction Operators", str(caught.exception))

    def test_an_added_operator_counts_towards_the_limit(self):
        with self.assertRaises(ValueError):
            self.splice(
                [
                    {"section": "### Operator 4: Refine / correct", "body": self.OPERATOR_BODY},
                    {
                        "section": "### Operator 5: Probe dynamics",
                        "after": "### Operator 4: Refine / correct",
                        "body": self.OPERATOR_BODY,
                    },
                ]
            )

    def test_frozen_sections_cannot_be_patched(self):
        for heading in ("## Principle", "## Prohibited Requests", "# Interaction Limits"):
            with self.subTest(heading=heading):
                with self.assertRaises(ValueError):
                    self.splice([{"section": heading, "body": "rewritten"}])

    def test_a_body_may_not_introduce_a_heading(self):
        with self.assertRaises(ValueError):
            self.splice(
                [
                    {
                        "section": "## Interaction Operators",
                        "body": "prose\n\n### Smuggled\n\nmore",
                    }
                ]
            )

    def test_the_budget_is_carried_from_the_parent(self):
        candidate = self.splice(
            [{"section": "## Interaction Operators", "body": "Read the state first."}]
        )
        self.assertEqual(candidate["max_exchanges"], self.seed["max_exchanges"])
        self.assertEqual(candidate["stop_condition"], self.seed["stop_condition"])

    def test_the_prompt_states_that_the_repertoire_is_frozen(self):
        prompt = base_prompt_for(self.seed)
        # The engine rejects any operator edit, so the prompt has to say so -- a
        # rule the optimizer cannot read is a rule that costs it a round.
        self.assertIn("**Frozen for now**", prompt)
        self.assertIn("No `### Operator` section", prompt)
        # The rules are enforced by the engine but only under an arm's opt-in,
        # and the arm opts in from `main()` -- which no test runs.  Read the
        # wiring off the source instead of the module, so a round that loses the
        # opt-in fails here rather than silently reverting to an unbounded patch.
        main_source = inspect.getsource(base.main)
        self.assertIn("workflow.POLICY_PATCH_OPERATOR_LIMIT = 0", main_source)
        self.assertIn("workflow.POLICY_PATCH_ONLY_USED_OPERATORS = True", main_source)
        # The evidence still states what the consultation applied; frozen or not,
        # it is the record of which operator carried which exchange.
        self.assertIn("operators_the_rollouts_reached_for", prompt)

    def test_a_frozen_repertoire_rejects_every_operator_edit(self):
        workflow.POLICY_PATCH_OPERATOR_LIMIT = 0
        for patch in (
            [{"section": "### Operator 4: Refine / correct", "body": self.OPERATOR_BODY}],
            [
                {"section": "## Interaction Operators", "body": "Read the state first."},
                {"section": "### Operator 1: Resolve uncertainty", "body": self.OPERATOR_BODY},
            ],
            [
                {
                    "section": "### Operator 5: Probe dynamics",
                    "after": "### Operator 4: Refine / correct",
                    "body": self.OPERATOR_BODY,
                }
            ],
        ):
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError) as caught:
                    self.splice(patch)
                # The message has to name the section that is still allowed,
                # or the retry has nowhere to go.
                self.assertIn("`## Interaction Operators`", str(caught.exception))
        # ...and the rule alone still splices.
        candidate = self.splice(
            [{"section": "## Interaction Operators", "body": "Read the state first."}]
        )
        self.assertIn("Read the state first.", candidate["policy_text"])
        self.assertEqual(len(candidate["actions"]), 4)

    def test_used_operators_are_read_off_the_question_headings(self):
        parents = self.evidence(
            "Operator 2: Challenge reasoning", "Operator 1: Resolve uncertainty"
        )
        self.assertEqual(
            workflow.cpe_used_operator_headings(parents),
            {"Operator 2: Challenge reasoning", "Operator 1: Resolve uncertainty"},
        )
        self.assertEqual(workflow.cpe_used_operator_headings([]), set())
        # A rollout that heads nothing states nothing.
        self.assertEqual(workflow.cpe_used_operator_headings(self.evidence()), set())

    def test_an_operator_the_rollouts_reached_for_may_be_rewritten(self):
        allowed = workflow.cpe_used_operator_headings(
            self.evidence("Operator 4: Refine / correct")
        )
        candidate = self.splice(
            [{"section": "### Operator 4: Refine / correct", "body": self.OPERATOR_BODY}],
            allowed=allowed,
        )
        self.assertIn(self.OPERATOR_BODY, candidate["policy_text"])

    def test_an_operator_no_rollout_reached_for_is_rejected(self):
        allowed = workflow.cpe_used_operator_headings(
            self.evidence("Operator 1: Resolve uncertainty")
        )
        with self.assertRaises(ValueError) as caught:
            self.splice(
                [{"section": "### Operator 4: Refine / correct", "body": self.OPERATOR_BODY}],
                allowed=allowed,
            )
        # The message has to say which operator the rollouts did reach for: it is
        # the whole retry hint, and on an empty set it has to say so plainly.
        self.assertIn("Operator 1: Resolve uncertainty", str(caught.exception))

    def test_an_unlabelled_rollout_permits_no_operator_edit(self):
        # The seed asks the solver to head every question with its operator, so
        # an unlabelled rollout means the consultation never stated one -- and a
        # trigger no exchange ran cannot be argued to have failed.
        with self.assertRaises(ValueError) as caught:
            self.splice(
                [{"section": "### Operator 4: Refine / correct", "body": self.OPERATOR_BODY}],
                allowed=workflow.cpe_used_operator_headings(self.evidence()),
            )
        self.assertIn("reached for: none", str(caught.exception))

    def test_the_rule_alone_is_allowed_however_the_rollout_ran(self):
        candidate = self.splice(
            [{"section": "## Interaction Operators", "body": "Read the state first."}],
            allowed=set(),
        )
        self.assertIn("Read the state first.", candidate["policy_text"])

    def test_the_seed_asks_for_the_operator_label(self):
        # The engine reads the label off the question heading; without the seed
        # asking for it there is nothing to read, and the rule above degenerates
        # to "no operator may ever change".
        self.assertIn("Name the operator you selected", self.seed["policy_text"])

    def test_the_solver_prompt_states_the_heading(self):
        # This block is rendered outside `policy_text`, so a round cannot evolve
        # the labelling requirement away -- which is the point of putting it here
        # as well as in the seed.
        rendered = base.interaction_workflow_block(self.seed)
        self.assertIn("(Operator <k>: <name>)", rendered)


class ExpertReplyReminderTests(unittest.TestCase):
    """The operator heading is re-stated with every reply, not only in the policy."""

    SCRIPT = REPO_ROOT / "src/OpenClaw/wait_for_expert_reply.py"

    def reply(self, number, exchanges):
        """Run the helper against a canned request/reply pair."""
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            request = tmp / f"expert_request_{number}.json"
            reply = tmp / f"expert_reply_{number}.json"
            request.write_text('{"ok": true}', encoding="utf-8")
            reply.write_text(
                json.dumps({"ok": True, "answer": "the expert's answer"}),
                encoding="utf-8",
            )
            return subprocess.run(
                [
                    sys.executable,
                    str(self.SCRIPT),
                    "--request",
                    str(request),
                    "--reply",
                    str(reply),
                    "--timeout",
                    "5",
                    "--exchanges",
                    str(exchanges),
                ],
                capture_output=True,
                text=True,
                check=True,
            ).stdout

    def test_the_reply_alone_is_returned_when_no_budget_is_stated(self):
        out = self.reply(1, 0)
        self.assertIn("the expert's answer", out)
        self.assertNotIn("[controller]", out)

    def test_a_later_exchange_is_reminded_of_the_header(self):
        out = self.reply(1, 3)
        self.assertIn("the expert's answer", out)
        self.assertIn("[controller]", out)
        # The reminder has to name the exchange the agent is about to write, and
        # the exact heading, or it is not actionable.
        self.assertIn("Expert Question 2 (Operator <k>: <name>)", out)
        self.assertIn("Exchange 1 of 3", out)

    def test_the_last_exchange_is_not_reminded(self):
        # A fourth question would exceed the budget, so the reminder would be
        # advice the solver must not take.
        out = self.reply(3, 3)
        self.assertIn("the expert's answer", out)
        self.assertNotIn("[controller]", out)

    def test_the_solver_prompt_passes_the_budget_and_mentions_the_echo(self):
        rendered = base.interaction_workflow_block(base.fixed_initial_workflow())
        self.assertIn("--exchanges 3", rendered)
        self.assertIn("echoes a reminder of that header", rendered)


class ExpertReplyFailFastTests(unittest.TestCase):
    """An exchange the controller cannot see must fail at once, and bounded.

    The run that prompted this waited the full 180 s handshake, spent six solver
    heartbeats on it, and then reported only "Timed out waiting for the
    controller-generated expert request/reply" -- the cause, a question written
    one directory short of the one the controller reads, was never named.
    """

    SCRIPT = REPO_ROOT / "src/OpenClaw/wait_for_expert_reply.py"

    def run_helper(self, root: Path, *extra: str):
        """Invoke the helper against a staged tree, without waiting the cap."""
        import subprocess

        feedback = root / "logs" / "operator_feedback"
        feedback.mkdir(parents=True, exist_ok=True)
        return subprocess.run(
            [
                sys.executable,
                str(self.SCRIPT),
                "--request",
                str(feedback / "expert_request_1.json"),
                "--reply",
                str(feedback / "expert_reply_1.json"),
                "--diagnose-after",
                "0.2",
                *extra,
            ],
            capture_output=True,
            text=True,
        )

    def test_the_handshake_is_capped_at_seventy_seconds(self):
        # The cap is a cap, not a default: prompts rendered before it existed
        # still carry `--timeout 180` as a literal.
        from src.OpenClaw import wait_for_expert_reply as helper

        self.assertEqual(helper.MAX_TIMEOUT_SECONDS, 70.0)
        self.assertEqual(helper.effective_timeout(180), 70.0)
        self.assertEqual(helper.effective_timeout(70), 70.0)
        # A caller asking for less still gets what it asked for.
        self.assertEqual(helper.effective_timeout(5), 5.0)

    def test_a_question_one_directory_short_is_named_and_fails_fast(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stray = root / "logs" / "expert_question_1.md"
            stray.parent.mkdir(parents=True, exist_ok=True)
            stray.write_text("# Expert Question 1 (Operator 1: Resolve uncertainty)\n", encoding="utf-8")

            started = time.monotonic()
            result = self.run_helper(root, "--timeout", "60")
            elapsed = time.monotonic() - started

        self.assertEqual(result.returncode, 2)
        # Both paths, or the message is not actionable.
        self.assertIn(str(stray), result.stderr)
        self.assertIn("operator_feedback", result.stderr)
        # Diagnosed on the grace period, not on the 60 s timeout.
        self.assertLess(elapsed, 20.0)

    def test_a_question_written_nowhere_is_reported(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_helper(Path(tmp), "--timeout", "60")

        self.assertEqual(result.returncode, 2)
        self.assertIn("No expert question at", result.stderr)
        self.assertIn("expert_question_1.md", result.stderr)

    def test_a_question_in_place_waits_rather_than_diagnosing(self):
        # The controller creates the request asynchronously, so a question that
        # is where it belongs must not be mistaken for a misplaced one.
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feedback = root / "logs" / "operator_feedback"
            feedback.mkdir(parents=True)
            (feedback / "expert_question_1.md").write_text(
                "# Expert Question 1 (Operator 1: Resolve uncertainty)\n", encoding="utf-8"
            )
            started = time.monotonic()
            result = self.run_helper(root, "--timeout", "3")
            elapsed = time.monotonic() - started

        self.assertEqual(result.returncode, 2)
        self.assertNotIn("No expert question at", result.stderr)
        # It waited out the timeout instead of diagnosing.
        self.assertGreaterEqual(elapsed, 3.0)


if __name__ == "__main__":
    unittest.main()
