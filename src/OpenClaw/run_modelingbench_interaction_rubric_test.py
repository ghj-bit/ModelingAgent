"""Evaluate the best evolved interaction rubric on ModelingBench test problems.

The runner deliberately follows ``run_modelingbench_baseline.py`` for problem
execution.  It injects the evolved interaction rubric and evaluates the same
four dimensions used as the interaction-evolution objective.
"""

import argparse
import copy
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

try:
    from . import baseline
    from . import run_interaction_rubric_evolution as interaction_evolution
    from . import run_judge_stability
    from . import run_modelingbench_baseline as baseline_runner
except ImportError:
    import baseline
    import run_interaction_rubric_evolution as interaction_evolution
    import run_judge_stability
    import run_modelingbench_baseline as baseline_runner


DEFAULT_EXPERIMENT = (
    baseline.REPO_ROOT
    / "openclaw_experiments"
    / "interaction_rubric_20260904_150313"
)
DEFAULT_OUTPUT_ROOT = (
    baseline.REPO_ROOT / "output_workspace_openclaw_interaction_rubric_test"
)
STAGE_OUTPUTS = {
    "problem_understanding": Path("results/step_01_problem_understanding.md"),
    "modeling_assumptions": Path("results/step_02_modeling_assumptions.md"),
    "external_data": Path("data/external_data.md"),
    "implementation": Path("results/step_04_implementation.md"),
    "validation_analysis": Path("results/step_05_validation_analysis.md"),
}
TEST_JUDGE_DIMENSIONS = interaction_evolution.EVALUATION_DIMENSIONS


def _completed_validation_ids(result: dict) -> set[str]:
    records = result.get("problem_results")
    if not isinstance(records, list):
        return set()
    return {
        item.get("problem_id")
        for item in records
        if isinstance(item, dict)
        and isinstance(item.get("problem_id"), str)
        and not item.get("error")
    }


def experiment_validation_problems(experiment: Path) -> tuple[str, ...]:
    """Read the validation contract used by this specific experiment.

    This must not be inferred from the evolution script's current defaults:
    historical experiments retain the validation set with which their utility
    values were calculated.
    """
    config_path = experiment / "config.json"
    if config_path.is_file():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        configured = config.get("validation_problems")
        if isinstance(configured, list) and configured and all(
            isinstance(problem_id, str) for problem_id in configured
        ):
            return tuple(configured)
    return interaction_evolution.VALIDATION_PROBLEMS


def load_best_rubric(experiment: Path) -> dict:
    """Return the highest-utility rubric with all validation runs completed."""
    results_path = experiment / "workflows" / "results.json"
    if not results_path.is_file():
        raise FileNotFoundError(f"Interaction evolution results not found: {results_path}")
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected a JSON list in {results_path}")

    required = set(experiment_validation_problems(experiment))
    eligible = [
        result
        for result in payload
        if isinstance(result, dict)
        and isinstance(result.get("utility"), (int, float))
        and isinstance(result.get("rubric"), dict)
        and required.issubset(_completed_validation_ids(result))
    ]
    if not eligible:
        raise ValueError(
            "No completed interaction-rubric node covers every validation problem"
        )
    # Prefer the earlier round on an exact utility tie: it is the simpler,
    # already-established treatment and avoids depending on JSON list order.
    selected = max(
        eligible,
        key=lambda result: (float(result["utility"]), -int(result.get("round", 0))),
    )
    interaction_evolution.validate_rubric(selected["rubric"])
    return copy.deepcopy(selected)


def select_test_problems(
    problems: dict[str, dict],
    problem_ids: list[str],
    run_all: bool,
    include_validation: bool = False,
    validation_problems: tuple[str, ...] | None = None,
) -> list[tuple[str, dict]]:
    selected = baseline_runner.select_problems(problems, problem_ids, run_all)
    if include_validation:
        return selected

    validation = set(validation_problems or interaction_evolution.VALIDATION_PROBLEMS)
    explicitly_selected = [problem_id for problem_id, _ in selected if problem_id in validation]
    if problem_ids and explicitly_selected:
        raise ValueError(
            "Validation problem(s) are excluded from the test set: "
            + ", ".join(explicitly_selected)
            + ". Pass --include-validation only for a deliberate diagnostic run."
        )
    test_problems = [item for item in selected if item[0] not in validation]
    if not test_problems:
        raise ValueError("No test problems remain after excluding validation problems")
    return test_problems


