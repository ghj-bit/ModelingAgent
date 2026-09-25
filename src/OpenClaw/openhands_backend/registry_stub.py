#!/usr/bin/env python3
"""Stand-in for the OpenClaw CLI, used by the OpenHands solver backend.

The evolution framework registers every solver agent through the OpenClaw CLI
before running it, and unregisters temporary agents afterwards:

    agents add <id> --workspace ... --model ... --non-interactive --json
    gateway call agents.delete --params ... --timeout 120000 --json
    agents list --json

OpenHands has no agent registry -- one run is one standalone conversation -- so
the OpenHands launcher points the framework's existing ``--openclaw-command``
option at this script instead of reimplementing those three call sites.  The
surrounding control flow (the registration lock, failure cleanup, and the
pipelined register-then-run workers) then behaves exactly as it does with the
real CLI.

Protocol notes, read off the call sites in ``run_interaction_rubric_evolution.py``:

* ``agents add`` (line 1234) and ``gateway call agents.delete`` (line 1289) go
  through ``baseline.run_checked``, which only checks the exit status.
* ``agents list --json`` (line 1327) is parsed: the caller requires stdout to
  match ``(?ms)^\\[\\s*\\{.*\\]\\s*$`` and then ``json.loads`` it into a list.
  An empty ``[]`` does *not* match that pattern, so an empty object is emitted
  inside the array; the consumer only ever calls ``agent.get(...)`` on each
  entry, so a blank object yields no cleanup candidates.
"""

from __future__ import annotations

import sys


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) >= 2 and argv[0] == "agents" and argv[1] == "list":
        # Matches the framework's JSON-array pattern while reporting no agents.
        print("[\n{}\n]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
