"""Repeatedly judge selected experiment rounds and summarize score variance."""

import argparse
import hashlib
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

try:
    from . import baseline as openclaw_baseline
    from . import run_evolution as workflow_evolution
except ImportError:
    import baseline as openclaw_baseline
    import run_evolution as workflow_evolution


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPERIMENT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "mlevolve_rubric_20260830_225420"
)


def now() -> str:
    return datetime.now().isoformat()


def load_round_reports(experiment: Path, rounds: list[int]) -> dict[int, Path]:
    results_path = experiment / "workflows" / "results.json"
    results = workflow_evolution.read_json(results_path, [])
    by_round = {item.get("round"): item for item in results}
    reports = {}
    for round_number in rounds:
        item = by_round.get(round_number)
        if not isinstance(item, dict):
            raise ValueError(f"Round {round_number} is absent from {results_path}")
        report_value = item.get("node", {}).get("final_report") or item.get(
            "selected_report"
        )
        report = Path(str(report_value)).resolve() if report_value else None
        if report is None or not report.is_file():
            raise FileNotFoundError(
                f"Round {round_number} report is missing: {report_value}"
            )
        reports[round_number] = report
    return reports


def parse_report_specs(specs: list[str]) -> dict[str, Path]:
    """Parse repeatable LABEL=REPORT_PATH values for direct-report evaluation."""
    reports = {}
    for spec in specs:
        label, separator, path_value = spec.partition("=")
        label = label.strip()
        report = Path(path_value.strip()).resolve()
        if not separator or not label or not path_value.strip():
            raise ValueError(
                "--report must use LABEL=PATH, for example baseline=report.md"
            )
        if label in reports:
            raise ValueError(f"Duplicate --report label: {label}")
        if not report.is_file():
            raise FileNotFoundError(f"Report for {label} is missing: {report}")
        reports[label] = report
    if not reports:
        raise ValueError("At least one --report is required")
    return reports


def score_judge_result(
    path: Path, judgers: tuple[str, ...] | None = None
) -> tuple[dict[str, float], float]:
    dimensions = openclaw_baseline.calculate_dimension_scores(path, judgers)
    overall = sum(dimensions.values()) / len(dimensions)
    return dimensions, overall


def score_summary(values: list[float]) -> dict:
    return {
        "mean": statistics.fmean(values),
        "population_std": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
        "range": max(values) - min(values),
    }


def summarize(evaluations: dict[str, list[dict]], rounds: list[int]) -> dict:
    summary = {"rounds": {}}
    for round_number in rounds:
        trials = evaluations[str(round_number)]
        if not trials:
            continue
        dimensions = sorted(trials[0]["dimension_scores"])
        summary["rounds"][str(round_number)] = {
            "trial_count": len(trials),
            "overall_score": score_summary(
                [trial["overall_score"] for trial in trials]
            ),
            "dimension_scores": {
                name: score_summary(
                    [trial["dimension_scores"][name] for trial in trials]
                )
                for name in dimensions
            },
        }

    if len(rounds) == 2:
        left, right = rounds
        left_by_trial = {
            item["trial"]: item for item in evaluations[str(left)]
        }
        right_by_trial = {
            item["trial"]: item for item in evaluations[str(right)]
        }
        common = sorted(set(left_by_trial) & set(right_by_trial))
        paired = [
            {
                "trial": trial,
                "difference": (
                    right_by_trial[trial]["overall_score"]
                    - left_by_trial[trial]["overall_score"]
                ),
            }
            for trial in common
        ]
        summary["paired_comparison"] = {
            "direction": f"round_{right}_minus_round_{left}",
            "trials": paired,
            "difference_summary": (
                score_summary([item["difference"] for item in paired])
                if paired
                else None
            ),
        }
    return summary


def average_scores(evaluations: dict[str, list[dict]], rounds: list[int]) -> dict:
    averages = {}
    for round_number in rounds:
        trials = evaluations.get(str(round_number), [])
        if not trials:
            continue
        dimensions = sorted(trials[0]["dimension_scores"])
        averages[f"round_{round_number}"] = {
            "trial_count": len(trials),
            "average_overall_score": statistics.fmean(
                trial["overall_score"] for trial in trials
            ),
            "average_dimension_scores": {
                name: statistics.fmean(
                    trial["dimension_scores"][name] for trial in trials
                )
                for name in dimensions
            },
        }
    return averages


def refresh_aggregates(payload: dict, rounds: list[int]) -> None:
    payload["average_scores"] = average_scores(payload["evaluations"], rounds)
    payload["summary"] = summarize(payload["evaluations"], rounds)


