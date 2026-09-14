"""Re-score existing interaction-rubric reports with DeepSeek V4 Pro.

This script reads reports recorded in an interaction-rubric experiment's
``workflows/results.json``.  It never starts OpenClaw or validates interaction
receipts, so it can be used as a standalone scoring/resume command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
JUDGER_DIR = REPO_ROOT / "src" / "judger"
if str(JUDGER_DIR) not in sys.path:
    sys.path.insert(0, str(JUDGER_DIR))

from evaluate_gpt4o_workspace import (  # noqa: E402
    configure_judgers,
)
from main_judge import MainJudger, result_file_path  # noqa: E402


DEFAULT_EXPERIMENT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_rubric_20260907_224917"
)
JUDGE_MODEL = "deepseek-v4-pro"
DEEPSEEK_OFFICIAL_BASE_URL = "https://api.deepseek.com"
EVALUATION_DIMENSIONS = (
    "structural_coherency",
    "scoring_decomposition",
    "modeling_groundedness",
    "analysis_groundedness",
)
ALL_DIMENSIONS = (
    "structural_coherency",
    "scoring_decomposition",
    "modeling_groundedness",
    "data_groundedness",
    "analysis_groundedness",
    "innovativeness",
)
DIMENSION_LABELS = {
    "structural_coherency": "结构完整度",
    "scoring_decomposition": "任务覆盖度",
    "modeling_groundedness": "建模扎实度",
    "analysis_groundedness": "分析扎实度",
    "data_groundedness": "数据扎实度",
    "innovativeness": "创新性",
}


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def parse_rounds(values: list[str]) -> list[int]:
    """Accept ``--rounds 1 2``, ``1,2`` and inclusive ranges such as ``1-3``."""
    rounds: list[int] = []
    for value in values:
        for token in value.split(","):
            token = token.strip()
            if not token:
                continue
            if "-" in token:
                start_text, separator, end_text = token.partition("-")
                if not separator or not start_text or not end_text:
                    raise ValueError(f"Invalid round range: {token}")
                start, end = int(start_text), int(end_text)
                if start > end:
                    raise ValueError(f"Round range must be ascending: {token}")
                rounds.extend(range(start, end + 1))
            else:
                rounds.append(int(token))
    if not rounds or any(round_number < 1 for round_number in rounds):
        raise ValueError("At least one positive round number is required")
    if len(rounds) != len(set(rounds)):
        raise ValueError("Round numbers must be unique")
    return rounds


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary.replace(path)


def export_excel(payload: dict[str, Any], path: Path) -> None:
    """Write analysis-friendly detail and aggregate score worksheets."""
    try:
        from openpyxl import Workbook
        from openpyxl.formatting.rule import ColorScaleRule
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError as error:
        raise RuntimeError(
            "Excel export requires openpyxl; install project requirements first"
        ) from error

    dimensions = tuple(payload["dimensions"])
    reports = payload.get("reports", [])
    workbook = Workbook()
    detail = workbook.active
    detail.title = "评分明细"
    detail_headers = [
        "轮次",
        "题目",
        "重复实验",
        *[DIMENSION_LABELS.get(name, name) for name in dimensions],
        "维度平均分",
        "状态",
        "报告路径",
        "Judge结果路径",
    ]
    detail.append(detail_headers)
    for report in reports:
        scores = report.get("dimension_scores", {})
        detail.append(
            [
                report["round"],
                report["problem_id"],
                report["repetition"],
                *[scores.get(name) for name in dimensions],
                report.get("average_score"),
                report.get("status"),
                report.get("report"),
                report.get("judge_result"),
            ]
        )

    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for report in reports:
        grouped[(report["round"], report["problem_id"])].append(report)
    summary = workbook.create_sheet("轮次题目汇总")
    summary_headers = [
        "轮次",
        "题目",
        "报告数",
        *[DIMENSION_LABELS.get(name, name) for name in dimensions],
        "维度平均分",
    ]
    summary.append(summary_headers)
    for (round_number, problem_id), items in sorted(grouped.items()):
        dimension_averages = []
        for name in dimensions:
            values = [
                item.get("dimension_scores", {}).get(name) for item in items
            ]
            values = [value for value in values if isinstance(value, (int, float))]
            dimension_averages.append(
                sum(values) / len(values) if values else None
            )
        valid_scores = [value for value in dimension_averages if value is not None]
        summary.append(
            [
                round_number,
                problem_id,
                len(items),
                *dimension_averages,
                sum(valid_scores) / len(valid_scores) if valid_scores else None,
            ]
        )

    round_groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for report in reports:
        round_groups[report["round"]].append(report)
    round_summary = workbook.create_sheet("轮次汇总")
    round_summary_headers = [
        "轮次",
        "报告数",
        *[DIMENSION_LABELS.get(name, name) for name in dimensions],
        "四维平均分",
        "六维平均分" if tuple(dimensions) == ALL_DIMENSIONS else "维度平均分",
    ]
    round_summary.append(round_summary_headers)
    for round_number, items in sorted(round_groups.items()):
        dimension_averages = []
        for name in dimensions:
            values = [
                item.get("dimension_scores", {}).get(name) for item in items
            ]
            values = [value for value in values if isinstance(value, (int, float))]
            dimension_averages.append(
                sum(values) / len(values) if values else None
            )
        valid_scores = [value for value in dimension_averages if value is not None]
        averages_by_dimension = dict(zip(dimensions, dimension_averages))
        four_dimension_values = [
            averages_by_dimension.get(name) for name in EVALUATION_DIMENSIONS
        ]
        four_dimension_values = [
            value for value in four_dimension_values if value is not None
        ]
        round_summary.append(
            [
                round_number,
                len(items),
                *dimension_averages,
                (
                    sum(four_dimension_values) / len(four_dimension_values)
                    if four_dimension_values
                    else None
                ),
                sum(valid_scores) / len(valid_scores) if valid_scores else None,
            ]
        )

    metadata = workbook.create_sheet("说明")
    metadata.append(["项目", "值"])
    metadata.append(["实验目录", payload.get("experiment")])
    metadata.append(["Judge模型", payload.get("judge_model")])
    metadata.append(["评估轮次", ", ".join(map(str, payload.get("rounds", [])))])
    metadata.append(["评分维度", ", ".join(dimensions)])
    metadata.append(["开始时间", payload.get("started_at")])
    metadata.append(["完成时间", payload.get("completed_at")])

    header_fill = PatternFill("solid", fgColor="1F4E78")
    score_fill = ColorScaleRule(
        start_type="num",
        start_value=0,
        start_color="F8696B",
        mid_type="num",
        mid_value=0.5,
        mid_color="FFEB84",
        end_type="num",
        end_value=1,
        end_color="63BE7B",
    )
    for sheet in workbook.worksheets:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
        for column_index, column_cells in enumerate(sheet.columns, start=1):
            values = [str(cell.value or "") for cell in column_cells]
            width = min(max(max(map(len, values)) + 2, 10), 55)
            sheet.column_dimensions[get_column_letter(column_index)].width = width

    for sheet, leading_columns, average_columns in (
        (detail, 3, 1),
        (summary, 3, 1),
        (round_summary, 2, 2),
    ):
        score_start = leading_columns + 1
        score_end = score_start + len(dimensions) + average_columns - 1
        for row in sheet.iter_rows(
            min_row=2,
            min_col=score_start,
            max_col=score_end,
        ):
            for cell in row:
                cell.number_format = "0.0000"
        if sheet.max_row >= 2:
            start_letter = get_column_letter(score_start)
            end_letter = get_column_letter(score_end)
            sheet.conditional_formatting.add(
                f"{start_letter}2:{end_letter}{sheet.max_row}", score_fill
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    workbook.save(temporary)
    temporary.replace(path)


def resolve_report(experiment: Path, round_number: int, item: dict) -> Path:
    report_value = item.get("final_report")
    if report_value:
        report = Path(str(report_value))
        if not report.is_absolute():
            report = experiment / report
        report = report.resolve()
        if report.is_file():
            return report

    run_value = item.get("run_dir")
    if run_value:
        run_dir = Path(str(run_value))
        candidates = [run_dir / "output" / "results" / "solution_report.md"]
        candidates.append(
            experiment
            / "runs"
            / f"round_{round_number}"
            / run_dir.name
            / "output"
            / "results"
            / "solution_report.md"
        )
        for candidate in candidates:
            if candidate.resolve().is_file():
                return candidate.resolve()
    raise FileNotFoundError(
        f"Report is missing for round {round_number}: {report_value!r}"
    )


def load_reports(experiment: Path, rounds: list[int]) -> list[dict[str, Any]]:
    results_path = experiment / "workflows" / "results.json"
    results = read_json(results_path)
    if not isinstance(results, list):
        raise ValueError(f"Expected a list in {results_path}")
    by_round = {
        item.get("round"): item for item in results if isinstance(item, dict)
    }
    reports: list[dict[str, Any]] = []
    for round_number in rounds:
        round_result = by_round.get(round_number)
        if not isinstance(round_result, dict):
            raise ValueError(
                f"Round {round_number} has no completed result in {results_path}"
            )
        problem_results = round_result.get("problem_results", [])
        if not isinstance(problem_results, list) or not problem_results:
            raise ValueError(f"Round {round_number} contains no problem reports")
        for problem_result in problem_results:
            problem_id = str(problem_result.get("problem_id", "")).strip()
            if not problem_id:
                raise ValueError(f"Round {round_number} has a missing problem_id")
            repetitions = problem_result.get("repetitions")
            candidates = repetitions if isinstance(repetitions, list) else []
            if not candidates:
                candidates = [problem_result]
            for fallback_index, repetition in enumerate(candidates, start=1):
                repetition_number = int(
                    repetition.get("repetition", fallback_index)
                )
                report = resolve_report(experiment, round_number, repetition)
                reports.append(
                    {
                        "round": round_number,
                        "problem_id": problem_id,
                        "repetition": repetition_number,
                        "report": report,
                    }
                )
    return reports


def dimension_score(judgement: dict[str, Any]) -> float | None:
    if judgement.get("error"):
        return None
    value = judgement.get("aggregated_score")
    if value is None:
        value = judgement.get("calculated_overall")
    return float(value) if isinstance(value, (int, float)) else None


def evaluate_one(
    report: dict[str, Any],
    benchmark: dict[str, Any],
    output_root: Path,
    dimensions: tuple[str, ...],
    api_key: str,
    base_url: str,
    retries: int,
) -> dict[str, Any]:
    problem_id = report["problem_id"]
    criteria = benchmark.get(problem_id)
    if not isinstance(criteria, dict):
        raise ValueError(f"Unknown benchmark problem: {problem_id}")

    report_path: Path = report["report"]
    writing = (
        f"# Submitted file: {report_path.name}\n\n"
        + report_path.read_text(encoding="utf-8")
    )
    report_hash = hashlib.sha1(str(report_path).encode("utf-8")).hexdigest()[:8]
    output_dir = (
        output_root
        / f"round_{report['round']}"
        / problem_id
        / f"repetition_{report['repetition']}_{report_hash}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    result: dict[str, Any] | None = None
    for attempt in range(1, retries + 1):
        judger = MainJudger(dimensions)
        configure_judgers(judger, api_key, base_url, JUDGE_MODEL)
        result = judger.judge(
            str(output_dir),
            problem_id,
            writing,
            criteria.get("decomposition", {}).get("grading_points", []),
            criteria.get("eval_roles", []),
        )
        judgements = result.get("judgements", {})
        missing = [
            name
            for name in dimensions
            if dimension_score(judgements.get(name, {})) is None
        ]
        if not missing:
            break
        print(
            f"[retry {attempt}/{retries}] round {report['round']} {problem_id}: "
            + ", ".join(missing),
            flush=True,
        )

    assert result is not None
    scores = {
        name: score
        for name in dimensions
        if (score := dimension_score(result.get("judgements", {}).get(name, {})))
        is not None
    }
    missing = [name for name in dimensions if name not in scores]
    return {
        "round": report["round"],
        "problem_id": problem_id,
        "repetition": report["repetition"],
        "report": str(report_path),
        "judge_result": str(result_file_path(output_dir, problem_id)),
        "dimension_scores": scores,
        "average_score": sum(scores.values()) / len(scores) if scores else None,
        "status": "completed" if not missing else "incomplete",
        "missing_dimensions": missing,
        "completed_at": now(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Directly score existing interaction-rubric reports with "
            "deepseek-v4-pro."
        )
    )
    parser.add_argument("--rounds", nargs="+", required=True)
    parser.add_argument("--experiment", type=Path, default=DEFAULT_EXPERIMENT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--excel-output",
        type=Path,
        help="Defaults to <output-dir>/four_dimension_scores.xlsx.",
    )
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument(
        "--all-dimensions",
        action="store_true",
        help="Score all six dimensions; the default matches the experiment's four.",
    )
    parser.add_argument(
        "--base-url",
        default=(
            os.environ.get("DEEPSEEK_JUDGE_BASE_URL")
            or os.environ.get("DEEPSEEK_BASE_URL")
            or DEEPSEEK_OFFICIAL_BASE_URL
        ),
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("DEEPSEEK_JUDGE_API_KEY"),
        help="Defaults to the dedicated DEEPSEEK_JUDGE_API_KEY variable.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only validate and list reports; do not call the Judge API.",
    )
    args = parser.parse_args()
    args.rounds = parse_rounds(args.rounds)
    args.experiment = args.experiment.resolve()
    if not args.experiment.is_dir():
        raise FileNotFoundError(f"Experiment not found: {args.experiment}")
    if args.concurrency < 1 or args.retries < 1:
        raise ValueError("concurrency and retries must be positive")
    if not args.dry_run and not str(args.api_key or "").strip():
        raise ValueError(
            "DeepSeek Judge API key is missing; set DEEPSEEK_JUDGE_API_KEY "
            "or pass --api-key"
        )
    args.api_key_source = (
        "--api-key"
        if "--api-key" in sys.argv
        else "DEEPSEEK_JUDGE_API_KEY"
        if os.environ.get("DEEPSEEK_JUDGE_API_KEY")
        else "not configured (dry run)"
    )
    args.output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else args.experiment / "workflows" / "deepseek_v4_pro_evaluation"
    )
    args.excel_output = (
        args.excel_output.resolve()
        if args.excel_output
        else args.output_dir / "four_dimension_scores.xlsx"
    )
    return args


def main(reports_override: list[dict[str, Any]] | None = None) -> None:
    args = parse_args()
    reports = reports_override if reports_override is not None else load_reports(args.experiment, args.rounds)
    dimensions = ALL_DIMENSIONS if args.all_dimensions else EVALUATION_DIMENSIONS
    print(f"Experiment: {args.experiment}")
    print("Rounds: " + ", ".join(map(str, args.rounds)))
    print(f"Reports: {len(reports)}")
    print(f"Judge model: {JUDGE_MODEL}")
    print(f"Judge API: {args.base_url}")
    print(f"Judge API key source: {args.api_key_source}")
    print("Dimensions: " + ", ".join(dimensions))
    print(f"Output: {args.output_dir}")
    print(f"Excel: {args.excel_output}")
    for report in reports:
        print(
            f"  round {report['round']} | {report['problem_id']} | "
            f"repetition {report['repetition']} | {report['report']}"
        )
    if args.dry_run:
        print("Dry run passed; no API calls were made.")
        return

    benchmark = read_json(REPO_ROOT / "data" / "modeling_data_final.json")
    payload: dict[str, Any] = {
        "experiment": str(args.experiment),
        "judge_model": JUDGE_MODEL,
        "rounds": args.rounds,
        "dimensions": list(dimensions),
        "reports": [],
        "started_at": now(),
    }
    checkpoint_path = args.output_dir / "results.json"
    checkpoint_lock = threading.Lock()

    def record(future: Any) -> None:
        result = future.result()
        with checkpoint_lock:
            payload["reports"].append(result)
            payload["reports"].sort(
                key=lambda item: (
                    item["round"], item["problem_id"], item["repetition"]
                )
            )
            write_json(checkpoint_path, payload)
            export_excel(payload, args.excel_output)
        print(
            f"Completed round {result['round']} {result['problem_id']} "
            f"rep {result['repetition']}: {result['average_score']}",
            flush=True,
        )

    with ThreadPoolExecutor(max_workers=min(args.concurrency, len(reports))) as pool:
        futures = [
            pool.submit(
                evaluate_one,
                report,
                benchmark,
                args.output_dir,
                dimensions,
                args.api_key,
                args.base_url,
                args.retries,
            )
            for report in reports
        ]
        for future in as_completed(futures):
            record(future)

    payload["completed_at"] = now()
    write_json(checkpoint_path, payload)
    export_excel(payload, args.excel_output)
    incomplete = [
        item for item in payload["reports"] if item["status"] != "completed"
    ]
    if incomplete:
        raise RuntimeError(
            f"{len(incomplete)} report(s) still have incomplete Judge results; "
            f"see {checkpoint_path}"
        )
    print(f"All evaluations completed: {checkpoint_path}")
    print(f"Excel summary: {args.excel_output}")


if __name__ == "__main__":
    main()
