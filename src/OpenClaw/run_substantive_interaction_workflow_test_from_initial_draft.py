"""Run the fixed interaction policy on ModelingBench or MM-Bench tasks.

The ModelingBench mode remains pinned to its existing three-task set.  The
MM-Bench mode reads native problem definitions from ``MMBench/problem`` and
selects only tasks represented under ``MMBench/dataset``.  It stages files only
from the corresponding dataset directory and uses MM-Bench's native evaluator.
Tasks are submitted in consecutive batches of at most five.  Reuse ``--exp``
to resume an interrupted run.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Sequence

try:
    from . import run_substantive_interaction_workflow_evolution as workflow
    from . import run_substantive_interaction_workflow_evolution_from_initial_draft as initial
    from .interaction_policy import MODELING_STRATEGY_ESCALATION as INTERACTION_POLICY
except ImportError:  # pragma: no cover - direct-file invocation support
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from src.OpenClaw import run_substantive_interaction_workflow_evolution as workflow
    from src.OpenClaw import run_substantive_interaction_workflow_evolution_from_initial_draft as initial
    from src.OpenClaw.interaction_policy import MODELING_STRATEGY_ESCALATION as INTERACTION_POLICY


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
# The pinned tasks live in the master dataset, not in modeling_data_test.json.
# All three are long-running: Gamma Knife needs a shot-placement MILP,
# Gerrymandering needs large-scale geospatial computation, and Wheel Chair
# Access was the slowest task in the clean-baseline train experiment (60.6 min,
# a 25 KB model plus ten result artifacts).  They are evaluated in one batch so
# their agent runs overlap instead of running back to back.
PINNED_PROBLEM_IDS = (
    "2003_Gamma_Knife_Treatment",
    "2007_Gerrymandering",
    "2006_Wheel_Chair_Access",
)
PROBLEM_DATASET = REPO_ROOT / "data" / "modeling_data_final.json"
DEFAULT_MMBENCH_ROOT = Path(r"D:\vscode_project\LLM-MM-Agent\MMBench")
MMBENCH_EVALUATION_DIMENSIONS = (
    "analysis_evaluation",
    "modeling_rigorousness_evaluation",
    "practicality_and_scientificity_evaluation",
    "result_and_bias_analysis_evaluation",
)
# Planning drafts come from three sources: the validation and train pools hold
# the pinned ModelingBench tasks, and every MM-Bench planner run publishes its
# own root under the mmbench prefix (the one that carries 2003_B, for example).
DEFAULT_PLANNING_DRAFT_ROOTS = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_initial_draft_val_20260916_211801",
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_initial_draft_train_20260916_202307",
    *sorted(
        (REPO_ROOT / "openclaw_experiments").glob(
            "interaction_strategy_clean_baseline_initial_draft_mmbench_*"
        )
    ),
)
DEFAULT_PROMPT_TEMPLATE = SCRIPT_DIR / "prompts" / "solver_prompt.md"
DEFAULT_MMBENCH_PROMPT_TEMPLATE = (
    SCRIPT_DIR / "prompts" / "mmbench_solver_prompt.md"
)
BATCH_SIZE = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--benchmark",
        choices=("modelingbench", "mmbench"),
        default="modelingbench",
        help="Select the native problem/data/evaluation source (default: modelingbench).",
    )
    parser.add_argument(
        "--mmbench-root",
        type=Path,
        default=DEFAULT_MMBENCH_ROOT,
        help=(
            "MM-Bench root containing problem/, dataset/, and evaluation/. "
            f"Default: {DEFAULT_MMBENCH_ROOT}"
        ),
    )
    parser.add_argument(
        "--planning-draft-test-root",
        type=Path,
        nargs="+",
        default=list(DEFAULT_PLANNING_DRAFT_ROOTS),
        help=(
            "Experiment roots containing the planning drafts for the pinned "
            "tasks. Defaults to the two roots that hold them."
        ),
    )
    parser.add_argument("--exp", type=Path)
    parser.add_argument(
        "--prompt-template",
        type=Path,
        help=(
            "Override the solver prompt. Defaults to solver_prompt.md for "
            "ModelingBench and mmbench_solver_prompt.md for MM-Bench."
        ),
    )
    parser.add_argument(
        "--problem-id",
        nargs="+",
        help=(
            "ModelingBench remains pinned to "
            + ", ".join(PINNED_PROBLEM_IDS)
            + ". In MM-Bench mode, select file stems that also have a directory "
            "under MMBench/dataset; the default is every such task."
        ),
    )
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--opt-model", default="deepseek-v4-pro")
    parser.add_argument("--opt-api-key")
    parser.add_argument("--opt-base-url")
    parser.add_argument(
        "--mmbench-judge-model",
        default="deepseek-v4-flash",
        help="Model used by the native MM-Bench evaluator.",
    )
    parser.add_argument(
        "--mmbench-judge-api-key",
        help=(
            "MM-Bench Judge API key. Falls back to DEEPSEEK_JUDGE_API_KEY, "
            "then the repository optimizer credentials."
        ),
    )
    parser.add_argument(
        "--mmbench-judge-base-url",
        help=(
            "MM-Bench Judge API base URL. Falls back to "
            "DEEPSEEK_JUDGE_BASE_URL, then the repository optimizer credentials."
        ),
    )
    parser.add_argument("--mmbench-judge-timeout", type=float, default=600.0)
    parser.add_argument("--optimizer-retries", type=int, default=5)
    parser.add_argument("--expert-model", default=workflow.substantive.DEFAULT_EXPERT_MODEL)
    parser.add_argument("--expert-api-key")
    parser.add_argument("--expert-base-url")
    parser.add_argument("--expert-timeout", type=float, default=600.0)
    parser.add_argument(
        "--expert-request-timeout",
        type=float,
        default=workflow.substantive.EXPERT_REQUEST_TIMEOUT,
    )
    parser.add_argument("--expert-attempts", type=int, default=3)
    parser.add_argument("--thinking", default="off")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--concurrency", type=int, default=BATCH_SIZE)
    parser.add_argument("--judge-repeats", type=int, default=1)
    parser.add_argument("--judge-concurrency", type=int, default=BATCH_SIZE)
    parser.add_argument("--validation-repetitions", type=int, default=1)
    parser.add_argument("--validation-attempts", type=int, default=3)
    parser.add_argument("--retry-concurrency", type=int, default=BATCH_SIZE)
    parser.add_argument("--validation-retry-delay", type=float, default=10.0)
    parser.add_argument("--openclaw-command")
    parser.add_argument("--initialize-only", action="store_true")
    parser.add_argument("--enforce-substantive-interaction-gate", action="store_true")
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    if args.mmbench_judge_timeout <= 0:
        parser.error("--mmbench-judge-timeout must be positive")
    return args


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Required JSON file does not exist: {path}") from None
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error


def fixed_interaction_workflow() -> dict[str, Any]:
    """Return the one fixed policy used for every test task."""
    selected = {
        "name": "Modeling strategy escalation policy",
        "purpose": (
            "Resolve one high-impact modeling-strategy uncertainty only when "
            "autonomous analysis cannot produce a clear decision."
        ),
        "policy_text": INTERACTION_POLICY,
        "max_exchanges": 3,
        "stop_condition": (
            "Stop without consultation unless every trigger condition holds; "
            "otherwise stop after three expert replies and continue autonomously."
        ),
    }
    initial.validate_workflow_with_inferred_start(selected)
    selected["workflow_id"] = workflow.workflow_id(selected)
    return selected


def load_modelingbench_problems(
    requested: list[str] | None,
) -> tuple[dict[str, Any], list[str]]:
    """Load the pinned tasks and reject any attempt to select a different set."""
    pinned = list(PINNED_PROBLEM_IDS)
    if requested and set(requested) != set(pinned):
        raise ValueError(
            "This runner is pinned to " + ", ".join(pinned) + "; "
            f"got: {', '.join(requested)}"
        )
    problems = read_json(PROBLEM_DATASET)
    if not isinstance(problems, dict) or not problems:
        raise ValueError(f"Problem dataset must be a non-empty object: {PROBLEM_DATASET}")
    missing = [problem_id for problem_id in pinned if problem_id not in problems]
    if missing:
        raise ValueError(
            f"Missing from {PROBLEM_DATASET}: " + ", ".join(missing)
        )
    return problems, pinned


def mmbench_question(raw: dict[str, Any]) -> str:
    """Render native MM-Bench fields without changing their values or schema."""
    sections = [
        "## Background\n\n" + str(raw.get("background", "")),
        "## Problem Requirements\n\n" + str(raw.get("problem_requirement", "")),
        "## Dataset Definition\n\n```json\n"
        + json.dumps(
            {
                "dataset_path": raw.get("dataset_path", []),
                "dataset_description": raw.get("dataset_description", {}),
                "variable_description": raw.get("variable_description", {}),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n```",
    ]
    if "addendum" in raw:
        sections.append("## Addendum\n\n" + str(raw.get("addendum", "")))
    return "\n\n".join(sections)


def load_mmbench_problems(
    mmbench_root: Path, requested: list[str] | None
) -> tuple[dict[str, Any], list[str]]:
    """Load unmodified native definitions for MM-Bench tasks.

    An explicit request selects any task defined under ``problem``; some native
    tasks, such as ``2003_B``, ship no dataset directory.  Without a request the
    default stays the tasks that do have one.
    """
    root = Path(mmbench_root).resolve()
    problem_dir = root / "problem"
    dataset_dir = root / "dataset"
    evaluation_dir = root / "evaluation"
    for required in (problem_dir, dataset_dir, evaluation_dir):
        if not required.is_dir():
            raise FileNotFoundError(f"Required MM-Bench directory does not exist: {required}")

    defined = sorted(path.stem for path in problem_dir.glob("*.json") if path.is_file())
    if not defined:
        raise ValueError(f"No task definitions found under {problem_dir}")
    with_dataset = sorted(
        path.name for path in dataset_dir.iterdir() if path.is_dir()
    )
    problem_ids = list(requested) if requested else with_dataset
    if not problem_ids:
        raise ValueError(f"No task directories found under {dataset_dir}")
    unknown = sorted(set(problem_ids) - set(defined))
    if unknown:
        raise ValueError(
            "MM-Bench mode accepts only tasks defined under MMBench/problem; missing: "
            + ", ".join(unknown)
        )

    problems: dict[str, Any] = {}
    for problem_id in problem_ids:
        problem_path = problem_dir / f"{problem_id}.json"
        raw = read_json(problem_path)
        if not isinstance(raw, dict):
            raise ValueError(f"MM-Bench problem must be a JSON object: {problem_path}")
        requirement = str(raw.get("problem_requirement", ""))
        grading_point = {
            "category": "Complete problem requirements",
            "description": requirement,
        }
        problems[problem_id] = {
            "year": problem_id.split("_", 1)[0],
            "title": f"MM-Bench {problem_id}",
            "source": "MM-Bench",
            "question": mmbench_question(raw),
            "requirements": [grading_point],
            "decomposition": {"grading_points": [grading_point]},
            "eval_roles": [],
            "dataset_path": raw.get("dataset_path", []),
            "dataset_description": raw.get("dataset_description", {}),
            "variable_description": raw.get("variable_description", {}),
            "_mmbench_raw_problem": raw,
            "_mmbench_problem_file": str(problem_path.resolve()),
            "_mmbench_dataset_dir": str((dataset_dir / problem_id).resolve()),
        }
    return problems, problem_ids


def load_benchmark_problems(
    benchmark: str, mmbench_root: Path, requested: list[str] | None
) -> tuple[dict[str, Any], list[str]]:
    if benchmark == "mmbench":
        return load_mmbench_problems(mmbench_root, requested)
    return load_modelingbench_problems(requested)


def resolve_planning_drafts(
    roots: Sequence[Path], problem_ids: list[str]
) -> dict[str, str]:
    """Find one non-empty planning draft per task across every source root."""
    by_problem: dict[str, list[Path]] = {}
    for root in roots:
        for draft in Path(root).glob("**/output/results/draft.md"):
            if not draft.read_text(encoding="utf-8", errors="replace").strip():
                continue
            metadata = workflow.workflow_evolution.read_json(
                draft.parents[2] / "meta" / "run.json", {}
            )
            problem_id = metadata.get("problem_id")
            if isinstance(problem_id, str):
                by_problem.setdefault(problem_id, []).append(draft)
    missing = [problem_id for problem_id in problem_ids if problem_id not in by_problem]
    if missing:
        searched = ", ".join(str(Path(root)) for root in roots)
        raise FileNotFoundError(
            f"No non-empty planning draft for test problem(s) under {searched}: "
            + ", ".join(missing)
        )
    return {
        problem_id: str(max(by_problem[problem_id], key=lambda item: item.stat().st_mtime_ns))
        for problem_id in problem_ids
    }


def render_fixed_prompt(template_path: Path, fixed_workflow: dict[str, Any]) -> str:
    template = template_path.read_text(encoding="utf-8")
    start = template.find("# Human Expert Interaction")
    end = template.find("\n---\n\n# Required Workflow", start)
    if start < 0 or end < 0:
        raise ValueError(
            "Prompt template must contain one '# Human Expert Interaction' section "
            "followed by '# Required Workflow'."
        )
    return (
        template[:start]
        + initial.interaction_workflow_block(fixed_workflow)
        + template[end:]
    )


def prepare_mmbench_from_planning_draft(
    mmbench_root: Path,
    problem_id: str,
    problem: dict,
    prompt_path: Path,
    round_number: int,
    repetition: int,
    experiment: Path,
    args,
) -> dict:
    """Prepare the normal run, then stage only the native dataset directory."""
    prepared = initial.prepare_from_planning_draft(
        problem_id,
        problem,
        prompt_path,
        round_number,
        repetition,
        experiment,
        args,
    )
    source_root = Path(mmbench_root).resolve() / "dataset" / problem_id
    declared_paths = problem.get("dataset_path", [])
    if source_root.is_dir():
        data_dir = Path(prepared["output_dir"]) / "data"
        for source in sorted(source_root.rglob("*")):
            target = data_dir / source.relative_to(source_root)
            if source.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif source.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    elif declared_paths:
        # The native definition names dataset files that this MMBench checkout
        # does not ship (2018_B is the only such task, and its data is a COMAP
        # contest file the upstream bundle omits).  The definition is still
        # rendered verbatim into the prompt, so the agent sees what the
        # benchmark declares and copes with the absence exactly as it does for a
        # task that ships no data.  Failing here would drop the task from an
        # otherwise fixed split and invalidate comparisons across rounds.
        print(
            f"MM-Bench problem {problem_id} declares dataset files "
            f"({', '.join(map(str, declared_paths))}) but {source_root} does not "
            "exist; staging nothing.",
            flush=True,
        )
    else:
        print(
            f"MM-Bench problem {problem_id} declares no dataset; staging nothing.",
            flush=True,
        )

    metadata_path = Path(prepared["run_dir"]) / "meta" / "run.json"
    metadata = workflow.workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "benchmark": "mmbench",
            "mmbench_problem_file": str(
                (Path(mmbench_root).resolve() / "problem" / f"{problem_id}.json")
            ),
            "mmbench_dataset_source": (
                str(source_root) if source_root.is_dir() else ""
            ),
            "mmbench_declared_dataset_paths": declared_paths,
        }
    )
    workflow.workflow_evolution.write_json(metadata_path, metadata)
    return prepared


def import_mmbench_evaluator(mmbench_root: Path):
    """Import the evaluator from the user-selected MM-Bench installation.

    MM-Bench's ``load_solution_json`` returns only ``tasks``, so every Judge
    prompt is built with ``Background: None`` and empty requirements even though
    the prompt templates ask for both.  The container we hand the evaluator
    already carries ``problem_background`` and ``problem_requirement`` next to
    ``tasks``, so the loader is wrapped to forward them and the Judge scores
    against the problem statement it was always meant to see.
    """
    root = Path(mmbench_root).resolve()
    parent = str(root.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    from MMBench.evaluation import run_evaluation as native
    from MMBench.evaluation.run_evaluation import evaluate_math_modeling

    install_solution_context_loader(native)
    return evaluate_math_modeling


class SolutionWithProblemContext(dict):
    """Solution tasks that still answer ``.get()`` for the problem context.

    MM-Bench's prompt builders read ``background`` and ``problem_requirement``
    through ``.get()`` but iterate ``.items()`` as though every value were a task
    object -- which is why its own loader drops the context.  Keeping the
    context out of iteration satisfies both halves at once.
    """

    def items(self):
        return [
            (key, value) for key, value in super().items() if isinstance(value, dict)
        ]

    def values(self):
        return [value for value in super().values() if isinstance(value, dict)]


def install_solution_context_loader(native) -> None:
    """Forward the problem context from the container into the Judge prompts."""
    original = getattr(native, "load_solution_json", None)
    if original is None or getattr(original, "_carries_problem_context", False):
        return

    def load_with_problem_context(path):
        tasks = original(path)
        if not isinstance(tasks, dict):
            return tasks
        try:
            payload = json.loads(
                judge_filesystem_path(Path(path)).read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            return tasks
        if not isinstance(payload, dict):
            return tasks
        context = {
            key: payload[source]
            for key, source in (
                ("background", "problem_background"),
                ("problem_requirement", "problem_requirement"),
            )
            if payload.get(source)
        }
        if not context:
            return tasks
        return SolutionWithProblemContext({**tasks, **context})

    load_with_problem_context._carries_problem_context = True
    native.load_solution_json = load_with_problem_context


def mmbench_judge_credentials(args) -> tuple[str, str, str]:
    """Resolve Judge credentials without consuming MM-Bench's legacy .env key."""
    api_key = (
        getattr(args, "mmbench_judge_api_key", None)
        or os.getenv("DEEPSEEK_JUDGE_API_KEY")
        or getattr(args, "opt_api_key", None)
    )
    base_url = (
        getattr(args, "mmbench_judge_base_url", None)
        or os.getenv("DEEPSEEK_JUDGE_BASE_URL")
        or getattr(args, "opt_base_url", None)
    )
    source = (
        "--mmbench-judge-api-key"
        if getattr(args, "mmbench_judge_api_key", None)
        else "DEEPSEEK_JUDGE_API_KEY"
        if os.getenv("DEEPSEEK_JUDGE_API_KEY")
        else "--opt-api-key"
        if getattr(args, "opt_api_key", None)
        else "repository optimizer credentials"
    )
    if not api_key or not base_url:
        shared_key, shared_base_url = (
            workflow.workflow_evolution.optimizer_credentials(args)
        )
        api_key = api_key or shared_key
        base_url = base_url or shared_base_url
    if not str(api_key).strip() or not str(base_url).strip():
        raise ValueError(
            "MM-Bench Judge credentials are missing. Pass "
            "--mmbench-judge-api-key and --mmbench-judge-base-url, set "
            "DEEPSEEK_JUDGE_API_KEY and DEEPSEEK_JUDGE_BASE_URL, or configure "
            "the repository optimizer credentials."
        )
    return str(api_key), str(base_url), source


