#!/usr/bin/env python3
"""Run one Claude Code session as the solver for a single evolution task.

Invoked by ``claude_backend.run_claude_modeling_phase`` through
``baseline.stream_command``, so everything printed here lands in the run's
``meta/solve.log`` and the process exit status is what the framework reads.

The task text is the rendered ``prompt.md`` the framework already produces; the
workspace is the task's ``output/`` directory.

Three things make this more than a ``claude -p`` call:

* Claude Code speaks the Anthropic Messages API and the local vLLM endpoint
  cannot serve that shape for this workload (the served template always emits a
  reasoning block, and the Anthropic request model has no field to stop it).  So
  this driver starts ``proxy.py`` on a free port and points Claude Code at it.
  One shim per task keeps concurrent solvers from contending for a shared port.

* Claude Code searches upward from its working directory for ``CLAUDE.md`` and
  reads the operator's own config directory.  Both would leak unrelated
  instructions into the solver's context, so the session gets a throwaway
  ``CLAUDE_CONFIG_DIR`` under the run's meta directory and no inherited memory.

* Headless runs cannot answer permission prompts.  Rather than bypassing
  approvals wholesale, the grant is an explicit allow-list of the tools the
  prompt's workflow actually needs, written into that isolated config.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROXY_SCRIPT = BACKEND_DIR / "proxy.py"

DEFAULT_CLAUDE_BIN = "/public1/home/stu52275901007/.local/bin/claude"

# The prompt's workflow needs file editing, shell execution, and the search and
# fetch tools it uses to gather data.  Spelled out rather than implied, so the
# width of the grant is visible in the run's config.
DEFAULT_ALLOWED_TOOLS = "Bash,Read,Write,Edit,MultiEdit,Glob,Grep,LS,WebFetch,WebSearch,NotebookEdit,TodoWrite"

# Seconds to wait for the shim to start answering before giving up on it.
SHIM_START_TIMEOUT = 30.0

# Repetitions per problem that the CPU lane below strides by.  Only affects which
# lane a run lands in, never how many CPUs it gets: two runs that collide merely
# share a window instead of each getting their own.  Interleaving by repetition
# (rather than by problem) keeps a phase's runs in distinct lanes whenever there
# are enough of them, and degrades to grouping by repetition on a small machine
# instead of collapsing every repetition onto one lane.
MAX_REPETITIONS = 4


def pin_to_cpu_lane(workspace: Path, announce=print) -> list[int] | None:
    """Confine this session, and everything it spawns, to a slice of the CPUs.

    ``CLAUDE_AGENT_CPUS`` names the size of the slice; unset or 0 leaves the
    session unpinned, which is what every arm but the CPU-capped one wants.  The
    pin is set on this process, and children inherit the mask -- that is the
    whole point: an agent's own numpy/sklearn/multiprocessing code cannot escape
    it, whereas thread-count variables only reach the libraries that read them.

    Lanes are picked from the run's name (``r<rep>p<problem>_<timestamp>``) so
    concurrent runs of one phase land in disjoint windows rather than stacking on
    the first four CPUs, and the mask is taken from the CPUs this process is
    already allowed to run on, so a job inside a Slurm allocation stays inside it.
    """
    requested = os.environ.get("CLAUDE_AGENT_CPUS", "").strip()
    try:
        cpus = int(requested) if requested else 0
    except ValueError:
        announce(f"[claude] CLAUDE_AGENT_CPUS={requested!r} is not a number; not pinning")
        return None
    if cpus <= 0:
        return None
    try:
        available = sorted(os.sched_getaffinity(0))
    except (AttributeError, OSError) as error:
        announce(f"[claude] cannot read the CPU mask ({error}); not pinning")
        return None
    lanes = max(1, len(available) // cpus)
    match = re.search(r"r(\d+)p(\d+)_", str(workspace))
    if match:
        repetition, problem = int(match.group(1)), int(match.group(2))
        lane = ((problem - 1) * MAX_REPETITIONS + (repetition - 1)) % lanes
    else:
        # No run name to stride by: spread by a stable hash of the path, so two
        # unnamed sessions do not stack either.
        lane = hash(str(workspace)) % lanes
    selected = [available[(lane * cpus + offset) % len(available)] for offset in range(cpus)]
    try:
        os.sched_setaffinity(0, set(selected))
    except (AttributeError, OSError) as error:
        announce(f"[claude] cannot pin to CPUs {selected} ({error}); running unpinned")
        return None
    announce(
        f"[claude] pinned to {cpus} CPUs {selected[0]}-{selected[-1]} "
        f"(lane {lane}/{lanes})"
    )
    return selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--persistence-dir", type=Path, required=True)
    # What Claude Code calls the model.  The shim rewrites it to the name the
    # server actually serves, so this only has to be a stable label.
    parser.add_argument("--model", required=True)
    # The OpenAI-compatible endpoint the shim translates for.
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key", default="EMPTY")
    parser.add_argument("--upstream-model", default="qwen3.8-27b")
    parser.add_argument("--claude-bin", default=DEFAULT_CLAUDE_BIN)
    parser.add_argument("--timeout", type=float, default=7200.0)
    parser.add_argument("--permission-mode", default="acceptEdits")
    parser.add_argument("--allowed-tools", default=DEFAULT_ALLOWED_TOOLS)
    # Claude Code's own agentic loop bound; the wall-clock --timeout below is
    # the outer guard.
    parser.add_argument("--max-turns", type=int, default=0)
    parser.add_argument("--output-format", default="stream-json")
    # "100k", not the model's real 131072 -- the CLI accepts nothing below 100k
    # (80000 and 99k are both rejected outright, which kills the session at
    # startup), so this is the earliest compaction the flag can ask for.
    #
    # It is still not early enough to be relied on.  Claude Code asks for 32k
    # output tokens every turn, so the prompt ceiling is window - 32k = 99072,
    # and 100k sits above that: a session that reaches the ceiling gets every
    # later turn refused before compaction ever fires, which is how a deep run
    # (73+ turns) dies with its context stuck at ~100k.  The real mitigation is
    # the shim's retry with a halved output budget (see proxy.shrink_to_fit).
    # "auto" leaves the CLI's own default in place.
    # 180k, raised from 100k on 2026-09-27.  The trigger is derived, not the raw
    # value: compaction fires at window - 33000 (20000 output budget + 13000
    # slack), so 180k here means a 147k trigger, and the CLI caps the model at a
    # 200k window, making 167k the highest trigger reachable at all.
    #
    # Why raise it: a compaction costs 2.6-5.4 minutes, and the cost is the
    # summary it *generates* (10-20k tokens at ~40 tok/s), not the context it
    # reads.  Measured on claude_fp8_r15b round 1 (11 compactions over 4 runs),
    # the runs kept working for 30-85 turns after 7 of them, but the last
    # compaction of a run left only 2-15 turns -- one spent 167s to summarise a
    # context it barely used again.  Break-even is 200s / 40 remaining turns =
    # 5s of extra latency per turn, against whole turns that take 5-10s total
    # here, so the longer context would have to double every remaining turn to
    # pay for the summary.  Prefill is 0.9s of a 22.9s call, the prefix cache
    # hits 95%, and 48 of this model's 64 layers are linear attention, so it is
    # not expected to.
    parser.add_argument("--autocompact", default="180k")
    parser.add_argument("--thinking", default="off")
    return parser.parse_args()


def free_port() -> int:
    """Reserve a port by binding it, then releasing it for the shim to claim."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def start_shim(
    base_url: str, model: str, api_key: str, log_path: Path
) -> tuple[subprocess.Popen, int]:
    """Start the translation shim and wait until it answers.

    ``api_key`` is what the shim presents to the upstream; the client's own token
    is separate (see session_environment) and the shim ignores it, because the
    two differ once the upstream is not the keyless local server.
    """
    port = free_port()
    log = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            sys.executable,
            str(PROXY_SCRIPT),
            "--upstream",
            base_url,
            "--port",
            str(port),
            "--model",
            model,
            "--api-key",
            api_key,
        ],
        stdout=log,
        stderr=log,
        start_new_session=True,
    )
    deadline = time.time() + SHIM_START_TIMEOUT
    url = f"http://127.0.0.1:{port}/v1/models"
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"shim exited during startup with code {process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=5):
                print(f"[claude] shim ready on 127.0.0.1:{port} -> {base_url}", flush=True)
                return process, port
        except urllib.error.HTTPError:
            # Any HTTP answer at all means it is listening.
            print(f"[claude] shim ready on 127.0.0.1:{port} -> {base_url}", flush=True)
            return process, port
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    process.kill()
    raise RuntimeError(f"shim did not start within {SHIM_START_TIMEOUT:.0f}s")


