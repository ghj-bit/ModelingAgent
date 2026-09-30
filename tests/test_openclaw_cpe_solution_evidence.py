"""The submitted solution reaches the optimizer's evidence only when asked for.

Two things have to hold, and neither is visible from a run's own files.  The
field must be absent unless an arm opts in -- every arm already collected under
the original evidence shape has to stay comparable, and the flag is module state
that a launcher must restore.  And the submission must arrive as the four fields
the Judge scores rather than as the whole container: ``solution.json`` is ~20 KB
per run, and a policy patch can be argued against the prose the Judge read but
not against five tasks of raw JSON.

``solution.json`` is the solver's own submission, so exposing it cannot leak the
Judge's verdict; the held-out split is a separate concern -- the validation
champion travels as policy text plus a net utility and carries no runs.
"""

import json
import pathlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import run_substantive_interaction_workflow_evolution as engine
from src.OpenClaw import (
    run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base,
)


LAUNCHER = (
    REPO_ROOT
    / "src"
    / "OpenClaw"
    / "run_substantive_interaction_workflow_evolution_from_initial_draft_claude.py"
)
FROM_SCRATCH = (
    REPO_ROOT
    / "src"
    / "OpenClaw"
    / "run_substantive_interaction_workflow_evolution_from_scratch_claude.py"
)
COEVOLUTION = (
    REPO_ROOT
    / "src"
    / "OpenClaw"
    / "run_substantive_interaction_workflow_evolution_from_initial_draft_claude_critic.py"
)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def submission(tasks: int = 5, filler: int = 0) -> dict:
    """An MM-Bench-shaped submission: five tasks, each with four scored fields."""
    return {
        "tasks": [
            {
                "task_description": f"task {index} description " + "d" * filler,
                "task_analysis": f"task {index} analysis " + "a" * filler,
                "mathematical_modeling_process": f"task {index} model " + "m" * filler,
                "subtask_outcome_analysis": f"task {index} outcome " + "o" * filler,
            }
            for index in range(1, tasks + 1)
        ]
    }


class SubmittedSolutionTests(unittest.TestCase):
    def test_a_run_that_submitted_nothing_reads_as_empty(self):
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            self.assertEqual(engine.submitted_solution(run_dir), {})

    def test_a_submission_without_tasks_reads_as_empty(self):
        for payload in ({}, {"tasks": []}, {"tasks": "not-a-list"}, {"notes": "x"}):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as temporary:
                    run_dir = Path(temporary)
                    write_json(
                        run_dir / "output" / "results" / "solution.json", payload
                    )
                    self.assertEqual(engine.submitted_solution(run_dir), {})

    def test_only_the_judged_fields_travel_and_they_are_clipped(self):
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            payload = submission(filler=4000)
            payload["tasks"][0]["task_description"] += " extra"
            write_json(run_dir / "output" / "results" / "solution.json", payload)

            solution = engine.submitted_solution(run_dir)

            self.assertEqual(solution["task_count"], 5, "the full count is reported")
            self.assertEqual(len(solution["tasks"]), engine.CPE_MAX_SOLUTION_TASKS)
            judged = {name for name, _ in engine.CPE_SOLUTION_FIELDS}
            for task in solution["tasks"]:
                self.assertLessEqual(set(task), judged, "no unjudged field travels")
                for name, limit in engine.CPE_SOLUTION_FIELDS:
                    if name in task:
                        self.assertLessEqual(len(task[name]), limit, name)
            # The first task arrives whole; the budget then cuts the tail of the
            # second rather than dropping it.
            self.assertEqual(set(solution["tasks"][0]), judged)
            self.assertIn("task_description", solution["tasks"][1])
            # Submitted text survives the clip; only its tail is dropped.
            self.assertTrue(
                solution["tasks"][0]["task_description"].startswith("task 1 description")
            )

    def test_the_whole_block_stays_within_its_own_budget(self):
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            write_json(
                run_dir / "output" / "results" / "solution.json",
                submission(filler=4000),
            )
            solution = engine.submitted_solution(run_dir)
            total = sum(
                len(value) for task in solution["tasks"] for value in task.values()
            )
            self.assertLessEqual(total, engine.CPE_MAX_SOLUTION_CHARS)


