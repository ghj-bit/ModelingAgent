#!/usr/bin/env python3
"""Run one isolated Codex CLI solver session at the server's lowest effort."""

from __future__ import annotations

import argparse
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


MAX_REPETITIONS = 4
PROXY_SCRIPT = Path(__file__).resolve().parent / "proxy.py"
# The shim binds a local port and answers immediately, so this only has to cover
# interpreter start-up.
SHIM_START_TIMEOUT = 30.0


def pin_to_cpu_lane(workspace: Path, announce=print) -> list[int] | None:
    """Confine this Codex session and its children to a stable CPU lane."""
    requested = os.environ.get("CODEX_AGENT_CPUS", "").strip()
    try:
        cpus = int(requested) if requested else 0
    except ValueError:
        announce(f"[codex] CODEX_AGENT_CPUS={requested!r} is not a number; not pinning")
        return None
    if cpus <= 0:
        return None
    try:
        available = sorted(os.sched_getaffinity(0))
    except (AttributeError, OSError) as error:
        announce(f"[codex] cannot read the CPU mask ({error}); not pinning")
        return None
    lanes = max(1, len(available) // cpus)
    match = re.search(r"r(\d+)p(\d+)_", str(workspace))
    if match:
        repetition, problem = int(match.group(1)), int(match.group(2))
        lane = ((problem - 1) * MAX_REPETITIONS + (repetition - 1)) % lanes
    else:
        lane = hash(str(workspace)) % lanes
    selected = [available[(lane * cpus + offset) % len(available)] for offset in range(cpus)]
    try:
        os.sched_setaffinity(0, set(selected))
    except (AttributeError, OSError) as error:
        announce(f"[codex] cannot pin to CPUs {selected} ({error}); running unpinned")
        return None
    announce(f"[codex] pinned to {cpus} CPUs {selected[0]}-{selected[-1]} (lane {lane}/{lanes})")
    return selected


def free_port() -> int:
    """Reserve a port by binding it, then release it for the shim to claim."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def start_shim(base_url: str, api_key: str, log_path: Path) -> tuple[subprocess.Popen, int]:
    """Start the role-rewriting shim and wait until it answers.

    Codex labels its own standing instructions with role "developer", which the
    served vLLM answers with a 400, so it cannot talk to the endpoint directly;
    see ``proxy.py`` for what the shim does and why that is the whole of it.
    """
    port = free_port()
    # The caller wipes persistence_dir just before this, and write_config is
    # what normally recreates it -- which happens after the shim is already
    # running, so the parent has to be made here.
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            sys.executable,
            str(PROXY_SCRIPT),
            "--upstream",
            base_url,
            "--port",
            str(port),
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
                pass
        except urllib.error.HTTPError:
            # Any HTTP answer at all means it is listening.
            pass
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
            continue
        print(f"[codex] shim ready on 127.0.0.1:{port} -> {base_url}", flush=True)
        return process, port
    process.kill()
    raise RuntimeError(f"shim did not start within {SHIM_START_TIMEOUT:.0f}s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--persistence-dir", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key", default="EMPTY")
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--timeout", type=float, default=7200.0)
    # The served model rejects "none" outright ("Supported types are xhigh
    # (default), medium, and low"), so "low" is the closest the server allows
    # to reasoning-off, and the only value in the accepted set that keeps the
    # per-turn budget small.
    parser.add_argument("--reasoning-effort", default="low")
    return parser.parse_args()


def write_config(path: Path, model: str, base_url: str, reasoning_effort: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "config.toml").write_text(
        "\n".join(
            [
                f'model = "{model}"',
                'model_provider = "local"',
                f'model_reasoning_effort = "{reasoning_effort}"',
                'model_verbosity = "low"',
                "disable_response_storage = true",
                "network_access = \"enabled\"",
                "",
                "[features]",
                "fast_mode = true",
                "enable_request_compression = true",
                "apps = false",
                "browser_use = false",
                "browser_use_external = false",
                "multi_agent = false",
                "memories = false",
                "plugins = false",
                "skill_search = false",
                "view_image = false",
                "",
                "[model_providers.local]",
                'name = "local"',
                f'base_url = "{base_url}"',
                'wire_api = "responses"',
                'env_key = "OPENAI_API_KEY"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    pin_to_cpu_lane(args.workspace, announce=lambda line: print(line, flush=True))
    prompt = args.prompt_file.read_text(encoding="utf-8")
    if not prompt.strip():
        raise SystemExit("prompt file is empty")
    args.workspace.mkdir(parents=True, exist_ok=True)
    if args.persistence_dir.exists():
        shutil.rmtree(args.persistence_dir, ignore_errors=True)
    # Codex labels its standing instructions with role "developer", which this
    # deployment's vLLM rejects with a 400 before any work is done, so the CLI
    # is pointed at the local shim and never at the endpoint itself.
    shim, port = start_shim(
        args.base_url, args.api_key, args.persistence_dir / "shim.log"
    )
    try:
        return launch_codex(args, prompt, f"http://127.0.0.1:{port}/v1")
    finally:
        shim.terminate()
        try:
            shim.wait(timeout=15)
        except subprocess.TimeoutExpired:
            shim.kill()


def launch_codex(args: argparse.Namespace, prompt: str, base_url: str) -> int:
    """Write the isolated config and run one Codex session against the shim."""
    write_config(args.persistence_dir, args.model, base_url, args.reasoning_effort)

    env = dict(os.environ)
    env["CODEX_HOME"] = str(args.persistence_dir)
    env["OPENAI_API_KEY"] = args.api_key
    env["CODEX_REASONING_EFFORT"] = args.reasoning_effort
    command = [
        args.codex_bin,
        "--model",
        args.model,
        "--sandbox",
        "workspace-write",
        "--ask-for-approval",
        "never",
        "--no-daemon",
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "-",
    ]
    if env.get("CODEX_JSON_LOG") == "1":
        command.insert(-1, "--json")
    print(
        f"[codex] reasoning_effort={args.reasoning_effort} verbosity=low "
        "fast_mode=true request_compression=true daemon=off json_log="
        f"{env.get('CODEX_JSON_LOG', '0')}",
        flush=True,
    )
    print(f"[codex] cwd={args.workspace}", flush=True)
    print(f"[codex] {' '.join(command[:-1])} -", flush=True)
    process = subprocess.Popen(
        command,
        cwd=str(args.workspace),
        env=env,
        stdin=subprocess.PIPE,
        stdout=None,
        stderr=None,
        text=True,
        start_new_session=True,
    )
    try:
        process.stdin.write(prompt)
        process.stdin.close()
    except BrokenPipeError:
        pass
    try:
        return process.wait(timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"[codex] timed out after {args.timeout:.0f}s; terminating", flush=True)
        process.terminate()
        try:
            return process.wait(timeout=60)
        except subprocess.TimeoutExpired:
            process.kill()
            return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
