"""The solver session's CPU budget.

Agents write their own numpy/sklearn/multiprocessing code, and nothing in those
libraries stops a script from taking every core on the machine: a single run was
measured at 127 threads holding 59 of 104 cores, which starved the rest of its
phase.  ``pin_to_cpu_lane`` is the cap -- an affinity mask set on the session
before anything is spawned, so the CLI and every shell it runs inherit it.

The affinity calls are faked here rather than exercised for real: the assertions
are about which CPUs the function *chooses*, and a test that pinned itself would
slow the whole suite down and behave differently on a small machine.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw.claude_backend import run_claude_task as driver


def workspace(name: str) -> Path:
    """A run directory as the backend receives it, seen through its output dir."""
    return Path("/tmp/exp/cpe_evaluations/round_0/phase/runs/round_0") / name / "output"


class CpuLaneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.calls: list[set[int]] = []
        self.available = set(range(8))
        self.messages: list[str] = []
        self.patches = [
            mock.patch.object(driver.os, "sched_getaffinity", lambda pid: set(self.available)),
            mock.patch.object(
                driver.os, "sched_setaffinity", lambda pid, mask: self.calls.append(set(mask))
            ),
        ]
        for patch in self.patches:
            patch.start()
            self.addCleanup(patch.stop)

    def pin(self, cpus: str | None, name: str = "r1p1_20260925_003243"):
        environment = {"CLAUDE_AGENT_CPUS": cpus} if cpus is not None else {}
        with mock.patch.dict(os.environ, environment):
            if cpus is None:
                # The suite may itself run under a budget; unset is the case here.
                os.environ.pop("CLAUDE_AGENT_CPUS", None)
            return driver.pin_to_cpu_lane(workspace(name), announce=self.messages.append)

    def test_unset_leaves_the_session_unpinned(self):
        self.assertIsNone(self.pin(None))
        self.assertEqual(self.calls, [])

    def test_zero_disables_the_pin(self):
        self.assertIsNone(self.pin("0"))
        self.assertEqual(self.calls, [])

    def test_pins_to_the_requested_number_of_cpus(self):
        selected = self.pin("2")
        self.assertEqual(len(selected), 2)
        self.assertEqual(self.calls, [{0, 1}])

    def test_every_run_of_a_phase_gets_its_own_window(self):
        """The real phase: 4 problems x 4 repetitions, each on its own CPUs."""
        self.available = set(range(32))  # sixteen two-CPU lanes
        windows = {
            (rep, problem): tuple(self.pin("2", f"r{rep}p{problem}_20260925_003243"))
            for rep in range(1, 5)
            for problem in range(1, 5)
        }
        self.assertEqual(len(set(windows.values())), 16)

    def test_repetitions_land_in_different_windows(self):
        self.available = set(range(32))
        self.assertNotEqual(self.pin("2", "r1p1_20260925_003243"),
                            self.pin("2", "r2p1_20260925_003243"))

    def test_a_small_machine_groups_by_repetition_instead_of_collapsing(self):
        """Eight CPUs leave four lanes for sixteen runs: they must share.

        Sharing is the documented degradation -- the cap still holds, the runs
        are just slower -- and grouping by repetition is what keeps every
        repetition's four problems from piling onto one lane.
        """
        windows = [self.pin("2", f"r1p{problem}_20260925_003243") for problem in range(1, 5)]
        self.assertEqual(len({tuple(window) for window in windows}), 1)
        self.assertTrue(all(set(window) <= self.available for window in windows))

    def test_the_pin_stays_inside_the_cpus_already_available(self):
        """A Slurm allocation restricts the mask; the lane must not escape it."""
        self.available = {10, 11, 12, 13}
        selected = self.pin("2")
        self.assertEqual(set(selected), {10, 11})
        self.assertTrue(set(selected) <= self.available)

    def test_an_unnamed_workspace_is_still_pinned(self):
        selected = self.pin("2", "somewhere/else/output")
        self.assertEqual(len(selected), 2)

    def test_a_non_numeric_budget_is_reported_and_ignored(self):
        self.assertIsNone(self.pin("plenty"))
        self.assertEqual(self.calls, [])
        self.assertTrue(any("not a number" in message for message in self.messages))

    def test_a_cpu_budget_larger_than_the_machine_caps_at_one_lane(self):
        selected = self.pin("64")
        self.assertEqual(len(selected), 64)
        self.assertTrue(set(selected) <= self.available)


if __name__ == "__main__":
    unittest.main()