def mmbench_judge_llm(
    prompt: str,
    *,
    api_key: str,
    base_url: str,
    model: str,
    timeout: float,
    max_tokens: int,
) -> list[str]:
    """Call the Judge once and fail immediately on invalid authentication."""
    from openai import AuthenticationError, OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        max_retries=0,
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            # Greedy decoding: repeated Judge trials on the same solution should
            # differ only by provider-side nondeterminism, not sampling.
            temperature=0,
            max_tokens=max_tokens,
            n=1,
            top_p=0.9,
        )
    except AuthenticationError as error:
        raise RuntimeError(
            "MM-Bench Judge authentication failed. Update the credential "
            "selected by --mmbench-judge-api-key, DEEPSEEK_JUDGE_API_KEY, "
            "--opt-api-key, or secret.json."
        ) from error
    return [
        str(choice.message.content or "")
        for choice in response.choices
    ]


def native_mmbench_solution(problem: dict[str, Any], report: str) -> dict[str, Any]:
    """Build the native solution container while preserving the native question."""
    raw = problem["_mmbench_raw_problem"]
    return {
        "problem_background": raw.get("background", ""),
        "problem_requirement": raw.get("problem_requirement", ""),
        "tasks": [
            {
                "task_description": report,
                "task_analysis": report,
                "preliminary_formulas": report,
                "mathematical_modeling_process": report,
                "task_code": "",
                "is_pass": True,
                "execution_result": "",
                "solution_interpretation": report,
                "subtask_outcome_analysis": report,
            }
        ],
    }