def checkpoint(path: Path, payload: dict) -> None:
    payload["updated_at"] = now()
    workflow_evolution.write_json(path, payload)


def evaluate_reports_repeated(
    problem_id: str,
    reports: dict[str, Path],
    repeats: int,
    judge_label: str,
    output: Path,
    runs_parent: Path,
    experiment: Path | None = None,
    direct_report_mode: bool = True,
    seed_results: dict[str, Path] | None = None,
    concurrency: int = 1,
    judgers: tuple[str, ...] | None = None,
) -> dict:
    """Judge each labeled report repeatedly and checkpoint after every trial."""
    if repeats < 1 or not reports:
        raise ValueError("repeats must be positive and reports must be non-empty")
    if concurrency < 1:
        raise ValueError("concurrency must be positive")
    labels = list(reports)
    if len(set(labels)) != len(labels):
        raise ValueError("Report labels must be unique")
    report_paths = {
        str(label): Path(report).resolve() for label, report in reports.items()
    }
    missing = [label for label, report in report_paths.items() if not report.is_file()]
    if missing:
        raise FileNotFoundError("Missing reports: " + ", ".join(missing))
    seed_results = {
        str(label): Path(result).resolve()
        for label, result in (seed_results or {}).items()
    }
    unknown_seeds = sorted(set(seed_results) - set(report_paths))
    if unknown_seeds:
        raise ValueError("Seed results have unknown labels: " + ", ".join(unknown_seeds))
    missing_seeds = [
        label for label, result in seed_results.items() if not result.is_file()
    ]
    if missing_seeds:
        raise FileNotFoundError("Missing seed Judge results: " + ", ".join(missing_seeds))

    output = Path(output).resolve()
    existing = workflow_evolution.read_json(output, {})
    selected_judgers = tuple(judgers or openclaw_baseline.EXPECTED_JUDGERS)
    payload = existing or {
        "experiment": str(experiment) if experiment else None,
        "problem_id": problem_id,
        "rounds": labels,
        "repeats": repeats,
        "judge_label": judge_label,
        "direct_report_mode": direct_report_mode,
        "judgers": list(selected_judgers),
        "reports": {label: str(report) for label, report in report_paths.items()},
        "evaluations": {str(label): [] for label in labels},
        "created_at": now(),
    }
    if payload.get("rounds") != labels or payload.get("repeats") != repeats:
        raise ValueError("Existing output uses different report labels or repeat count")
    if payload.get("problem_id") != problem_id:
        raise ValueError("Existing output uses a different problem ID")
    # Checkpoints created before dimension selection may contain all six
    # scores. Retain only the selected objective when resuming them.
    if payload.get("judgers") != list(selected_judgers):
        for trials in payload.get("evaluations", {}).values():
            for trial in trials:
                cached = trial.get("dimension_scores", {})
                trial["dimension_scores"] = {
                    name: cached[name] for name in selected_judgers if name in cached
                }
                if len(trial["dimension_scores"]) != len(selected_judgers):
                    raise ValueError(
                        "Existing Judge checkpoint lacks a requested dimension"
                    )
                trial["overall_score"] = statistics.fmean(
                    trial["dimension_scores"].values()
                )
        payload["judgers"] = list(selected_judgers)
    for label in labels:
        payload.setdefault("evaluations", {}).setdefault(str(label), [])

    # Preserve an already-completed single Judge as trial 1, then perform only
    # the remaining trials requested by ``repeats``.
    for label, raw_result in seed_results.items():
        trials = payload["evaluations"][label]
        if any(item.get("trial") == 1 for item in trials):
            continue
        dimensions, overall = score_judge_result(raw_result, selected_judgers)
        trials.append(
            {
                "trial": 1,
                "execution_order": 0,
                "dimension_scores": dimensions,
                "overall_score": overall,
                "raw_result": str(raw_result),
                "seeded": True,
                "completed_at": now(),
            }
        )
        trials.sort(key=lambda item: item["trial"])
    if seed_results:
        refresh_aggregates(payload, labels)
        checkpoint(output, payload)

    # Judge workspaces include a copied ``final_submission`` report. Keep this
    # path short because benchmark run directories can reach Windows' legacy
    # path-length limit before the temporary Judge suffix is appended.
    runs_root = Path(runs_parent).resolve() / ".judge"
    model_slug = openclaw_baseline.slugify(judge_label)
    evaluation_id = hashlib.sha1(str(output).encode("utf-8")).hexdigest()[:10]
    print(f"Checkpoint: {output}", flush=True)

    pending = []
    execution_order = 0
    for trial in range(1, repeats + 1):
        order = labels if trial % 2 else list(reversed(labels))
        for label in order:
            key = str(label)
            completed = {item.get("trial") for item in payload["evaluations"][key]}
            if trial in completed:
                print(
                    f"Round {label}, trial {trial} already completed; skipping",
                    flush=True,
                )
                continue
            execution_order += 1
            run_name = (
                f"j_{evaluation_id}_"
                f"{openclaw_baseline.slugify(str(label))[:16]}_{trial}"
            )
            run_dir = runs_root / run_name
            run_dir.mkdir(parents=True, exist_ok=True)
            pending.append((execution_order, trial, label, key, run_dir))

    def evaluate_one(job):
        order_number, trial, label, key, run_dir = job
        print(f"Evaluating Round {label}, trial {trial}/{repeats}", flush=True)
        raw_result = openclaw_baseline.judge_final_report(
            problem_id,
            report_paths[key],
            model_slug,
            run_dir,
            judgers=selected_judgers,
        )
        dimensions, overall = score_judge_result(raw_result, selected_judgers)
        return order_number, trial, label, key, raw_result, dimensions, overall

    with ThreadPoolExecutor(max_workers=min(concurrency, len(pending) or 1)) as executor:
        futures = [executor.submit(evaluate_one, job) for job in pending]
        for future in as_completed(futures):
            order_number, trial, label, key, raw_result, dimensions, overall = (
                future.result()
            )
            payload["evaluations"][key].append(
                {
                    "trial": trial,
                    "execution_order": order_number,
                    "dimension_scores": dimensions,
                    "overall_score": overall,
                    "raw_result": str(raw_result),
                    "completed_at": now(),
                }
            )
            payload["evaluations"][key].sort(key=lambda item: item["trial"])
            refresh_aggregates(payload, labels)
            checkpoint(output, payload)
            print(f"Round {label}, trial {trial}: overall={overall:.6f}", flush=True)

    refresh_aggregates(payload, labels)
    payload["completed_at"] = now()
    checkpoint(output, payload)
    print(f"Completed repeated Judge evaluation: {output}", flush=True)
    return payload


