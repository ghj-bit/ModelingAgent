"""The feedback-translation arm adds one paragraph, and it is the whole mechanism.

The arm composes the from-scratch arm rather than copying it, so what has to be
asserted is narrow: that the paragraph is actually in the prompt the solver
receives, that it names the deliverable and the fixed categories, that it
requires the translation to be *read back* before the next exchange, and that
the composition survives the arm below it re-binding its own hook.

The last one is the reason this file exists.  ``scratch.main`` calls
``patch_sibling_launcher``, which binds the solver-prompt builder by looking the
name up in the from-scratch module at call time; an arm that replaced the
attribute *after* that call, or rebound ``base`` itself, would silently drop the
paragraph and every run would look normal.
"""

import inspect
import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_feedback_translation_claude as arm,
)
from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch,
)

CATEGORIES = (
    "Assumption",
    "Objective",
    "Variable",
    "Constraint",
    "Parameter",
    "Data interpretation",
    "Validation",
    "Conclusion",
)

SEED_PATH = (
    REPO_ROOT
    / "openclaw_experiments"
    / "exp_prompt"
    / "initial_interaction_workflow_info_first.json"
)


class FeedbackTranslationPromptTests(unittest.TestCase):
    def setUp(self):
        self.seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))[0]
        self.prompt = arm.build_translation_solver_prompt(self.seed)

    def test_the_translation_section_is_in_the_prompt(self):
        self.assertIn("### Translate every reply before you use it", self.prompt)
        # The deliverable, under the results directory the renderer substitutes.
        self.assertIn("{{RESULTS_DIR}}/interaction_translation.md", self.prompt)

    def test_every_category_is_named_and_an_entry_may_carry_more_than_one(self):
        for category in CATEGORIES:
            with self.subTest(category=category):
                self.assertIn(f"**{category}**", self.prompt)
        self.assertIn("an entry\nmay carry more than one category", self.prompt)
        # The entry shape, which is what makes the artifact comparable.
        self.assertIn('Category: "<the statement', self.prompt)

    def test_it_requires_reading_the_file_back_before_the_next_exchange(self):
        self.assertIn("Read the file back before you continue", self.prompt)
        self.assertIn("The next question is built from the", self.prompt)
        # And that the reply itself is not what later work cites.
        self.assertIn(
            "nothing the expert said may enter the\nreport except through an entry",
            self.prompt,
        )

    def test_the_notes_inherited_from_the_arm_below_still_follow_it(self):
        # The arm below states a bound on the consultation and a ceiling on what
        # may be asked; this arm adds a demand inside the consultation, so losing
        # either paragraph would be a behaviour change nobody asked for.
        self.assertIn("### Ask one short, common-sense question", self.prompt)
        self.assertIn("### Keep the consultation proportionate", self.prompt)
        self.assertLess(
            self.prompt.index("### Translate every reply"),
            self.prompt.index("### Ask one short, common-sense question"),
        )
        self.assertLess(
            self.prompt.index("### Ask one short, common-sense question"),
            self.prompt.index("### Keep the consultation proportionate"),
        )


class FromScratchNoteTests(unittest.TestCase):
    """Both notes reach every run of the arm that owns them, not just this one."""

    def setUp(self):
        self.seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))[0]
        self.prompt = scratch.build_from_scratch_solver_prompt(self.seed)

    def test_the_from_scratch_prompt_carries_both_notes(self):
        for heading in (
            "### Ask one short, common-sense question",
            "### Keep the consultation proportionate",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, self.prompt)
        self.assertLess(
            self.prompt.index("### Ask one short, common-sense question"),
            self.prompt.index("### Keep the consultation proportionate"),
        )

    def test_the_notes_are_composed_from_the_tuple(self):
        # The tuple is what lets an arm laid on top join the notes without
        # restating either; an arm that concatenates the constants by hand would
        # silently drop a paragraph added here later.
        self.assertEqual(
            scratch.INTERACTION_NOTES,
            (
                scratch.INTERACTION_NON_MODELER_NOTE,
                scratch.INTERACTION_PROPORTIONALITY_NOTE,
            ),
        )
        self.assertIn(
            'interaction_note="\\n\\n".join(INTERACTION_NOTES)',
            inspect.getsource(scratch.build_from_scratch_solver_prompt),
        )


class FeedbackTranslationWiringTests(unittest.TestCase):
    def test_the_from_scratch_patch_binds_this_arms_builder(self):
        # The composition, exercised rather than described: `main` replaces the
        # from-scratch module's global name, and `patch_sibling_launcher`
        # resolves that name when it runs -- so the hook it binds onto `base` is
        # this arm's builder.  An arm that rebinds `base` itself *after*
        # delegating, or that patches the name after `main`, lands on the plain
        # builder instead and every run silently loses the paragraph.
        from src.OpenClaw import (
            run_substantive_interaction_workflow_evolution_from_initial_draft_claude
            as base,
        )

        original_builder = scratch.build_from_scratch_solver_prompt
        original_base_builder = base.build_interactive_solver_prompt
        touched = (
            "fixed_initial_workflow",
            "build_interactive_solver_prompt",
            "prepare_from_planning_draft",
            "SOLVER_SOURCE_CONTEXT",
            "SOLVER_START_CONTEXT",
            "write_planning_draft_added_content",
            "run_planning_draft_solution_check",
        )
        before = {name: getattr(base, name) for name in touched}
        try:
            scratch.build_from_scratch_solver_prompt = arm.build_translation_solver_prompt
            scratch.patch_sibling_launcher()
            self.assertIs(
                base.build_interactive_solver_prompt,
                arm.build_translation_solver_prompt,
            )
        finally:
            scratch.build_from_scratch_solver_prompt = original_builder
            for name, value in before.items():
                setattr(base, name, value)
            base.build_interactive_solver_prompt = original_base_builder

    def test_main_assigns_before_it_delegates(self):
        # The order is the mechanism; read it off the source so a reordering
        # fails here rather than in a run that looks normal.
        import inspect

        source = inspect.getsource(arm.main)
        self.assertIn(
            "scratch.build_from_scratch_solver_prompt = build_translation_solver_prompt",
            source,
        )
        self.assertLess(
            source.index("scratch.build_from_scratch_solver_prompt ="),
            source.index("scratch.main()"),
        )

    def test_the_deliverable_is_not_counted_as_a_solver_edit(self):
        # It sits in results/ beside interaction_evidence.md, and that one is
        # already excluded from the refinement record; a controller-produced
        # artifact must not be reported as a file the solver changed.
        from src.OpenClaw import record_refinement_changes as record

        self.assertIn("results/interaction_translation.md", record.IGNORED_FILES)


if __name__ == "__main__":
    unittest.main()
