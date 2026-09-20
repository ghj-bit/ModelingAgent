"""Resume a stopped interaction-workflow evolution run.

Designed to be invoked periodically by an external scheduler (a Windows
scheduled task, say) rather than to sit in a loop.  Each invocation does one
check and exits, so there is no long-lived process for a session-level kill to
take down along with the experiment it is meant to protect.

    python scripts/watch_evolution_experiment.py [experiment-dir] [--dry-run]

Exit codes
    0  nothing to do (experiment alive, finished, or in its cooldown window)
    0  a resume was launched
    1  the check could not be completed

Completion is read from the experiment's own state: `cpe_state.json` lists a
`rounds` entry per finished round, and the run is done once that count reaches
`max_rounds` in `config.json`.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_EXPERIMENT = REPO / "openclaw_experiments/evolve_exp/evolve_20260920_001619"

LAUNCHER_MODULE = (
    "src.OpenClaw.run_substantive_interaction_workflow_evolution_from_initial_draft"
)
# A fresh launcher needs a moment to appear in the process table; without this
# the very next scheduled tick could start a second copy.
RESUME_COOLDOWN_SECONDS = 600.0
# Ignore lock files older than this: a crashed invocation must not wedge the job.
LOCK_STALE_SECONDS = 900.0


def log(path: pathlib.Path, message: str) -> None:
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line, flush=True)
    try:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        pass


def launcher_alive() -> list[int]:
    """PIDs of running launcher processes.

    The process name is checked as well as the command line: the shell wrapper
    that started a run carries the same command string, and matching on that
    alone would report a dead experiment as alive.
    """
    try:
        import psutil
    except ImportError:
        return []

    found = []
    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = (process.info.get("name") or "").lower()
            cmdline = " ".join(process.info.get("cmdline") or [])
        except Exception:  # noqa: BLE001  (NoSuchProcess / AccessDenied)
            continue
        if not name.startswith("python"):
            continue
        if "evolution_from_initial_draft" in cmdline:
            found.append(process.info["pid"])
    return found


def progress(experiment: pathlib.Path) -> tuple[int, int]:
    """(completed rounds, declared max rounds)."""
    max_rounds = 0
    config_path = experiment / "config.json"
    if config_path.is_file():
        try:
            max_rounds = int(
                json.loads(config_path.read_text(encoding="utf-8")).get("max_rounds", 0)
            )
        except (ValueError, OSError):
            max_rounds = 0

    state_path = experiment / "workflows/cpe_state.json"
    done = 0
    if state_path.is_file():
        try:
            rounds = json.loads(state_path.read_text(encoding="utf-8")).get("rounds", {})
            done = sum(
                1
                for entry in rounds.values()
                if isinstance(entry, dict) and entry.get("status") == "complete"
            )
        except (ValueError, OSError):
            done = 0
    return done, max_rounds


def take_lock(lock_path: pathlib.Path) -> bool:
    """Atomically claim the lock; return False when another check holds it."""
    if lock_path.exists():
        age = time.time() - lock_path.stat().st_mtime
        if age < LOCK_STALE_SECONDS:
            return False
        lock_path.unlink(missing_ok=True)
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(descriptor, str(os.getpid()).encode())
        os.close(descriptor)
        return True
    except FileExistsError:
        return False


def resume_command(experiment: pathlib.Path, config: dict) -> list[str]:
    """Rebuild the flags from the experiment's own recorded configuration.

    The resume guard rejects a run whose sampling settings differ from those it
    saved, so every value that feeds that comparison is passed explicitly.
    """
    cpe = config.get("cpe", {})
    return [
        sys.executable,
        "-m",
        LAUNCHER_MODULE,
        "--benchmark", "mmbench",
        "--max-rounds", str(config.get("max_rounds", 5)),
        "--thinking", "off",
        "--train-batch-size", str(cpe.get("train_batch_size", 2)),
        "--validation-size", str(cpe.get("validation_size", 5)),
        "--exp", str(experiment),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "experiment", nargs="?", type=pathlib.Path, default=DEFAULT_EXPERIMENT
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="report the decision without resuming"
    )
    args = parser.parse_args()

    experiment = args.experiment.resolve()
    if not (experiment / "config.json").is_file():
        print(f"not an experiment directory: {experiment}", file=sys.stderr)
        return 1

    log_path = experiment.parent / f"watchdog_{experiment.name}.log"
    lock_path = experiment.parent / f".watchdog_{experiment.name}.lock"

    if not take_lock(lock_path):
        return 0
    try:
        alive = launcher_alive()
        if alive:
            # Quiet on the happy path so the log only shows real events.
            return 0

        done, total = progress(experiment)
        if total and done >= total:
            log(log_path, f"experiment finished ({done}/{total} rounds); nothing to do")
            return 0

        config = json.loads((experiment / "config.json").read_text(encoding="utf-8"))
        stamp_path = experiment.parent / f".watchdog_{experiment.name}.last_resume"
        if stamp_path.exists():
            since = time.time() - stamp_path.stat().st_mtime
            if since < RESUME_COOLDOWN_SECONDS:
                log(
                    log_path,
                    f"launcher gone, progress {done}/{total}, but a resume was "
                    f"launched {since:.0f}s ago; waiting out the cooldown",
                )
                return 0
            # A resume was attempted and the launcher is still absent. Treat the
            # attempt as failed and allow another.
            log(log_path, f"previous resume did not take (waited {since:.0f}s)")

        command = resume_command(experiment, config)
        if args.dry_run:
            log(log_path, "DRY RUN would resume: " + " ".join(command))
            return 0

        log(
            log_path,
            f"INTERRUPTED: no launcher and only {done}/{total} rounds complete; resuming",
        )
        output = (experiment.parent / f"resume_{experiment.name}.out").open(
            "a", encoding="utf-8"
        )
        output.write(
            f"\n===== resume at {datetime.datetime.now():%Y-%m-%d %H:%M:%S} =====\n"
        )
        output.flush()
        subprocess.Popen(
            command,
            cwd=str(REPO),
            stdout=output,
            stderr=subprocess.STDOUT,
            creationflags=(
                subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            ),
            close_fds=True,
        )
        stamp_path.write_text(str(time.time()), encoding="utf-8")
        log(log_path, "resume launched detached")
        return 0
    finally:
        lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
