#!/usr/bin/env python3
"""Live terminal dashboard for an interaction-workflow evolution experiment.

Reads the experiment directory directly -- no state file, no database -- so it
can be started at any point during a run and it never interferes with it.  Every
panel answers a question you actually ask while babysitting a run:

* is the launcher still alive, and how many solvers is it driving in parallel?
* which problem is in which phase, and how long has it been there?
* has the expert bridge completed an exchange with ``ok: true``?  A run whose
  exchanges all failed will be rejected by the interaction gate no matter how
  good its report is, so this is the first thing to watch.
* has anything raised?

Usage::

    python scripts/openhands_experiment_dashboard.py [experiment_dir] [-i 5]

Without an argument it picks the newest experiment under
``openclaw_experiments/evolve_exp`` that is not a preserved failure directory.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

ANSI_RE = re.compile(r"\033\[[0-9;]*m")

# A run whose report exists but that still wrote something within this window is
# taken to be in the prompt's post-report self-check pass rather than finished.
REPORT_SETTLE_SECONDS = 120.0


def display_width(text: str) -> int:
    """Terminal columns a string occupies: ANSI escapes free, CJK double."""
    plain = ANSI_RE.sub("", text)
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in plain)


def pad(text: str, width: int) -> str:
    """Left-justify to a column width, ignoring colour escapes."""
    return text + " " * max(0, width - display_width(text))

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPERIMENT_ROOT = REPO_ROOT / "openclaw_experiments" / "evolve_exp"
RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"


def newest_experiment() -> Path | None:
    candidates = [
        path
        for path in DEFAULT_EXPERIMENT_ROOT.glob("evolve*")
        if path.is_dir() and not path.name.startswith("_")
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def launcher_pids() -> list[int]:
    """PIDs of the experiment launcher, matched on its full command line."""
    try:
        out = subprocess.run(
            ["ps", "-eo", "pid=,cmd="], capture_output=True, text=True, timeout=10
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    pids = []
    for line in out.splitlines():
        pid, _, cmd = line.strip().partition(" ")
        if "run_substantive_interaction_workflow_evolution_from_initial_draft" in cmd:
            # Exclude the ssh/bash wrapper that carries the same text.
            if "python" in cmd and "-m src.OpenClaw" in cmd:
                pids.append(int(pid))
    return pids


def solver_processes() -> int:
    try:
        out = subprocess.run(
            ["ps", "-eo", "cmd="], capture_output=True, text=True, timeout=10
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return 0
    return sum(
        1
        for line in out.splitlines()
        if "openhands_backend/run_openhands_task.py" in line and "grep" not in line
    )


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def expert_exchange_state(run_dir: Path) -> tuple[int, int]:
    """Return (exchanges with ok=true, exchanges with ok=false)."""
    ok = failed = 0
    for path in glob.glob(str(run_dir / "output/logs/operator_feedback/expert_reply_*.json")):
        reply = read_json(Path(path))
        if reply.get("ok") is True and str(reply.get("answer", "")).strip():
            ok += 1
        elif reply:
            failed += 1
    return ok, failed


def count_events(run_dir: Path) -> int:
    return len(glob.glob(str(run_dir / "meta/openhands/*/events/event-*.json")))


def human_age(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds / 60:.0f}m"
    return f"{seconds / 3600:.1f}h"


def collect_runs(experiment: Path) -> list[dict]:
    """One record per solver run, newest activity first."""
    pattern = str(experiment / "cpe_evaluations" / "*" / "*" / "runs" / "*" / "r1p*_*")
    runs = []
    for run_dir in sorted(glob.glob(pattern)):
        run_path = Path(run_dir)
        if not run_path.is_dir():
            continue
        metadata = read_json(run_path / "meta" / "run.json")
        parts = run_path.relative_to(experiment).parts
        # cpe_evaluations / round_N / <phase> / runs / round_N / <run>
        round_name = parts[1] if len(parts) > 1 else "?"
        phase = parts[2] if len(parts) > 2 else "?"
        report_path = run_path / "output" / "results" / "solution_report.md"
        report_ok = report_path.is_file() and bool(
            report_path.read_text(encoding="utf-8", errors="replace").strip()
        )
        draft_ok = (run_path / "output" / "results" / "draft.md").is_file()
        ok, failed = expert_exchange_state(run_path)
        events = count_events(run_path)
        # A run directory with no events never got an agent.  These appear when
        # a phase prepares a workspace that is then superseded -- nothing ran in
        # it, nothing will, and listing it as "solving" misreads the run.
        if events == 0:
            continue
        # The most recent write anywhere under the run is the best liveness signal.
        newest = run_path.stat().st_mtime
        for sub in ("meta/openhands", "output", "meta"):
            for path in (run_path / sub).rglob("*"):
                try:
                    newest = max(newest, path.stat().st_mtime)
                except OSError:
                    continue
        idle = time.time() - newest
        if report_ok and idle < REPORT_SETTLE_SECONDS:
            # Writing solution_report.md is step 4.1 of the prompt's workflow;
            # the agent then re-reads it for consistency and repairs what it
            # finds (4.2-4.3), which can run for tens of minutes.  Judging only
            # starts once that finishes, so a report on disk is not yet a
            # finished task -- showing it as one is what makes the run look
            # stuck between "report ready" and "judging".
            state, colour = "报告已出·自检中", YELLOW
        elif report_ok:
            state, colour = "完成", GREEN
        elif failed and not ok:
            state, colour = "expert FAILED", RED
        elif ok:
            state, colour = "expert ok", CYAN
        elif draft_ok:
            state, colour = "solving", YELLOW
        else:
            state, colour = "starting", DIM
        runs.append(
            {
                "problem": metadata.get("problem_id") or run_path.name.split("_")[0],
                "run": run_path.name,
                "round": round_name,
                "phase": phase,
                "report": report_ok,
                "expert_ok": ok,
                "expert_failed": failed,
                "events": events,
                "idle": idle,
                "settled": report_ok and idle >= REPORT_SETTLE_SECONDS,
                "state": state,
                "colour": colour,
            }
        )
    runs.sort(key=lambda item: item["idle"])
    return runs


def tail_line(experiment: Path) -> str:
    """Last non-empty line of the launcher log, for a sense of momentum."""
    log = REPO_ROOT / ".env_setup_logs" / f"{experiment.name}.log"
    if not log.is_file():
        return "(no log)"
    try:
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "(log unreadable)"
    skip = ("UserWarning", "warnings.warn", "site-packages", "Cost calculation")
    for line in reversed(lines):
        stripped = line.strip()
        if not stripped or any(token in stripped for token in skip):
            continue
        # The SDK's rich formatting wraps and pads lines; collapse the runs of
        # spaces that leaves behind so the text reads as one sentence.
        return re.sub(r"\s{2,}", " ", stripped)[:96]
    return "(log empty)"


def traceback_count(experiment: Path) -> int:
    log = REPO_ROOT / ".env_setup_logs" / f"{experiment.name}.log"
    if not log.is_file():
        return 0
    try:
        text = log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    return text.count("Traceback (most recent call last)")


def render(experiment: Path, started: float) -> str:
    width = min(shutil.get_terminal_size((110, 40)).columns, 130)
    inside = width - 4
    lines: list[str] = []

    def rule(char: str = "─") -> str:
        return "├" + char * (width - 2) + "┤"

    def row(text: str) -> str:
        return "│ " + pad(text, inside) + " │"

    pids = launcher_pids()
    solvers = solver_processes()
    alive = bool(pids)
    status = (
        f"{GREEN}● 运行中{RESET}" if alive else f"{RED}● 已退出{RESET}"
    )
    stamp = datetime.now().strftime("%H:%M:%S")
    lines.append("┌" + "─" * (width - 2) + "┐")
    lines.append(row(f"{BOLD}OpenHands 演化实验{RESET}  {status}   {DIM}{stamp}{RESET}"))
    lines.append(rule())
    runs = collect_runs(experiment)
    rounds = sorted({item["round"] for item in runs})
    lines.append(
        row(
            f"实验 {experiment.name}   轮次 {','.join(rounds) or '-'}   "
            f"launcher PID {pids[0] if pids else '-'}   并发 agent {solvers}"
        )
    )
    lines.append(rule())

    header = (
        pad("题目", 13)
        + pad("run", 23)
        + pad("相位", 25)
        + pad("报告", 6)
        + pad("专家桥", 9)
        + pad("事件", 7)
        + pad("静默", 7)
        + "状态"
    )
    lines.append(row(BOLD + header + RESET))
    if not runs:
        lines.append(row(f"{DIM}尚无 run 目录（实验可能还在初始化）{RESET}"))
    for item in runs[:14]:
        if item["expert_ok"]:
            expert = f"{GREEN}ok×{item['expert_ok']}{RESET}"
        elif item["expert_failed"]:
            expert = f"{RED}fail×{item['expert_failed']}{RESET}"
        else:
            expert = f"{DIM}-{RESET}"
        report = f"{GREEN}✓{RESET}" if item["report"] else f"{DIM}·{RESET}"
        lines.append(
            row(
                pad(item["problem"][:12], 13)
                + pad(item["run"][:22], 23)
                + pad((item["round"] + "/" + item["phase"])[:24], 25)
                + pad(report, 6)
                + pad(expert, 9)
                + pad(str(item["events"]), 7)
                + pad(human_age(item["idle"]), 7)
                + f"{item['colour']}{item['state']}{RESET}"
            )
        )

    lines.append(rule())
    total = len(runs)
    settled = sum(1 for item in runs if item["settled"])
    self_checking = sum(
        1 for item in runs if item["report"] and not item["settled"]
    )
    expert_ok = sum(1 for item in runs if item["expert_ok"])
    expert_bad = sum(1 for item in runs if item["expert_failed"] and not item["expert_ok"])
    errors = traceback_count(experiment)
    lines.append(
        row(
            f"汇总  {GREEN}完成 {settled}{RESET}   "
            f"{YELLOW}报告已出·自检中 {self_checking}{RESET}   "
            f"总计 {total}   "
            f"{GREEN}专家桥 ok {expert_ok}{RESET}   "
            f"{RED}专家桥失败 {expert_bad}{RESET}   "
            f"traceback {errors}"
        )
    )
    lines.append(row(f"{DIM}最新 {tail_line(experiment)}{RESET}"))
    lines.append("└" + "─" * (width - 2) + "┘")
    lines.append(f"{DIM}  每 5 秒刷新 · Ctrl-C 退出 · 数据直接读自实验目录{RESET}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", nargs="?", type=Path)
    parser.add_argument("-i", "--interval", type=float, default=5.0)
    args = parser.parse_args()

    experiment = args.experiment
    if experiment is None:
        experiment = newest_experiment()
        if experiment is None:
            print("没有找到实验目录，请显式传入路径。", file=sys.stderr)
            return 2
    experiment = experiment.resolve()
    if not experiment.is_dir():
        print(f"实验目录不存在: {experiment}", file=sys.stderr)
        return 2

    interactive = sys.stdout.isatty()
    try:
        while True:
            frame = render(experiment, time.time())
            if interactive:
                # Home the cursor and repaint, so the panel does not scroll away.
                sys.stdout.write("\033[H\033[J" + frame + "\n")
            else:
                sys.stdout.write(frame + "\n")
            sys.stdout.flush()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
