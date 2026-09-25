"""Run the from-scratch substantive workflow evolution with Codex CLI.

This is the non-coevolution Codex counterpart of the Claude from-scratch arm.
It reuses the exact workflow, prompt, CPE, expert, judge, and validation
pipeline, replacing only the solver backend and fixing reasoning to ``none``.
"""

from __future__ import annotations

try:
    from . import codex_backend
    from . import run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch
except ImportError:  # pragma: no cover
    import codex_backend
    import run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch


def main() -> None:
    scratch.base.claude_backend = codex_backend
    scratch.main()


if __name__ == "__main__":
    main()
