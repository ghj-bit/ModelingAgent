"""Run the from-scratch substantive workflow evolution on the OpenHands backend.

The OpenHands counterpart of the Claude from-scratch arm, and a copy of the
Codex one: the workflow, the seed, the prompt, the CPE gates, the expert, the
judge and the validation pipeline are the Claude arm's unchanged, and only the
solver backend is replaced.

Thinking is off.  That is not a flag this module sets -- it is what the backend
does: ``openhands_backend.run_openhands_task.reasoning_settings`` drops the
``--thinking`` value and pins the SDK options to ``reasoning_effort=None`` with
``chat_template_kwargs.enable_thinking=False``, because the locally served model
has no "off" reasoning level and the switch for it is the chat template's.
Passing ``--thinking off`` on the command line therefore records the intent in
the run metadata and changes nothing else.

The one seam is ``base.claude_backend``: the Claude arm's launcher holds the
backend module as an attribute and looks every backend call up through it, so
rebinding that attribute is the whole port.  ``openhands_backend`` carries a
``run_claude_modeling_phase`` alias for the same reason ``codex_backend`` does --
the shared launcher asks for the phase runner under that name.
"""

from __future__ import annotations

try:
    from . import openhands_backend
    from . import run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch
except ImportError:  # pragma: no cover - direct-file invocation support
    import openhands_backend
    import run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch


def main() -> None:
    scratch.base.claude_backend = openhands_backend

    print(
        "OpenHands from-scratch arm: the same pipeline as the Claude arm, with "
        "every Solver run as an OpenHands conversation (thinking off in the "
        "backend, not on the command line).",
        flush=True,
    )
    scratch.main()


if __name__ == "__main__":
    main()
