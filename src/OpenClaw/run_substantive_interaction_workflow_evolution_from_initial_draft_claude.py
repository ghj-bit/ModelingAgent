"""Evolve expert-interaction workflows that solve from planning ``draft.md`` files.

Claude Code backend variant of
``run_substantive_interaction_workflow_evolution_from_initial_draft``.  The
pipeline, prompts, concurrency and gates are byte-identical to that launcher;
the only difference is which executable solves each task.  Instead of the
OpenClaw CLI, every Solver runs as a headless Claude Code session driven by
``claude_backend``, and OpenClaw's agent-registry calls are answered by a
stub so the surrounding control flow is untouched.

Unlike the OpenClaw and OpenHands backends, this one cannot reach the local
model directly: Claude Code speaks the Anthropic Messages API and the served
endpoint cannot run this workload in that shape, so each task carries its own
translation shim (see ``claude_backend/proxy.py``).

This is intentionally separate from the clean-baseline refinement launcher. It
starts each Solver from a planning blueprint, not from an inherited completed
solution report, and supplies a single planning-derived initial workflow.

Exactly one interaction strategy is live at any time: the initial strategy is
also the initial best strategy, and every later round evolves one candidate from
the current best parent.  The pipeline runs on either benchmark; MM-Bench mode
uses a fixed year-based split of the native ``MMBench/problem`` tasks.
"""

from __future__ import annotations

import argparse
import copy
import difflib
import json
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import partial
from pathlib import Path

try:
    from . import claude_backend
    from . import run_substantive_interaction_workflow_evolution as workflow
    from . import run_substantive_interaction_workflow_evolution_from_clean_baseline as clean
    from .interaction_policy import STRATEGIC_DECISION_CONSULTATION
except ImportError:
    import claude_backend
    import run_substantive_interaction_workflow_evolution as workflow
    import run_substantive_interaction_workflow_evolution_from_clean_baseline as clean
    from src.OpenClaw.interaction_policy import STRATEGIC_DECISION_CONSULTATION


REPO_ROOT = Path(__file__).resolve().parents[2]

# The locally served model backs every role in this launcher.  The values live in
# the backend module so the solver, optimizer, expert and judge cannot drift
# apart; override them per run with the CLAUDE_MODEL / CLAUDE_BASE_URL /
# CLAUDE_API_KEY environment variables.
LOCAL_MODEL = claude_backend.DEFAULT_MODEL
LOCAL_BASE_URL = claude_backend.DEFAULT_BASE_URL
LOCAL_API_KEY = claude_backend.DEFAULT_API_KEY

# The shared engine's --fixed-rubric default points at a rubric evolved on the
# original Windows machine (round 4 of interaction_rubric_substantive_...),
# which this repository does not ship.  What it does ship is the rubric that
# experiment started from, so that is the fixed rubric here.
LOCAL_FIXED_RUBRIC = REPO_ROOT / "src" / "OpenClaw" / "interaction_initial_substantive_v1.json"

# How the solver starts, as the evolution prompt describes it to the optimizer.
# The draft-based arm leaves it as is; a draft-free arm sets it before main() so
# the optimizer is not told about a planning draft that arm never has.
SOLVER_SOURCE_CONTEXT = "from a planning draft"
SOLVER_START_CONTEXT = "starts from a planning draft"


def skip_round_dimension_plot(results, output_path):
    """Stand in for the engine's end-of-run dimension chart.

    matplotlib is deliberately not installed (these runs produce no figures),
    and the engine calls the real plot unguarded on its last line, so without
    this stand-in a fully completed experiment would still exit non-zero and be
    reported as a failure.
    """
    print(
        f"Round dimension plot skipped (matplotlib not installed): {output_path}",
        flush=True,
    )
    return output_path


def disable_thinking_for_direct_api_calls() -> None:
    """Make the launcher's direct provider calls usable with the local model.

    The shared code turns provider thinking off only when the base URL contains
    "deepseek.com" -- the provider the original experiments ran against.  The
    locally served model also defaults to thinking, and all three direct callers
    here (the human expert, the optimizer, and the MM-Bench judge) want short,
    immediately usable output.  With thinking on, the reasoning consumes the
    small max_tokens budget and the response body comes back empty, which the
    callers report as a failed API call rather than as an empty answer: the
    expert bridge dies with "expert API response contains no text" and the task
    fails its interaction gate.

    The three call sites each construct their own openai.OpenAI client, so the
    injection goes on the SDK's shared completions resource.  Calls that already
    pass extra_body -- the DeepSeek branch -- are left untouched.
    """
    from openai.resources.chat.completions import Completions

    if getattr(Completions.create, "_disables_provider_thinking", False):
        return
    original_create = Completions.create

    def create(self, *args, **kwargs):
        if not kwargs.get("extra_body"):
            kwargs["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": False}
            }
        return original_create(self, *args, **kwargs)

    create._disables_provider_thinking = True
    Completions.create = create
# These are default source experiments. Their task IDs are discovered from
# completed draft artifacts at runtime rather than duplicated here.
PLANNING_DRAFT_TRAIN_ROOT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_initial_draft_train_20260916_202307"
)
PLANNING_DRAFT_VALIDATION_ROOT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_initial_draft_val_20260916_211801"
)
TRAIN_PROBLEMS: list[str] = []
VALIDATION_PROBLEMS: list[str] = []
DEFAULT_INITIAL_DRAFT_TRAIN_BATCH_SIZE = 2
DEFAULT_INITIAL_DRAFT_VALIDATION_SIZE = 5
# Experiments live under their own subtree with a short name.  Everything below
# a run directory is long (cpe_evaluations/round_N/<phase>/runs/round_N/
# r1pN_<stamp>/meta/mmbench_judge/trial_N/evaluation_result/solution/...), so a
# short prefix buys real headroom against the Windows 260-character path limit.
EXPERIMENT_ROOT = REPO_ROOT / "openclaw_experiments" / "evolve_exp"
EXPERIMENT_PREFIX = "evolve"
# Each report is scored by this many Judge calls running in parallel; the run
# records their mean.  Judge noise within a phase is large enough that a single
# call is not a usable fitness signal.
DEFAULT_JUDGE_REPEATS = 3
# Each training problem is run this many times per round and their scores are
# averaged, so a train batch of three costs six agent runs.  A single run of one
# problem can swing by 0.03-0.06, which is larger than the differences the
# evolution is chasing, so one run per problem cannot support a gate decision.
DEFAULT_TRAIN_REPETITIONS = 2
# A candidate must beat the incumbent train utility by more than this to be
# worth a validation run.  Set deliberately *below* the observed spread of the
# same policy re-run (that spread exceeds 0.01), so a candidate can clear this
# gate on run-to-run noise alone: it is a cheap screen that decides who gets
# measured on the validation set, not a claim that the candidate is better.
# The real comparison is the champion gate below, which uses five-task
# validation means and therefore needs a far smaller margin to be meaningful.
# Kept identical to the OpenClaw launcher's margin: the two backends are run as
# comparison arms, and different gates would make their acceptances incomparable.
DEFAULT_TRAIN_ACCEPTANCE_MARGIN = 0.005
DEFAULT_VALIDATION_ACCEPTANCE_MARGIN = 0.005
# Thinking level for the solving agent.  The DeepSeek provider collapses
# minimal/low/medium/high onto one wire value (reasoning_effort="high"), so only
# "off" is a distinct setting: reasoning falls to 0% of output tokens and
# generated tokens per call drop by roughly 46%.  Overridable with --thinking.
DEFAULT_THINKING_LEVEL = "off"
INTERACTION_WORKFLOW_PLACEHOLDER = "{{INTERACTION_WORKFLOW}}"
DRAFT_PATH_PLACEHOLDER = "{{DRAFT_PATH}}"

# The MM-Bench mirror that ships with this repository.  The upstream default is
# a Windows path; every native problem definition the train and validation pools
# name is present here, and the dataset attachment directories that exist are
# staged per task.
DEFAULT_MMBENCH_ROOT = REPO_ROOT / "data" / "MMBench"
# Fixed MM-Bench split, selected by publication year over MMBench/problem/*.json
# (111 tasks, 2000-2025):
#   test       = every task from 2021 onward                              (32)
#   validation = the five newest tasks dated 2020 or earlier (2020_B..2020_F)
#   train      = the thirty newest remaining tasks (2014_C..2020_A)       (30)
# The 44 tasks older than the training window are deliberately unused.
MMBENCH_TEST_PROBLEMS = (
    "2021_A", "2021_B", "2021_C", "2021_D", "2021_E", "2021_F",
    "2022_A", "2022_B", "2022_C", "2022_D", "2022_E", "2022_F",
    "2023_A", "2023_B", "2023_C", "2023_D", "2023_E", "2023_F",
    "2023_Y", "2023_Z",
    "2024_A", "2024_B", "2024_C", "2024_D", "2024_E", "2024_F",
    "2025_A", "2025_B", "2025_C", "2025_D", "2025_E", "2025_F",
)
# 2020_C retired 2026-09-25: its review-text task makes agents launch unbounded
# parallel sentiment jobs (one run measured at 127 threads / 59 of 104 cores),
# which starved every other run in the phase.  Four problems now, so
# --validation-size must be 4 -- see launch_claude_evolution_from_scratch.sh.
MMBENCH_VALIDATION_PROBLEMS = (
    "2020_B", "2020_D", "2020_E", "2020_F",
)
MMBENCH_TRAIN_PROBLEMS = (
    "2014_C",
    "2015_A", "2015_B", "2015_C", "2015_D",
    "2016_A", "2016_B", "2016_C", "2016_D", "2016_E", "2016_F",
    "2017_A", "2017_B", "2017_C", "2017_D", "2017_E", "2017_F",
    "2018_A", "2018_B", "2018_C", "2018_D", "2018_E", "2018_F",
    "2019_A", "2019_B", "2019_C", "2019_D", "2019_E", "2019_F",
    "2020_A",
)

_active_experiment: Path | None = None
_draft_train_root: Path | None = None
_draft_validation_root: Path | None = None
_initialize_only = False
_round0_only = False
_benchmark = "modelingbench"
_mmbench_root: Path = DEFAULT_MMBENCH_ROOT
# Resolved once in main(); injected into run_args so the shared preparation hook
# can find each task's planning draft.
_mmbench_draft_reports: dict[str, str] = {}
_mmbench_judge: dict[str, object] = {}
_mmbench_problems: dict = {}
# Captured while the patches below are active; record_config() runs after they
# are restored, so it cannot read the live constants.
_effective_evolution: dict[str, object] = {}