def materialize_treatment_prompt(
    experiment: Path, output_root: Path, base_prompt_path: Path
) -> tuple[dict, Path, Path]:
    """Select the best rubric and write the exact reusable treatment prompt."""
    selected = load_best_rubric(experiment)
    base_prompt = base_prompt_path.read_text(encoding="utf-8")
    prompt = interaction_evolution.build_prompt(base_prompt, selected["rubric"])
    output_root.mkdir(parents=True, exist_ok=True)
    prompt_path = output_root / "prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    selection_path = output_root / "selected_interaction_rubric.json"
    selection_payload = {
        "source_experiment": str(experiment),
        "source_results": str(experiment / "workflows" / "results.json"),
        "selected_round": selected.get("round"),
        "rubric_id": selected.get("rubric_id") or selected["rubric"].get("rubric_id"),
        "validation_utility": selected["utility"],
        "validation_dimension_scores": selected.get("average_dimension_scores"),
        "rubric": selected["rubric"],
        "base_prompt": str(base_prompt_path),
        "generated_prompt": str(prompt_path),
    }
    selection_path.write_text(
        json.dumps(selection_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return selected, prompt_path, selection_path


def validate_stage_outputs(result: dict) -> dict[str, str]:
    """Require each process artifact promised by the treatment prompt."""
    output_dir = Path(result["run_dir"]) / "output"
    missing = []
    stage_files = {}
    for stage, relative_path in STAGE_OUTPUTS.items():
        path = output_dir / relative_path
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            missing.append(str(path))
        else:
            stage_files[stage] = str(path)
    if missing:
        raise RuntimeError("Missing non-empty stage output(s): " + ", ".join(missing))
    return stage_files


def result_record(problem_id: str, result: dict) -> dict:
    record = baseline_runner.result_record(problem_id, result)
    record["prompt"] = str(result["prompt"])
    record["stage_files"] = result.get("stage_files")
    receipt = result.get("interaction_receipt")
    record["interaction_receipt"] = receipt
    return record


def run_selected(
    selected: list[tuple[str, dict]], args, rubric: dict
) -> tuple[list[dict], list[dict]]:
    """Run test problems concurrently and Judge final reports like baseline."""
    completed = []
    failed = []

    def run_one(problem_id: str, problem: dict) -> dict:
        task_args = copy.copy(args)
        directory_prefixes = getattr(args, "run_directory_prefixes", None)
        if isinstance(directory_prefixes, dict):
            task_args.run_directory_prefix = directory_prefixes.get(problem_id)
        # This runner's repeated evaluation is the sole Judge path.
        task_args.skip_judge = True
        result = baseline.run_problem(problem_id, problem, task_args)
        if args.prepare_only:
            return result

        result["stage_files"] = validate_stage_outputs(result)
        result["interaction_receipt"] = interaction_evolution.validate_interaction_run(
            result, rubric
        )
        if args.skip_judge:
            return result

        stability_path = result["run_dir"] / "meta" / "judge_stability.json"
        payload = run_judge_stability.evaluate_reports_repeated(
            problem_id,
            {"report": result["final_report"]},
            args.judge_repeats,
            args.judge_label,
            stability_path,
            result["run_dir"] / "meta",
            concurrency=args.judge_concurrency,
            judgers=TEST_JUDGE_DIMENSIONS,
        )
        repeated = payload["average_scores"]["round_report"]
        trials = payload["evaluations"]["report"]
        result.update(
            {
                "repeated_judge": True,
                "judge_stability_result": stability_path,
                "judge_repeats": repeated["trial_count"],
                "judge_result": Path(trials[-1]["raw_result"]),
                "average_score": repeated["average_overall_score"],
                "dimension_scores": repeated["average_dimension_scores"],
            }
        )
        return result

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {
            executor.submit(run_one, problem_id, problem): problem_id
            for problem_id, problem in selected
        }
        for future in as_completed(futures):
            problem_id = futures[future]
            try:
                completed.append(result_record(problem_id, future.result()))
            except Exception as error:
                failed.append(
                    {"problem_id": problem_id, "status": "failed", "error": repr(error)}
                )
                print(f"[{problem_id}] failed: {error}", flush=True)
    completed.sort(key=lambda item: item["problem_id"])
    failed.sort(key=lambda item: item["problem_id"])
    return completed, failed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the best completed interaction rubric from an evolution "
            "experiment on held-out ModelingBench test problems."
        )
    )
    parser.add_argument("problem_ids", nargs="*", help="One or more test problem IDs.")
    parser.add_argument(
        "--all", action="store_true", help="Run all problems except the validation set."
    )
    parser.add_argument(
        "--include-validation",
        action="store_true",
        help="Allow validation problems (diagnostics only; not a clean test evaluation).",
    )
    parser.add_argument(
        "--rubric-experiment", default=str(DEFAULT_EXPERIMENT), help="Evolution experiment."
    )
    parser.add_argument(
        "--base-prompt-template",
        default=str(baseline.BASELINE_PROMPT_TEMPLATE_PATH),
        help="Baseline prompt into which the selected interaction rubric is injected.",
    )
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--agent", help="Use an existing OpenClaw agent ID.")
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--openclaw-command")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--judge-repeats", type=int, default=3)
    parser.add_argument(
        "--judge-concurrency",
        type=int,
        default=1,
        help="Maximum repeated Judge calls per problem run concurrently.",
    )
    parser.add_argument(
        "--judge-label",
        default="best-interaction-rubric-test-deepseek-v4-flash",
        help="Output label only; Judge model configuration remains unchanged.",
    )
    parser.add_argument("--prepare-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.concurrency < 1:
        raise ValueError("--concurrency must be at least 1")
    if args.judge_repeats < 1:
        raise ValueError("--judge-repeats must be at least 1")
    if args.judge_concurrency < 1:
        raise ValueError("--judge-concurrency must be at least 1")
    if args.agent and args.concurrency > 1:
        raise ValueError("--agent cannot be shared by concurrent problem runs")

    experiment = Path(args.rubric_experiment).resolve()
    output_root = Path(args.output_root).resolve()
    selected_node, prompt_path, selection_path = materialize_treatment_prompt(
        experiment, output_root, Path(args.base_prompt_template).resolve()
    )
    source_validation_problems = experiment_validation_problems(experiment)
    args.prompt_template = str(prompt_path)
    problems = baseline.load_problems()
    selected_problems = select_test_problems(
        problems,
        args.problem_ids,
        args.all,
        args.include_validation,
        source_validation_problems,
    )

    rubric = selected_node["rubric"]
    print(
        f"Selected interaction rubric: round={selected_node.get('round')} "
        f"id={rubric['rubric_id']} utility={selected_node['utility']:.6f}",
        flush=True,
    )
    print(f"Treatment prompt: {prompt_path}", flush=True)
    print(f"Test problems: {len(selected_problems)}", flush=True)

    started_at = datetime.now()
    completed, failed = run_selected(selected_problems, args, rubric)
    finished_at = datetime.now()
    average_score, average_dimension_scores = baseline_runner.aggregate_scores(completed)
    summary = {
        "evaluation": "best_evolved_interaction_rubric_test",
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "elapsed_seconds": (finished_at - started_at).total_seconds(),
        "source_experiment": str(experiment),
        "selected_rubric_metadata": str(selection_path),
        "selected_round": selected_node.get("round"),
        "rubric_id": rubric["rubric_id"],
        "validation_utility": selected_node["utility"],
        "prompt_template": str(prompt_path),
        "validation_problems_excluded": (
            []
            if args.include_validation
            else list(source_validation_problems)
        ),
        "model": args.model,
        "concurrency": args.concurrency,
        "judge_repeats": args.judge_repeats,
        "judge_concurrency": args.judge_concurrency,
        "judge_dimensions": list(TEST_JUDGE_DIMENSIONS),
        "average_score": average_score,
        "average_dimension_scores": average_dimension_scores,
        "completed": completed,
        "failed": failed,
    }
    summary_path = output_root / (
        f"interaction_rubric_test_results_{finished_at.strftime('%Y%m%d_%H%M%S')}.json"
    )
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Interaction-rubric test summary: {summary_path}", flush=True)
    if failed:
        raise RuntimeError(f"{len(failed)} benchmark problem(s) failed")


if __name__ == "__main__":
    main()
