"""Solve with every expert reply translated into the model's own terms first.

Claude Code backend sibling of
``run_substantive_interaction_workflow_evolution_from_scratch_claude``, which it
composes rather than copies: the engine, the seed, the gates, the utility, the
judge wiring, the evolution prompt and the solver's starting point are that
arm's, unchanged.  What differs is one paragraph appended to the interaction
section of the solver prompt.

A reply arrives as prose about the task.  This arm requires it to be turned into
the model's own terms before anything else may read it, and it requires that
translation to be interleaved with the consultation rather than written up at
the end: after every reply, before the next question and before any further
modelling, the solver decomposes the reply into the statements it makes, sorts
each into the categories below, and rewrites the whole translation to
``results/interaction_translation.md``.  The translation -- not the reply -- is
then the source the rest of the work reads and cites.

The categories are fixed and a statement may belong to more than one:

* Assumption, Objective, Variable, Constraint, Parameter, Data interpretation,
  Validation, Conclusion.

Why the paragraph is here rather than in the policy: the policy under
`## Interaction Strategy` is what a round evolves, so a rule that has to survive
every round is stated in this arm's own prompt addition, outside the text the
optimizer rewrites.
"""

from __future__ import annotations

try:
    from . import run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch
except ImportError:  # pragma: no cover - direct-file invocation support
    import run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch


# Arm-specific, not policy.  Long by the standards of the proportionality note
# next to it, on purpose: this paragraph is the whole mechanism, and the
# categories and the entry shape are what make the artifact comparable across
# runs.  The closing clause is the part that makes it an *injection* rather than
# a write-up -- the translation is what the later decisions cite.
FEEDBACK_TRANSLATION_NOTE = """\
### Translate every reply before you use it

An expert reply arrives as prose about the task. Before it can govern the work it
has to be turned into the model's own terms, and once it has been, **the
translation is the only thing the rest of the work may read**: the reply is
evidence, the translation is the instruction.

**After every expert reply, before anything else** -- before the next question,
before any further modelling, before any code -- write the complete translation
to `{{RESULTS_DIR}}/interaction_translation.md`. Rewrite the whole file each
time, so it carries every exchange so far and never only the last one.

The translation is one entry per line. An entry is a single thing the reply
asserts, decides or excludes, sorted into the categories it belongs to; an entry
may carry more than one category. The categories are fixed:

- **Assumption** -- something the work takes as true without support from the statement or the data;
- **Objective** -- what the work maximises, minimises, or has to satisfy;
- **Variable** -- a quantity the model carries and solves for;
- **Constraint** -- a bound, exclusion, or feasibility condition the work must respect;
- **Parameter** -- a quantity fixed before the model runs, including any value or range the reply supplied;
- **Data interpretation** -- what a given quantity, column, or measurement is taken to mean;
- **Validation** -- how the output is to be checked, bounded, or falsified;
- **Conclusion** -- a claim the work is entitled to make when it is done.

Write each entry as

    Category: "<the statement, expanded until it can be applied on its own>"

and expand it as far as the reply allows -- the magnitude, the unit, the case it
holds in, what it rules out -- so that a reader who never sees the reply can act
on the entry. Where one thing is both, name both on the entry that carries it
(`Parameter, Variable: ...`).

**Read the file back before you continue.** The next question is built from the
translation and never from the reply: ask only about a gap the translation shows
is still open. Every later decision -- every assumption the model states, every
variable it carries, every parameter, what the result is validated against --
must cite the entry it came from, and nothing the expert said may enter the
report except through an entry that carries it."""


def build_translation_solver_prompt(
    workflow_value: dict, include_interaction: bool = True
) -> str:
    """The from-scratch arm's prompt, with the translation paragraph in front.

    The proportionality note stays: it bounds what a consultation may cost the
    modelling work, and this arm adds a demand *inside* the consultation, so the
    bound matters more here than in the arm it came from.
    """
    return scratch._ORIGINAL_SOLVER_PROMPT(
        workflow_value,
        include_interaction=include_interaction,
        include_draft=False,
        interaction_note=(
            FEEDBACK_TRANSLATION_NOTE + "\n\n" + "\n\n".join(scratch.INTERACTION_NOTES)
        ),
    )


def main() -> None:
    """Lay this arm's prompt builder over the from-scratch arm, then run it.

    ``scratch.main`` calls ``patch_sibling_launcher`` itself, and that function
    resolves the builder through this module's global name at call time.  So
    replacing the attribute here -- rather than rebinding ``base`` again
    afterwards -- is what keeps the arm a composition of the arms below it: the
    from-scratch hook list stays exactly as it is, and only the one function at
    the top of it changes.
    """
    scratch.build_from_scratch_solver_prompt = build_translation_solver_prompt

    print(
        "Feedback-translation arm: every expert reply is decomposed into "
        "categorised entries before the work may use it.",
        flush=True,
    )
    scratch.main()


if __name__ == "__main__":
    main()