_original_prepare_refinement = workflow.substantive.prepare_refinement_validation_problem
_original_runtime_args = workflow.substantive.runtime_args
_original_parse_args = workflow.parse_args
_original_load_cpe_split = workflow.load_cpe_split
_original_baseline_report_root = workflow.substantive.BASELINE_REPORT_ROOT
_original_default_problems = workflow.substantive.DEFAULT_PROBLEMS
_original_resolve_baseline_report = workflow.substantive.resolve_baseline_report
_missing = object()
_original_baseline_report_matches = getattr(
    workflow.substantive, "baseline_report_matches_problem", _missing
)
_original_experiment_path = workflow.experiment_path
_original_build_refinement_prompt = workflow.build_workflow_refinement_prompt
_original_build_cpe_prompt = workflow.build_cpe_workflow_evolution_prompt
_original_initial_population = workflow.initial_strategy_population
_original_validate_workflow = workflow.validate_workflow
_original_ensure_original_scores = workflow.ensure_cpe_original_report_scores
_original_execute_cpe_evaluation = workflow.execute_cpe_evaluation
_original_plot_round_dimension = workflow.plot_round_average_dimension_scores
_original_utility_basis = workflow.CPE_UTILITY_BASIS
_original_cost_weight = workflow.DEFAULT_CPE_COST_PENALTY_WEIGHT
_original_latency_cost_weight = workflow.DEFAULT_CPE_LATENCY_COST_WEIGHT
_original_min_rounds = workflow.MIN_CPE_EVOLUTION_ROUNDS
_original_max_exchanges = workflow.MAX_WORKFLOW_EXCHANGES
_original_collapse_initial_parents = workflow.CPE_COLLAPSE_INITIAL_PARENTS
_original_run_collapsed_initial_parents = (
    workflow.run_cpe_collapsed_initial_parent_evaluations
)
_original_write_interaction_added_content = (
    workflow.substantive.write_interaction_added_content
)
_original_run_consolidated_refinement_check = (
    workflow.substantive.run_consolidated_refinement_check
)
_original_training_parent_count = workflow.CPE_TRAINING_PARENT_COUNT
_original_evolution_modes = workflow.CPE_EVOLUTION_MODES
_original_train_epsilon = workflow.CPE_TRAIN_ACCEPTANCE_EPSILON
_original_validation_epsilon = workflow.CPE_VALIDATION_ACCEPTANCE_EPSILON
_original_interaction_judge_report = workflow.interaction.judge_report
_original_load_problems = workflow.baseline.load_problems


def parse_planning_draft_sources() -> argparse.Namespace:
    """Consume this launcher's source arguments before the shared parser runs."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--planning-draft-train-root", type=Path)
    parser.add_argument("--planning-draft-validation-root", type=Path)
    parser.add_argument(
        "--benchmark",
        choices=("modelingbench", "mmbench"),
        default="mmbench",
        help="Problem/data/evaluation source (default: mmbench).",
    )
    parser.add_argument(
        "--mmbench-root",
        type=Path,
        default=DEFAULT_MMBENCH_ROOT,
        help=f"MM-Bench root (default: {DEFAULT_MMBENCH_ROOT}).",
    )
    parser.add_argument(
        "--planning-draft-root",
        type=Path,
        nargs="+",
        help=(
            "MM-Bench roots holding the planning drafts. Defaults to every "
            "interaction_strategy_clean_baseline_initial_draft_mmbench_* run."
        ),
    )
    # Every role -- solver, optimizer, expert and MM-Bench judge -- runs against
    # the locally served model; the DeepSeek defaults in the shared parser are
    # overridden in parse_args_with_pool_defaults below.
    parser.add_argument("--mmbench-judge-model", default=LOCAL_MODEL)
    parser.add_argument("--mmbench-judge-api-key", default=LOCAL_API_KEY)
    parser.add_argument("--mmbench-judge-base-url", default=LOCAL_BASE_URL)
    parser.add_argument("--mmbench-judge-timeout", type=float, default=600.0)
    # Launcher-private, and consumed here rather than by the shared parser.  The
    # engine's own validation requires --max-rounds to be at least 1, so "stop
    # after round 0" cannot be expressed through that flag without editing the
    # engine every other experiment also uses.
    parser.add_argument(
        "--round0-only",
        action="store_true",
        help=(
            "Run the round-0 initial-parent validation on the validation pool "
            "and stop before the initial training parents and every evolved "
            "round.  Use --max-rounds 1 alongside it: that value is only there "
            "to satisfy the shared parser."
        ),
    )
    values, remainder = parser.parse_known_args(sys.argv[1:])
    sys.argv = [sys.argv[0], *remainder]
    return values


def load_current_draft_split(_path: Path) -> tuple[list[str], list[str]]:
    return list(TRAIN_PROBLEMS), list(VALIDATION_PROBLEMS)


def run_initial_draft_parent_evaluations(
    experiment: Path,
    initial_problem_ids: list[str],
    initial_population: list[dict],
    fixed_rubric: dict,
    problems: dict,
    run_args,
    args,
    state: dict,
    original_scores: dict[str, dict],
) -> None:
    """Validate seed policies in round 0, then train them in round 1."""
    if len(initial_population) != workflow.CPE_TRAINING_PARENT_COUNT:
        raise ValueError(
            "Initial-draft CPE initialization requires "
            f"{workflow.CPE_TRAINING_PARENT_COUNT} seed workflow(s)"
        )

    initialization_mode = "round_0_validation_then_round_1_training"
    saved_mode = state.get("initialization_mode")
    if saved_mode not in (None, initialization_mode):
        raise ValueError(
            "This experiment was created with a different CPE initialization mode; "
            "start a new experiment directory instead of resuming it."
        )
    state["initialization_mode"] = initialization_mode
    validation_problems = [str(item) for item in state["validation_problems"]]

    workflow.ensure_cpe_baseline_reports(
        experiment,
        validation_problems,
        run_args,
        Path(args.baseline_report_root),
    )
    original_scores.update(
        workflow.ensure_cpe_original_report_scores(
            experiment, validation_problems, run_args
        )
    )
    parent_validation_results: list[dict | None] = [
        None
    ] * workflow.CPE_TRAINING_PARENT_COUNT
    print(
        "Running the initial parent validations in parallel in CPE round 0",
        flush=True,
    )
    with ThreadPoolExecutor(
        max_workers=workflow.CPE_TRAINING_PARENT_COUNT
    ) as executor:
        futures = {
            executor.submit(
                workflow.execute_cpe_evaluation,
                experiment,
                0,
                f"initial_validation_parent_{parent_rank}",
                "validation",
                validation_problems,
                workflow.without_removed_workflow_fields(parent),
                fixed_rubric,
                problems,
                run_args,
                args.enforce_substantive_interaction_gate,
                original_scores,
            ): parent_rank
            for parent_rank, parent in enumerate(initial_population, start=1)
        }
        for future in as_completed(futures):
            parent_rank = futures[future]
            result, failures = future.result()
            if failures:
                raise RuntimeError(
                    f"{len(failures)} round-0 initial parent validation run(s) "
                    "failed the substantive gate"
                )
            parent_validation_results[parent_rank - 1] = result
    parent_validation_results = [
        result for result in parent_validation_results if result is not None
    ]
    if len(parent_validation_results) != workflow.CPE_TRAINING_PARENT_COUNT:
        raise RuntimeError("Round-0 initial parent validation did not produce two results")

    validation_champion = max(
        parent_validation_results,
        key=lambda result: (float(result["utility"]), str(result["workflow_id"])),
    )
    state["initial_parent_validation_results"] = copy.deepcopy(
        parent_validation_results
    )
    state["best_policy"] = {
        "source_round": 0,
        "source_phase": "initial_validation_parent",
        "workflow_id": validation_champion["workflow_id"],
        "workflow": workflow.without_removed_workflow_fields(
            validation_champion["workflow"]
        ),
        "validation_utility": float(validation_champion["utility"]),
        "utility_basis": workflow.CPE_UTILITY_BASIS,
    }
    state["updated_at"] = workflow.now()
    workflow.workflow_evolution.write_json(workflow.cpe_state_path(experiment), state)

    if _round0_only:
        # Validation-only run.  The initial training parents exist to seed the
        # first evolved round -- the first candidate is selected against their
        # utilities -- so with no evolved round scheduled nothing would ever
        # read their results, and running them anyway means solving the reserved
        # training batch for a consumer that never arrives.  Stop before them,
        # and before every evolved round: the round-0 validation results and the
        # policy chosen from them were saved above, so the experiment is left
        # consistent and resumable.  Resume without --round0-only to continue.
        print(
            "Round-0-only run: stopping before the initial training parents and "
            "all evolved rounds.  Round-0 validation results are complete.",
            flush=True,
        )
        raise SystemExit(0)

    parent_train_results: list[dict | None] = [
        None
    ] * workflow.CPE_TRAINING_PARENT_COUNT
    print(
        "Running the initial training-parent workflows in parallel in CPE round 1",
        flush=True,
    )
    with ThreadPoolExecutor(
        max_workers=workflow.CPE_TRAINING_PARENT_COUNT
    ) as executor:
        futures = {
            executor.submit(
                workflow.execute_cpe_evaluation,
                experiment,
                1,
                f"initial_train_parent_{parent_rank}",
                "train",
                initial_problem_ids,
                workflow.without_removed_workflow_fields(parent),
                fixed_rubric,
                problems,
                run_args,
                args.enforce_substantive_interaction_gate,
                original_scores,
            ): parent_rank
            for parent_rank, parent in enumerate(initial_population, start=1)
        }
        for future in as_completed(futures):
            parent_rank = futures[future]
            result, failures = future.result()
            if failures:
                raise RuntimeError(
                    f"{len(failures)} round-1 initial training-parent run(s) "
                    "failed the substantive gate"
                )
            parent_train_results[parent_rank - 1] = result
    parent_train_results = [
        result for result in parent_train_results if result is not None
    ]
    if len(parent_train_results) != workflow.CPE_TRAINING_PARENT_COUNT:
        raise RuntimeError("Round-1 initial parent training did not produce two results")

    state["initial_parent_train_results"] = copy.deepcopy(parent_train_results)
    state["initial_seed_train"] = [
        {
            "round": 1,
            "workflow_id": result["workflow_id"],
            "train_utility": float(result["utility"]),
        }
        for result in parent_train_results
    ]
    state["training_elites"] = workflow.select_cpe_training_elites(
        parent_train_results
    )
    best_train = state["training_elites"][0]
    state["current_policy"] = {
        **copy.deepcopy(best_train),
        "train_utility": float(best_train["selection_utility"]),
        "utility_basis": workflow.CPE_UTILITY_BASIS,
    }
    state["updated_at"] = workflow.now()
    workflow.workflow_evolution.write_json(workflow.cpe_state_path(experiment), state)


def discover_planning_draft_problem_ids(root: Path) -> list[str]:
    """Return completed planner IDs, preserving the source experiment's order."""
    problem_ids: set[str] = set()
    for draft in root.glob("**/output/results/draft.md"):
        if not draft.read_text(encoding="utf-8", errors="replace").strip():
            continue
        metadata = workflow.workflow_evolution.read_json(
            draft.parents[2] / "meta" / "run.json", {}
        )
        problem_id = metadata.get("problem_id")
        if isinstance(problem_id, str) and problem_id.strip():
            problem_ids.add(problem_id)
    if not problem_ids:
        raise FileNotFoundError(f"No non-empty output/results/draft.md files found under {root}")
    config = workflow.workflow_evolution.read_json(root / "runs" / "config.json", {})
    configured = config.get("validation_problems", [])
    if isinstance(configured, list):
        missing = [
            str(problem_id)
            for problem_id in configured
            if str(problem_id) not in problem_ids
        ]
        if missing:
            raise FileNotFoundError(
                f"Configured planning drafts missing under {root}: "
                + ", ".join(missing)
            )
        ordered = [str(problem_id) for problem_id in configured]
    else:
        ordered = []
    ordered.extend(sorted(problem_ids - set(ordered)))
    return ordered


