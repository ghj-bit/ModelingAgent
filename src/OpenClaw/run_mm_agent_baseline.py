"""Run a coarse-grained MM-Agent workflow as an OpenClaw baseline."""

import argparse
import copy
import json
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

try:
    from . import baseline
    from .run_modelingbench_baseline import aggregate_scores, result_record, select_problems
except ImportError:
    import baseline
    from run_modelingbench_baseline import aggregate_scores, result_record, select_problems


PROMPT_PATH = baseline.REPO_ROOT / "prompt.md"
SKILL_NAME = "mm-agent-pipeline"

SKILL_TEXT = """---
name: mm-agent-pipeline
description: Solve a complete ModelingBench problem with a dependency-aware mathematical modeling workflow.
---

# MM-Agent Modeling Workflow

Use this skill for a complete mathematical modeling problem. Treat the current problem statement and explicitly supplied attachments as authoritative. Adapt the workflow to the actual mix of optimization, prediction, simulation, evaluation, and qualitative recommendations.

## Step 1: Understand the problem

Read the complete statement. Identify every requested subproblem and special deliverable, the system being modeled, available data, decisions or predictions, constraints, and expected outputs. Keep a checklist of requirements. Clearly separate supplied facts from assumptions.

## Step 2: Design the overall approach

Define important variables, units, objectives, constraints, uncertainty, and relationships. Choose a coherent modeling strategy that connects all requested outputs. Review it for missing requirements, weak assumptions, and needless complexity, then revise it.

## Step 3: Decompose and schedule the work

Create a small set of meaningful subtasks, each with a goal, inputs, outputs, and covered requirements. Identify dependencies and place the subtasks in an executable order without cycles. Adapt the decomposition to the current ModelingBench problem instead of forcing a fixed template.

## Step 4: Model and solve each subtask

Process subtasks in dependency order. For each one, read prerequisite results, analyze the task, select suitable modeling methods, formulate assumptions and equations, and solve it. Use supplied data when available. Write and execute reproducible code when calculation, optimization, simulation, fitting, or data processing is useful. Check errors, feasibility, units, and numerical scale. With no dataset, use analytic reasoning, scenario analysis, or clearly labeled simulated data and state the evidence limits. Interpret and save each result before starting a dependent subtask.

## Step 5: Integrate the solution

Combine subtask results into one consistent answer. Align notation, units, parameters, time scales, and assumptions. Resolve contradictions and trace each main conclusion to quantitative evidence or an explicitly labeled qualitative argument. Recheck the original requirement checklist.

## Step 6: Validate and test robustness

Use checks appropriate to the problem, such as feasibility tests, baselines, holdout validation, limiting cases, sensitivity analysis, or scenarios. Explain what was tested and how conclusions changed. State uncertainty and limitations honestly, especially when validation data are absent.

## Step 7: Write the final report

Create the final report at the exact path given in the task prompt. Make it self-contained and include the problem restatement, assumptions, data treatment, models, solution process, results, validation, limitations, conclusions, recommendations, and special deliverables. Put essential equations, values, and conclusions in the report itself. Verify that it is non-empty UTF-8 Markdown and answers the complete problem.
"""


def build_skill_bundle(destination: Path, data_dir: Path | None = None) -> Path:
    """Create the natural-language skill copied into an OpenClaw workspace."""
    skill = destination / SKILL_NAME
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(SKILL_TEXT, encoding="utf-8")
    if data_dir is not None:
        shutil.copytree(data_dir.resolve(), skill / "data")
    return destination


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem_ids", nargs="*", help="One or more ModelingBench problem IDs.")
    parser.add_argument("--all", action="store_true", help="Run all ModelingBench problems.")
    parser.add_argument("--prompt-template", type=Path, default=PROMPT_PATH)
    parser.add_argument("--data-dir", type=Path, help="Attachments for one selected problem.")
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Maximum number of problems executed concurrently.",
    )
    parser.add_argument("--openclaw-command")
    parser.add_argument("--agent")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=baseline.REPO_ROOT / "output_workspace_mm_agent_openclaw",
    )
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args(argv)
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    if args.concurrency < 1:
        parser.error("--concurrency must be positive")
    if args.agent and args.concurrency > 1:
        parser.error("--agent cannot be shared by concurrent problem runs")
    if args.data_dir and (args.all or len(args.problem_ids) != 1):
        parser.error("--data-dir requires exactly one problem ID")
    if args.data_dir and not args.data_dir.is_dir():
        parser.error(f"data directory not found: {args.data_dir}")
    if not args.prompt_template.is_file():
        parser.error(f"prompt template not found: {args.prompt_template}")
    return args


def main(argv=None):
    args = parse_args(argv)
    selected = select_problems(baseline.load_problems(), args.problem_ids, args.all)
    selected = list(dict(selected).items())
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    completed, failed = [], []

    with tempfile.TemporaryDirectory(prefix="mm_agent_skill_") as temporary:
        args.skills_source = build_skill_bundle(Path(temporary), args.data_dir)
        args.selected_skills = [SKILL_NAME]

        def run_one(problem_id, problem):
            result = baseline.run_problem(problem_id, problem, copy.copy(args))
            record = result_record(problem_id, result)
            if args.prepare_only:
                record["status"] = "prepared"
                record["final_report"] = None
            record["prompt"] = str(result["prompt"])
            return record

        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            futures = {
                executor.submit(run_one, problem_id, problem): problem_id
                for problem_id, problem in selected
            }
            for future in as_completed(futures):
                problem_id = futures[future]
                try:
                    completed.append(future.result())
                except Exception as error:
                    failed.append({"problem_id": problem_id, "error": repr(error)})
                    print(f"[{problem_id}] failed: {error}", flush=True)

    order = {problem_id: index for index, (problem_id, _) in enumerate(selected)}
    completed.sort(key=lambda item: order[item["problem_id"]])
    failed.sort(key=lambda item: order[item["problem_id"]])

    average, dimensions = aggregate_scores(completed)
    summary = {
        "baseline": "mm-agent-openclaw",
        "execution": "coarse-grained-prompt-workflow",
        "prompt_template": str(args.prompt_template.resolve()),
        "model": args.model,
        "concurrency": args.concurrency,
        "prepare_only": args.prepare_only,
        "average_score": average,
        "average_dimension_scores": dimensions,
        "completed": completed,
        "failed": failed,
    }
    summary_path = output_root / f"mm_agent_results_{datetime.now():%Y%m%d_%H%M%S_%f}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"MM-Agent baseline summary: {summary_path}")
    if failed:
        raise RuntimeError(f"{len(failed)} problem(s) failed; see {summary_path}")


if __name__ == "__main__":
    main()