def parse_args() -> argparse.Namespace:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, default=DEFAULT_EXPERIMENT)
    parser.add_argument("--problem-id", default="2013_Bank_Service_Problem")
    parser.add_argument("--rounds", type=int, nargs="+", default=[6, 10])
    parser.add_argument(
        "--report",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help=(
            "Directly evaluate a Markdown report. Repeat for each report; "
            "this bypasses --experiment/--rounds."
        ),
    )
    parser.add_argument(
        "--seed-result",
        action="append",
        default=[],
        metavar="LABEL=JUDGE_RESULT_JSON",
        help=(
            "Use an existing raw Judge JSON as trial 1 for its report label; "
            "only the remaining trials are evaluated."
        ),
    )
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument(
        "--judge-label",
        default="judge-stability-deepseek-v4-flash",
        help="Output label only; Judger model configuration remains unchanged.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    args.experiment = args.experiment.resolve()
    args.direct_reports = parse_report_specs(args.report) if args.report else None
    args.seed_results = (
        parse_report_specs(args.seed_result) if args.seed_result else {}
    )
    if args.direct_reports:
        args.rounds = list(args.direct_reports)
    if args.output is None and args.direct_reports:
        args.output = (
            REPO_ROOT
            / "output_judge"
            / "OpenClaw"
            / "repeated_evaluations"
            / f"judge_stability_{timestamp}.json"
        )
    elif args.output is None:
        args.output = (
            args.experiment / f"judge_stability_{timestamp}.json"
        )
    else:
        args.output = args.output.resolve()
    if (
        args.repeats < 1
        or args.concurrency < 1
        or len(args.rounds) < 1
        or len(set(args.rounds)) != len(args.rounds)
    ):
        raise ValueError("repeats must be positive and rounds must be unique")
    return args


def main() -> None:
    args = parse_args()
    if not args.direct_reports and not args.experiment.is_dir():
        raise FileNotFoundError(f"Experiment not found: {args.experiment}")
    reports = (
        args.direct_reports
        if args.direct_reports is not None
        else load_round_reports(args.experiment, args.rounds)
    )
    runs_parent = args.output.parent if args.direct_reports else args.experiment
    evaluate_reports_repeated(
        args.problem_id,
        reports,
        args.repeats,
        args.judge_label,
        args.output,
        runs_parent,
        experiment=args.experiment,
        direct_report_mode=bool(args.direct_reports),
        seed_results=args.seed_results,
        concurrency=args.concurrency,
    )


if __name__ == "__main__":
    main()