def source_root_for_problem(problem_id: str) -> Path:
    if problem_id in TRAIN_PROBLEMS and _draft_train_root is not None:
        return _draft_train_root
    if problem_id in VALIDATION_PROBLEMS and _draft_validation_root is not None:
        return _draft_validation_root
    raise ValueError(
        f"No planning-draft root configured for {problem_id}. Supply the matching "
        "--planning-draft-train-root or --planning-draft-validation-root."
    )


def resolve_planning_draft(problem_id: str, _unused_root: Path) -> Path:
    """Resolve one non-empty draft.md by its controller-authored problem metadata."""
    # The shared engine validates source artifacts before it branches for
    # --initialize-only. No task is executed in that mode, so an existing
    # placeholder avoids requiring draft roots merely to materialize seeds.
    if _initialize_only:
        return Path(__file__).resolve()
    if _benchmark == "mmbench":
        # MM-Bench drafts have no train/validation root split; main() already
        # resolved one draft path per task, so use it directly.
        resolved = _mmbench_draft_reports.get(problem_id)
        if not resolved:
            raise FileNotFoundError(
                f"No planning draft resolved for MM-Bench problem {problem_id}"
            )
        return Path(resolved)
    root = source_root_for_problem(problem_id)
    candidates = []
    for draft in root.glob("**/output/results/draft.md"):
        metadata_path = draft.parents[2] / "meta" / "run.json"
        metadata = workflow.workflow_evolution.read_json(metadata_path, {})
        if (
            metadata.get("problem_id") == problem_id
            and draft.read_text(encoding="utf-8", errors="replace").strip()
        ):
            candidates.append(draft)
    if not candidates:
        raise FileNotFoundError(
            f"No non-empty planning draft.md for {problem_id} under {root}"
        )
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, str(path)))


def planning_draft_matches_problem(problem_id: str, draft: Path) -> bool:
    if _benchmark == "mmbench":
        # main() pinned one draft per task, so identity is the whole check and
        # there is no train/validation root to be relative to.
        resolved = _mmbench_draft_reports.get(problem_id)
        if not resolved:
            return False
        try:
            return Path(draft).resolve() == Path(resolved).resolve()
        except OSError:
            return False
    expected_root = source_root_for_problem(problem_id).resolve()
    try:
        Path(draft).resolve().relative_to(expected_root)
    except ValueError:
        return False
    metadata = workflow.workflow_evolution.read_json(
        Path(draft).parents[2] / "meta" / "run.json", {}
    )
    return metadata.get("problem_id") == problem_id


def interaction_workflow_block(workflow_value: dict, note: str = "") -> str:
    """Render every seed or evolved workflow as ordinary Markdown prose.

    ``note`` is one arm-specific paragraph appended to the section, so a run can
    state a constraint that is not part of the policy the optimizer may rewrite.
    """
    name = str(workflow_value.get("name", "Interaction workflow"))
    purpose = str(workflow_value.get("purpose", "")).strip()
    actions = list(workflow_value.get("actions", []))
    max_exchanges = int(workflow_value.get("max_exchanges", 1))
    rounds = "round" if max_exchanges == 1 else "rounds"
    interactions = "expert interaction" if max_exchanges == 1 else "expert interactions"
    policy_text = str(workflow_value.get("policy_text", "")).strip()
    if policy_text:
        lines = policy_text.splitlines()
        lines.append("")
    else:
        lines = [
            "# Human Expert Interaction",
            "",
            f"## {name}",
            "",
            purpose,
            "",
            "## Interaction Workflow",
            "",
        ]
        for index, action in enumerate(actions, start=1):
            lines.extend(
                [
                    f"### Step {index}",
                    "",
                    str(action["rule"]),
                    "",
                ]
            )
    lines.extend(
        [
            f"Expert exchanges: **{max_exchanges}**, fixed. The consultation runs "
            f"exactly {max_exchanges} {rounds}: ask the first question before the work "
            "it governs, and make each later question build on the previous reply. "
            "Do not stop early, and do not exceed it.",
            "",
            "### How to request expert feedback",
            "",
            "When a step requests expert feedback:",
            "",
            "1. Set `N` to the exchange number, starting at 1 and increasing by one.",
            "2. Write only the qualitative question to "
            "`{{OPERATOR_FEEDBACK_DIR}}/expert_question_N.md`.",
            "3. Run this command once in the foreground:",
            "",
            f'`python "{{{{OUTPUT_DIR}}}}/code/wait_for_expert_reply.py" '
            f'--request "{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_request_N.json" '
            f'--reply "{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_reply_N.json" '
            f'--timeout {workflow.substantive.EXPERT_REQUEST_TIMEOUT:.0f}`',
            "",
            "4. Read the returned expert reply, apply it as required by the current "
            "step, and then continue to the next step.",
            "",
            "The controller owns the request and reply files. Do not edit them, poll "
            "for them, or retry the command. Every later question must build on an "
            f"earlier reply. Complete exactly {max_exchanges} {interactions}, "
            "one per round.",
            "",
        ]
    )
    if note.strip():
        lines.extend(["", str(note).strip(), ""])
    return "\n".join(lines)


def policy_text_for_evolution(workflow_value: dict) -> str:
    """Render policy behavior without exposing internal graph field names."""
    policy_text = str(workflow_value.get("policy_text", "")).strip()
    if policy_text:
        return policy_text
    lines = [
        f"### {workflow_value.get('name', 'Interaction policy')}",
        "",
        str(workflow_value.get("purpose", "")).strip(),
        "",
        "#### Interaction workflow",
        "",
    ]
    for index, action in enumerate(workflow_value.get("actions", []), start=1):
        lines.extend([f"Step {index}: {action.get('rule', '')}", ""])
    lines.extend(
        [
            f"Maximum expert interactions: {workflow_value.get('max_exchanges', 1)}.",
            "",
            f"Termination: {workflow_value.get('stop_condition', '')}",
        ]
    )
    return "\n".join(lines).strip()


def evolution_history_entries(patch_history: list[dict]) -> list[dict]:
    """Compact prior rounds into what was tried, what was predicted, what happened.

    Each round is otherwise independent, so without this the optimizer
    re-derives the same plausible change every round and cannot learn that a
    direction already failed validation.

    The round's own ``interaction_policy`` is included verbatim.  The optimizer's
    ``changed_components`` cannot stand in for it: across rounds those strings
    repeat word for word while the policy text they claim to describe differs
    substantially, so reading them alone tells the optimizer it already tried
    something it in fact never tried.
    """
    entries = []
    for event in patch_history or []:
        if not isinstance(event, dict):
            continue
        policy_text = str(event.get("candidate_policy_text") or "").strip()
        entry = {
            "round": event.get("round"),
            "evolution_mode": event.get("evolution_mode"),
            "interaction_policy": (
                policy_text if policy_text else "(policy text not recorded for this round)"
            ),
            "changed_components": event.get("changed_components", []),
            "parent_train_net_utilities": event.get("parent_train_net_utilities"),
            "candidate_train_net_utility": event.get("candidate_train_net_utility"),
            "train_accepted": event.get("train_accepted"),
            "validation_utility": event.get("validation_utility"),
            "validation_accepted": event.get("validation_accepted"),
        }
        predicted = event.get("predicted_effect")
        # The optimizer is no longer asked to predict its effect, so a round
        # normally carries an empty mapping here; keep it out of the evidence.
        if isinstance(predicted, dict) and predicted:
            entry["predicted_effect"] = predicted
        entries.append(entry)
    return entries


