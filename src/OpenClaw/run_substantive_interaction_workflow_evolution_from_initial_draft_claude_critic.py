"""Co-evolve interaction workflows from scratch with an LLM critic in the loop.

Identical to ``run_substantive_interaction_workflow_evolution_from_scratch_claude``
in every respect -- same pipeline, same solver workspace, same frozen seed, same
prompts, same gates, same concurrency -- with one addition: after a round's
training-parent runs finish and before the candidate is evolved, an LLM critic
scores each parent's *interaction* (policy text + recorded expert consultation +
recorded post-reply change) against the active rubric (see
``interaction_strategy_critic.DEFAULT_RUBRIC``; override with ``CRITIC_RUBRIC``),
and that review is appended to the workflow-evolution prompt as one extra
evidence node.

The arm is *composed*, not copied: the from-scratch launcher's hook set is laid
down first, then the critic's hook on top of it.  The critic is meant to be the
only difference between the two arms being compared, so keeping them in step is
the point -- a change to the from-scratch arm reaches this one for free, and a
difference that shows up in a result is a difference the critic caused.

Everything else the optimizer receives stays exactly as it was, and the critic's
scores never enter the utility computation or any acceptance gate.  The review is
written next to the round, as ``workflows/round_N/critic_review.{json,md}``.

Second addition: the rubric itself evolves.  A rubric that mis-measures one round
mis-measures every round after it, so every round whose parent and candidate both
finished sends its evidence to ``interaction_rubric_proposer``, which writes the
next version under ``workflows/rubric_evolution/round_N/`` and points later rounds
at it.  Which evidence depends on the gate, and that choice is made in code: when
the candidate beat its parent the validation split has run, so the candidate's
held-out record (scores, policy text and interaction history) is used; when the
parent still won there is no validation, and the two training records alone are
used.  See that module for the protocol and the validation the proposal must pass.

Both endpoints default to the pipeline's roles (override the critic with
``CRITIC_MODEL`` / ``CRITIC_BASE_URL`` / ``CRITIC_API_KEY`` / ``CRITIC_TIMEOUT``
and the rubric proposer with ``RUBRIC_MODEL`` / ``RUBRIC_BASE_URL`` /
``RUBRIC_API_KEY``).  Either failure is recorded and the round continues without
it.

The file name still says ``from_initial_draft`` because the arm was converted in
place from that baseline; only the docstring and the composed hooks changed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


# The rubric proposer runs on the optimizer endpoint unless the environment
# names another one -- the same split the launch script uses for the critic.
_DEFAULT_OPT_MODEL = os.environ.get("OPT_MODEL") or "qwen3.8-27b"
_DEFAULT_OPT_BASE_URL = os.environ.get("OPT_BASE_URL") or "http://gpu6:18763/v1"
_DEFAULT_OPT_API_KEY = os.environ.get("OPT_API_KEY") or "EMPTY"

try:
    from . import cpe_seed_reuse
    from . import interaction_rubric_proposer as proposer
    from . import interaction_strategy_critic as critic
    from . import run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base
    from . import run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch
except ImportError:  # pragma: no cover - direct-file invocation support
    from src.OpenClaw import cpe_seed_reuse
    from src.OpenClaw import interaction_rubric_proposer as proposer
    from src.OpenClaw import interaction_strategy_critic as critic
    from src.OpenClaw import (
        run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base,
    )
    from src.OpenClaw import (
        run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch,
    )


# Captured before anything rebinds the name: the launcher's own main() reads this
# module attribute when it wires the engine, so the patch has to be in place
# before main() runs, and the wrapper has to call through to the original.
_original_build = base.build_initial_draft_cpe_workflow_evolution_prompt
_review_cache: dict[int, dict] = {}


def build_with_critic_review(
    training_parents: list[dict],
    validation_champion: dict,
    patch_history: list[dict],
    dialogue_operators: dict | None = None,
) -> str:
    """Build the usual evolution prompt, then append this round's critic review."""
    prompt = _original_build(
        training_parents, validation_champion, patch_history, dialogue_operators
    )
    experiment = base._active_experiment
    if experiment is None:
        print("[critic] no active experiment; skipping the interaction review", flush=True)
        return prompt
    round_number = (training_parents[0].get("training_evidence") or {}).get("round")
    if round_number is None:
        print("[critic] round number missing; skipping the interaction review", flush=True)
        return prompt
    key = int(round_number)
    review = _review_cache.get(key)
    if review is None:
        model, api_key, base_url, timeout = critic.critic_credentials(
            mmbench_judge=base._mmbench_judge
        )
        print(
            f"[critic] scoring round {key} interaction with {model} at {base_url}",
            flush=True,
        )
        try:
            review = critic.review_training_parents(
                training_parents,
                experiment=experiment,
                model=model,
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
            )
        except Exception as error:  # noqa: BLE001 - never break the round
            print(f"[critic] review failed: {type(error).__name__}: {error}", flush=True)
            review = {"error": f"{type(error).__name__}: {error}", "parents": []}
        _review_cache[key] = review
    if review.get("error"):
        print(f"[critic] no review for round {key}: {review['error']}", flush=True)
        return prompt
    block = critic.render_critic_block(review)
    print(
        f"[critic] round {key} review appended to the evolution prompt "
        f"({len(block)} chars)",
        flush=True,
    )
    return prompt + "\n\n" + block


