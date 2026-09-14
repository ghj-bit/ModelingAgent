"""Run a fixed OpenClaw workflow with one concise external-data search step."""

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

try:
    from . import baseline as openclaw_baseline
    from . import run_evolution as evolution
    from .baseline import REPO_ROOT, load_problems, run_problem
except ImportError:
    import baseline as openclaw_baseline
    import run_evolution as evolution
    from baseline import REPO_ROOT, load_problems, run_problem


SOURCE_PROMPT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "run_20260826_150237"
    / "runs"
    / "round_2"
    / "deepseek-deepseek-v4-pro"
    / "2013_Bank_Service_Problem_20260826_154216"
    / "prompt.md"
)
DEFAULT_EXPERIMENT = (
    REPO_ROOT / "openclaw_experiments" / "data_search_20260827_213419"
)
DATA_SEARCH_POLICY_MARKER = "Empirical data search policy v5"
DATA_SEARCH_STEP_TEMPLATE = (
    f"[{DATA_SEARCH_POLICY_MARKER}] Search for at most 1–2 missing empirical "
    "data items that can change a "
    "model parameter, sensitivity scenario, or external validation result. "
    "Use numerical observations from accessible primary, official, or "
    "peer-reviewed sources; record each value's unit, population, time, "
    "location, source URL, applicability, and exact downstream use in "
    "`{{DATA_DIR}}/external_data.md`. For this bank-queue task, prioritize "
    "empirical customer patience or abandonment data and time-of-day bank "
    "arrival patterns that can parameterize a sensitivity scenario. Formulas, "
    "modeling methods, tutorials, "
    "calculators, generic advice, and search-result snippets are not data and "
    "must not be selected. Do not replace supplied problem data or invent "
    "branch-specific facts; if no admissible item can be verified from the "
    "full source, record that outcome instead. Later modeling, code, analysis, "
    "and the final report must use every accepted item as declared or clearly "
    "state why it was excluded."
)
SOURCE_CACHE_STEP_SUFFIX = (
    " Before any network request, check the shared full-source cache at "
    "`{source_cache}` by canonical URL and content hash; reuse a matching "
    "verified source, copy it into `{{DATA_DIR}}/_sources`, and fetch only "
    "missing or stale sources."
)


def data_search_step(source_cache: Path | None = None) -> str:
    step = DATA_SEARCH_STEP_TEMPLATE
    if source_cache is not None:
        step += SOURCE_CACHE_STEP_SUFFIX.replace(
            "{source_cache}", str(source_cache.resolve())
        )
    return step


def restore_workspace_placeholders(prompt: str) -> str:
    match = re.search(r"^- Workspace root: `([^`]+)`", prompt, re.MULTILINE)
    if not match:
        raise ValueError("Source prompt has no rendered workspace root")
    output_dir = match.group(1)
    replacements = (
        (output_dir + r"\results\solution_report.md", "{{FINAL_REPORT}}"),
        (output_dir + r"\logs\workflow_evidence", "{{EVIDENCE_DIR}}"),
        (output_dir + r"\logs\operator_feedback", "{{OPERATOR_FEEDBACK_DIR}}"),
        (output_dir + r"\logs\operator_roles", "{{OPERATOR_ROLE_DIR}}"),
        (output_dir + r"\results", "{{RESULTS_DIR}}"),
        (output_dir + r"\code", "{{CODE_DIR}}"),
        (output_dir + r"\logs", "{{LOGS_DIR}}"),
        (output_dir, "{{OUTPUT_DIR}}"),
    )
    for old, new in replacements:
        prompt = prompt.replace(old, new)
    return prompt


def build_prompt_template(
    destination: Path, source_cache: Path | None = None
) -> None:
    if not SOURCE_PROMPT.is_file():
        raise FileNotFoundError(f"Source prompt not found: {SOURCE_PROMPT}")
    source = restore_workspace_placeholders(
        SOURCE_PROMPT.read_text(encoding="utf-8")
    )
    data_directory_line = "- Data directory: `{{DATA_DIR}}`"
    if data_directory_line not in source:
        result_directory_line = "- Result directory: `{{RESULTS_DIR}}`"
        if result_directory_line not in source:
            raise ValueError("Source prompt has no result-directory declaration")
        source = source.replace(
            result_directory_line,
            result_directory_line + "\n" + data_directory_line,
            1,
        )
    prefix, workflow, suffix = evolution.split_required_workflow(source)
    steps = evolution.parse_steps(workflow)
    search_step = data_search_step(source_cache)
    if any(DATA_SEARCH_POLICY_MARKER in step for step in steps):
        raise ValueError("Source workflow already contains the data-search step")
    ask_index = next(
        (
            index
            for index, step in enumerate(steps)
            if evolution.step_operator(step) == "AskExpert"
        ),
        None,
    )
    if ask_index is None:
        raise ValueError("Source workflow has no AskExpert step")
    steps.insert(ask_index + 1, search_step)
    steps = evolution.render_operator_steps(steps)
    numbered = "\n".join(
        f"{index}. {step}" for index, step in enumerate(steps, start=1)
    )
    prompt = prefix + numbered + "\n\n" + suffix
    prompt = evolution.synchronize_workflow_evidence_contract(prompt)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(prompt, encoding="utf-8")