# Appended to Claude Code's own system prompt -- via --append-system-prompt, so
# it lands in the system array next to the instruction it is fighting, not in
# the task prompt where a rule has to out-shout it from a lower layer.
#
# It targets the edit-run loop: the solver makes two or three small edits, runs
# the script, reads the failure, makes two or three more, runs again.  That is
# ordinary development, but here every turn is a round trip to the model and
# the round trip, not the edit, is what costs -- measured on one 2017_A run:
# 50 Edits and 51 Bash runs against a single file, 123 turns, ~10s of fixed
# overhead per turn.  A previous wording of this rule ("Batch your work: make
# every change to one region ...") sat in the task prompt and did nothing,
# because it named a principle rather than the act to stop.
BATCHING_SYSTEM_PROMPT = (
    "When a script fails, fix every error it revealed in one pass, then run it "
    "once more — do not fix one error, run, fix the next error, run. Batch the "
    "changes you already know a file needs before running it again. One run in "
    "this experiment edited the same file 52 times across 51 script runs, and "
    "each of those round trips cost more than the edit it carried."
)


def session_environment(config_dir: Path, port: int, model: str, api_key: str,
                        allowed_tools: str, permission_mode: str) -> tuple[dict, Path]:
    """Build the isolated environment and settings file for one session."""
    config_dir.mkdir(parents=True, exist_ok=True)
    settings_path = config_dir / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "permissions": {
                    # The prompt's workflow runs shell commands and edits files
                    # with nobody to approve them, so the grant is enumerated
                    # here instead of requested interactively.
                    "allow": [item for item in allowed_tools.split(",") if item],
                    # The agent wraps a slow command in `timeout NNN` so it fails
                    # cleanly rather than being killed, and picks that NNN from
                    # the tool's ceiling rather than from the work.  When the
                    # number is too small the command is cut off with nothing to
                    # show and has to be repeated from the start.  Measured on
                    # 2020_D: the solver's own pipeline needs ~5 minutes, was
                    # wrapped in `timeout 570`, and the run was lost.  The
                    # tool's limit is where that bound belongs, so the wrapper
                    # is denied outright.
                    "deny": ["Bash(timeout *)"],
                },
                "enableAllProjectMcpServers": False,
                # Stop the solver narrating between tool calls.  That habit is
                # not the solver's invention: the default system prompt asks for
                # it ("Before your first tool call, state in one sentence what
                # you're about to do ... Brief is good -- silent is not."), so a
                # rule in the task prompt only overrode it partially -- measured
                # 22% fewer such turns, ~19 per validation problem still.  The
                # built-in Concise style injects its prompt into the same
                # system array and carries an explicit "these rules win" over
                # other communication guidance, and unlike a custom style it
                # keeps the coding instructions (keep-coding-instructions).
                # Measured baseline it has to beat: 83 such turns per round-0
                # validation phase (4 problems).
                "outputStyle": "Concise",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    env = dict(os.environ)
    # Point the session at the local shim rather than api.anthropic.com.
    env["ANTHROPIC_BASE_URL"] = f"http://127.0.0.1:{port}"
    env["ANTHROPIC_AUTH_TOKEN"] = api_key
    env["ANTHROPIC_API_KEY"] = api_key
    env["ANTHROPIC_MODEL"] = model
    # Claude Code uses a smaller model for background work (title generation,
    # summarisation); point it at the same local model so nothing reaches out.
    env["ANTHROPIC_SMALL_FAST_MODEL"] = model
    env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = model
    # A throwaway config directory: without it the session would read the
    # operator's own ~/.claude (memory files, MCP servers, credentials), and
    # would search upward from the workspace for a CLAUDE.md that belongs to
    # the surrounding repository rather than to this task.
    env["CLAUDE_CONFIG_DIR"] = str(config_dir)
    # Claude Code's per-turn output request sets the prompt ceiling: the server
    # refuses anything where prompt + requested output exceeds its window, so
    # asking for 32k caps the prompt at 99072.  That is BELOW the smallest
    # auto-compact window the CLI accepts (100k, and it rejects anything lower),
    # so compaction could never fire before the session died -- which is how a
    # deep run ends at 63+ turns with the whole turn refused.  Keeping the
    # request under 28672 puts the ceiling above 102400 and lets compaction run.
    env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = os.environ.get(
        "CLAUDE_CODE_MAX_OUTPUT_TOKENS", "20000"
    )
    # ...and the window that ceiling was computed against has to be the one the
    # command line asks for.  Claude Code resolves the auto-compact window in
    # this order (cli.js: `function ok(e,n)`): CLAUDE_CODE_AUTO_COMPACT_WINDOW
    # first and it RETURNS on a hit, then --autocompact, then clientdata,
    # experiment, model default.  So an inherited env var silently voids the
    # --autocompact passed on the command line, and the CLI's own UI says as
    # much: "CLAUDE_CODE_AUTO_COMPACT_WINDOW is set and takes precedence."
    #
    # It is not hypothetical.  A Claude Code session injects this variable into
    # its own process, and `dict(os.environ)` above passes it straight through,
    # so every solver launched from one inherited it.  Measured on
    # claude_r0_val4x3 (2026-09-25): the value in force was 786432, which beat
    # the --autocompact 100k on the command line; the window became
    # min(model 200000, 786432) = 200000 and the threshold window-33000 = 167000,
    # so none of the 12 runs compacted -- their peak contexts were 48806..125519.
    # With the variable gone the window is min(200000, 100000) = 100000 and the
    # threshold 67000, which 11 of those 12 runs would have crossed.
    #
    # The threshold is derived, never the raw window: Claude Code reserves the
    # output budget (20000, capped at the model's own limit) and then a further
    # 13000 of hardcoded slack, so compaction fires at window - 33000.
    env.pop("CLAUDE_CODE_AUTO_COMPACT_WINDOW", None)
    # A modelling pipeline is legitimately slow: on 2020_D the solver's own
    # full run needs about five minutes, mostly null-model graph rebuilds.  The
    # CLI's stock ceiling of 600s is close enough to that for the agent to wrap
    # each run in its own `timeout 570` -- and a run cut off at 570s is work
    # thrown away, which it then repeats.  Raising the ceiling lets it ask for
    # the time the command actually needs instead of a number chosen to fail
    # cleanly.  Measured on this cluster: `timeout 5xx` appeared 32 times in one
    # evolution run and 16 in a single-problem run.
    # The default has to match the maximum, because the agent almost never sets
    # an explicit timeout -- measured: 49 of 50 Bash calls left it unset and took
    # the default, counting on it as their budget when polling with
    # `sleep N && tail progress.log`.  A 5-minute default therefore became the
    # real ceiling and killed a `sleep 420` poll at 300s.  These polls end on
    # their own, so the long default costs nothing.
    env["BASH_DEFAULT_TIMEOUT_MS"] = os.environ.get(
        "BASH_DEFAULT_TIMEOUT_MS", "1800000"
    )
    env["BASH_MAX_TIMEOUT_MS"] = os.environ.get("BASH_MAX_TIMEOUT_MS", "1800000")
    # This cluster has no route to GitHub or npm; leaving the updater and the
    # telemetry on would only add stalls to every run.
    env["DISABLE_AUTOUPDATER"] = "1"
    env["DISABLE_TELEMETRY"] = "1"
    env["DISABLE_ERROR_REPORTING"] = "1"
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
    return env, settings_path