EVOLUTION_PROMPT_HEAD = """System prompt. You are a senior interaction-policy engineer.
The downstream solver agent solves MM-Bench modeling tasks {solver_source}
and may consult a human expert while it works. You must respond with one JSON
object only (no markdown fences), matching the schema in §3.

§1 Optimization goals. Evolve one executable human-expert interaction policy for
a modeling agent that {solver_start} and otherwise solves autonomously. Treat the policy as the communication contract: it governs only the
consultation itself — when the agent asks, what it asks, how many exchanges it
uses, how those exchanges relate to one another, and what it does with each
reply. It governs no other part of the solver's work, and a policy that asks
the agent to account for, log, or document the consultation is not a
behavioural improvement.

The evidence JSON holds the single training parent and its rollouts on the current
training batch, the historical validation champion, and every round already run.
Each sampled task carries its problem statement, the complete expert dialogue, a
short summary of what the reply changed in the work, and its scores. Judge prose is
withheld; judge the consultation by the questions the agent asked and the replies
it received — what was asked, when, how often, and what the agent did with each
reply — and read the change summaries and scores as the coarse consequences of
that, not as the thing to optimize.

Use the parent's rollouts to identify communication failures and transferable
successes, and treat the aggregate net utilities and the decision history as
coarse fitness signals. Propose a targeted behavioural patch rather than a
task-specific solution: never copy task-specific facts, entities, parameters,
methods, or conclusions out of the rollouts, and do not name a task inside the
policy.

Every earlier round is listed in `evolution_history` with the `interaction_policy`
it actually proposed and its `train_accepted` verdict. A round whose
`train_accepted` is false was measured against the training gate and lost; do not
resubmit that direction in the same shape. Either abandon it, or change it enough
that the failure it produced no longer applies — and name the earlier round you
are departing from in `evolution_rationale`.

The solver agent keeps all calculation, implementation, external-data validation,
simulation, debugging, and report writing; the expert supplies high-impact
strategic judgment only. Keep the policy compact.

`interaction_policy` is the whole deliverable. It is the only artifact the solver
agent ever reads and the only one the round is scored on, so every change you
intend must appear in it. Before you answer, re-read the steps of your
`interaction_policy` that govern the consultation against the parent's and confirm
they differ. If they do not, the round is discarded and the attempt is wasted.

A candidate whose behavioural similarity to a round already evaluated reaches
{similarity_threshold} is rejected before it runs.

§2 Modification requirements.

- Mutate the parent policy. Only one policy is live; crossover is unavailable.
- Change only the consultation's own behaviour: what the agent does before it
  asks (the question's content and form), how it treats the reply, and whether and
  how a further exchange is used. Everything else in `interaction_policy` is fixed
  and must be carried over exactly as the parent states it: the trigger conditions
  for consulting, the exchange budget, the stop conditions, any efficiency or
  scope rule, and any prohibition on asking the expert to compute, implement, or
  execute. Where the parent marks the mutable part with a heading, that heading is
  the boundary; the policy text itself is the only thing the solver reads.
- Keep each step the policy states concise: one or two sentences each. A short
  workflow the solver follows exactly is worth more than a longer one it follows
  only in part. Do not restate the fixed parts inside the workflow.
- Make the smallest edit that carries the patch. Add or rewrite only the lines
  your change needs and leave every other line of `interaction_policy` exactly as
  the parent wrote it. Rewording, reordering, and cosmetic deletion are not
  behavioural changes and are rejected as noise.
- Return the policy in the shape the parent uses: `name`, `purpose`,
  `interaction_policy`, `maximum_expert_interactions`, and
  `termination_condition`. `interaction_policy` is the deliverable and must stand
  alone: it is the only thing the solver agent ever receives.
- `interaction_policy` must differ from the parent's and from every policy already
  listed in `evolution_history`. Reproducing either is rejected before the round
  runs, whatever else differs. Do not spend a retry re-submitting the parent in
  new wording.
- `changed_components` must name only differences the returned
  `interaction_policy` actually carries against the parent's. Guidance the
  parent already states is not a change; describing it as one misreports the
  round and is recorded as such in `evolution_history`.
"""


EVOLUTION_OUTPUT_SCHEMA = """§3 Output JSON schema.

`interaction_policy` comes first because it is the deliverable. Write it before
the bookkeeping fields, and make it differ from the parent's text.

{
  "interaction_policy": "<the complete evolved policy, one Markdown string. It must NOT reproduce the parent's text: a verbatim copy is rejected before the round runs, whatever else differs.>",
  "name": "<concise policy name>",
  "purpose": "<the strategic role of human interaction>",
  "maximum_expert_interactions": <positive integer>,
  "termination_condition": "<concise textual stopping rule>",
  "evolution_mode": "mutation",
  "changed_components": ["<non-empty list of behavioural changes>"],
  "evolution_rationale": "<why the changes fit the parent policy's evidence>"
}
"""


EVOLUTION_EVIDENCE_GUIDE = """§4 Evidence

The JSON object below is the input for this round. Its `net_utility` is the
quantity §1 asks you to raise.
"""


EVOLUTION_PROMPT_FOOT = """§5 Final instruction. Emit one JSON object as in §3, with
`interaction_policy` written first. Compare the steps of that policy that govern
the consultation against the parent's before you emit: if they still read the
same, the proposal is discarded and the attempt is wasted. No markdown outside
that JSON."""


def build_initial_draft_cpe_workflow_evolution_prompt(
    training_parents: list[dict],
    validation_champion: dict,
    patch_history: list[dict],
    dialogue_operators: dict | None = None,
) -> str:
    """Build policy evolution evidence without the retired operator catalogue."""
    del dialogue_operators
    if len(training_parents) != workflow.CPE_TRAINING_PARENT_COUNT:
        raise ValueError(
            f"CPE workflow evolution requires {workflow.CPE_TRAINING_PARENT_COUNT} "
            "training parents"
        )
    workflow.assert_no_cpe_judge_evidence(training_parents)
    champion_workflow = validation_champion.get("workflow", {})
    evidence_parents = []
    for parent in training_parents:
        # Keep the cost model and the average penalty.  Without them the
        # operator cannot tell whether a low net utility came from weak report
        # quality or from expensive interaction, and would have to guess which
        # side of the objective to move.
        training_evidence = copy.deepcopy(parent.get("training_evidence", {}))
        evidence_parent = {
            "parent_rank": parent.get("parent_rank"),
            "workflow_id": parent.get("workflow_id"),
            "interaction_policy": policy_text_for_evolution(
                parent.get("workflow", {})
            ),
            "net_utility_on_current_training_batch": parent.get(
                "net_utility_on_current_training_batch"
            ),
            "training_evidence": training_evidence,
        }
        evidence_parents.append(evidence_parent)
    evidence_bundle = {
        "training_parents": evidence_parents,
        "historical_validation_champion": {
            "workflow_id": champion_workflow.get("workflow_id"),
            "interaction_policy": policy_text_for_evolution(champion_workflow),
            "mean_net_utility": validation_champion.get("utility"),
        },
        "evolution_history": evolution_history_entries(patch_history),
    }
    workflow.assert_no_cpe_judge_evidence(evidence_bundle)
    evidence_json = json.dumps(evidence_bundle, ensure_ascii=False, indent=2)
    return "\n".join(
        [
            EVOLUTION_PROMPT_HEAD.replace(
                "{similarity_threshold}",
                f"{workflow.DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD:.2f}",
            ).replace("{solver_source}", SOLVER_SOURCE_CONTEXT)
            .replace("{solver_start}", SOLVER_START_CONTEXT),
            EVOLUTION_OUTPUT_SCHEMA,
            EVOLUTION_EVIDENCE_GUIDE,
            "",
            "```json",
            evidence_json,
            "```",
            "",
            EVOLUTION_PROMPT_FOOT,
            "",
        ]
    )


def _synthesise_actions(interaction_policy: str) -> list[dict]:
    """Derive the internal action graph from the policy's interaction workflow.

    The workflow this pipeline evolves is the interaction workflow: the steps the
    solver follows while consulting.  The optimizer authors only the text, so the
    graph is projected from it here rather than being asked for separately -- one
    action per step the policy states, which keeps the graph a faithful
    single-sourced view of the text.

    It also has to be derived this way for the evolution to work at all: the
    similarity guard compares candidates through this graph, so if every
    candidate carried one generic action holding the whole policy, two distinct
    policies would look almost identical and every round after the first would be
    rejected as a duplicate.

    Falls back to the generic four-stage graph when the policy states no steps of
    its own; the fixed-section check already rejects a candidate that drops the
    workflow section, so that path is the seeds' alone.
    """
    steps = _interaction_workflow_steps(interaction_policy)
    if not steps:
        return [
            {
                "action_id": "apply_policy_trigger",
                "action_type": "agent_step",
                "rule": "Apply the complete natural-language interaction policy below to decide whether and when strategic expert feedback is required.\n\n"
                + interaction_policy,
            },
            {
                "action_id": "request_strategic_feedback",
                "action_type": "expert_exchange",
                "rule": "When the interaction policy requires consultation, present the specified strategic context and request only the qualitative expert judgment defined by that policy.",
            },
            {
                "action_id": "integrate_strategic_feedback",
                "action_type": "agent_analysis",
                "rule": "Evaluate and apply the expert reply according to the interaction policy, then continue all technical modeling work autonomously.",
            },
            {
                "action_id": "close_policy_interaction",
                "action_type": "close",
                "rule": "Stop expert interaction at the stated limit or termination condition and complete the remaining modeling work autonomously.",
            },
        ]
    actions = []
    exchange_assigned = False
    for index, (title, body) in enumerate(steps, start=1):
        text = re.sub(
            r"\s+", " ", (title.rstrip(":").strip() + ". " + body).strip()
        ).strip(" .")
        label = re.sub(r"(?i)^step\s*\d+\s*:?\s*", "", title).strip()
        consults = bool(re.search(r"(?i)\b(ask|query|request|consult|expert|reply)\b", text))
        if index == 1:
            action_type = "agent_step"
        elif consults and not exchange_assigned:
            action_type = "expert_exchange"
            exchange_assigned = True
        elif index == len(steps) and re.search(
            r"(?i)\b(stop|terminat|close|end|limit)\b", label
        ):
            action_type = "close"
        else:
            action_type = "agent_analysis"
        actions.append(
            {
                "action_id": f"step_{index}_{_slug(label) or action_type}",
                "action_type": action_type,
                "rule": text[:2000],
            }
        )
    if not exchange_assigned:
        # The graph is bookkeeping, but one exchange has to be represented.
        actions[min(1, len(actions) - 1)]["action_type"] = "expert_exchange"
    return actions


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")[:40]


def _interaction_workflow_steps(interaction_policy: str) -> list[tuple[str, str]]:
    """Split the policy's interaction-workflow section into (title, body) steps.

    The split itself lives in the shared engine, which also uses it to compare
    two policies by the steps they state; this wrapper keeps the titles here,
    because an action's id is built from its step's title.
    """
    section = workflow._workflow_section(interaction_policy)
    if section is None:
        return []
    body, _, level = section
    levels = [len(match) for match in re.findall(rf"(?m)^(#{{{level + 1},}}) ", body)]
    blocks: list[tuple[str, str]] = []
    if levels:
        step_level = min(levels)
        parts = re.split(rf"(?m)^#{{{step_level}}} (.+)$", body)
        for title, chunk in zip(parts[1::2], parts[2::2]):
            blocks.append((title.strip(), chunk.strip()))
    else:
        for item in re.split(r"(?m)^\s*(?=\d+\.\s)", body)[1:]:
            text = re.sub(r"^\s*\d+\.\s*", "", item).strip()
            title = text.splitlines()[0].strip(" *").rstrip(":") if text else ""
            blocks.append((title, text))
    return [(title, body) for title, body in blocks if body]


