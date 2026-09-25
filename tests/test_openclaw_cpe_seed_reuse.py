"""Seeding an experiment from another one must expose the seed's phases, and only those.

The test that matters here is the negative one: a seeded experiment writes its own
candidate, validation and later rounds into its round directories, so if a whole
source round were linked in, the engine would find the source's completed
candidate checkpoint under this experiment's round 1 and score a brand-new policy
with an old policy's runs -- finishing a round in a minute, with numbers that
belong to a different policy and no sign anything was borrowed.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import cpe_seed_reuse


SEED_ID = "interaction_workflow_seed0000000"


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def workflow(workflow_id: str, policy_text: str) -> dict:
    return {
        "workflow_id": workflow_id,
        "name": "seed policy",
        "purpose": "consult once, strategically",
        "policy_text": policy_text,
        "max_exchanges": 3,
        "stop_condition": "stop when settled",
    }


def build_source(root: Path) -> None:
    """A source experiment that finished its seed rounds, candidate phase included."""
    seed = workflow(SEED_ID, "# Human Expert Interaction\n\nStep 1. Ask once.\n")
    train_result = {
        "round": 1,
        "workflow_id": SEED_ID,
        "workflow": seed,
        "utility": 0.8648,
        "cpe_phase": "initial_train_parent_1",
        "problem_results": [],
    }
    validation_result = {
        "round": 0,
        "workflow_id": SEED_ID,
        "workflow": seed,
        "utility": 0.8565,
        "cpe_phase": "initial_validation_parent_1",
        "problem_results": [],
    }
    write_json(
        root / "workflows" / "cpe_state.json",
        {
            "schema_version": 5,
            "sampling_seed": 12345,
            "train_pool": ["2017_A", "2017_D", "2018_A", "2018_E"],
            "validation_pool": ["2020_B", "2020_C"],
            "train_batch_size": 2,
            "validation_size": 5,
            "selection_epsilon": 0.0,
            "train_sampling": "independent_batches_with_replacement_across_rounds",
            "validation_problems": ["2020_B", "2020_C"],
            "utility_basis": "mean_report_score_minus_interaction_cost",
            "interaction_cost": {"max_exchanges": 3},
            "initialization_mode": "round_0_validation_then_round_1_training",
            "initial_parent_validation_results": [validation_result],
            "initial_parent_train_results": [train_result],
            "initial_seed_train": [
                {"round": 1, "workflow_id": SEED_ID, "train_utility": 0.8648}
            ],
            "initial_training_batch": ["2017_D", "2017_A"],
            "initial_training_batch_reserved_at": "2026-09-23T22:22:21",
            "rounds": {"4": {"status": "complete"}},
            "patch_history": [{"round": 1}],
        },
    )
    write_json(root / "initial_interaction_workflows.json", [seed])
    for round_number, phase in (
        (0, "initial_validation_parent_1"),
        (1, "initial_train_parent_1"),
        (1, "train_candidate"),
    ):
        marker = (
            root / "cpe_evaluations" / f"round_{round_number}" / phase
            / "workflows" / f"round_{round_number}"
        )
        write_json(marker / "result.json", {"round": round_number, "phase": phase})


class SeedReuseTests(unittest.TestCase):
    def seed(self, temporary: str) -> tuple[Path, Path, dict]:
        root = Path(temporary)
        source, target = root / "source", root / "target"
        build_source(source)
        state = cpe_seed_reuse.build_seeded_experiment(source, target)
        return source, target, state

    def test_round_directories_are_real_and_expose_only_the_seed_phases(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, target, _ = self.seed(temporary)
            round_one = target / "cpe_evaluations" / "round_1"

            self.assertFalse(
                round_one.is_symlink(),
                "the round directory must be this experiment's own, not a link "
                "into the source: the arm writes its candidate into it",
            )
            self.assertFalse(
                (round_one / "train_candidate").exists(),
                "the source's candidate phase must not be reachable from here -- "
                "the engine would reuse its checkpoint and score a new policy "
                "with an old policy's runs",
            )
            for round_number, phase in (
                (0, "initial_validation_parent_1"),
                (1, "initial_train_parent_1"),
            ):
                link = target / "cpe_evaluations" / f"round_{round_number}" / phase
                self.assertTrue(link.is_symlink(), f"{phase} should be linked in")
                self.assertEqual(
                    link.resolve(),
                    (source / "cpe_evaluations" / f"round_{round_number}" / phase).resolve(),
                )

    def test_a_round_directory_that_is_a_symlink_is_refused(self):
        """The layout the bug produced must fail loudly instead of silently."""
        with tempfile.TemporaryDirectory() as temporary:
            source, target, _ = self.seed(temporary)
            round_one = target / "cpe_evaluations" / "round_1"
            for child in round_one.iterdir():
                child.unlink()
            round_one.rmdir()
            round_one.symlink_to(source / "cpe_evaluations" / "round_1")

            with self.assertRaises(ValueError):
                cpe_seed_reuse.link_reused_rounds(target, source)

    def test_state_carries_the_seed_and_nothing_evolved(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, target, state = self.seed(temporary)

            self.assertEqual(state["rounds"], {})
            self.assertEqual(state["patch_history"], [])
            self.assertEqual(state[cpe_seed_reuse.SEEDED_KEY]["source_experiment"], str(source.resolve()))
            self.assertEqual(state["initial_training_batch"], ["2017_D", "2017_A"])
            # The bar comes from the seed's own round-0 number, not from whatever
            # the source's later rounds went on to win.
            self.assertEqual(state["best_policy"]["validation_utility"], 0.8565)
            self.assertEqual(state["current_policy"]["workflow_id"], SEED_ID)
            self.assertEqual(state["current_policy"]["train_utility"], 0.8648)
            self.assertEqual(state["training_elites"][0]["workflow_id"], SEED_ID)

    def test_sampling_contract_is_copied_verbatim(self):
        """The engine refuses a resume whose pools or seed differ; that is the guard."""
        with tempfile.TemporaryDirectory() as temporary:
            source, target, state = self.seed(temporary)
            source_state = json.loads(
                (source / "workflows" / "cpe_state.json").read_text(encoding="utf-8")
            )
            for key in cpe_seed_reuse.CONFIG_KEYS:
                self.assertEqual(state[key], source_state[key], key)

    def test_the_wrapper_is_a_no_op_for_an_unseeded_state(self):
        """Installing the hook must not change what an ordinary run does."""
        calls = []

        def original(*args, **kwargs):
            calls.append(args)
            return "ran"

        wrapped = cpe_seed_reuse.reuse_or_run(original)
        self.assertEqual(
            wrapped(Path("/tmp/exp"), [], [], {}, {}, None, None, {"rounds": {}}, {}),
            "ran",
        )
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