def main() -> int:
    args = parse_args()
    args.persistence_dir.mkdir(parents=True, exist_ok=True)
    workspace = args.workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    prompt = args.prompt_file.read_text(encoding="utf-8")
    if not prompt.strip():
        print(f"[claude] prompt file is empty: {args.prompt_file}", file=sys.stderr, flush=True)
        return 1

    config_dir = args.persistence_dir / "claude_config"
    if config_dir.exists():
        shutil.rmtree(config_dir, ignore_errors=True)

    # Before anything is spawned, so the shim, the CLI and every shell the agent
    # runs inherit the same CPU window.
    pin_to_cpu_lane(workspace, announce=lambda line: print(line, flush=True))

    shim, port = start_shim(
        args.base_url, args.upstream_model, args.api_key, args.persistence_dir / "shim.log"
    )
    try:
        env, settings_path = session_environment(
            config_dir, port, args.model, args.api_key, args.allowed_tools,
            args.permission_mode,
        )
        command = [
            args.claude_bin,
            "--print",
            "--settings",
            str(settings_path),
            "--permission-mode",
            args.permission_mode,
            "--output-format",
            args.output_format,
        ]
        if args.output_format == "stream-json":
            # Required by the CLI when streaming JSON outside of --print piping.
            command.append("--verbose")
        if args.max_turns:
            command.extend(["--max-turns", str(args.max_turns)])
        if args.autocompact and args.autocompact != "auto":
            command.extend(["--autocompact", str(args.autocompact)])
        command.extend(["--append-system-prompt", BATCHING_SYSTEM_PROMPT])

        print(f"[claude] cwd={workspace}", flush=True)
        print(f"[claude] {' '.join(command)}", flush=True)
        print(f"[claude] prompt={len(prompt)} chars", flush=True)

        process = subprocess.Popen(
            command,
            cwd=str(workspace),
            env=env,
            stdin=subprocess.PIPE,
            stdout=None,  # inherit: baseline.stream_command captures it
            stderr=None,
            text=True,
            start_new_session=True,
        )
        try:
            # The prompt goes over stdin rather than argv: prompt.md is large
            # and carries model output, so it is safer not to push it through
            # the argument vector.
            process.stdin.write(prompt)
            process.stdin.close()
        except BrokenPipeError:
            pass  # the CLI exited before reading; the wait below reports why

        try:
            returncode = process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            # process.wait closes stdin itself, which is already closed.
            print(f"[claude] timed out after {args.timeout:.0f}s; terminating", flush=True)
            process.terminate()
            try:
                returncode = process.wait(timeout=60)
            except subprocess.TimeoutExpired:
                process.kill()
                returncode = process.wait()
            return 1
        print(f"[claude] session exited with code {returncode}", flush=True)
        return returncode
    finally:
        shim.terminate()
        try:
            shim.wait(timeout=15)
        except subprocess.TimeoutExpired:
            shim.kill()


if __name__ == "__main__":
    raise SystemExit(main())
