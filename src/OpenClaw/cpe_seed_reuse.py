"""Start an experiment from another experiment's initial-parent results.

A fresh CPE experiment spends its first two rounds measuring the frozen seed: a
round-0 validation on the blind split, then a round-1 evaluation on one reserved
training batch.  That work is about the seed, not about the experiment, so a run
that means to continue the same comparison -- same seed, same batch, same bar --
can adopt the earlier run's numbers instead of solving the same tasks again.

Two halves, deliberately separate:

* :func:`build_seeded_experiment` writes the new experiment's ``cpe_state.json``
  from a source experiment's stored snapshots and links the reused rounds' run
  directories, so the evidence the state points at still resolves.
* :func:`reuse_or_run` wraps the launcher's initial-parent evaluations: a state
  that carries ``seeded_from`` is reused, and every other state runs as before.
  The wrapper is therefore a no-op for a normal run, which is why it is safe to
  install unconditionally.

What is *not* copied is any evolved material: the new state has no rounds and no
patch history, so its first evolved round is round 1 and its lineage starts
where the source's seed left off.
"""

from __future__ import annotations

import copy
import shutil
from pathlib import Path
from typing import Any, Callable

try:
    from . import run_evolution as workflow_evolution
    from . import run_substantive_interaction_workflow_evolution as engine
except ImportError:  # pragma: no cover - direct-file invocation support
    import run_evolution as workflow_evolution
    import run_substantive_interaction_workflow_evolution as engine


SEEDED_KEY = "seeded_from"
REUSED_ROUNDS = (0, 1)

# The seed's own phases, and nothing else.  Round 1 also holds the source's
# *candidate* phase, and exposing that one is a trap: the engine would find the
# source's completed candidate checkpoint under this experiment's round directory
# and score the new candidate with the old candidate's runs, finishing a round in
# a minute with results that belong to a different policy.
SEED_PHASES = {
    0: ("initial_validation_parent_1",),
    1: ("initial_train_parent_1",),
}

# The state fields `load_or_create_cpe_state` validates on resume.  They are the
# experiment's sampling contract, so they must come across unchanged or the
# engine refuses the resume -- which is the point.
CONFIG_KEYS = (
    "schema_version",
    "sampling_seed",
    "train_pool",
    "validation_pool",
    "train_batch_size",
    "validation_size",
    "selection_epsilon",
    "train_sampling",
    "validation_problems",
    "utility_basis",
    "interaction_cost",
)


def is_seeded(state: dict[str, Any]) -> bool:
    seeded = state.get(SEEDED_KEY)
    return isinstance(seeded, dict) and bool(seeded.get("source_experiment"))


def link_reused_rounds(target: Path, source: Path) -> None:
    """Expose the source's seed phases under the target, one link per phase.

    The round directory itself is **real**: this experiment writes its own
    candidate, validation and later rounds into it, and only the seed's phases
    are borrowed from the source.  Linking a whole round directory instead would
    hand this experiment the source's candidate phase as well, and the engine
    would reuse the source's completed candidate checkpoint -- scoring a new
    policy with an old policy's runs, in a minute, with no sign anything was
    borrowed.
    """
    for round_number, phases in SEED_PHASES.items():
        round_dir = Path(target) / "cpe_evaluations" / f"round_{round_number}"
        source_round = Path(source) / "cpe_evaluations" / f"round_{round_number}"
        if round_dir.is_symlink():
            raise ValueError(
                f"{round_dir} is a symlink to the source's whole round; that layout "
                "exposes its candidate phase. Remove it and re-seed this experiment."
            )
        round_dir.mkdir(parents=True, exist_ok=True)
        for phase in phases:
            link = round_dir / phase
            origin = source_round / phase
            if link.exists() or link.is_symlink():
                continue
            if not origin.is_dir():
                raise FileNotFoundError(
                    f"source experiment has no {origin}; cannot reuse round {round_number}"
                )
            link.symlink_to(origin.resolve())


