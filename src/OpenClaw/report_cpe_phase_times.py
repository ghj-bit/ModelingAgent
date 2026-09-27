#!/usr/bin/env python3
"""Print a per-round, per-phase execution-time table for a CPE evolution experiment.

The engine already writes ``round_execution_times.xlsx``, but that sheet only
covers the train-candidate phase, so it understates a round's real cost by
roughly 2.5x.  This script reconstructs every phase from the run artifacts:

  start  = ``meta/run.json`` -> ``created_at``
  end    = mtime of ``meta/mmbench_judge/judge_stability.json`` (last artifact)
  solver = last ``duration_ms`` in ``meta/transport.log`` (the claude session)

Usage:
    python -m OpenClaw.report_cpe_phase_times <experiment_dir> [--detail]
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

PHASE_LABELS = {
    "initial_validation_parent_1": "初始验证",
    "initial_train_parent_1": "初始父代",
    "train_parent_1": "父代评测",
    "train_candidate": "候选评测",
    "validation": "验证",
}
PHASE_ORDER = ["初始验证", "初始父代", "父代评测", "演化", "候选评测", "验证"]

RUN_GLOB = "cpe_evaluations/round_*/*/runs/round_*/*/meta/run.json"
DURATION_RE = re.compile(r'"duration_ms":(\d+)')
LIVE_SECONDS = 15 * 60  # a run still writing within this window is in flight, not aborted


def load_runs(experiment: Path) -> list[dict[str, Any]]:
    """Collect one record per run directory, newest artifacts last."""
    runs: list[dict[str, Any]] = []
    for run_json in sorted(experiment.glob(RUN_GLOB)):
        run_dir = run_json.parent.parent
        rel = run_dir.relative_to(experiment).parts
        # cpe_evaluations / round_N / <phase> / runs / round_N / <run>
        meta = json.loads(run_json.read_text())
        started = datetime.fromisoformat(meta["created_at"])

        stability = run_dir / "meta/mmbench_judge/judge_stability.json"
        finished = datetime.fromtimestamp(stability.stat().st_mtime) if stability.exists() else None

        solver_seconds = None
        transport = run_dir / "meta/transport.log"
        if transport.exists():
            matches = DURATION_RE.findall(transport.read_text(errors="replace"))
            if matches:  # the session's final result line carries the total
                solver_seconds = int(matches[-1]) / 1000.0

        # A run without a judge checkpoint either died in a restart or is still
        # live; its most recent write separates the two.
        newest = max(
            (os.path.getmtime(os.path.join(root, name))
             for root, _, names in os.walk(run_dir) for name in names
             if "/claude_config" not in root),
            default=run_dir.stat().st_mtime,
        )

        runs.append(
            {
                "round": int(rel[1].split("_")[1]),
                "phase": rel[2],
                "attempt": "_".join(run_dir.name.split("_")[-2:]),  # e.g. 20260927_001745
                "run": run_dir.name,
                "problem": meta.get("problem_id"),
                "repetition": meta.get("repetition"),
                "started": started,
                "finished": finished,
                "active": finished is None and (datetime.now().timestamp() - newest) < LIVE_SECONDS,
                "solver_seconds": solver_seconds,
                "dir": str(run_dir),
            }
        )
    runs.sort(key=lambda r: r["started"])
    return runs


def phase_windows(runs: list[dict[str, Any]], round_number: int) -> dict[str, dict[str, Any]]:
    """Canonical window per phase: completed runs only, aborted attempts excluded.

    A run that was aborted mid-session leaves no ``judge_stability.json``, so it
    never counts.  A run that *did* finish before a restart keeps its place (the
    engine reuses it from its per-problem checkpoint), which is why the round-1
    validation window starts at the first attempt.
    """
    by_phase: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        if run["round"] == round_number:
            by_phase[run["phase"]].append(run)

    windows: dict[str, dict[str, Any]] = {}
    for phase, group in by_phase.items():
        done = [r for r in group if r["finished"]]
        aborted = [r for r in group if not r["finished"] and not r["active"]]
        window: dict[str, Any] = {
            "label": PHASE_LABELS.get(phase, phase),
            "aborted": len(aborted),
            "active": len([r for r in group if r["active"]]),
            "attempts": sorted({r["attempt"] for r in group}),
        }
        if done:
            window["start"] = min(r["started"] for r in done)
            window["end"] = max(r["finished"] for r in done)
            window["minutes"] = (window["end"] - window["start"]).total_seconds() / 60
            # The runs are parallel, so the phase wall clock is set by the slowest
            # one, not by the sum -- compare against that run, not the total.
            slowest = max(done, key=lambda r: (r["finished"] - r["started"]).total_seconds())
            window["slowest"] = (slowest["finished"] - slowest["started"]).total_seconds() / 60
            window["slowest_solver"] = (slowest["solver_seconds"] or 0.0) / 60
            window["solver_minutes"] = sum(r["solver_seconds"] or 0.0 for r in done) / 60
            window["mean"] = sum((r["finished"] - r["started"]).total_seconds() for r in done) / 60 / len(done)
            window["runs"] = len(done)
        windows[phase] = window
    return windows


def evolution_window(experiment: Path, round_number: int) -> dict[str, Any] | None:
    """Optimizer call window from prompt/response mtimes; retries extend the span."""
    round_dir = experiment / f"workflows/round_{round_number}"
    stamps = [
        (p.name, datetime.fromtimestamp(p.stat().st_mtime))
        for p in list(round_dir.glob("evolution_prompt*.md")) + list(round_dir.glob("evolution_response*.json"))
    ]
    if not stamps:
        return None
    stamps.sort(key=lambda item: item[1])
    # The engine writes both ``evolution_prompt.md`` and ``evolution_prompt_attempt_1.md``
    # for a single call, so only the response files identify real attempts.
    responses = [name for name, _ in stamps if re.match(r"evolution_response_attempt_\d+\.json", name)]
    attempts = len(responses) or 1
    return {
        "label": "演化",
        "start": stamps[0][1],
        "end": stamps[-1][1],
        "minutes": (stamps[-1][1] - stamps[0][1]).total_seconds() / 60,
        "attempts": attempts,
        "runs": attempts,
    }


def round_bounds(experiment: Path, runs: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Round wall clock from cpe_state, falling back to the run artifacts."""
    state_path = experiment / "workflows/cpe_state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    rounds = state.get("rounds", {})

    bounds: dict[int, dict[str, Any]] = {}
    numbers = sorted({r["round"] for r in runs} | {int(k) for k in rounds})
    for number in numbers:
        entry = rounds.get(str(number), {})
        started = None
        if entry.get("batch_reserved_at"):
            started = datetime.fromisoformat(entry["batch_reserved_at"])
        else:  # round 0 predates the reservation record
            own = [r["started"] for r in runs if r["round"] == number]
            started = min(own) if own else None
        finished = datetime.fromisoformat(entry["completed_at"]) if entry.get("completed_at") else None
        if finished is None:  # round 0 is never stamped complete; use its artifacts
            own = [r["finished"] for r in runs if r["round"] == number and r["finished"]]
            finished = max(own) if own else None
        bounds[number] = {"start": started, "end": finished}
    return bounds