def validate_workflow_with_inferred_start(workflow_value: dict) -> None:
    """Translate prose-policy output into the shared engine's internal graph."""
    interaction_policy = str(
        workflow_value.get("interaction_policy")
        or workflow_value.get("policy_text")
        or ""
    ).strip()
    if interaction_policy:
        workflow_value["policy_text"] = interaction_policy
    if not workflow_value.get("max_exchanges"):
        maximum = workflow_value.get("maximum_expert_interactions", 1)
        try:
            workflow_value["max_exchanges"] = int(maximum)
        except (TypeError, ValueError):
            workflow_value["max_exchanges"] = 1
    if not workflow_value.get("stop_condition"):
        termination = workflow_value.get("termination_condition", "")
        if isinstance(termination, list):
            termination = "; ".join(str(item) for item in termination)
        workflow_value["stop_condition"] = str(termination).strip()
    actions = workflow_value.get("actions")
    if not actions and interaction_policy:
        workflow_value["actions"] = _synthesise_actions(interaction_policy)
        actions = workflow_value["actions"]
    actions = workflow_value.get("actions")
    if not workflow_value.get("entry_action") and isinstance(actions, list) and actions:
        first_action = actions[0]
        if isinstance(first_action, dict):
            workflow_value["entry_action"] = first_action.get("action_id")
    _original_validate_workflow(workflow_value)


# Emitted only in MM-Bench mode.  The Markdown report alone is not a complete
# submission there: the native evaluator reads this container instead, so the
# solver has to be told to produce it.  Placeholders are resolved downstream,
# exactly like the rest of the solver prompt.
MMBENCH_SOLUTION_FILE_SECTION = """\
## MM-Bench Solution File

This machine-readable container is the submission that MM-Bench Judge reads:

`{{RESULTS_DIR}}/solution.json`

It must be valid UTF-8 JSON with exactly this shape:

```json
{
  "tasks": [
    {
      "task_description": "该子任务要解决的问题、目标和范围",
      "task_analysis": "该子任务的假设、建模思路、方法选择及合理性",
      "mathematical_modeling_process": "具体数学模型、公式、变量、约束和求解过程",
      "subtask_outcome_analysis": "计算结果、结果解释、模型局限和偏差分析"
    }
  ]
}
```
"""


def build_interactive_solver_prompt(
    workflow_value: dict,
    include_interaction: bool = True,
    include_draft: bool = True,
    interaction_note: str = "",
) -> str:
    """Build the Planner-to-Solver prompt with a workflow insertion point.

    ``include_interaction=False`` returns the same prompt with the
    ``# Human Expert Interaction`` section removed, which is what the
    no-interaction baseline runs on: everything else, including the submission
    contract and the pre-gathered data step, stays identical so the two arms
    differ by that one section.

    ``include_draft=False`` is the draft-free arm's prompt: the same task, the
    same submission contract and the same pre-gathered evidence, but the solver
    is told it starts from the problem statement alone and owns the modeling
    plan.  Every ``draft.md`` reference in the head and the closing step is
    replaced rather than left dangling.

    ``interaction_note`` appends one extra paragraph to the interaction section.
    """
    mmbench_section = (
        MMBENCH_SOLUTION_FILE_SECTION if _benchmark == "mmbench" else ""
    )
    # How much latitude the solver has over the draft it was handed.  Without a
    # consultation there is nothing that could justify a deviation, so the
    # baseline is told to carry the plan out as written; the interactive arm may
    # depart from it only on the strength of the expert's reply or of knowledge
    # it has established itself.
    draft_stance = (
        "Follow it as written unless the expert's reply, or knowledge you have "
        "established from the problem statement and the supplied evidence, "
        "justifies changing it. Modify assumptions, model choices, "
        "implementation strategy, and validation methods only then, and record "
        "what justified each change."
        if include_interaction
        else
        "Follow it as written. Carry out that plan without changing its "
        "assumptions, model choices, implementation strategy, or validation "
        "methods."
    )
    # The evidence file only has content to hold when there is a consultation.
    # Leaving its two mentions in place made the no-interaction arm plan a task
    # ("Record expert interaction") that can never happen.
    interaction_evidence_entry = (
        "\nInteraction evidence: `{{RESULTS_DIR}}/interaction_evidence.md`\n"
        if include_interaction
        else ""
    )
    interaction_evidence_note = (
        "\nRecord the expert question, expert reply, and how the reply affected "
        "the work in\n`{{RESULTS_DIR}}/interaction_evidence.md`. Keep this "
        "evidence separate from the submission.\n"
        if include_interaction
        else ""
    )
    # Test-only: guard rules against the runaway tool calls observed in this
    # experiment (a whole-filesystem `find` that burned 30 minutes, and a
    # nested resampling loop in the solver's own analysis script that ran into
    # the 30-minute Bash ceiling).  Appended only when the flag is set, so
    # production prompts are byte-identical.
    runaway_guard = (
        """
# Search Scope and Long Commands

Search and read only inside the four workspace directories above. Never scan
from `/`, `/tmp`, or the repository root: a whole-disk `find` has cost half an
hour here and found nothing.

Do not nest computation loops. If a calculation needs two levels of repetition,
restructure it so the inner level is a vectorized array operation, or flatten it
into a single loop.

"""
        if os.environ.get("INTERACTION_RUNAWAY_GUARD") == "1"
        else ""
    )
    if include_draft:
        intro = """# ModelingBench Task — Interactive Modeling Solver Agent

You are an advanced mathematical modeling solver agent.

Your task is to solve the given modeling problem by following the provided
modeling plan draft and collaborating with a human expert when needed.

You are NOT starting from scratch.

A previous planning agent has generated a modeling blueprint (`draft.md`).

Your role is to:

1. Review the draft.
2. Refine the modeling strategy with human expert feedback.
3. Execute the modeling workflow.
4. Produce the machine-readable solution container.
"""
        planning_draft_section = f"""## Planning Draft

A preliminary modeling blueprint is available at:

`{DRAFT_PATH_PLACEHOLDER}`

Read and analyze this file before starting. It provides planned assumptions,
candidate models, a data strategy, and validation ideas. {draft_stance}

---

"""
        first_step = ""
    else:
        intro = """# ModelingBench Task — Interactive Modeling Solver Agent

You are an advanced mathematical modeling solver agent.

Your task is to solve the given modeling problem, consulting a human expert only
where the interaction policy below requires it.

"""
        planning_draft_section = ""
        first_step = ""
    template = f"""{intro}
---

# Inputs

## Problem

Problem ID: `{{{{PROBLEM_ID}}}}`

Title: `{{{{TITLE}}}}`

Source: `{{{{SOURCE}}}}`

Problem Statement:

{{{{QUESTION}}}}

---

{planning_draft_section}

---

{INTERACTION_WORKFLOW_PLACEHOLDER}

---

# Required Workflow

1. Understand the complete problem and all requested deliverables.
2. State the necessary modeling assumptions.
3. Choose and formulate suitable models.
4. Read the empirical data already gathered for this problem at
   `{{{{DATA_DIR}}}}/external_data.md`, apply each item where it materially
   affects the model or validation, and record its sources and intended use. Do
   not search the web for further data.
5. Write and execute reproducible code when needed.
6. Analyze the results, then answer every subproblem.
7. Produce the machine-readable submission at the required path.

These seven steps are the whole task. Do every check you intend to do as part of
steps 5 and 6, then write the submission. Once it exists the task is over: do not
begin another verification, revision, or recomputation pass afterwards.

---

# Submission Requirements

The submission for this task is the machine-readable solution container
described below. That container is what the judge reads and the only deliverable
whose completeness is checked, so every part of the analysis it asks for --
assumptions, modeling approach, formulas, results, interpretation, limitations
and conclusions -- belongs in the four fields of each task.

Do not also write a separate Markdown report. It would restate the same work,
is never scored, and costs a substantial amount of time on a long problem; put
that effort into the container instead.

Do not generate or include images.

---

{mmbench_section}---

# Workspace

Workspace: `{{{{OUTPUT_DIR}}}}`

Submission: `{{{{RESULTS_DIR}}}}/solution.json`
{interaction_evidence_entry}
Code: `{{{{CODE_DIR}}}}`

Results: `{{{{RESULTS_DIR}}}}`

Data: `{{{{DATA_DIR}}}}`

Logs: `{{{{LOGS_DIR}}}}`

Create directories when needed. Those four directories already exist and are the
only entries allowed in the workspace root: put everything you produce inside
them. Do not create any other file or directory at the workspace root — a stray
entry there fails the run outright, whatever the rest of the work looks like.

Never run the same script twice. The only reason to run it again is that you
changed its code. To see more of what it printed, read
`{{{{LOGS_DIR}}}}/<script>.log` — do not re-run it with a different
tail/head/sed filter.
{interaction_evidence_note}

# Python Environment

Run all Python work with the `math_modeling` conda environment:
`/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python`. The plain
`python` on PATH is a different interpreter; always use that path.

{runaway_guard}{first_step}
"""
    if not include_draft and DRAFT_PATH_PLACEHOLDER in template:
        raise RuntimeError(
            "Draft-free Solver prompt still references the planning-draft path"
        )
    if not include_interaction:
        # Drop the section along with the separator pair that framed it, so the
        # no-interaction prompt differs from the interactive one by exactly this
        # block and nothing else.
        framed = f"---\n\n{INTERACTION_WORKFLOW_PLACEHOLDER}\n\n---\n"
        if template.count(framed) != 1:
            raise RuntimeError(
                "Interactive Solver prompt has an unexpected interaction frame"
            )
        template = template.replace(framed, "---\n", 1)
        if INTERACTION_WORKFLOW_PLACEHOLDER in template:
            raise RuntimeError(
                "Interactive Solver prompt still references the workflow placeholder"
            )
        return template
    if template.count(INTERACTION_WORKFLOW_PLACEHOLDER) != 1:
        raise RuntimeError("Interactive Solver prompt has an invalid workflow placeholder")
    return template.replace(
        INTERACTION_WORKFLOW_PLACEHOLDER,
        interaction_workflow_block(workflow_value, note=interaction_note),
        1,
    )


