"""The OpenHands from-scratch arm is a backend swap, and the swap has one hazard.

The arm reuses the Claude from-scratch launcher whole and rebinds
``base.claude_backend``.  That works only because the OpenHands backend answers
to the name the shared launcher asks for -- ``run_claude_modeling_phase`` -- and
that alias is the one thing here that fails *late*: without it the port imports
fine, stages fine, and dies at the first modelling phase with an
AttributeError, one round into an experiment.

The Codex arm carries the same alias for the same reason, so what is asserted
here is that the OpenHands backend keeps carrying it.
"""

import inspect
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import openhands_backend
from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch,
)
from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_from_scratch_openhands as arm,
)


class OpenHandsBackendAliasTests(unittest.TestCase):
    def test_the_phase_runner_answers_to_the_claude_launchers_name(self):
        self.assertIs(
            openhands_backend.run_claude_modeling_phase,
            openhands_backend.run_openhands_modeling_phase,
        )
        # Exported, so a consumer that reads the backend's public surface sees
        # it rather than having to know the private convention.
        self.assertIn("run_claude_modeling_phase", openhands_backend.__all__)

    def test_the_backend_is_otherwise_interface_compatible(self):
        # Everything the shared launcher resolves through the attribute it holds.
        for name in (
            "DEFAULT_MODEL",
            "DEFAULT_BASE_URL",
            "DEFAULT_API_KEY",
            "default_settings",
            "REGISTRY_STUB",
            "run_claude_modeling_phase",
        ):
            with self.subTest(name=name):
                self.assertTrue(hasattr(openhands_backend, name))


class OpenHandsArmWiringTests(unittest.TestCase):
    def test_main_swaps_the_backend_before_delegating(self):
        source = inspect.getsource(arm.main)
        self.assertIn("scratch.base.claude_backend = openhands_backend", source)
        self.assertLess(
            source.index("scratch.base.claude_backend = openhands_backend"),
            source.index("scratch.main()"),
        )

    def test_the_shared_launcher_holds_the_backend_as_a_module_attribute(self):
        # The swap is a rebind only if the launcher looks the backend up through
        # the module object at call time; a launcher that imported the functions
        # directly would ignore the rebind and the arm would silently run Claude.
        self.assertTrue(hasattr(scratch.base, "claude_backend"))
        source = inspect.getsource(scratch.base)
        self.assertIn("claude_backend.run_claude_modeling_phase", source)


if __name__ == "__main__":
    unittest.main()