def minutes(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f}"


def print_matrix(experiment: Path, runs: list[dict[str, Any]], bounds: dict[int, dict[str, Any]]) -> None:
    print()
    print("=" * 96)
    print(f"各轮次各阶段执行时间（分钟）   {experiment.name}")
    print("=" * 96)
    header = f"{'轮':>3} {'起始':>9} " + "".join(f"{label:>10}" for label in PHASE_ORDER) + f"{'轮合计':>10}"
    print(header)
    print("-" * len(header))

    totals: dict[str, list[float]] = defaultdict(list)
    for number in sorted(bounds):
        windows = phase_windows(runs, number)
        cells: dict[str, float | None] = {label: None for label in PHASE_ORDER}
        notes = []
        for phase, window in windows.items():
            if "minutes" in window:
                cells[window["label"]] = window["minutes"]
                totals[window["label"]].append(window["minutes"])
                if window["aborted"]:
                    notes.append(f"{window['label']}重跑")
        evolution = evolution_window(experiment, number)
        if evolution:
            cells["演化"] = evolution["minutes"]
            totals["演化"].append(evolution["minutes"])

        start = bounds[number]["start"]
        end = bounds[number]["end"]
        total = (end - start).total_seconds() / 60 if start and end else None
        if total is not None:
            totals["轮合计"].append(total)

        stamp = start.strftime("%m-%d %H:%M") if start else "—"
        row = f"{number:>3} {stamp:>9} " + "".join(f"{minutes(cells[label]):>10}" for label in PHASE_ORDER)
        row += f"{minutes(total) if total else '进行中':>10}"
        if notes:
            row += "   " + "、".join(notes)
        print(row)

    print("-" * len(header))
    if "轮合计" in totals and totals["轮合计"]:
        mean_all = sum(totals["轮合计"]) / len(totals["轮合计"])
        print(f"合计 {sum(totals['轮合计']):>6.1f} 分钟 = {sum(totals['轮合计'])/60:.1f} 小时，"
              f"已完成轮次均值 {mean_all:.1f} 分钟/轮")
    print()
    print("阶段均值: ", end="")
    print("  ".join(f"{label}={sum(totals[label])/len(totals[label]):.1f}"
                    for label in PHASE_ORDER if totals.get(label)))


