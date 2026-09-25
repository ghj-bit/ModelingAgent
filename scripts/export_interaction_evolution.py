"""Refresh the interaction-strategy workbook for one evolution experiment.

The engine writes the workbook itself at the end of every round, so this script
exists for the two cases the engine cannot cover: a round that ran before the
export was wired in, and a long round whose progress is worth reading before it
finishes.  It only reads the experiment's artifacts and rewrites one workbook,
which makes it safe to run against a live experiment.

    python scripts/export_interaction_evolution.py <experiment-dir>

Exit codes: 0 written, 1 the experiment directory has no workflows/ directory,
2 the export failed (the traceback says where).
"""

from __future__ import annotations

import pathlib
import sys
import traceback

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.OpenClaw import interaction_workflow_excel  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 1
    experiment = pathlib.Path(argv[1]).expanduser().resolve()
    if not (experiment / "workflows").is_dir():
        print(f"No workflows/ directory under {experiment}")
        return 1
    output = experiment / "workflows" / interaction_workflow_excel.WORKBOOK_NAME
    try:
        interaction_workflow_excel.write_interaction_evolution_workbook(output, experiment)
    except Exception:  # noqa: BLE001 - the CLI is where a failure should be loud
        traceback.print_exc()
        return 2
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
