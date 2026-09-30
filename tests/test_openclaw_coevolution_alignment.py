"""The co-evolution arm must be the from-scratch arm plus the critic, and nothing else.

These tests exist because the two arms are meant to be compared against each
other: a difference in a result should be a difference the critic caused.  That
only holds while the co-evolution launcher is *composed* from the from-scratch
one, so the hook chain is asserted rather than trusted, and the critic's prompt
wrapper is exercised on its skip, success and failure paths.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import interaction_rubric_proposer as proposer
from src.OpenClaw import interaction_strategy_critic as critic
from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_from_initial_draft_claude_critic as coevolution,
)
from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base,
)
from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch,
)


# Every hook the from-scratch arm lays on the sibling launcher.  Listed once so
# "what the co-evolution arm inherits" is a fact in the test, not a claim in a
# docstring.
FROM_SCRATCH_HOOKS = {
    "fixed_initial_workflow": scratch.fixed_initial_workflow,
    "prepare_from_planning_draft": scratch.prepare_from_evidence,
    "build_interactive_solver_prompt": scratch.build_from_scratch_solver_prompt,
    "write_planning_draft_added_content": scratch.write_added_content_without_baseline,
    "run_planning_draft_solution_check": scratch.run_solution_only_check,
}


class CoevolutionAlignmentTests(unittest.TestCase):
    def test_coevolution_inherits_every_from_scratch_hook(self):
        coevolution.patch_sibling_launcher()

        for name, expected in FROM_SCRATCH_HOOKS.items():
            self.assertIs(
                getattr(base, name),
                expected,
                f"{name} should be the from-scratch arm's hook",
            )
        self.assertEqual(base.SOLVER_SOURCE_CONTEXT, "from the problem statement alone")
        self.assertEqual(base.SOLVER_START_CONTEXT, "starts from the problem statement alone")
        self.assertIs(
            scratch.support.prepare_mmbench_from_planning_draft,
            scratch.prepare_mmbench_from_evidence,
        )

    def test_the_critic_hook_is_the_only_difference_between_the_arms(self):
        scratch.patch_sibling_launcher()
        inherited = {name: getattr(base, name) for name in FROM_SCRATCH_HOOKS}
        inherited_context = (base.SOLVER_SOURCE_CONTEXT, base.SOLVER_START_CONTEXT)

        coevolution.patch_sibling_launcher()

        for name, value in inherited.items():
            self.assertIs(getattr(base, name), value, f"{name} moved after the critic patch")
        self.assertEqual(
            (base.SOLVER_SOURCE_CONTEXT, base.SOLVER_START_CONTEXT), inherited_context
        )
        self.assertIs(
            base.build_initial_draft_cpe_workflow_evolution_prompt,
            coevolution.build_with_critic_review,
        )
        self.assertIsNot(
            base.build_initial_draft_cpe_workflow_evolution_prompt,
            coevolution._original_build,
            "the critic must replace the prompt builder the sibling launcher wires, "
            "not wrap a builder another test already left in place",
        )

    def test_wrapper_calls_through_and_appends_the_review(self):
        original = coevolution._original_build
        coevolution._original_build = lambda *args, **kwargs: "BASE-PROMPT"
        try:
            with patch.object(coevolution, "_review_cache", {}), patch.object(
                coevolution.critic, "review_training_parents", return_value={"parents": []}
            ) as review, patch.object(
                coevolution.critic, "render_critic_block", return_value="REVIEW-BLOCK"
            ), patch.object(
                base, "_active_experiment", Path(tempfile.gettempdir())
            ):
                prompt = coevolution.build_with_critic_review(
                    [{"training_evidence": {"round": 4}}], {}, []
                )
        finally:
            coevolution._original_build = original

        self.assertEqual(prompt, "BASE-PROMPT\n\nREVIEW-BLOCK")
        self.assertEqual(review.call_count, 1)

    def test_wrapper_survives_a_critic_failure_without_the_review(self):
        original = coevolution._original_build
        coevolution._original_build = lambda *args, **kwargs: "BASE-PROMPT"
        try:
            with patch.object(coevolution, "_review_cache", {}), patch.object(
                coevolution.critic,
                "review_training_parents",
                side_effect=RuntimeError("endpoint down"),
            ), patch.object(base, "_active_experiment", Path(tempfile.gettempdir())):
                prompt = coevolution.build_with_critic_review(
                    [{"training_evidence": {"round": 4}}], {}, []
                )
        finally:
            coevolution._original_build = original

        self.assertEqual(prompt, "BASE-PROMPT")

    def test_wrapper_skips_the_critic_without_an_experiment_or_a_round(self):
        original = coevolution._original_build
        coevolution._original_build = lambda *args, **kwargs: "BASE-PROMPT"
        try:
            with patch.object(coevolution, "_review_cache", {}), patch.object(
                coevolution.critic, "review_training_parents"
            ) as review, patch.object(base, "_active_experiment", None):
                no_experiment = coevolution.build_with_critic_review(
                    [{"training_evidence": {"round": 4}}], {}, []
                )
            with patch.object(coevolution, "_review_cache", {}), patch.object(
                coevolution.critic, "review_training_parents"
            ) as review_missing_round, patch.object(
                base, "_active_experiment", Path(tempfile.gettempdir())
            ):
                no_round = coevolution.build_with_critic_review([{}], {}, [])
        finally:
            coevolution._original_build = original

        self.assertEqual(no_experiment, "BASE-PROMPT")
        self.assertEqual(no_round, "BASE-PROMPT")
        self.assertEqual(review.call_count, 0)
        self.assertEqual(review_missing_round.call_count, 0)

    def test_one_round_is_scored_once_across_retries(self):
        """A retried prompt build must not re-run the critic against the endpoint."""
        original = coevolution._original_build
        coevolution._original_build = lambda *args, **kwargs: "BASE-PROMPT"
        try:
            with patch.object(
                coevolution.critic, "review_training_parents", return_value={"parents": []}
            ) as review, patch.object(
                coevolution.critic, "render_critic_block", return_value="REVIEW-BLOCK"
            ), patch.object(
                base, "_active_experiment", Path(tempfile.gettempdir())
            ):
                # A real cache instance, so the second call is served from it.
                with patch.object(coevolution, "_review_cache", {}):
                    parents = [{"training_evidence": {"round": 5}}]
                    coevolution.build_with_critic_review(parents, {}, [])
                    coevolution.build_with_critic_review(parents, {}, [])
        finally:
            coevolution._original_build = original

        self.assertEqual(review.call_count, 1)

    def test_rubric_is_read_from_the_active_file(self):
        """The arm must not pin a rubric version; CRITIC_RUBRIC has to win."""
        with tempfile.TemporaryDirectory() as temporary:
            custom = Path(temporary) / "rubric.md"
            custom.write_text("[10] One criterion: does the thing.\n", encoding="utf-8")
            with patch.dict("os.environ", {"CRITIC_RUBRIC": str(custom)}):
                self.assertEqual(critic.rubric_path(), custom.resolve())


class RubricEvolutionHookTests(unittest.TestCase):
    """The rubric step must fire once per finished round and never cost a round."""

    RUBRIC_V4 = (
        "Interaction Strategy: Multi-Round Consultation\n\n"
        "[60] First criterion: does the first thing, stated at length enough to judge.\n\n"
        "[40] Second criterion: does the second thing, stated at length enough to judge.\n\n"
        "Scores are summed and normalized by this rubric's theoretical maximum (100): "
        "normalized = total / 100. Score only the dialogue.\n"
    )

    def _revise(self, temporary: str, result: dict) -> tuple[Path | None, str]:
        """Run one round through the proposer with a stubbed model."""
        rubric = Path(temporary) / "interaction_strategy_rubric_v4.md"
        rubric.write_text(self.RUBRIC_V4, encoding="utf-8")
        payload = {
            "criterion": {
                "name": "Names a magnitude",
                "max": 10,
                "rule": "The question asks for a value the text does not carry, or it is not a gap.",
                "example": "Asks for the tidal range; not asking whether the model is any good.",
            },
            "evolution_rationale": "x" * 40,
        }
        with patch.dict("os.environ", {"CRITIC_RUBRIC": str(rubric)}), patch.object(
            proposer, "ensure_usable_direct_calls"
        ), patch.object(
            proposer.interaction.local, "optimizer_response", return_value=payload
        ):
            out = proposer.evolve_rubric(
                Path(temporary) / "experiment",
                3,
                result,
                model="stub",
                base_url="http://stub",
                api_key="stub",
            )
            prompt = (out.parent / "evolution_prompt.md").read_text(encoding="utf-8")
        return out, prompt

    def test_launcher_installs_the_rubric_hook(self):
        coevolution.patch_sibling_launcher()
        self.assertIs(
            base.workflow.persist_cpe_round_result,
            coevolution.persist_with_rubric_evolution,
        )

    def test_round_the_parent_won_still_revises_the_rubric(self):
        """No held-out evidence, so the revision leans on the training records."""
        with tempfile.TemporaryDirectory() as temporary:
            out, prompt = self._revise(
                temporary, {"round": 3, "train_accepted": False}
            )
            self.assertIsNotNone(out, "every finished round must produce a version")
            self.assertEqual(out.name, "interaction_strategy_rubric_v5.md")
            self.assertIn("本轮候选在训练集上的表现", prompt)
            self.assertNotIn("验证集（held-out）", prompt)
            self.assertIn("没有 held-out 证据", prompt)
            self.assertIn("验证：未运行", prompt, "the decision block must not claim a gate ran")
            written = out.read_text(encoding="utf-8")
            self.assertIn("[60] First criterion", written, "earlier criteria must not move")
            self.assertIn("[10] Names a magnitude", written)
            self.assertIn("Example: Asks for the tidal range", written)
            self.assertIn("theoretical maximum (110)", written, "the footer states the new total")

    def test_a_validated_round_revises_from_the_held_out_record(self):
        """When validation ran, the held-out record is the evidence."""
        with tempfile.TemporaryDirectory() as temporary:
            held_out = Path(temporary) / "experiment" / "round_3_validation.json"
            held_out.parent.mkdir(parents=True, exist_ok=True)
            held_out.write_text(json.dumps({"utility": 0.9}), encoding="utf-8")
            out, prompt = self._revise(
                temporary,
                {
                    "round": 3,
                    "train_accepted": True,
                    "validation_result_path": str(held_out),
                },
            )
            self.assertIsNotNone(out)
            self.assertIn("本轮候选在验证集（held-out）上的表现", prompt)
            self.assertIn("验证门（须高于现任冠军", prompt)
            self.assertNotIn("未运行", prompt)
            written = out.read_text(encoding="utf-8")
            self.assertIn("[10] Names a magnitude", written)
            self.assertIn("theoretical maximum (110)", written)

    def test_hook_hands_the_round_to_the_proposer(self):
        with patch.object(coevolution.proposer, "evolve_rubric") as evolve:
            coevolution.evolve_round_rubric(Path("/tmp/exp"), {"round": 3})
        self.assertEqual(evolve.call_args.args[:2], (Path("/tmp/exp"), 3))

    def test_hook_persists_before_it_evolves_and_survives_a_failure(self):
        """A rubric failure must cost a log line, not the round's persisted result."""
        with patch.object(
            coevolution, "_original_persist", return_value=["stored"]
        ) as persist, patch.object(
            coevolution, "evolve_round_rubric", side_effect=RuntimeError("proposer down")
        ):
            result = coevolution.persist_with_rubric_evolution(
                Path("/tmp/workflows/results.json"), {"round": 3, "train_accepted": True}
            )
        self.assertEqual(result, ["stored"])
        persist.assert_called_once()

    def test_append_keeps_every_existing_criterion_byte_identical(self):
        """The protocol: one appended criterion per version, nothing else moves."""
        current = proposer.parse_criteria(
            "Interaction Strategy: T\n\n"
            "[60] First criterion: does the first thing, stated at length.\n\n"
            "[40] Second criterion: does the second thing, stated at length.\n"
        )
        payload = {
            "criterion": {
                "name": "Names a magnitude",
                "max": 10,
                "rule": "The question asks for a value the text does not carry, or it is not a gap.",
                "example": "Asks for the tidal range; not asking whether the model is any good.",
            },
            "evolution_rationale": "x" * 40,
        }
        self.assertEqual(proposer.proposal_errors(payload, current), [])
        updated = proposer.append_criterion(current, payload)
        self.assertEqual(updated[:2], current, "the criteria in force must not move")
        self.assertEqual(len(updated), 3)
        self.assertEqual(updated[2]["example"].startswith("Asks for"), True)

    def test_proposal_without_an_example_is_rejected(self):
        """The rule and one short example are both required of the new criterion."""
        current = proposer.parse_criteria(
            "[60] First criterion: does the first thing, stated at length.\n"
        )
        payload = {
            "criterion": {
                "name": "Names a magnitude",
                "max": 10,
                "rule": "The question asks for a value the text does not carry, or it is not a gap.",
            },
            "evolution_rationale": "x" * 40,
        }
        errors = proposer.proposal_errors(payload, current)
        self.assertTrue(any("example" in error for error in errors), errors)

    def test_criterion_already_in_the_rubric_is_rejected(self):
        """Appending is monotone: a duplicate adds nothing and is refused."""
        current = proposer.parse_criteria(
            "[60] Names a magnitude: the question asks for a value, stated at length.\n"
        )
        payload = {
            "criterion": {
                "name": "Names a magnitude",
                "max": 10,
                "rule": "The question asks for a value the text does not carry, or it is not a gap.",
                "example": "Asks for the tidal range; not asking whether the model is any good.",
            },
            "evolution_rationale": "x" * 40,
        }
        errors = proposer.proposal_errors(payload, current)
        self.assertTrue(any("already in the rubric" in error for error in errors), errors)

    def test_the_submission_is_part_of_a_run_record(self):
        """A criterion about the consultation needs to see what the work asserted."""
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary) / "run"
            (run_dir / "output" / "results").mkdir(parents=True)
            (run_dir / "output" / "results" / "solution.json").write_text(
                json.dumps(
                    {
                        "tasks": [
                            {
                                "task_description": "the scope of the model, stated at length",
                                "task_analysis": "the assumptions, stated at length enough",
                                "mathematical_modeling_process": "the model and its equations, at length",
                                "subtask_outcome_analysis": "results and biases, at length enough",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            block = proposer.run_record(
                {"problem_id": "2020_B", "average_score": 0.8}, run_dir
            )
            self.assertIn("提交的 solution.json", block)
            self.assertIn("mathematical_modeling_process: the model and its equations", block)

    def test_parent_submissions_are_resolved_from_the_phase_result(self):
        """The bundle carries no run directory, so the phase result supplies it."""
        with tempfile.TemporaryDirectory() as temporary:
            experiment = Path(temporary) / "experiment"
            round_dir = experiment / "workflows" / "round_3"
            round_dir.mkdir(parents=True)
            run_dir = (
                experiment / "cpe_evaluations" / "round_3" / "train_parent_1"
                / "runs" / "round_3" / "r1p1_stamp"
            )
            (run_dir / "output" / "results").mkdir(parents=True)
            (run_dir / "output" / "results" / "solution.json").write_text(
                json.dumps({"tasks": [{"task_analysis": "the parent's assumptions, at length"}]}),
                encoding="utf-8",
            )
            phase_dir = (
                experiment / "cpe_evaluations" / "round_3" / "train_parent_1"
                / "workflows" / "round_3"
            )
            phase_dir.mkdir(parents=True)
            (phase_dir / "result.json").write_text(
                json.dumps(
                    {"problem_results": [{"problem_id": "2014_C", "repetitions": [{"run_dir": str(run_dir)}]}]}
                ),
                encoding="utf-8",
            )
            (round_dir / "training_parent_evidence.json").write_text(
                json.dumps(
                    [
                        {
                            "parent_rank": 1,
                            "workflow_id": "interaction_workflow_parent",
                            "net_utility_on_current_training_batch": 0.8,
                            "workflow": {"policy_text": "# Human Expert Interaction\n\n## Interaction Strategy\n\nx"},
                            "training_evidence": {
                                "training_runs": [
                                    {"problem_id": "2014_C", "scores": {"report_score": 0.8}}
                                ]
                            },
                        }
                    ]
                ),
                encoding="utf-8",
            )
            block = proposer.training_evidence_block(round_dir)
            self.assertIn("提交的 solution.json", block)
            self.assertIn("the parent's assumptions", block)

    def test_render_states_the_new_total_in_the_footer(self):
        """An appended criterion raises the basis above 100, and the footer says so."""
        template = (
            "Interaction Strategy: T\n\n"
            "[100] Only criterion: does the one thing, stated at length.\n\n"
            "Scores are summed and normalized by this rubric's theoretical maximum (100): "
            "normalized = total / 100. Score only the dialogue.\n"
        )
        criteria = proposer.parse_criteria(template)
        criteria = proposer.append_criterion(
            criteria,
            {
                "criterion": {
                    "name": "Names a magnitude",
                    "max": 10,
                    "rule": "The question asks for a value the text does not carry, or it is not a gap.",
                    "example": "Asks for the tidal range; not asking whether the model is any good.",
                },
                "evolution_rationale": "x" * 40,
            },
        )
        rendered = proposer.render_rubric_markdown(criteria, template=template)
        self.assertIn("theoretical maximum (110)", rendered)
        self.assertIn("total / 110", rendered)
        self.assertIn("[100] Only criterion: does the one thing, stated at length.", rendered)
        self.assertIn("Example: Asks for the tidal range", rendered)


class StrategyFormSelectionTests(unittest.TestCase):
    """The evolution prompt's `{strategy_form}` slot, and its default.

    The slot decides only what shape the rewritten rule must take; everything
    else in the prompt is the same text.  Two things therefore have to hold, and
    neither is visible from the emitted policy: an unnamed form must render the
    prompt exactly as it read before the slot existed, and a named form must
    change that slot and nothing else.
    """

    def _head(self, value=None):
        environ = (
            {} if value is None else {"EVOLUTION_STRATEGY_FORM": value}
        )
        with patch.dict(os.environ, environ, clear=False):
            if value is None:
                os.environ.pop("EVOLUTION_STRATEGY_FORM", None)
            form = base.evolution_strategy_form()
        return base.EVOLUTION_PROMPT_HEAD.replace("{strategy_form}", form), form

    def test_the_slot_is_always_filled(self):
        for value in (None, "linear", "conditional", "workflow", "nonsense"):
            with self.subTest(value=value):
                head, _ = self._head(value)
                self.assertNotIn("{strategy_form}", head)

    def test_no_form_selected_renders_the_linear_text(self):
        head, form = self._head()
        self.assertEqual(form, base.STRATEGY_FORM_LINEAR)
        self.assertIn("State, in the parent's own order:", head)

    def test_an_unknown_form_falls_back_to_the_linear_text(self):
        linear, linear_form = self._head()
        for value in ("", "nonsense", "LINEAR", "linear-2"):
            with self.subTest(value=value):
                head, form = self._head(value)
                self.assertEqual(form, linear_form, f"{value!r} must fall back")
                self.assertEqual(head, linear, f"{value!r} must render the default")

    def test_every_named_form_replaces_only_that_slot(self):
        linear, _ = self._head()
        for name, body in base.STRATEGY_FORMS.items():
            with self.subTest(form=name):
                head, form = self._head(name)
                self.assertEqual(form, body)
                self.assertNotEqual(head, linear)
                # Same prompt everywhere else: cutting the slot out of each
                # rendering leaves one identical remainder.
                before, after = base.EVOLUTION_PROMPT_HEAD.split("{strategy_form}")
                self.assertEqual(head, before + body + after)

    def test_both_extra_forms_ask_for_conditions_and_the_workflow_one_for_stages(self):
        conditional, workflow = (
            base.STRATEGY_FORMS["conditional"],
            base.STRATEGY_FORMS["workflow"],
        )
        for body in (conditional, workflow):
            self.assertIn('"if"', body, "a conditional form has to ask for conditions")
        self.assertIn("the stages", workflow, "the workflow form has to ask for stages")
        self.assertNotIn("the stages", conditional)


if __name__ == "__main__":
    unittest.main()
