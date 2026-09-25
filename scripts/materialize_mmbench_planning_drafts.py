"""Materialize ``data/planning_drafts`` into the layout the launchers resolve.

The repository ships the clean-baseline planning blueprints as one directory per
MM-Bench task::

    data/planning_drafts/2014_C/draft.md

but every planning-draft resolver in ``src/OpenClaw`` discovers drafts by
globbing ``**/output/results/draft.md`` under an *experiment root* and reading
each draft's ``meta/run.json`` for its ``problem_id``::

    <root>/<task>/output/results/draft.md
    <root>/<task>/meta/run.json          {"problem_id": "<task>", ...}

This script bridges the two: it copies each shipped draft into that layout under
a target root, so the launchers can consume the repository's drafts without an
experiment tree.  The target name starts with the prefix the launchers glob for,
so ``--planning-draft-root`` is not even needed; re-running is idempotent.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "data" / "planning_drafts"
# Matches the glob in default_mmbench_draft_roots(), so the launcher finds this
# root by default.  Stable rather than timestamped: re-running must not pile up
# roots that hold identical drafts.
DEFAULT_TARGET = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_initial_draft_mmbench_from_repo_data"
)

MANIFEST_NOTE = (
    "Materialized from data/planning_drafts by "
    "scripts/materialize_mmbench_planning_drafts.py. The draft text is the "
    "clean-baseline initial-draft stage's output; see "
    "data/planning_drafts/README.md for the per-task source experiment and run."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    target = args.target.resolve()
    if not source.is_dir():
        print(f"Planning-draft source not found: {source}", file=sys.stderr)
        return 2

    drafts = sorted(path for path in source.glob("*/draft.md") if path.is_file())
    if not drafts:
        print(f"No <task>/draft.md under {source}", file=sys.stderr)
        return 2

    written, skipped = 0, 0
    for draft in drafts:
        problem_id = draft.parent.name
        run_dir = target / problem_id
        draft_target = run_dir / "output" / "results" / "draft.md"
        meta_target = run_dir / "meta" / "run.json"
        draft_target.parent.mkdir(parents=True, exist_ok=True)
        meta_target.parent.mkdir(parents=True, exist_ok=True)

        text = draft.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            print(f"  skip (empty): {draft}", file=sys.stderr)
            skipped += 1
            continue
        if not draft_target.is_file() or draft_target.read_text(
            encoding="utf-8", errors="replace"
        ) != text:
            shutil.copy2(draft, draft_target)
            written += 1

        # The resolver reads only problem_id, but a full manifest keeps the
        # materialized run directory self-describing next to real ones.
        meta_target.write_text(
            json.dumps(
                {
                    "problem_id": problem_id,
                    "benchmark": "mmbench",
                    "experiment_type": "materialized_planning_draft",
                    "source_draft": str(draft),
                    "note": MANIFEST_NOTE,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    print(
        f"Materialized {len(drafts) - skipped} planning draft(s) from {source}\n"
        f"  into {target}\n"
        f"  copied/updated: {written}, already current: {len(drafts) - skipped - written}"
        + (f", skipped empty: {skipped}" if skipped else "")
    )
    print(
        "\nThe launchers now resolve these by default:\n"
        "  python -m src.OpenClaw."
        "run_substantive_interaction_workflow_evolution_from_initial_draft_openhands\n"
        f"or explicitly with --planning-draft-root {target}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
