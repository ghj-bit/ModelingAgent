"""Evaluate workflow-evolution reports with all six ModelingBench judges."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

# Do not allow a general-purpose legacy key inherited by the process to affect
# Judge authentication. This evaluator accepts only the dedicated Judge key.
os.environ.pop("DEEPSEEK_API_KEY", None)

try:
    from . import evaluate_interaction_reports_deepseek as evaluator
    from . import compare_workflow_judge_stability_excel as comparison
except ImportError:
    import evaluate_interaction_reports_deepseek as evaluator
    import compare_workflow_judge_stability_excel as comparison


JUDGE_MODEL = "deepseek-v4-flash"
DEFAULT_EXPERIMENT = (
    evaluator.REPO_ROOT
    / "openclaw_experiments"
    / "interaction_workflow_substantive_20260909_214301"
)


def remove_impact_section(text: str) -> tuple[str, str]:
    """Remove matching ATX sections, including children, but keep peer sections."""
    kept, removed = [], []
    removal_level = None
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        heading = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$", line) if fence is None else None
        if heading:
            level = len(heading[1])
            if removal_level is not None and level <= removal_level:
                removal_level = None
            if re.search(r"\bExpert\s+Interaction\s+Impact\b", heading[2], re.I):
                removal_level = level
        (removed if removal_level is not None else kept).append(line)
    return "".join(kept), "".join(removed)


def prepare_reports(reports: list[dict], dry_run: bool = False) -> list[dict]:
    prepared = []
    for item in reports:
        source = item["report"]
        text = source.read_bytes().decode("utf-8")
        cleaned, removed = remove_impact_section(text)
        target = source.with_name("solution_report_without_expert_impact.md")
        backup = source.with_name("solution_report.with_expert_impact.backup.md")
        extracted = source.with_name("expert_interaction_impact.removed.md")
        if not cleaned.strip():
            raise ValueError(f"Removal would empty report: {source}")
        artifacts = {backup: source.read_bytes(), target: cleaned.encode("utf-8"), extracted: removed.encode("utf-8")}
        for path, content in artifacts.items():
            if path.exists() and path.read_bytes() != content:
                raise ValueError(f"Existing artifact differs; refusing to overwrite: {path}")
        if not dry_run:
            for path, content in artifacts.items():
                if not path.exists():
                    if path == backup:
                        shutil.copy2(source, path)
                    else:
                        path.write_bytes(content)
        prepared.append({**item, "report": target})
    return prepared


def export_comparisons(experiment: Path, excel: Path, output: Path) -> None:
    current = comparison.load_repeat(excel)
    sources = [
        (experiment / "workflows" / "round_problem_dimension_scores.xlsx", comparison.load_original,
         "four_dimension_judge_stability_comparison.xlsx"),
        (experiment / "workflows" / "deepseek_v4_flash_six_dimension_evaluation" / "six_dimension_scores.xlsx",
         comparison.load_repeat, "four_dimension_before_after_comparison.xlsx"),
    ]
    for source, loader, filename in sources:
        if not source.exists() or source.resolve() == excel.resolve():
            continue
        original = loader(source)
        # Restrict the reference to selected rounds; missing pairs remain an error.
        original = {key: value for key, value in original.items() if key in current}
        rows = comparison.comparison_rows(original, current)
        target = output / filename
        comparison.export_excel(rows, target, source, excel)
        print(f"Four-dimension comparison: {target}")


def completed_rounds(experiment: Path) -> list[int]:
    """Return every round that has at least one recorded problem result."""
    results_path = experiment / "workflows" / "results.json"
    results = evaluator.read_json(results_path)
    if not isinstance(results, list):
        raise ValueError(f"Expected a list in {results_path}")
    rounds = sorted(
        {
            int(item["round"])
            for item in results
            if isinstance(item, dict)
            and isinstance(item.get("round"), int)
            and item.get("problem_results")
        }
    )
    if not rounds:
        raise ValueError(f"No completed rounds found in {results_path}")
    return rounds


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Score existing solution_report.md files with all six ModelingBench "
            f"dimensions using {JUDGE_MODEL}."
        )
    )
    parser.add_argument("--experiment", type=Path, default=DEFAULT_EXPERIMENT)
    parser.add_argument(
        "--rounds",
        nargs="+",
        help="Rounds such as 1 2 3, 1,2,3, or 1-5; defaults to all completed rounds.",
    )
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--excel-output", type=Path)
    parser.add_argument("--base-url")
    parser.add_argument("--api-key")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--remove-expert-impact", action="store_true",
                        help="Back up reports, create section-free copies and evaluate those copies.")
    parser.add_argument("--prepare-only", action="store_true",
                        help="Prepare report copies without calling the Judge.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    experiment = args.experiment.resolve()
    if not experiment.is_dir():
        raise FileNotFoundError(f"Experiment not found: {experiment}")
    rounds = (
        evaluator.parse_rounds(args.rounds)
        if args.rounds
        else completed_rounds(experiment)
    )
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else experiment / "workflows" / (
            "deepseek_v4_flash_six_dimension_evaluation_without_expert_impact"
            if args.remove_expert_impact else "deepseek_v4_flash_six_dimension_evaluation"
        )
    )
    excel_output = (
        args.excel_output.resolve()
        if args.excel_output
        else output_dir / "six_dimension_scores.xlsx"
    )
    reports = evaluator.load_reports(experiment, rounds)
    if args.remove_expert_impact:
        reports = prepare_reports(reports, dry_run=args.dry_run)
    if args.prepare_only:
        if not args.remove_expert_impact:
            raise ValueError("--prepare-only requires --remove-expert-impact")
        print(f"Prepared {len(reports)} reports; no Judge calls made.")
        return

    forwarded = [
        str(Path(evaluator.__file__).resolve()),
        "--experiment",
        str(experiment),
        "--rounds",
        *map(str, rounds),
        "--concurrency",
        str(args.concurrency),
        "--retries",
        str(args.retries),
        "--output-dir",
        str(output_dir),
        "--excel-output",
        str(excel_output),
        "--all-dimensions",
    ]
    if args.base_url:
        forwarded.extend(["--base-url", args.base_url])
    if args.api_key:
        forwarded.extend(["--api-key", args.api_key])
    if args.dry_run:
        forwarded.append("--dry-run")

    original_argv = sys.argv
    try:
        evaluator.JUDGE_MODEL = JUDGE_MODEL
        sys.argv = forwarded
        evaluator.main(reports_override=reports)
    finally:
        sys.argv = original_argv
    if not args.dry_run:
        export_comparisons(experiment, excel_output, output_dir)


if __name__ == "__main__":
    main()
