"""One-click launcher: clean no-interaction baseline on MM-Bench ``2003_B`` only.

This is a thin wrapper over ``scripts/run_clean_baseline_train.py`` that pins the
MM-Bench task to ``2003_B`` so no benchmark/problem flags are needed:

    python scripts/run_2003_B_clean_baseline.py
    python scripts/run_2003_B_clean_baseline.py --exp <existing experiment>

``2003_B`` ships no dataset directory, so the runner stages nothing into the
task's data directory; the native MM-Bench problem definition and evaluator are
used unchanged.

Extra arguments after the known ones are forwarded verbatim, for example:

    python scripts/run_2003_B_clean_baseline.py --timeout 14400 --thinking high

Without ``--exp`` a new timestamped experiment is created. Re-running with the
same ``--exp`` resumes the unfinished tasks in that experiment.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TRAIN_LAUNCHER = REPO_ROOT / "scripts" / "run_clean_baseline_train.py"
PROBLEM_ID = "2003_B"


def main() -> int:
    known, forwarded = [], []
    arguments = sys.argv[1:]
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument in ("--exp", "--experiment"):
            if index + 1 >= len(arguments):
                print(f"{argument} requires a path", file=sys.stderr)
                return 2
            known.extend([argument, arguments[index + 1]])
            index += 2
        elif argument.startswith(("--exp=", "--experiment=")):
            known.append(argument)
            index += 1
        else:
            forwarded.append(argument)
            index += 1

    command = [
        sys.executable,
        str(TRAIN_LAUNCHER),
        "--benchmark",
        "mmbench",
        "--problem-id",
        PROBLEM_ID,
        *known,
        *forwarded,
    ]
    print("Clean baseline (MM-Bench " + PROBLEM_ID + ")", flush=True)
    print("Command: " + subprocess.list2cmdline(command), flush=True)
    result = subprocess.run(command, cwd=REPO_ROOT)
    if result.returncode:
        print(
            f"Clean baseline failed with exit code {result.returncode}. "
            "Resume with the same options plus --exp <experiment directory>.",
            file=sys.stderr,
        )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
