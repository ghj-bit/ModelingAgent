"""Print one screen of status for a running evaluation phase.

Meant to be invoked periodically by an external scheduler (or by hand) rather
than to sit in a loop: each call prints the current phase's runs and exits, so a
session-level kill takes down the report and not the experiment it describes.

    python scripts/monitor_phase_runs.py [experiment-dir] [--baseline <dir>]

For every run of the phase it reports where the run is in its own pipeline --
prepared, solving, report written, judged -- plus its elapsed time, and it
flags the two failure shapes this pipeline actually produces: a run that has
outlived the per-run timeout without a report, and a run that is far slower than
its siblings (the straggler that decides the phase's wall clock, because the
phase ends when its slowest run does).

The baseline is optional and only used for the one comparison worth making: the
same phase of an earlier experiment, whose wall clock is the number to beat.
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

# The engine abandons a run at two hours and re-runs it under a new directory;
# past this age without a report, that is what is happening.
RUN_TIMEOUT_MINUTES = 120.0
SLOW_FACTOR = 1.6  # a run this much slower than the median is the phase's tail


def read_json(path: pathlib.Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return default


def newest_mtime(directory: pathlib.Path) -> float | None:
    stamps = [p.stat().st_mtime for p in directory.rglob("*") if p.is_file()]
    return max(stamps) if stamps else None


def alive(pattern: str) -> int:
    """Processes whose command line names the experiment (this script excluded)."""
    try:
        out = subprocess.run(
            ["pgrep", "-f", pattern], capture_output=True, text=True, timeout=20
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return 0
    pids = [pid for pid in out.split() if pid.isdigit()]
    return max(len(pids) - 1, 0)  # pgrep matches this script's own argv


def current_phase(experiment: pathlib.Path, phase_name: str | None = None) -> pathlib.Path | None:
    """The phase with run directories, newest first.

    ``phase_name`` restricts the search to that phase, which is what makes a
    baseline comparison meaningful: the same phase of an earlier experiment is
    the only comparable one, and picking the earlier experiment's *newest* phase
    instead compares a validation phase against a later training phase.
    """
    pattern = (
        f"cpe_evaluations/round_*/{phase_name}/runs/round_*"
        if phase_name
        else "cpe_evaluations/round_*/**/runs/round_*"
    )
    phases = [
        runs.parent.parent
        for runs in experiment.glob(pattern)
        if runs.is_dir() and any(runs.iterdir())
    ]
    return max(phases, key=lambda p: p.stat().st_mtime) if phases else None


def run_state(run_dir: pathlib.Path) -> dict:
    metadata = read_json(run_dir / "meta" / "run.json", {}) or {}
    report = run_dir / "output" / "results" / "solution_report.md"
    judge = read_json(run_dir / "meta" / "mmbench_judge" / "judge_stability.json", {}) or {}
    started = metadata.get("created_at")
    try:
        started_at = datetime.datetime.fromisoformat(str(started))
    except (TypeError, ValueError):
        started_at = None
    last = newest_mtime(run_dir)
    elapsed = (
        (datetime.datetime.fromtimestamp(last) - started_at).total_seconds() / 60.0
        if started_at and last
        else None
    )
    if judge.get("average_score") is not None:
        state = "已判分"
    elif report.is_file():
        state = "判分中"
    elif elapsed is not None and elapsed >= RUN_TIMEOUT_MINUTES:
        state = "超时待重跑"
    else:
        state = "求解中"
    return {
        "run": run_dir.name,
        "problem": metadata.get("problem_id", "?"),
        "repetition": metadata.get("repetition", "?"),
        "state": state,
        "elapsed": elapsed,
        "score": judge.get("average_score"),
        "started_at": started_at,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", nargs="?", type=pathlib.Path)
    parser.add_argument(
        "--baseline",
        type=pathlib.Path,
        default=REPO / "openclaw_experiments/evolve_exp/claude_scratch_evolve_r10",
        help="earlier experiment to compare with (default: the 5-run round 0)",
    )
    args = parser.parse_args()

    experiment = (args.experiment or REPO / "openclaw_experiments/evolve_exp/claude_r0_conc20").resolve()
    if not experiment.is_dir():
        print(f"no such experiment: {experiment}")
        return 1
    phase = current_phase(experiment)
    if phase is None:
        print(f"{experiment.name}: no phase has started yet")
        return 0
    runs = sorted(p for p in (phase / "runs").glob("round_*/*") if p.is_dir())
    states = [run_state(run) for run in runs]
    started = [s["started_at"] for s in states if s["started_at"]]
    phase_start = min(started) if started else None
    now = datetime.datetime.now()
    wall = (now - phase_start).total_seconds() / 60.0 if phase_start else None
    elapsed = sorted(s["elapsed"] for s in states if s["elapsed"] is not None)
    median = elapsed[len(elapsed) // 2] if elapsed else None

    label = phase.relative_to(experiment)
    stamp = now.strftime("%H:%M:%S")
    print(f"[{stamp}] {experiment.name} · {label}")
    if phase_start:
        print(f"  阶段开始 {phase_start:%H:%M:%S}   已运行 {wall:.1f} 分钟   相关进程 {alive(experiment.name)} 个")
    counts: dict[str, int] = {}
    for state in states:
        counts[state["state"]] = counts.get(state["state"], 0) + 1
    print("  进度  " + "  ".join(f"{k} {v}" for k, v in sorted(counts.items())) + f"   合计 {len(states)}")
    if median is not None:
        print(f"  单 run 已用：最快 {elapsed[0]:.1f}m  中位 {median:.1f}m  最慢 {elapsed[-1]:.1f}m")
    if args.baseline and args.baseline.is_dir():
        base = current_phase(args.baseline.resolve(), phase.name)
        if base is not None:
            base_runs = [run_state(r) for r in (base / "runs").glob("round_*/*") if r.is_dir()]
            base_elapsed = [s["elapsed"] for s in base_runs if s["elapsed"] is not None]
            if base_elapsed:
                base_wall = max(base_elapsed)
                ratio = f"{wall / base_wall:.2f}×" if wall else "—"
                print(
                    f"  参照  {args.baseline.name} 同阶段 {len(base_runs)} 个 run 用了 "
                    f"{base_wall:.1f} 分钟 → 当前 {ratio}"
                )
    print()
    for state in states:
        flag = ""
        if state["elapsed"] and median and state["elapsed"] > median * SLOW_FACTOR:
            flag = "  ← 拖尾"
        if state["state"] == "超时待重跑":
            flag = "  ← 已超时"
        score = f"{state['score']:.4f}" if state["score"] is not None else "—"
        used = f"{state['elapsed']:.1f}m" if state["elapsed"] is not None else "—"
        print(
            f"  {state['run'].split('_')[0]:<6} {state['problem']:<8} rep{state['repetition']:<2} "
            f"{state['state']:<10} {used:>7}  分数 {score}{flag}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