def fixed_initial_workflow() -> dict:
    """Return the one frozen interaction policy used by the whole run.

    This is the Claude Code arm's own seed (``STRATEGIC_DECISION_CONSULTATION``),
    not the text the OpenHands arm and the workflow-test runner pin: the two
    arms therefore start from different strengths of the same rule.  Everything
    downstream -- the gates, the utility, the evolution prompt -- is unchanged.
    """
    selected = {
        "name": "Strategic decision consultation policy",
        "purpose": (
            "Solve the task autonomously by default and consult the expert only "
            "for a high-impact strategic decision -- an ambiguous objective, "
            "fundamentally different modeling approaches, a critical assumption, "
            "or a framework choice with major downstream impact."
        ),
        "policy_text": STRATEGIC_DECISION_CONSULTATION,
        "max_exchanges": 3,
        "stop_condition": (
            "Never end the run with zero expert replies: if no uncertainty "
            "qualifies, consult once on the most consequential open modeling "
            "decision. After the first reply, stop consulting once the strategic "
            "uncertainty is resolved, the modeling direction is determined, and "
            "the remaining decisions can be handled autonomously; never exceed "
            "three expert replies."
        ),
    }
    # Test-only: replay an already-evolved policy in an isolated experiment, so
    # one policy/problem combination can be re-run without replaying the whole
    # evolution.  Unset in every production run.
    override = os.environ.get("INTERACTION_INITIAL_WORKFLOW_JSON")
    if override:
        saved = json.loads(Path(override).read_text())
        if isinstance(saved, list):
            saved = saved[0]
        selected = {
            key: saved[key]
            for key in (
                "name",
                "purpose",
                "policy_text",
                "max_exchanges",
                "stop_condition",
        )
            if key in saved
        }
    validate_workflow_with_inferred_start(selected)
    selected["workflow_id"] = workflow.workflow_id(selected)
    return selected


def initial_planning_workflows() -> list[dict]:
    """Use the single frozen policy as the initial and the initial best strategy."""
    return [fixed_initial_workflow()]


def prepare_from_planning_draft(
    problem_id: str,
    problem: dict,
    prompt_path: Path,
    round_number: int,
    repetition: int,
    experiment: Path,
    args,
) -> dict:
    """Prepare a fresh Solver workspace containing only the prior planning draft."""
    prepared = workflow.substantive.ORIGINAL_PREPARE_VALIDATION_PROBLEM(
        problem_id,
        problem,
        prompt_path,
        round_number,
        repetition,
        experiment,
        args,
    )
    output_dir = Path(prepared["output_dir"])
    # The shared evaluator resolves this source into args.baseline_reports before
    # calling this preparation hook; the legacy field name is retained for API
    # compatibility only.
    source = Path(args.baseline_reports[problem_id])
    draft_target = output_dir / "results" / "draft.md"
    if not prepared["recovered"] or not draft_target.is_file():
        shutil.copy2(source, draft_target)
    if not draft_target.read_text(encoding="utf-8", errors="replace").strip():
        raise RuntimeError(f"Planning draft is empty: {draft_target}")
    # The empirical facts the planner looked up travel with the draft.  The
    # solver prompt forbids external searches, so the file has to be staged here
    # or the run would have no factual basis and no sanctioned way to obtain one.
    # It sits beside draft.md in the draft directory: <draft_root>/output/data.
    empirical_source = source.parents[1] / "data" / "external_data.md"
    empirical_target = output_dir / "data" / "external_data.md"
    if (
        empirical_source.is_file()
        and empirical_source.read_text(encoding="utf-8", errors="replace").strip()
    ):
        if not prepared["recovered"] or not empirical_target.is_file():
            empirical_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(empirical_source, empirical_target)
    else:
        # Older draft pools predate the lookup step.  Warn rather than fail so a
        # partially regenerated pool still runs, but make the gap visible.
        print(
            f"Planning draft for {problem_id} has no data/external_data.md at "
            f"{empirical_source}; the solver will have no pre-gathered evidence.",
            flush=True,
        )
    prompt_path = Path(prepared["prompt"])
    prompt = prompt_path.read_text(encoding="utf-8")
    resolved_draft = str(draft_target.resolve())
    if DRAFT_PATH_PLACEHOLDER in prompt:
        prompt_path.write_text(
            prompt.replace(DRAFT_PATH_PLACEHOLDER, resolved_draft),
            encoding="utf-8",
        )
    elif resolved_draft not in prompt:
        raise RuntimeError(
            "Interactive Solver prompt contains neither {{DRAFT_PATH}} nor its "
            "resolved planning-draft path"
        )
    metadata_path = Path(prepared["run_dir"]) / "meta" / "run.json"
    metadata = workflow.workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "initial_draft_used": True,
            "initial_draft_source": str(source),
            "initial_draft_path": str(draft_target),
            "empirical_data_source": (
                str(empirical_source) if empirical_target.is_file() else ""
            ),
            "empirical_data_path": (
                str(empirical_target) if empirical_target.is_file() else ""
            ),
            "execution_mode": "expert_guided_planning_draft_solution",
        }
    )
    workflow.workflow_evolution.write_json(metadata_path, metadata)
    if prepared["recovered"]:
        ensure_planning_interaction_evidence(output_dir)
    return prepared


def write_planning_draft_added_content(run_dir: Path) -> Path:
    """Record solution additions relative to draft.md without an original-report copy."""
    results_dir = Path(run_dir) / "output" / "results"
    draft_path = results_dir / "draft.md"
    solution_path = results_dir / "solution_report.md"
    if not draft_path.is_file() or not solution_path.is_file():
        raise FileNotFoundError(
            f"Cannot compare missing draft/solution report under {results_dir}"
        )
    draft = draft_path.read_text(encoding="utf-8", errors="replace").splitlines()
    solution = solution_path.read_text(encoding="utf-8", errors="replace").splitlines()
    blocks = []
    for tag, _, _, start, end in difflib.SequenceMatcher(
        None, draft, solution, autojunk=False
    ).get_opcodes():
        if tag in {"insert", "replace"} and start != end:
            blocks.append((tag, solution[start:end]))
    lines = [
        "# Interaction-Attributed Added Content",
        "",
        "Generated programmatically by comparing `draft.md` with the final "
        "`solution_report.md`.",
        "",
    ]
    if not blocks:
        lines.extend(["No added or revised content was detected.", ""])
    for index, (change_type, content) in enumerate(blocks, start=1):
        lines.extend(
            [f"## Change {index} ({change_type})", "", *content, ""]
        )
    output_path = results_dir / "interaction_added_content.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def ensure_planning_interaction_evidence(output_dir: Path) -> Path:
    """Build missing evidence from controller-owned completed exchanges."""
    output_dir = Path(output_dir)
    evidence_path = output_dir / "results" / "interaction_evidence.md"
    if evidence_path.is_file() and evidence_path.read_text(
        encoding="utf-8", errors="replace"
    ).strip():
        return evidence_path
    feedback_dir = output_dir / "logs" / "operator_feedback"
    exchanges = []
    for reply_path in sorted(feedback_dir.glob("expert_reply_*.json")):
        payload = workflow.workflow_evolution.read_json(reply_path, {})
        answer = str(payload.get("answer", "")).strip()
        if payload.get("ok") is not True or not answer:
            continue
        suffix = reply_path.stem.removeprefix("expert_reply_")
        question_path = feedback_dir / f"expert_question_{suffix}.md"
        question = (
            question_path.read_text(encoding="utf-8", errors="replace").strip()
            if question_path.is_file()
            else "Question text unavailable."
        )
        exchanges.append((suffix, question, answer))
    if not exchanges:
        return evidence_path
    lines = [
        "# Interaction Evidence",
        "",
        "Generated from the controller-owned expert exchange artifacts.",
        "",
    ]
    for suffix, question, answer in exchanges:
        lines.extend(
            [
                f"## Exchange {suffix}",
                "",
                "### Agent question",
                "",
                question,
                "",
                "### Expert reply",
                "",
                answer,
                "",
            ]
        )
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text("\n".join(lines), encoding="utf-8")
    return evidence_path


def run_planning_draft_solution_check(prepared: dict) -> Path:
    """Validate the planning draft and final Solver artifacts directly."""
    output_dir = Path(prepared["output_dir"])
    results_dir = output_dir / "results"
    checks = []

    def require_text(relative: str) -> str:
        path = output_dir / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise RuntimeError(f"Cannot read UTF-8 artifact {relative}: {error}") from error
        if not text.strip():
            raise RuntimeError(f"Required artifact is empty: {relative}")
        if "\x00" in text:
            raise RuntimeError(f"NUL bytes detected in text artifact: {relative}")
        checks.append({"check": "utf8_nonempty", "path": relative, "passed": True})
        return text

    ensure_planning_interaction_evidence(output_dir)
    draft = require_text("results/draft.md")
    solution = require_text("results/solution_report.md")
    require_text("results/interaction_evidence.md")
    if draft == solution:
        raise RuntimeError("Final report is byte-for-byte identical to draft.md")
    checks.append({"check": "draft_expanded_into_solution", "passed": True})
    if workflow.substantive.has_expert_interaction_impact_section(solution):
        raise RuntimeError(
            "Final report must not contain an 'Expert Interaction Impact' section"
        )
    checks.append({"check": "expert_impact_section_absent", "passed": True})
    if not any(
        payload.get("ok") is True and str(payload.get("answer", "")).strip()
        for payload in (
            workflow.workflow_evolution.read_json(path, {})
            for path in sorted(
                (output_dir / "logs" / "operator_feedback").glob("expert_reply_*.json")
            )
        )
    ):
        raise RuntimeError("No successful expert reply is available")
    checks.append({"check": "successful_expert_reply", "passed": True})
    output_path = results_dir / "refinement_validation.json"
    workflow.workflow_evolution.write_json(
        output_path,
        {
            "generated_at": workflow.substantive.now(),
            "generated_by": "python_controller",
            "execution_count": 1,
            "checks": checks,
            "passed": True,
        },
    )
    return output_path


