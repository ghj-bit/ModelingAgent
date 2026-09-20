"""Export the frozen initial interaction policy to Markdown.

`src/OpenClaw/interaction_policy.py` is the source of truth: the evolution
launcher and the workflow-test runner both import it so their copies cannot
drift.  This script renders that same string to a readable file for review and
sharing, and is meant to be re-run whenever the module changes.

    python scripts/export_initial_interaction_policy.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.OpenClaw.interaction_policy import MODELING_STRATEGY_ESCALATION  # noqa: E402

OUT = REPO / "src" / "OpenClaw" / "prompts" / "initial_interaction_policy.md"

HEADER = """\
<!--
Generated from `src/OpenClaw/interaction_policy.py::MODELING_STRATEGY_ESCALATION`.

That module is the source of truth: the initial-draft evolution launcher and the
workflow-test runner both import it, so their copies cannot drift.  Do not edit
this file by hand — change the module and re-run:

    python scripts/export_initial_interaction_policy.py
-->

*Frozen initial interaction policy — {length:,} characters.*

"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    body = HEADER.format(length=len(MODELING_STRATEGY_ESCALATION))
    OUT.write_text(body + MODELING_STRATEGY_ESCALATION + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"policy length: {len(MODELING_STRATEGY_ESCALATION):,} characters")


if __name__ == "__main__":
    main()
