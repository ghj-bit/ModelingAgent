"""Create an experiment that continues another one's comparison from its seed.

A fresh CPE run measures the frozen seed twice before evolving anything: round 0
validates it on the blind split, round 1 evaluates it on one reserved training
batch.  When the point of a new run is to keep evolving the same seed -- with a
different arm, a different rubric, or a different optimizer -- that work is
already done, and this script adopts its results instead of solving the same
tasks again.

    python scripts/bootstrap_coevolution_experiment.py \\
        --source openclaw_experiments/evolve_exp/claude_scratch_evolve_r10 \\
        --target claude_coevolve_from_r10

The target's first evolved round is round 1, its champion bar is the source
seed's round-0 validation number, and its sampling configuration is copied
verbatim -- the engine refuses to resume an experiment whose pools, batch size,
seed or cost model differ from the state it finds, so the copy cannot drift.
Nothing evolved is carried over: no rounds, no patch history.

Launch the result with the arm of your choice, e.g.

    bash scripts/launch_claude_coevolution.sh <target-name> 5
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import cpe_seed_reuse  # noqa: E402

EXPERIMENT_ROOT = REPO_ROOT / "openclaw_experiments" / "evolve_exp"


def resolve_experiment(value: str) -> Path:
    """Accept an absolute path, a path relative to the repo, or a bare name."""
    candidate = Path(value).expanduser()
    if candidate.is_dir():
        return candidate.resolve()
    named = EXPERIMENT_ROOT / value
    if named.is_dir():
        return named.resolve()
    raise SystemExit(f"No such experiment directory: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True, help="name under evolve_exp/, or a path")
    args = parser.parse_args()

    source = resolve_experiment(args.source)
    target = Path(args.target).expanduser()
    if not target.is_absolute():
        target = EXPERIMENT_ROOT / args.target

    state = cpe_seed_reuse.build_seeded_experiment(source, target)
    print(f"Created {target}")
    print(f"  seed batch        : {state['initial_training_batch']}")
    print(f"  champion bar (val): {state['best_policy']['validation_utility']}")
    print(f"  current policy    : {state['current_policy']['workflow_id']} "
          f"(train utility {state['current_policy']['train_utility']})")
    print(f"  reused rounds     : {state[cpe_seed_reuse.SEEDED_KEY]['reused_rounds']} "
          f"from {source.name}")
    print(f"  evolved rounds    : none yet -- round 1 is this experiment's first")
    # The engine refuses to resume a state whose sampling configuration differs
    # from the launch's, so a seeded run has to be launched with the same pools
    # the source used.  Printing the command makes that hard to forget.
    pools = ",".join(str(item) for item in state["train_pool"])
    print(
        "\nLaunch it with the source's train pool:\n"
        f"  MMBENCH_TRAIN_POOL={pools} \\\n"
        f"    bash scripts/launch_claude_coevolution.sh {target.name} <max-rounds>"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