def runtime_args_with_immediate_agent_start(*args, **kwargs):
    run_args = _original_runtime_args(*args, **kwargs)
    run_args.pipeline_agent_start = True
    run_args.require_clean_task_workspace = True
    if _benchmark == "mmbench":
        # The shared parser knows nothing about MM-Bench, and the planning
        # drafts were resolved once in main() rather than discovered per task.
        run_args.benchmark = "mmbench"
        run_args.mmbench_root = _mmbench_root
        run_args.baseline_reports = dict(_mmbench_draft_reports)
        for name, value in _mmbench_judge.items():
            if value is not None:
                setattr(run_args, f"mmbench_judge_{name}", value)
    return run_args


def execute_cpe_evaluation_with_phase_concurrency(
    experiment: Path,
    round_number: int,
    phase: str,
    split_name: str,
    problem_ids: list[str],
    interaction_workflow: dict,
    fixed_rubric: dict,
    problems: dict,
    run_args,
    enforce_gate: bool,
    original_scores: dict[str, dict],
):
    """Use one immediately-started worker per task in the current CPE phase."""
    if not problem_ids:
        raise ValueError(f"CPE {split_name} phase has no problems")
    phase_args = copy.copy(run_args)
    # Training problems repeat so the phase score is an average over several
    # independent agent runs; validation keeps the configured repetition count.
    repetitions = (
        DEFAULT_TRAIN_REPETITIONS
        if split_name == "train"
        else run_args.validation_repetitions
    )
    phase_args.validation_repetitions = repetitions
    # One worker per agent run this phase will actually execute.  Derived from
    # the problem count and the repetition count instead of pinned, so changing
    # either keeps the phase fully parallel.
    run_count = len(problem_ids) * repetitions
    phase_args.concurrency = run_count
    phase_args.retry_concurrency = run_count
    # Judging happens once per aggregated problem result, not once per run.
    phase_args.judge_concurrency = len(problem_ids)
    phase_args.pipeline_agent_start = True
    print(
        f"CPE {split_name} phase {phase}: problems={len(problem_ids)}, "
        f"repetitions={repetitions} ({run_count} agent runs), "
        f"agent concurrency={run_count}, immediate start enabled",
        flush=True,
    )
    return _original_execute_cpe_evaluation(
        experiment,
        round_number,
        phase,
        split_name,
        problem_ids,
        interaction_workflow,
        fixed_rubric,
        problems,
        phase_args,
        enforce_gate,
        original_scores,
    )


def parse_args_with_pool_defaults():
    args = _original_parse_args()


    def supplied(option: str) -> bool:
        return any(value == option or value.startswith(option + "=") for value in sys.argv[1:])

    # Scoped to this launcher: the shared engine keeps its own --thinking
    # default, so other experiments that delegate to it are unaffected.
    if not supplied("--thinking"):
        args.thinking = DEFAULT_THINKING_LEVEL
    if not supplied("--train-batch-size"):
        args.train_batch_size = DEFAULT_INITIAL_DRAFT_TRAIN_BATCH_SIZE
    # record_config() runs after the monkey-patches are restored, so capture the
    # effective margins here rather than reading the module globals later.
    _effective_evolution["train_acceptance_margin"] = DEFAULT_TRAIN_ACCEPTANCE_MARGIN
    _effective_evolution["validation_acceptance_margin"] = (
        DEFAULT_VALIDATION_ACCEPTANCE_MARGIN
    )
    # Every report is judged this many times in parallel and averaged.
    if not supplied("--judge-repeats"):
        args.judge_repeats = DEFAULT_JUDGE_REPEATS
    if not supplied("--validation-size"):
        args.validation_size = len(VALIDATION_PROBLEMS)
    # CPE evaluations replace this base value with the size of their current
    # problem list: the sampled train batch or the complete validation pool.
    phase_concurrency = args.train_batch_size
    if not supplied("--concurrency"):
        args.concurrency = phase_concurrency
    if not supplied("--retry-concurrency"):
        args.retry_concurrency = phase_concurrency
    if not supplied("--judge-concurrency"):
        args.judge_concurrency = phase_concurrency
    # Every role runs against the locally served model.  The shared parser's
    # defaults name DeepSeek models and carry no credentials, so leaving them
    # alone would send the optimizer, the expert and the MM-Bench judge to
    # api.deepseek.com.  The judge reads the optimizer's credentials when it has
    # none of its own, so --opt-base-url/--opt-api-key cover both.
    for option, attribute, value in (
        ("--model", "model", LOCAL_MODEL),
        ("--opt-model", "opt_model", LOCAL_MODEL),
        ("--opt-base-url", "opt_base_url", LOCAL_BASE_URL),
        ("--opt-api-key", "opt_api_key", LOCAL_API_KEY),
        ("--expert-model", "expert_model", LOCAL_MODEL),
        ("--expert-base-url", "expert_base_url", LOCAL_BASE_URL),
        ("--expert-api-key", "expert_api_key", LOCAL_API_KEY),
        ("--judge-feedback-model", "judge_feedback_model", LOCAL_MODEL),
    ):
        if not supplied(option):
            setattr(args, attribute, value)
    # Surfaced in the run's config.json so the recorded configuration names the
    # endpoint that actually served each solver run.
    for attribute, value in claude_backend.default_settings().items():
        setattr(args, attribute, value)
    # Claude Code keeps no agent registry, so the framework's registration and
    # cleanup calls are answered by the stub rather than a real OpenClaw install.
    if not supplied("--openclaw-command"):
        args.openclaw_command = str(claude_backend.REGISTRY_STUB)
    # See LOCAL_FIXED_RUBRIC: the engine's default names a rubric this
    # repository does not contain.
    if not supplied("--fixed-rubric"):
        args.fixed_rubric = str(LOCAL_FIXED_RUBRIC)
    return args


def experiment_path(value: str | None) -> tuple[Path, bool]:
    global _active_experiment
    if value:
        path = Path(value).resolve()
        _active_experiment = path
        return path, path.is_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = EXPERIMENT_ROOT / f"{EXPERIMENT_PREFIX}_{stamp}"
    _active_experiment = path
    return path, False


def record_config() -> None:
    if _active_experiment is None:
        return
    path = _active_experiment / "config.json"
    config = workflow.workflow_evolution.read_json(path, {})
    if not config:
        return
    config.update(
        {
            "initial_draft_used": True,
            "initial_draft_source_roots": {
                "train": str(_draft_train_root) if _draft_train_root else None,
                "validation": str(_draft_validation_root) if _draft_validation_root else None,
            },
            "initial_draft_train_pool_size": len(TRAIN_PROBLEMS),
            "initial_draft_validation_pool_size": len(VALIDATION_PROBLEMS),
            "phase_agent_concurrency": {
                "train": "current_train_batch_size",
                "validation": "complete_validation_pool_size",
                "pipeline_agent_start": True,
            },
            "interaction_latency_cost_ignored": True,
            "solver_prompt": "interactive_modeling_solver_agent_from_planning_draft",
            "benchmark": _benchmark,
            "mmbench_root": str(_mmbench_root) if _benchmark == "mmbench" else None,
            "mmbench_split": (
                {
                    "test": list(MMBENCH_TEST_PROBLEMS),
                    "validation": list(MMBENCH_VALIDATION_PROBLEMS),
                    "train": list(MMBENCH_TRAIN_PROBLEMS),
                    "unused_older_tasks": "44 tasks dated 2014_B and earlier",
                }
                if _benchmark == "mmbench"
                else None
            ),
            "training_parent_count": _effective_evolution.get("training_parent_count"),
            "evolution_modes": _effective_evolution.get("evolution_modes"),
            "train_repetitions_per_problem": DEFAULT_TRAIN_REPETITIONS,
            "train_acceptance_margin": _effective_evolution.get("train_acceptance_margin"),
            "validation_acceptance_margin": _effective_evolution.get(
                "validation_acceptance_margin"
            ),
            "initial_workflows": ["modeling_strategy_escalation_policy"],
            "initial_evaluation_schedule": {
                "round_0": "validate_initial_parent",
                "round_1": "train_initial_parent_then_evolve_candidate",
                "round_1_parent_validation": False,
            },
        }
    )
    workflow.workflow_evolution.write_json(path, config)


def mmbench_support():
    """Import the MMBench helpers, which import this module back."""
    try:
        from . import run_substantive_interaction_workflow_test_from_initial_draft as support
    except ImportError:  # pragma: no cover - direct-file invocation support
        from src.OpenClaw import (
            run_substantive_interaction_workflow_test_from_initial_draft as support,
        )
    return support


def default_mmbench_draft_roots() -> list[Path]:
    """Every planner run that published MM-Bench planning drafts."""
    return sorted(
        (REPO_ROOT / "openclaw_experiments").glob(
            "interaction_strategy_clean_baseline_initial_draft_mmbench_*"
        )
    )


