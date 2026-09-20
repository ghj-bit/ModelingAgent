"""One-click launcher: fixed-interaction-policy test on MM-Bench ``2003_B`` only.

Runs ``src/OpenClaw/run_substantive_interaction_workflow_test_from_initial_draft.py``
with ``--benchmark mmbench`` and ``--problem-id 2003_B``, and resolves the
planning-draft roots so no ``--planning-draft-test-root`` flag is needed:

    python scripts/run_2003_B_workflow_test.py
    python scripts/run_2003_B_workflow_test.py --exp <existing experiment>

A planning draft for ``2003_B`` must exist first. Generate one with:

    python scripts/run_clean_baseline_initial_draft_mmbench.py --problem-id 2003_B

Draft roots are discovered from every ``interaction_strategy_clean_baseline_
initial_draft_mmbench_*`` experiment plus the two pinned ModelingBench pools,
and the newest non-empty draft per problem wins. ``2003_B`` ships no dataset
directory, so the runner stages nothing into the task's data directory.

Without ``--exp`` a new timestamped experiment is created. Re-running with the
same ``--exp`` resumes that experiment.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import run_substantive_interaction_workflow_test_from_initial_draft as runner

PROBLEM_ID = "2003_B"


def missing_draft_message() -> str:
    searched = "\n".join(f"  - {root}" for root in runner.DEFAULT_PLANNING_DRAFT_ROOTS)
    return (
        f"No planning draft for MM-Bench {PROBLEM_ID} was found. Searched:\n"
        f"{searched}\n"
        "Generate one first:\n"
        "  python scripts/run_clean_baseline_initial_draft_mmbench.py "
        f"--problem-id {PROBLEM_ID}"
    )


def main() -> int:
    known, forwarded = [], []
    arguments = sys.argv[1:]
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument == "--exp":
            if index + 1 >= len(arguments):
                print("--exp requires a path", file=sys.stderr)
                return 2
            known.extend([argument, arguments[index + 1]])
            index += 2
        elif argument.startswith("--exp="):
            known.append(argument)
            index += 1
        else:
            forwarded.append(argument)
            index += 1

    # Fail before launching anything if the draft this task depends on is absent.
    try:
        draft = runner.resolve_planning_drafts(
            runner.DEFAULT_PLANNING_DRAFT_ROOTS, [PROBLEM_ID]
        )
    except FileNotFoundError as error:
        print(missing_draft_message(), file=sys.stderr)
        print(f"\n{error}", file=sys.stderr)
        return 2

    command = [
        sys.executable,
        "-m",
        "src.OpenClaw.run_substantive_interaction_workflow_test_from_initial_draft",
        "--benchmark",
        "mmbench",
        "--problem-id",
        PROBLEM_ID,
        "--planning-draft-test-root",
        *[str(root) for root in runner.DEFAULT_PLANNING_DRAFT_ROOTS],
        *known,
        *forwarded,
    ]
    print(f"Planning draft: {draft[PROBLEM_ID]}", flush=True)
    print("Workflow test (MM-Bench " + PROBLEM_ID + ")", flush=True)
    print("Command: " + subprocess.list2cmdline(command), flush=True)
    result = subprocess.run(command, cwd=REPO_ROOT)
    if result.returncode:
        print(
            f"Workflow test failed with exit code {result.returncode}. "
            "Resume with the same options plus --exp <experiment directory>.",
            file=sys.stderr,
        )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