def build_seeded_experiment(source: Path, target: Path) -> dict[str, Any]:
    """Write ``target``'s state from ``source``'s stored seed results."""
    source = Path(source).resolve()
    target = Path(target).resolve()
    source_state = workflow_evolution.read_json(
        engine.cpe_state_path(source), {}
    )
    if not source_state:
        raise FileNotFoundError(f"no CPE state under {source}")
    validation_results = source_state.get("initial_parent_validation_results") or []
    train_results = source_state.get("initial_parent_train_results") or []
    if not validation_results or not train_results:
        raise ValueError(
            f"{source} has no stored initial-parent results; pick a source experiment "
            "that finished its seed rounds"
        )
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"{target} is not empty; refusing to overwrite it")

    state = {key: copy.deepcopy(source_state[key]) for key in CONFIG_KEYS if key in source_state}
    state["initialization_mode"] = source_state.get("initialization_mode")
    state["initial_parent_validation_results"] = copy.deepcopy(validation_results)
    state["initial_parent_train_results"] = copy.deepcopy(train_results)
    state["initial_seed_train"] = copy.deepcopy(source_state.get("initial_seed_train") or [])
    state["initial_training_batch"] = list(source_state.get("initial_training_batch") or [])
    if not state["initial_training_batch"]:
        raise ValueError(f"{source} has no reserved initial training batch")

    # Recomputed rather than copied: the source has moved on, so its `best_policy`
    # is whatever later round won validation.  The bar the new experiment starts
    # from is the seed's own round-0 number.
    champion = max(
        validation_results,
        key=lambda result: (float(result["utility"]), str(result["workflow_id"])),
    )
    state["best_policy"] = {
        "source_round": 0,
        "source_phase": "initial_validation_parent",
        "workflow_id": champion["workflow_id"],
        "workflow": engine.without_removed_workflow_fields(champion["workflow"]),
        "validation_utility": float(champion["utility"]),
        "utility_basis": engine.CPE_UTILITY_BASIS,
    }
    # `select_cpe_training_elites` reads the arm's parent count off the engine's
    # module global -- 2 for the two-parent arms, 1 for the single-policy ones
    # this pipeline runs.  The seed results say how many parents this experiment
    # has, so the count is derived from them rather than assumed, and restored
    # afterwards so a stand-alone call cannot re-configure the engine.
    previous_count = engine.CPE_TRAINING_PARENT_COUNT
    engine.CPE_TRAINING_PARENT_COUNT = len(train_results)
    try:
        state["training_elites"] = engine.select_cpe_training_elites(train_results)
    finally:
        engine.CPE_TRAINING_PARENT_COUNT = previous_count
    best_train = state["training_elites"][0]
    state["current_policy"] = {
        **copy.deepcopy(best_train),
        "train_utility": float(best_train["selection_utility"]),
        "utility_basis": engine.CPE_UTILITY_BASIS,
    }
    state["rounds"] = {}
    state["patch_history"] = []
    state["created_at"] = engine.now()
    state["updated_at"] = state["created_at"]
    state["initial_training_batch_reserved_at"] = source_state.get(
        "initial_training_batch_reserved_at"
    ) or state["created_at"]
    state[SEEDED_KEY] = {
        "source_experiment": str(source),
        "reused_rounds": list(REUSED_ROUNDS),
        "initial_training_batch": list(state["initial_training_batch"]),
        "seeded_at": state["created_at"],
        "note": (
            "rounds 0-1 adopted from the source experiment; the first evolved "
            "round of this experiment is round 1"
        ),
    }

    (target / "workflows").mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        source / "initial_interaction_workflows.json",
        target / "initial_interaction_workflows.json",
    )
    # The engine reads the source's resolved baseline reports out of config.json;
    # carrying it over keeps one fewer thing to re-resolve.
    config = source / "config.json"
    if config.is_file():
        shutil.copy2(config, target / "config.json")
    workflow_evolution.write_json(engine.cpe_state_path(target), state)
    link_reused_rounds(target, source)
    return state


def reuse_or_run(
    original: Callable[..., None],
) -> Callable[..., None]:
    """Wrap the launcher's initial-parent evaluations so a seeded state is reused.

    A state without ``seeded_from`` falls through to the launcher's own
    implementation, so installing this changes nothing for an ordinary run.
    """

    def run(
        experiment: Path,
        initial_problem_ids: list[str],
        initial_population: list[dict],
        fixed_rubric: dict,
        problems: dict,
        run_args,
        args,
        state: dict[str, Any],
        original_scores: dict[str, dict],
    ) -> None:
        if not is_seeded(state):
            return original(
                experiment,
                initial_problem_ids,
                initial_population,
                fixed_rubric,
                problems,
                run_args,
                args,
                state,
                original_scores,
            )
        source = Path(str(state[SEEDED_KEY]["source_experiment"]))
        link_reused_rounds(Path(experiment), source)
        state["updated_at"] = engine.now()
        workflow_evolution.write_json(engine.cpe_state_path(experiment), state)
        print(
            f"[seed] adopting rounds {list(REUSED_ROUNDS)} from {source}; the "
            "initial parents are not re-evaluated",
            flush=True,
        )
        return None

    return run