def print_phase_detail(experiment: Path, runs: list[dict[str, Any]], bounds: dict[int, dict[str, Any]]) -> None:
    print()
    print("=" * 108)
    print("阶段明细")
    print("=" * 108)
    header = (f"{'轮':>3} {'阶段':<8} {'起→止':<21} {'墙钟':>7} {'run':>4} {'最慢':>7} "
              f"{'均值':>7} {'claude':>7} {'判分':>6}  备注")
    print(header)
    print("-" * len(header))
    for number in sorted(bounds):
        windows = phase_windows(runs, number)
        for phase, label in PHASE_LABELS.items():
            window = windows.get(phase)
            if not window:
                continue
            if "minutes" not in window:  # nothing finished yet -- still in flight
                print(f"{number:>3} {label:<8} {'（尚未产生完成产物）':<21} {'—':>7} "
                      f"{window['active']:>4} {'—':>7} {'—':>7} {'—':>7} {'—':>6}  进行中")
                continue
            # judging is what the slowest run spends beyond its claude session
            judge = window["slowest"] - window["slowest_solver"]
            notes = []
            if window["aborted"]:
                notes.append(f"{window['aborted']} 个 run 中止后重跑")
            if window["active"]:
                notes.append(f"{window['active']} 个 run 进行中")
            note = "、".join(notes)
            print(
                f"{number:>3} {label:<8} "
                f"{window['start'].strftime('%m-%d %H:%M:%S')}→{window['end'].strftime('%H:%M:%S'):<8} "
                f"{window['minutes']:>7.1f} {window['runs']:>4} {window['slowest']:>7.1f} "
                f"{window['mean']:>7.1f} {window['slowest_solver']:>7.1f} {judge:>6.1f}  {note}"
            )
        evolution = evolution_window(experiment, number)
        if evolution:
            note = f"{evolution['attempts']} 次优化器调用" if evolution["attempts"] > 1 else ""
            print(
                f"{number:>3} {'演化':<8} "
                f"{evolution['start'].strftime('%m-%d %H:%M:%S')}→{evolution['end'].strftime('%H:%M:%S'):<8} "
                f"{evolution['minutes']:>7.1f} {evolution['runs']:>4} {'—':>7} {'—':>7} {'—':>7} {'—':>6}  {note}"
            )


def print_run_detail(runs: list[dict[str, Any]]) -> None:
    print()
    print("=" * 108)
    print("单个 run 明细")
    print("=" * 108)
    header = f"{'轮':>3} {'阶段':<10} {'题目':<8} {'次':>3} {'开始':<17} {'结束':<17} {'墙钟':>7} {'claude':>7} {'轮次':>5}"
    print(header)
    print("-" * 108)
    turns_re = re.compile(r'"num_turns":(\d+)')
    for run in runs:
        mark = "" if run["finished"] else ("  ← 进行中" if run["active"] else "  ← 中止")
        end = run["finished"].strftime("%m-%d %H:%M:%S") if run["finished"] else "—"
        wall = (run["finished"] - run["started"]).total_seconds() / 60 if run["finished"] else None
        turns = ""
        print(
            f"{run['round']:>3} {PHASE_LABELS.get(run['phase'], run['phase']):<10} "
            f"{str(run['problem']):<8} {str(run['repetition']):>3} "
            f"{run['started'].strftime('%m-%d %H:%M:%S')}  {end:<17} "
            f"{minutes(wall):>7} {minutes((run['solver_seconds'] or 0)/60 if run['solver_seconds'] else None):>7} {turns:>5}{mark}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiment", type=Path, help="experiment directory (holds cpe_evaluations/ and workflows/)")
    parser.add_argument("--detail", action="store_true", help="also print one row per run")
    args = parser.parse_args()

    experiment = args.experiment.resolve()
    runs = load_runs(experiment)
    if not runs:
        raise SystemExit(f"no runs found under {experiment}/cpe_evaluations")
    bounds = round_bounds(experiment, runs)
    print_matrix(experiment, runs, bounds)
    print_phase_detail(experiment, runs, bounds)
    if args.detail:
        print_run_detail(runs)
    completed = [r for r in runs if r["finished"]]
    failed = len(runs) - len(completed)
    judge = sum((r["finished"] - r["started"]).total_seconds() - (r["solver_seconds"] or 0)
                for r in completed) / 60
    print()
    print(f"共 {len(runs)} 个 run，完成 {len(completed)}，中止 {failed}")
    print(f"完成的 run：claude 会话合计 {sum(r['solver_seconds'] or 0 for r in completed)/3600:.1f} 小时"
          f"（并行，不等于墙钟），判分+收尾合计 {judge:.0f} 分钟（{judge*60/len(completed):.0f} 秒/run）")


if __name__ == "__main__":
    main()