# The native evaluator reads one element per subproblem from ``tasks`` and scores
# each dimension from a different field, so the Agent's own container is the only
# input that carries the problem decomposition.
MMBENCH_SUBTASK_TEXT_FIELDS = (
    "task_description",
    "task_analysis",
    "preliminary_formulas",
    "mathematical_modeling_process",
    "task_code",
    "execution_result",
    "solution_interpretation",
    "subtask_outcome_analysis",
)


def agent_mmbench_solution_path(run_dir: Path) -> Path:
    """Return the native solution container the Agent prompt asks for."""
    return Path(run_dir) / "output" / "results" / "solution.json"


def solution_text_field(value: Any) -> str:
    """Coerce one native solution field to the string the evaluator expects.

    The native prompts call ``.strip()`` on every field they read, so a missing
    or non-string value must not reach the evaluator as ``None`` or a list.
    """
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return str(value)


def load_agent_mmbench_solution(
    problem: dict[str, Any], run_dir: Path
) -> dict[str, Any] | None:
    """Load the Agent's per-subtask solution container, or None when unusable.

    Falls back to the single-task report container when the Agent wrote no
    solution file, wrote invalid JSON, or produced no usable subtask element.
    """
    path = agent_mmbench_solution_path(run_dir)
    if not judge_filesystem_path(path).is_file():
        print(
            f"No Agent solution file at {path}; scoring the report container.",
            flush=True,
        )
        return None
    try:
        data = json.loads(judge_filesystem_path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(
            f"Ignoring unreadable Agent solution file {path}: {error}; "
            "scoring the report container.",
            flush=True,
        )
        return None
    raw_tasks = data.get("tasks") if isinstance(data, dict) else None
    tasks: list[dict[str, Any]] = []
    for raw_task in raw_tasks if isinstance(raw_tasks, list) else []:
        if not isinstance(raw_task, dict):
            continue
        container: dict[str, Any] = {
            field: solution_text_field(raw_task.get(field))
            for field in MMBENCH_SUBTASK_TEXT_FIELDS
        }
        container["is_pass"] = raw_task.get("is_pass") is not False
        tasks.append(container)
    if not tasks:
        print(
            f"Ignoring Agent solution file without usable subtasks: {path}; "
            "scoring the report container.",
            flush=True,
        )
        return None
    raw = problem["_mmbench_raw_problem"]
    return {
        "problem_background": raw.get("background", ""),
        "problem_requirement": raw.get("problem_requirement", ""),
        "tasks": tasks,
    }


def judge_filesystem_path(path: Path) -> Path:
    """Reuse the shared Windows long-path prefix for deep judge artifacts.

    Run directories under a CPE evaluation already pass 200 characters, and the
    native evaluator appends ``evaluation_result/solution/...`` to them, so its
    plain ``open()`` calls fail past MAX_PATH without this prefix.
    """
    return workflow.workflow_evolution._json_filesystem_path(path)


def copy_judge_artifacts(source_root: Path, target_root: Path) -> None:
    """Copy an artifact tree, tolerating long paths on both ends."""
    source_root = judge_filesystem_path(source_root)
    if not source_root.is_dir():
        return
    for source in sorted(source_root.rglob("*")):
        target = judge_filesystem_path(target_root / source.relative_to(source_root))
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def mmbench_dimension_scores(native_result: dict[str, Any]) -> dict[str, float]:
    """Normalize MM-Bench's native 1-10 scores for the shared controller."""
    scores: dict[str, float] = {}
    missing: list[str] = []
    for dimension in MMBENCH_EVALUATION_DIMENSIONS:
        entries = native_result.get(dimension, {})
        values = [
            float(entry["score"])
            for entry in entries.values()
            if isinstance(entry, dict)
            and isinstance(entry.get("score"), (int, float))
        ] if isinstance(entries, dict) else []
        if len(values) != 2:
            missing.append(dimension)
        else:
            scores[dimension] = sum(values) / len(values) / 10.0
    if missing:
        raise RuntimeError(
            "MM-Bench evaluator returned incomplete dimensions: " + ", ".join(missing)
        )
    return scores


def mean_dimension_score(scores: dict[str, float]) -> float:
    """Collapse the four controller-normalized dimensions into a total score."""
    return sum(scores[name] for name in MMBENCH_EVALUATION_DIMENSIONS) / len(
        MMBENCH_EVALUATION_DIMENSIONS
    )


def judge_report_with_mmbench(
    problems: dict[str, Any],
    mmbench_root: Path,
    problem_id: str,
    result: dict,
    round_number: int,
    experiment: Path,
    args,
) -> dict:
    """Evaluate the report through MM-Bench's unchanged native evaluator."""
    del round_number, experiment
    evaluate_math_modeling = import_mmbench_evaluator(mmbench_root)
    api_key, base_url, credential_source = mmbench_judge_credentials(args)
    judge_model = str(args.mmbench_judge_model)
    judge_timeout = float(args.mmbench_judge_timeout)
    # Score the Agent's own per-subtask container when it exists.  The native
    # evaluator reads a different field per dimension, so the report fallback
    # repeats one report into every field and drops the problem decomposition.
    agent_solution = load_agent_mmbench_solution(
        problems[problem_id], Path(result["run_dir"])
    )
    if agent_solution is None:
        container = native_mmbench_solution(
            problems[problem_id],
            judge_filesystem_path(
                Path(result["final_report"])
            ).read_text(encoding="utf-8", errors="replace"),
        )
        solution_source = "final_report"
    else:
        container = agent_solution
        solution_source = "agent_solution"
    judge_root = Path(result["run_dir"]) / "meta" / "mmbench_judge"
    judge_filesystem_path(judge_root).mkdir(parents=True, exist_ok=True)

    def run_judge_trial(trial: int) -> tuple[dict[str, float], dict[str, Any]]:
        """Score the container once inside this trial's own directory."""
        trial_dir = judge_root / f"trial_{trial}"
        judge_filesystem_path(trial_dir).mkdir(parents=True, exist_ok=True)
        solution_path = trial_dir / "solution.json"
        workflow.workflow_evolution.write_json(solution_path, container)
        llm = lambda prompt: mmbench_judge_llm(
            prompt,
            api_key=api_key,
            base_url=base_url,
            model=judge_model,
            timeout=judge_timeout,
            max_tokens=int(os.getenv("MMBENCH_JUDGE_MAX_TOKENS", "8192")),
        )
        native_dir = trial_dir / "evaluation_result"
        native_path = native_dir / "solution" / "evaluation_results.json"
        # The native evaluator writes beside the solution file with plain
        # open(), which fails once this run directory passes Windows MAX_PATH.
        # Evaluate from a short staging directory, seeded with anything a
        # previous attempt already scored so its per-dimension resume still
        # works, then keep the artifacts in their usual place.
        with tempfile.TemporaryDirectory(prefix="mmbench-judge-") as staging_root:
            staging = Path(staging_root)
            copy_judge_artifacts(native_dir, staging / "evaluation_result")
            staged_solution = staging / "solution.json"
            workflow.workflow_evolution.write_json(staged_solution, container)
            evaluate_math_modeling(llm, str(staged_solution))
            copy_judge_artifacts(staging / "evaluation_result", native_dir)
        if not judge_filesystem_path(native_path).is_file():
            raise RuntimeError(f"MM-Bench evaluator did not produce: {native_path}")
        native_result = read_json(judge_filesystem_path(native_path))
        scores = mmbench_dimension_scores(native_result)
        return scores, {
            "trial": trial,
            "native_result": str(native_path.resolve()),
            "dimension_scores": scores,
            "total_score": mean_dimension_score(scores),
            "raw_result": native_result,
        }

    # Trials are independent: each owns a trial_N directory and runs the native
    # evaluator in its own staging directory, so they run concurrently.  Keep
    # them ordered by trial index because the averages and the stability record
    # below are index-sensitive.
    repeats = int(args.judge_repeats)
    with ThreadPoolExecutor(max_workers=max(1, repeats)) as executor:
        completed = list(executor.map(run_judge_trial, range(1, repeats + 1)))
    trial_scores = [scores for scores, _ in completed]
    trial_results = [entry for _, entry in completed]

    dimensions = {
        name: sum(scores[name] for scores in trial_scores) / len(trial_scores)
        for name in MMBENCH_EVALUATION_DIMENSIONS
    }
    trial_total_scores = [mean_dimension_score(scores) for scores in trial_scores]
    average_score = sum(trial_total_scores) / len(trial_total_scores)
    stability_path = judge_root / "judge_stability.json"
    stability_payload = {
        "problem_id": problem_id,
        "evaluator": str(
            (Path(mmbench_root).resolve() / "evaluation" / "run_evaluation.py")
        ),
        "native_score_scale": "1-10",
        "controller_score_scale": "0.1-1.0",
        "judge_model": judge_model,
        "judge_base_url": base_url,
        "judge_credential_source": credential_source,
        "solution_source": solution_source,
        "agent_solution_file": str(
            agent_mmbench_solution_path(result["run_dir"])
        ),
        "subtask_count": len(container["tasks"]),
        "trials": trial_results,
        "trial_total_scores": trial_total_scores,
        "average_dimension_scores": dimensions,
        "average_score": average_score,
    }
    workflow.workflow_evolution.write_json(stability_path, stability_payload)
    return {
        "average_score": average_score,
        "dimension_scores": dimensions,
        "judge_repeats": len(trial_results),
        "judge_stability_result": str(stability_path),
        "judge_result": trial_results[-1]["raw_result"],
        "solution_source": solution_source,
        "subtask_count": len(container["tasks"]),
    }


def chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def experiment_path(value: Path | None) -> Path:
    if value is not None:
        return value.resolve()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return REPO_ROOT / "openclaw_experiments" / f"interaction_workflow_initial_draft_test_{stamp}"


def main() -> None:
    args = parse_args()
    selected_workflow = fixed_interaction_workflow()
    mmbench_root = args.mmbench_root.resolve()
    problems, problem_ids = load_benchmark_problems(
        args.benchmark, mmbench_root, args.problem_id
    )
    draft_roots = [Path(root).resolve() for root in args.planning_draft_test_root]
    baseline_reports = resolve_planning_drafts(draft_roots, problem_ids)
    template_path = (
        args.prompt_template
        or (
            DEFAULT_MMBENCH_PROMPT_TEMPLATE
            if args.benchmark == "mmbench"
            else DEFAULT_PROMPT_TEMPLATE
        )
    ).resolve()
    if not template_path.is_file():
        raise FileNotFoundError(f"Prompt template does not exist: {template_path}")

    experiment = experiment_path(args.exp)
    experiment.mkdir(parents=True, exist_ok=True)
    config_path = experiment / "config.json"
    existing_config = workflow.workflow_evolution.read_json(config_path, {})
    configuration = {
        "experiment_type": "fixed_interaction_policy_test_from_initial_draft",
        "rounds": 1,
        "benchmark": args.benchmark,
        "split": (
            "mmbench_dataset_tasks"
            if args.benchmark == "mmbench"
            else "pinned_task_set"
        ),
        "problem_ids": list(problem_ids),
        "batch_size": BATCH_SIZE,
        "task_count": len(problem_ids),
        "planning_draft_test_roots": [str(root) for root in draft_roots],
        "prompt_template": str(template_path),
        "workflow_source": "built_in_fixed_interaction_policy",
        "workflow_id": selected_workflow["workflow_id"],
    }
    if args.benchmark == "mmbench":
        configuration["mmbench_root"] = str(mmbench_root)
    if existing_config and any(
        existing_config.get(key) != value
        for key, value in configuration.items()
        if key in existing_config
    ):
        raise ValueError("Existing --exp was created with incompatible test settings")
    workflow.workflow_evolution.write_json(config_path, {**existing_config, **configuration})

    run_args = initial.runtime_args_with_immediate_agent_start(args, baseline_reports)
    run_args.concurrency = BATCH_SIZE
    run_args.retry_concurrency = BATCH_SIZE
    run_args.judge_concurrency = BATCH_SIZE
    run_args.evaluation_problem_ids = tuple(problem_ids)
    run_args.benchmark = args.benchmark
    run_args.mmbench_root = mmbench_root
    run_args.mmbench_judge_model = args.mmbench_judge_model
    run_args.mmbench_judge_api_key = args.mmbench_judge_api_key
    run_args.mmbench_judge_base_url = args.mmbench_judge_base_url
    run_args.mmbench_judge_timeout = args.mmbench_judge_timeout
    fixed_rubric = workflow.substantive.load_rubric()

    saved = {
        "prepare": workflow.substantive.prepare_refinement_validation_problem,
        "write": workflow.substantive.write_interaction_added_content,
        "check": workflow.substantive.run_consolidated_refinement_check,
        "prompt": workflow.build_workflow_refinement_prompt,
        "validate": workflow.validate_workflow,
        "interaction_validation_problems": workflow.interaction.VALIDATION_PROBLEMS,
        "interaction_rubric": workflow.interaction.INITIAL_RUBRIC,
        "interaction_finalize": workflow.interaction.finalize_interaction_receipt,
        "interaction_modeling": workflow.interaction.run_local_modeling_phase,
        "interaction_prepare": workflow.interaction.prepare_validation_problem,
        "interaction_bridge": workflow.interaction.serve_expert_requests,
        "interaction_judge": workflow.interaction.judge_report,
        "expert_role_prompt": workflow.baseline.HUMAN_MODELING_EXPERT_ROLE_PROMPT,
        "operator_role_prompts": workflow.baseline.create_operator_role_prompts,
        "utility_basis": workflow.CPE_UTILITY_BASIS,
    }
    isolated_config = previous_config = None
    try:
        if args.benchmark == "mmbench":
            workflow.substantive.prepare_refinement_validation_problem = partial(
                prepare_mmbench_from_planning_draft, mmbench_root
            )
            workflow.interaction.judge_report = partial(
                judge_report_with_mmbench, problems, mmbench_root
            )
        else:
            workflow.substantive.prepare_refinement_validation_problem = (
                initial.prepare_from_planning_draft
            )
        workflow.substantive.write_interaction_added_content = initial.write_planning_draft_added_content
        workflow.substantive.run_consolidated_refinement_check = initial.run_planning_draft_solution_check
        workflow.build_workflow_refinement_prompt = lambda value: render_fixed_prompt(
            template_path, selected_workflow
        )
        workflow.validate_workflow = initial.validate_workflow_with_inferred_start
        # This runner starts from a planning draft and passes no original-report
        # scores, so quality *gain* is undefined.  Score the run on its own mean
        # report score instead, as the sibling from-initial-draft launcher does.
        workflow.CPE_UTILITY_BASIS = workflow.CPE_UTILITY_BASIS_ABSOLUTE_SCORE
        # execute_cpe_evaluation delegates task execution to the shared interaction
        # evaluator.  Install the same substantive bindings as the full workflow
        # entry point so the controller consumes expert_question_N.md, creates the
        # request/reply JSON pair, and prepares the planning draft before launch.
        workflow.interaction.VALIDATION_PROBLEMS = tuple(problem_ids)
        workflow.interaction.INITIAL_RUBRIC = fixed_rubric
        workflow.interaction.finalize_interaction_receipt = (
            workflow.finalize_workflow_receipt
        )
        workflow.interaction.run_local_modeling_phase = (
            workflow.substantive.run_substantive_modeling_phase
        )
        workflow.interaction.prepare_validation_problem = (
            workflow.prepare_workflow_validation_problem
        )
        workflow.interaction.serve_expert_requests = (
            workflow.substantive.serve_substantive_expert_requests
        )
        workflow.baseline.HUMAN_MODELING_EXPERT_ROLE_PROMPT = (
            workflow.substantive.SUBSTANTIVE_EXPERT_ROLE_PROMPT
        )
        workflow.baseline.create_operator_role_prompts = (
            workflow.substantive.create_substantive_operator_role_prompt
        )
        if not args.initialize_only:
            isolated_config, previous_config = initial.clean.activate_subagent_enabled_openclaw_config()

        batches = chunks(problem_ids, BATCH_SIZE)
        for batch_index, batch in enumerate(batches, start=1):
            cumulative = problem_ids[: batch_index * BATCH_SIZE]
            current_args = copy.copy(run_args)
            current_args.concurrency = len(batch)
            current_args.retry_concurrency = len(batch)
            current_args.judge_concurrency = len(batch)
            print(
                f"Test batch {batch_index}/{len(batches)}: {len(batch)} task(s), "
                f"concurrency={len(batch)}; cumulative tasks={len(cumulative)}",
                flush=True,
            )
            result, failures = workflow.execute_cpe_evaluation(
                experiment,
                0,
                "selected_test_workflow",
                "test",
                cumulative,
                selected_workflow,
                fixed_rubric,
                problems,
                current_args,
                args.enforce_substantive_interaction_gate,
                {},
            )
            if failures:
                raise RuntimeError(f"Substantive-interaction gate failures: {failures}")
            if args.initialize_only:
                break
        result_path = (
            experiment / "cpe_evaluations" / "round_0" / "selected_test_workflow"
            / "workflows" / "round_0" / "result.json"
        )
        print(f"Test evaluation complete: {result_path}", flush=True)
    finally:
        workflow.substantive.prepare_refinement_validation_problem = saved["prepare"]
        workflow.substantive.write_interaction_added_content = saved["write"]
        workflow.substantive.run_consolidated_refinement_check = saved["check"]
        workflow.build_workflow_refinement_prompt = saved["prompt"]
        workflow.validate_workflow = saved["validate"]
        workflow.interaction.VALIDATION_PROBLEMS = saved[
            "interaction_validation_problems"
        ]
        workflow.interaction.INITIAL_RUBRIC = saved["interaction_rubric"]
        workflow.interaction.finalize_interaction_receipt = saved[
            "interaction_finalize"
        ]
        workflow.interaction.run_local_modeling_phase = saved[
            "interaction_modeling"
        ]
        workflow.interaction.prepare_validation_problem = saved[
            "interaction_prepare"
        ]
        workflow.interaction.serve_expert_requests = saved["interaction_bridge"]
        workflow.interaction.judge_report = saved["interaction_judge"]
        workflow.baseline.HUMAN_MODELING_EXPERT_ROLE_PROMPT = saved[
            "expert_role_prompt"
        ]
        workflow.baseline.create_operator_role_prompts = saved[
            "operator_role_prompts"
        ]
        workflow.CPE_UTILITY_BASIS = saved["utility_basis"]
        if isolated_config is not None:
            initial.clean.clean_baseline.remove_clean_openclaw_config(isolated_config, previous_config)


if __name__ == "__main__":
    main()