def configure_problem_pools(sources: argparse.Namespace) -> None:
    """Populate the train/validation pools for the selected benchmark."""
    global _draft_train_root, _draft_validation_root
    global _benchmark, _mmbench_root, _mmbench_problems
    global TRAIN_PROBLEMS, VALIDATION_PROBLEMS
    _benchmark = sources.benchmark
    _mmbench_root = (sources.mmbench_root or DEFAULT_MMBENCH_ROOT).resolve()

    if _benchmark == "mmbench":
        # The MM-Bench split is fixed by publication year rather than discovered
        # from draft artifacts, so every run uses the same pools.  Loading the
        # problems and resolving their drafts here fails fast, before any agent
        # starts, if a draft is missing.
        TRAIN_PROBLEMS = list(MMBENCH_TRAIN_PROBLEMS)
        # Narrow the training pool to the named tasks (comma-separated).  Used to
        # keep only the single-model tasks, whose plans carry no sub-model blocks
        # and therefore cost far less per CPE round.  The split file is untouched;
        # unset in every run that should use the full publication-year pool.
        light = [
            value.strip()
            for value in os.environ.get("MMBENCH_TRAIN_POOL", "").split(",")
            if value.strip()
        ]
        if light:
            TRAIN_PROBLEMS = light
        # Test-only: pin the validation pool to the named tasks so a single
        # policy/problem combination can be replayed on its own.  Unset in every
        # production run, where the pool is the fixed publication-year split.
        pinned = [
            value.strip()
            for value in os.environ.get("MMBENCH_PIN_VALIDATION", "").split(",")
            if value.strip()
        ]
        VALIDATION_PROBLEMS = pinned or list(MMBENCH_VALIDATION_PROBLEMS)
        _draft_train_root = _draft_validation_root = None
        roots = [
            path.resolve()
            for path in (sources.planning_draft_root or default_mmbench_draft_roots())
        ]
        support = mmbench_support()
        _mmbench_problems, problem_ids = support.load_mmbench_problems(
            _mmbench_root, [*TRAIN_PROBLEMS, *VALIDATION_PROBLEMS]
        )
        _mmbench_draft_reports.update(
            support.resolve_planning_drafts(roots, problem_ids)
        )
        print(
            "MM-Bench split: "
            f"train={len(TRAIN_PROBLEMS)}, validation={len(VALIDATION_PROBLEMS)}, "
            f"test={len(MMBENCH_TEST_PROBLEMS)}; "
            f"drafts={len(_mmbench_draft_reports)}; "
            f"default train batch={DEFAULT_INITIAL_DRAFT_TRAIN_BATCH_SIZE}",
            flush=True,
        )
        return

    _draft_train_root = (
        sources.planning_draft_train_root or PLANNING_DRAFT_TRAIN_ROOT
    ).resolve()
    _draft_validation_root = (
        sources.planning_draft_validation_root or PLANNING_DRAFT_VALIDATION_ROOT
    ).resolve()
    TRAIN_PROBLEMS = discover_planning_draft_problem_ids(_draft_train_root)
    discovered_validation_problems = discover_planning_draft_problem_ids(
        _draft_validation_root
    )
    if len(discovered_validation_problems) < DEFAULT_INITIAL_DRAFT_VALIDATION_SIZE:
        raise ValueError(
            "Planning-draft validation pool has fewer than "
            f"{DEFAULT_INITIAL_DRAFT_VALIDATION_SIZE} completed drafts"
        )
    VALIDATION_PROBLEMS = discovered_validation_problems[
        :DEFAULT_INITIAL_DRAFT_VALIDATION_SIZE
    ]
    overlap = sorted(set(TRAIN_PROBLEMS) & set(VALIDATION_PROBLEMS))
    if overlap:
        raise ValueError(
            "Planning-draft train and validation pools overlap: "
            + ", ".join(overlap)
        )
    print(
        "Planning-draft pools: "
        f"train={len(TRAIN_PROBLEMS)}, validation={len(VALIDATION_PROBLEMS)}; "
        f"default train batch={DEFAULT_INITIAL_DRAFT_TRAIN_BATCH_SIZE}",
        flush=True,
    )


def main() -> None:
    global _initialize_only, _round0_only
    sources = parse_planning_draft_sources()
    _initialize_only = "--initialize-only" in sys.argv[1:]
    # Read from the extension namespace: parse_planning_draft_sources has
    # already stripped --round0-only out of sys.argv by this point.
    _round0_only = bool(sources.round0_only)
    _mmbench_judge.update(
        {
            "model": sources.mmbench_judge_model,
            "api_key": sources.mmbench_judge_api_key,
            "base_url": sources.mmbench_judge_base_url,
            "timeout": sources.mmbench_judge_timeout,
        }
    )
    configure_problem_pools(sources)

    workflow.load_cpe_split = load_current_draft_split
    workflow.parse_args = parse_args_with_pool_defaults
    workflow.substantive.BASELINE_REPORT_ROOT = _draft_train_root or REPO_ROOT
    workflow.substantive.DEFAULT_PROBLEMS = tuple(VALIDATION_PROBLEMS)
    workflow.substantive.resolve_baseline_report = resolve_planning_draft
    workflow.substantive.baseline_report_matches_problem = planning_draft_matches_problem
    # One interaction strategy at a time: the single constant that gates every
    # parent/elite count in the shared module becomes 1, so the initial strategy
    # is also the initial best strategy and each round evolves one candidate.
    workflow.CPE_TRAINING_PARENT_COUNT = 1
    # Crossover needs two parents; with one live policy only mutation is coherent.
    workflow.CPE_EVOLUTION_MODES = frozenset({"mutation"})
    # A gate has to clear the re-run noise of the score it compares, and the two
    # gates compare scores of different variance.
    workflow.CPE_TRAIN_ACCEPTANCE_EPSILON = DEFAULT_TRAIN_ACCEPTANCE_MARGIN
    workflow.CPE_VALIDATION_ACCEPTANCE_EPSILON = DEFAULT_VALIDATION_ACCEPTANCE_MARGIN
    _effective_evolution.update(
        {
            "training_parent_count": workflow.CPE_TRAINING_PARENT_COUNT,
            "evolution_modes": sorted(workflow.CPE_EVOLUTION_MODES),
        }
    )
    if _benchmark == "mmbench":
        support = mmbench_support()
        workflow.baseline.load_problems = lambda: _mmbench_problems
        workflow.substantive.prepare_refinement_validation_problem = partial(
            support.prepare_mmbench_from_planning_draft, _mmbench_root
        )
        workflow.interaction.judge_report = partial(
            support.judge_report_with_mmbench, _mmbench_problems, _mmbench_root
        )
    else:
        workflow.substantive.prepare_refinement_validation_problem = (
            prepare_from_planning_draft
        )
    workflow.substantive.write_interaction_added_content = (
        write_planning_draft_added_content
    )
    workflow.substantive.run_consolidated_refinement_check = (
        run_planning_draft_solution_check
    )
    # Claude Code backend.  The engine binds interaction.run_local_modeling_phase
    # from this name while workflow.main() starts up (workflow_evolution.py:3704),
    # so the patch has to land on the source name -- patching interaction.* here
    # would be overwritten before any agent runs.
    workflow.substantive.run_substantive_modeling_phase = (
        claude_backend.run_claude_modeling_phase
    )
    # The engine calls this by bare name on its last line, so patching the module
    # attribute is enough to keep a matplotlib-free run from failing at the end.
    workflow.plot_round_average_dimension_scores = skip_round_dimension_plot
    # Without this the expert, optimizer and judge calls all come back empty.
    disable_thinking_for_direct_api_calls()
    workflow.substantive.runtime_args = runtime_args_with_immediate_agent_start
    workflow.build_workflow_refinement_prompt = build_interactive_solver_prompt
    workflow.build_cpe_workflow_evolution_prompt = (
        build_initial_draft_cpe_workflow_evolution_prompt
    )
    workflow.initial_strategy_population = initial_planning_workflows
    workflow.validate_workflow = validate_workflow_with_inferred_start
    workflow.execute_cpe_evaluation = execute_cpe_evaluation_with_phase_concurrency
    workflow.CPE_UTILITY_BASIS = workflow.CPE_UTILITY_BASIS_ABSOLUTE_SCORE
    workflow.DEFAULT_CPE_COST_PENALTY_WEIGHT = 0.05
    workflow.DEFAULT_CPE_LATENCY_COST_WEIGHT = 0.0
    workflow.ensure_cpe_original_report_scores = lambda *_args, **_kwargs: {}
    workflow.MIN_CPE_EVOLUTION_ROUNDS = None
    workflow.MAX_WORKFLOW_EXCHANGES = None
    workflow.CPE_COLLAPSE_INITIAL_PARENTS = True
    workflow.run_cpe_collapsed_initial_parent_evaluations = (
        run_initial_draft_parent_evaluations
    )
    workflow.experiment_path = experiment_path
    isolated_config = previous_config = None
    try:
        # The OpenClaw launcher rewrites a private copy of ~/.openclaw/openclaw.json
        # here to enable sub-agent tools.  Claude Code reads no such config and the
        # file does not exist on this cluster, so the step is skipped entirely.
        # Teardown is guarded by `isolated_config is not None`, so leaving both
        # names as None above keeps it a no-op.
        workflow.main(cpe_mode=True, compact_experiment_inputs=True, dialogue_operator_evolution=False)
    finally:
        workflow.load_cpe_split = _original_load_cpe_split
        workflow.parse_args = _original_parse_args
        workflow.substantive.BASELINE_REPORT_ROOT = _original_baseline_report_root
        workflow.substantive.DEFAULT_PROBLEMS = _original_default_problems
        workflow.substantive.resolve_baseline_report = _original_resolve_baseline_report
        if _original_baseline_report_matches is _missing:
            delattr(workflow.substantive, "baseline_report_matches_problem")
        else:
            workflow.substantive.baseline_report_matches_problem = _original_baseline_report_matches
        workflow.CPE_TRAINING_PARENT_COUNT = _original_training_parent_count
        workflow.CPE_EVOLUTION_MODES = _original_evolution_modes
        workflow.CPE_TRAIN_ACCEPTANCE_EPSILON = _original_train_epsilon
        workflow.CPE_VALIDATION_ACCEPTANCE_EPSILON = _original_validation_epsilon
        workflow.interaction.judge_report = _original_interaction_judge_report
        workflow.baseline.load_problems = _original_load_problems
        workflow.substantive.prepare_refinement_validation_problem = _original_prepare_refinement
        workflow.substantive.write_interaction_added_content = (
            _original_write_interaction_added_content
        )
        workflow.substantive.run_consolidated_refinement_check = (
            _original_run_consolidated_refinement_check
        )
        workflow.substantive.runtime_args = _original_runtime_args
        workflow.build_workflow_refinement_prompt = _original_build_refinement_prompt
        workflow.build_cpe_workflow_evolution_prompt = _original_build_cpe_prompt
        workflow.initial_strategy_population = _original_initial_population
        workflow.validate_workflow = _original_validate_workflow
        workflow.execute_cpe_evaluation = _original_execute_cpe_evaluation
        workflow.plot_round_average_dimension_scores = _original_plot_round_dimension
        workflow.CPE_UTILITY_BASIS = _original_utility_basis
        workflow.DEFAULT_CPE_COST_PENALTY_WEIGHT = _original_cost_weight
        workflow.DEFAULT_CPE_LATENCY_COST_WEIGHT = _original_latency_cost_weight
        workflow.ensure_cpe_original_report_scores = _original_ensure_original_scores
        workflow.MIN_CPE_EVOLUTION_ROUNDS = _original_min_rounds
        workflow.MAX_WORKFLOW_EXCHANGES = _original_max_exchanges
        workflow.CPE_COLLAPSE_INITIAL_PARENTS = _original_collapse_initial_parents
        workflow.run_cpe_collapsed_initial_parent_evaluations = (
            _original_run_collapsed_initial_parents
        )
        workflow.experiment_path = _original_experiment_path
        _initialize_only = False
        record_config()
        if isolated_config is not None:
            clean.clean_baseline.remove_clean_openclaw_config(isolated_config, previous_config)


if __name__ == "__main__":
    main()