def has_current_data_search_step(
    prompt_path: Path, use_source_cache: bool = False
) -> bool:
    """Return whether an existing template contains the current search policy."""
    if not prompt_path.is_file():
        return False
    try:
        _, workflow, _ = evolution.split_required_workflow(
            prompt_path.read_text(encoding="utf-8")
        )
        search_steps = [
            step
            for step in evolution.parse_steps(workflow)
            if DATA_SEARCH_POLICY_MARKER in step
        ]
        if not search_steps:
            return False
        has_cache_instruction = "shared full-source cache" in search_steps[0]
        return has_cache_instruction == use_source_cache
    except (OSError, ValueError):
        return False


def sync_source_cache(source: Path, destination: Path) -> int:
    """Merge downloaded full-source artifacts into the experiment cache."""
    if not source.is_dir():
        return 0
    copied = 0
    for item in source.rglob("*"):
        if not item.is_file():
            continue
        target = destination / item.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or item.read_bytes() != target.read_bytes():
            shutil.copy2(item, target)
            copied += 1
    return copied


def hydrate_source_cache(experiment: Path, destination: Path) -> int:
    """Seed the shared cache from completed runs created before cache support."""
    copied = 0
    for source in sorted(experiment.glob("runs/*/*/output/data/_sources")):
        copied += sync_source_cache(source, destination)
    destination.mkdir(parents=True, exist_ok=True)
    return copied


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the fixed OpenClaw data-search treatment experiment."
    )
    parser.add_argument(
        "problem_id", nargs="?", default="2013_Bank_Service_Problem"
    )
    parser.add_argument("--exp", type=Path, default=DEFAULT_EXPERIMENT)
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument(
        "--completion-grace",
        type=float,
        default=evolution.DEFAULT_COMPLETION_GRACE_SECONDS,
        help="Seconds to wait after the completed agent and final report are detected.",
    )
    parser.add_argument("--agent")
    parser.add_argument("--openclaw-command")
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument(
        "--use-source-cache",
        action="store_true",
        help="Reuse and update the experiment-level external-source cache.",
    )
    parser.add_argument(
        "--initialize-only",
        action="store_true",
        help="Create prompt.md without starting an OpenClaw run.",
    )
    parser.add_argument(
        "--rebuild-prompt",
        action="store_true",
        help="Regenerate prompt.md from the source Round 2 prompt.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.problem_id != "2013_Bank_Service_Problem":
        raise ValueError(
            "This fixed prompt is only valid for 2013_Bank_Service_Problem"
        )
    problems = load_problems()
    if args.problem_id not in problems:
        raise ValueError(f"Unknown problem ID: {args.problem_id}")
    evolution.configure_completion_grace(run_problem, args.completion_grace)

    experiment = args.exp.resolve()
    experiment.mkdir(parents=True, exist_ok=True)
    source_cache = experiment / "source_cache"
    if args.use_source_cache:
        copied = hydrate_source_cache(experiment, source_cache)
        if copied:
            print(
                f"Seeded external-source cache with {copied} file(s): "
                f"{source_cache}"
            )
    prompt_template = experiment / "prompt.md"
    prompt_is_current = has_current_data_search_step(
        prompt_template, args.use_source_cache
    )
    if args.rebuild_prompt or not prompt_is_current:
        if prompt_template.is_file() and not args.rebuild_prompt:
            print("Existing prompt uses an outdated data-search policy; rebuilding it.")
        build_prompt_template(
            prompt_template,
            source_cache if args.use_source_cache else None,
        )
        print(f"Created data-search prompt: {prompt_template}")
    else:
        print(f"Using existing data-search prompt: {prompt_template}")

    if args.initialize_only:
        return

    run_args = SimpleNamespace(
        output_root=str(experiment / "runs"),
        model=args.model,
        prompt_template=str(prompt_template),
        prepare_only=args.prepare_only,
        openclaw_command=args.openclaw_command,
        agent=args.agent,
        thinking=args.thinking,
        timeout=args.timeout,
        skip_judge=args.skip_judge,
        react_role_prompts=evolution.optimized_react_role_prompts(
            openclaw_baseline.REACT_VERIFIER_ROLE_PROMPTS
        ),
    )
    result = run_problem(args.problem_id, problems[args.problem_id], run_args)
    if args.use_source_cache:
        cached = sync_source_cache(
            Path(result["run_dir"]) / "output" / "data" / "_sources",
            source_cache,
        )
        if cached:
            print(
                f"Updated external-source cache with {cached} file(s): "
                f"{source_cache}"
            )
    dimension_scores = None
    if result["judge_result"]:
        dimension_scores = evolution.judge_dimension_scores(
            Path(result["judge_result"])
        )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = experiment / f"result_{timestamp}.json"
    summary_path.write_text(
        json.dumps(
            {
                "experiment_type": "fixed_openclaw_data_search",
                "problem_id": args.problem_id,
                "model": args.model,
                "source_prompt": str(SOURCE_PROMPT),
                "prompt_template": str(prompt_template),
                "source_cache": (
                    str(source_cache) if args.use_source_cache else None
                ),
                "run_dir": str(result["run_dir"]),
                "final_report": str(result["final_report"]),
                "judge_result": (
                    str(result["judge_result"])
                    if result["judge_result"]
                    else None
                ),
                "dimension_scores": dimension_scores,
                "average_score": result["average_score"],
                "created_at": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Experiment: {experiment}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