def evolve_round_rubric(experiment, result: dict) -> None:
    """Hand a finished round to the rubric proposer.

    Every round that reached this point ran both its parent and its candidate
    rollouts, so every one of them revises the rubric.  Which evidence the
    revision is made from -- the candidate's held-out record when validation ran,
    both training records when it did not -- is decided in the proposer, from the
    round's own gate outcome.
    """
    proposer.evolve_rubric(
        experiment,
        int(result.get("round", 0)),
        result,
        model=os.environ.get("RUBRIC_MODEL") or _DEFAULT_OPT_MODEL,
        base_url=os.environ.get("RUBRIC_BASE_URL") or _DEFAULT_OPT_BASE_URL,
        api_key=os.environ.get("RUBRIC_API_KEY") or _DEFAULT_OPT_API_KEY,
    )


_original_persist = base.workflow.persist_cpe_round_result


def persist_with_rubric_evolution(results_path, result: dict):
    """Persist the round first, then let it revise the rubric.

    Wrapping the round-end funnel rather than the engine's loop keeps this arm's
    extra step out of the shared engine, and one edit covers both call sites --
    the normal round end and the resume path.  The proposer is idempotent, so a
    resumed round re-activates its existing version instead of writing another.
    """
    results = _original_persist(results_path, result)
    try:
        evolve_round_rubric(Path(results_path).parent.parent, result)
    except Exception as error:  # noqa: BLE001 - a round costs hours; never lose one
        print(f"[rubric] evolution failed: {type(error).__name__}: {error}", flush=True)
    return results


def patch_sibling_launcher() -> None:
    """Lay this arm's hooks on the sibling launcher: from scratch, then the critic.

    Same name and same shape as the from-scratch arm's patch function, so the two
    arms stay comparable line for line: this one is that one plus the last two
    hooks.
    """
    scratch.patch_sibling_launcher()
    base.build_initial_draft_cpe_workflow_evolution_prompt = build_with_critic_review
    base.workflow.persist_cpe_round_result = persist_with_rubric_evolution
    # A no-op unless the experiment's state was seeded from another run's
    # initial-parent results, which is how an experiment continues a comparison
    # without re-solving the seed's two rounds.
    base.run_initial_draft_parent_evaluations = cpe_seed_reuse.reuse_or_run(
        base.run_initial_draft_parent_evaluations
    )


def main() -> None:
    """Rebind the sibling launcher's hooks, then run it unchanged."""
    patch_sibling_launcher()
    print(
        "Interaction-workflow co-evolution from scratch: the solver starts from "
        "the problem statement alone, and an LLM critic scores each parent's "
        "consultation before the candidate is evolved.",
        flush=True,
    )
    base.main()


if __name__ == "__main__":
    sys.exit(main())