class EvidenceTests(unittest.TestCase):
    """The field's presence is the flag's, and the flag's default is off."""

    def fake_run(self, run_dir: Path) -> dict:
        write_json(
            run_dir / "output" / "results" / "solution.json", submission()
        )
        return {
            "problem_id": "2014_C",
            "run_dir": str(run_dir),
            "average_score": 0.8,
            "dimension_scores": {"analysis_evaluation": 0.8},
            "interaction_cost": 0.85,
            "interaction_penalty": 0.04,
            "net_utility": 0.76,
        }

    def evidence(self, run: dict) -> dict:
        with tempfile.TemporaryDirectory() as temporary:
            return engine.cpe_training_parent_evidence(
                {
                    "workflow_id": "interaction_workflow_test000000",
                    "workflow": {"policy_text": "# Human Expert Interaction"},
                    "utility": 0.76,
                    "round": 1,
                    "problem_results": [run],
                },
                1,
                {"2014_C": {"title": "t", "question": "q"}},
                Path(temporary),
                None,
            )

    def test_the_engine_defines_it_off(self):
        """Read from the source: the flag is set by an arm, so the live value
        depends on which arm's patch ran first in this process."""
        source = pathlib.Path(engine.__file__).read_text(encoding="utf-8")
        self.assertIn("CPE_INCLUDE_SUBMITTED_SOLUTION: bool = False", source)
        self.assertIn("CPE_INCLUDE_JUDGE_REPORT_FEEDBACK: bool = False", source)

    def test_the_evidence_omits_it_until_an_arm_asks(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = self.fake_run(Path(temporary) / "run")
            with patch.object(engine, "CPE_INCLUDE_SUBMITTED_SOLUTION", False):
                evidence = self.evidence(run)
            training_run = evidence["training_evidence"]["training_runs"][0]
            self.assertNotIn("submitted_solution", training_run)

    def test_the_evidence_carries_it_when_the_arm_asks(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = self.fake_run(Path(temporary) / "run")
            with patch.object(engine, "CPE_INCLUDE_SUBMITTED_SOLUTION", True):
                evidence = self.evidence(run)
            training_run = evidence["training_evidence"]["training_runs"][0]
            self.assertIn("submitted_solution", training_run)
            self.assertEqual(training_run["submitted_solution"]["task_count"], 5)
            # The withheld-Judge guard runs inside the builder and must still pass:
            # the submission's own field names may not collide with that list.
            engine.assert_no_cpe_judge_evidence(evidence)


class LauncherWiringTests(unittest.TestCase):
    """Enough arms opt in -- and no more than that.

    Read from the source rather than exercised: the flag is set from a patch
    function that ``main()`` runs, and what is being protected against is a
    deleted line (an arm loses the submission) or a moved one (the draft arm,
    which shares this launcher, gains an evidence shape the arms collected
    before it did not have).
    """

    def test_the_from_scratch_arm_sets_the_flag(self):
        source = FROM_SCRATCH.read_text(encoding="utf-8")
        self.assertIn("workflow.CPE_INCLUDE_SUBMITTED_SOLUTION = True", source)
        self.assertIn("def patch_sibling_launcher", source)

    def test_the_coevolution_arm_inherits_it_rather_than_setting_its_own(self):
        source = COEVOLUTION.read_text(encoding="utf-8")
        self.assertNotIn("CPE_INCLUDE_SUBMITTED_SOLUTION", source)

    def test_the_draft_arm_keeps_the_original_evidence_shape(self):
        source = LAUNCHER.read_text(encoding="utf-8")
        self.assertNotIn("workflow.CPE_INCLUDE_SUBMITTED_SOLUTION = True", source)
        # It still brackets whatever an arm sets, so a run leaves no residue.
        self.assertIn(
            "_original_submitted_solution = workflow.CPE_INCLUDE_SUBMITTED_SOLUTION",
            source,
        )
        self.assertIn(
            "workflow.CPE_INCLUDE_SUBMITTED_SOLUTION = _original_submitted_solution",
            source,
        )

    def test_the_evidence_guide_states_the_field_only_when_it_travels(self):
        """The prompt's `{submitted_solution_note}` slot follows the flag, and the
        builder and the exporter both fill it."""
        with patch.object(engine, "CPE_INCLUDE_SUBMITTED_SOLUTION", False):
            self.assertEqual(base.solution_evidence_note(), "")
        with patch.object(engine, "CPE_INCLUDE_SUBMITTED_SOLUTION", True):
            note = base.solution_evidence_note()
            self.assertIn("submitted_solution", note)
        self.assertIn("{submitted_solution_note}", base.EVOLUTION_PROMPT_HEAD)
        self.assertIn(
            '.replace("{submitted_solution_note}", solution_evidence_note())',
            LAUNCHER.read_text(encoding="utf-8"),
        )
        self.assertIn(
            '"{submitted_solution_note}", base.solution_evidence_note()',
            (REPO_ROOT / "scripts" / "export_evolution_prompts.py").read_text(
                encoding="utf-8"
            ),
        )


if __name__ == "__main__":
    unittest.main()
