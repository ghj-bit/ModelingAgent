"""Dump one interaction-evolution experiment's rounds into a single workbook.

The engine's own workbook (``interaction_workflow_excel.py``) carries the round
ledger, a one-line digest of each exchange and the timings.  What it does not
carry is the reading material: the full policy a round evolved, the full
question and reply of every exchange, what each run recorded about the
exchange's effect, and the Judge's per-criterion reasons.  Those are the four
things this script collects, one sheet each, plus a per-phase ledger so the
numbers can be read next to the text they came from.

    python scripts/export_rounds_xlsx.py --exp <experiment-dir> [--out <xlsx>]

Re-run it as rounds complete; every sheet is rebuilt from what is on disk.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

REPO = pathlib.Path(__file__).resolve().parents[1]

# Excel refuses a cell over 32,767 characters; keep a margin for the marker.
CELL_LIMIT = 32000
TRUNCATED = "\n…[截断]"

OPERATOR = re.compile(r"Operator\s*(\d+)")
HEADING = re.compile(r"(?im)^#{1,4}\s*(.*Operator\s*\d.*)$")

SHEETS = (
    "轮次总览",
    "交互策略",
    "交互内容",
    "交互证据",
    "judge反馈",
)
WIDTHS = {
    "轮次总览": [6, 26, 12, 26, 30, 30, 6, 10, 10, 10, 10, 10, 10, 10, 20, 8],
    "交互策略": [6, 26, 20, 20, 10, 22, 20, 60, 90, 60],
    "交互内容": [6, 26, 26, 10, 6, 6, 34, 90, 9, 90, 9, 60],
    "交互证据": [6, 26, 26, 10, 6, 8, 10, 10, 90, 90, 60],
    "judge反馈": [6, 26, 26, 10, 6, 22, 34, 8, 8, 90],
}


def read_json(path: pathlib.Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def cell_text(value) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    if len(text) > CELL_LIMIT:
        return text[:CELL_LIMIT] + TRUNCATED
    return text


def number(value, digits: int = 4):
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def phase_split(phase: str) -> str:
    if "validation" in phase:
        return "validation"
    if phase.startswith("train"):
        return "train"
    return phase


def runs_of(experiment: pathlib.Path):
    """Every completed run directory, as (round, phase, run_dir, meta)."""
    for round_dir in sorted(experiment.glob("cpe_evaluations/round_*")):
        match = re.fullmatch(r"round_(\d+)", round_dir.name)
        if not match:
            continue
        round_number = int(match.group(1))
        for phase_dir in sorted(round_dir.iterdir()):
            if not phase_dir.is_dir():
                continue
            run_root = phase_dir / "runs" / round_dir.name
            if not run_root.is_dir():
                continue
            for run_dir in sorted(run_root.iterdir()):
                meta = read_json(run_dir / "meta" / "run.json", {})
                yield round_number, phase_dir.name, run_dir, meta


def exchanges_of(run_dir: pathlib.Path):
    """(exchange number, operator, question, reply) for each recorded exchange."""
    feedback = run_dir / "output" / "logs" / "operator_feedback"
    if not feedback.is_dir():
        return []
    found = []
    for question_path in sorted(feedback.glob("expert_question_*.md")):
        # A killed run can leave a question file with no exchange number in its
        # name; there is no reply to pair it with, so it is skipped.
        match = re.search(r"(\d+)", question_path.stem)
        if not match:
            continue
        index = int(match.group(1))
        question = read_text(question_path)
        heading = HEADING.search(question)
        operator = OPERATOR.search(heading.group(1)) if heading else OPERATOR.search(question)
        reply_path = feedback / f"expert_reply_{index}.json"
        reply = read_json(reply_path, {})
        found.append(
            (
                index,
                f"Operator {operator.group(1)}" if operator else "",
                question.strip(),
                str(reply.get("answer") or "").strip(),
            )
        )
    return found


def judge_of(run_dir: pathlib.Path):
    """Per-criterion score (trials pooled) and reasons for one run."""
    stability = read_json(run_dir / "meta" / "mmbench_judge" / "judge_stability.json", {})
    pooled: dict[tuple[str, str], list[float]] = {}
    reasons: dict[tuple[str, str], list[str]] = {}
    for trial in stability.get("trials") or []:
        for dimension, items in (trial.get("raw_result") or {}).items():
            if not isinstance(items, dict):
                continue
            for criterion, payload in items.items():
                if not isinstance(payload, dict) or "score" not in payload:
                    continue
                key = (dimension, criterion)
                pooled.setdefault(key, []).append(float(payload["score"]) / 10.0)
                reason = " ".join(str(payload.get("reason") or "").split())
                if reason and reason not in reasons.setdefault(key, []):
                    reasons[key].append(reason)
    return pooled, reasons, stability


def policy_of(experiment: pathlib.Path, round_number: int, phase: str) -> dict:
    path = (
        experiment
        / "cpe_evaluations"
        / f"round_{round_number}"
        / phase
        / "workflows"
        / f"round_{round_number}"
        / "workflow.json"
    )
    return read_json(path, {})


def round_records(experiment: pathlib.Path) -> dict[int, dict]:
    state = read_json(experiment / "workflows" / "cpe_state.json", {})
    return {int(k): (v.get("result") or {}) for k, v in (state.get("rounds") or {}).items()}


def policy_diff(candidate: str, parent: str) -> str:
    import difflib

    lines = difflib.unified_diff(
        (parent or "").splitlines(), (candidate or "").splitlines(), lineterm="", n=1
    )
    return "\n".join(line for line in lines if line[:1] in "+-@" and not line.startswith(("+++", "---")))


def build(experiment: pathlib.Path) -> Workbook:
    state = read_json(experiment / "workflows" / "cpe_state.json", {})
    records = round_records(experiment)
    seed = (state.get("initial_parent_validation_results") or [{}])[0]

    workbook = Workbook()
    workbook.remove(workbook.active)
    sheets = {name: workbook.create_sheet(name) for name in SHEETS}

    ledger = [("轮次", "阶段", "拆分", "策略名", "工作流ID", "题目", "题数", "净效用", "报告分", "交互成本", "交互惩罚", "训练闸门", "验证效用", "验证闸门", "完成时间", "运行数")]
    policies = [("轮次", "策略名", "工作流ID", "父代工作流ID", "来源", "演化算子", "改动组件", "演化理由", "策略全文", "与父代差异")]
    contents = [("轮次", "阶段", "策略名", "题目", "重复", "交换", "算子", "提问", "问字数", "回复", "答字数", "运行目录")]
    evidence = [("轮次", "阶段", "策略名", "题目", "重复", "交换次数", "交互成本", "交互惩罚", "交互证据（interaction_evidence.md）", "报告改动（interaction_added_content.md）", "交互回执")]
    feedback = [("轮次", "阶段", "策略名", "题目", "重复", "维度", "准则", "均分", "试次极差", "理由")]

    # Round 0 is the seed's own validation, and it is not in `rounds`.
    if seed:
        workflow = seed.get("workflow") or {}
        policies.append(
            (
                0,
                workflow.get("name") or "",
                seed.get("workflow_id") or "",
                "",
                "种子（round 0 验证）",
                seed.get("evolution_operator") or "initial_strategy",
                "",
                "",
                workflow.get("policy_text") or "",
                "",
            )
        )

    for round_number, phase, run_dir, meta in runs_of(experiment):
        result = read_json(
            experiment / "cpe_evaluations" / f"round_{round_number}" / phase / "workflows" / f"round_{round_number}" / "result.json",
            {},
        )
        workflow = result.get("workflow") or policy_of(experiment, round_number, phase)
        policy_name = workflow.get("name") or ""
        problem_id = str(meta.get("problem_id") or "")
        repetition = meta.get("repetition", "")
        exchanges = exchanges_of(run_dir)
        pooled, reasons, stability = judge_of(run_dir)

        receipt = read_json(run_dir / "output" / "results" / "interaction_receipt.json", {})
        evidence_path = run_dir / "output" / "results" / "interaction_evidence.md"
        added_path = run_dir / "output" / "results" / "interaction_added_content.md"
        if evidence_path.is_file():
            evidence.append(
                (
                    round_number,
                    phase,
                    policy_name,
                    problem_id,
                    repetition,
                    len(exchanges) or receipt.get("exchange_count", ""),
                    number(result.get("interaction_cost")),
                    number(result.get("interaction_penalty")),
                    read_text(evidence_path).strip(),
                    read_text(added_path).strip(),
                    cell_text(
                        {
                            "questions": receipt.get("questions_asked"),
                            "answers": receipt.get("expert_answers"),
                            "complete": receipt.get("interaction_complete"),
                        }
                    )
                    if receipt
                    else "",
                )
            )

        for index, operator, question, reply in exchanges:
            contents.append(
                (
                    round_number,
                    phase,
                    policy_name,
                    problem_id,
                    repetition,
                    index,
                    operator,
                    question,
                    len(question),
                    reply,
                    len(reply),
                    str(run_dir.relative_to(experiment)),
                )
            )

        for (dimension, criterion), scores in sorted(pooled.items()):
            feedback.append(
                (
                    round_number,
                    phase,
                    policy_name,
                    problem_id,
                    repetition,
                    dimension,
                    criterion,
                    round(statistics.mean(scores), 3),
                    round(max(scores) - min(scores), 3),
                    " | ".join(reasons.get((dimension, criterion), [])[:2]),
                )
            )

    # Phase-level ledger rows.
    phase_runs: dict[tuple[int, str], int] = {}
    for round_number, phase, _, _ in runs_of(experiment):
        key = (round_number, phase)
        phase_runs[key] = phase_runs.get(key, 0) + 1

    seen: set[tuple[int, str]] = set()
    for round_number, phase, run_dir, meta in runs_of(experiment):
        if (round_number, phase) in seen:
            continue
        seen.add((round_number, phase))
        result = read_json(
            experiment / "cpe_evaluations" / f"round_{round_number}" / phase / "workflows" / f"round_{round_number}" / "result.json",
            {},
        )
        workflow = result.get("workflow") or policy_of(experiment, round_number, phase)
        problems = result.get("evaluation_problems") or []
        # The gates are decided per round, not per phase, so they repeat on the
        # rows of the round they belong to.
        record = records.get(round_number) or {}
        runs = phase_runs.get((round_number, phase), 0)
        ledger.append(
            (
                round_number,
                phase,
                result.get("evaluation_split") or phase_split(phase),
                workflow.get("name") or "",
                result.get("workflow_id") or workflow.get("workflow_id") or "",
                ", ".join(map(str, problems)),
                len(problems),
                number(result.get("net_utility") or result.get("utility")),
                number(result.get("absolute_utility")),
                number(result.get("interaction_cost")),
                number(result.get("interaction_penalty")),
                "接受" if record.get("train_accepted") else ("拒绝" if record else ""),
                number(record.get("validation_utility")),
                "接受" if record.get("validation_accepted") else ("拒绝" if record.get("validation_utility") is not None else ""),
                result.get("completed_at") or "",
                runs,
            )
        )

    # Policy rows: the seed, then each round's candidate with its parent's text.
    parent_text = (seed.get("workflow") or {}).get("policy_text") or ""
    for round_number in sorted(records):
        record = records[round_number]
        workflow = record.get("workflow") or {}
        if not workflow:
            continue
        parents = record.get("parent_workflow_ids") or []
        policies.append(
            (
                round_number,
                workflow.get("name") or "",
                record.get("workflow_id") or "",
                ", ".join(parents),
                "轮内候选",
                record.get("evolution_operator") or "",
                ", ".join(workflow.get("changed_components") or []),
                workflow.get("evolution_rationale") or "",
                workflow.get("policy_text") or "",
                policy_diff(workflow.get("policy_text") or "", parent_text),
            )
        )
        parent_text = workflow.get("policy_text") or ""

    for name, headers in (
        ("轮次总览", ledger),
        ("交互策略", policies),
        ("交互内容", contents),
        ("交互证据", evidence),
        ("judge反馈", feedback),
    ):
        sheet = sheets[name]
        sheet.append(list(headers[0]))
        for row in headers[1:]:
            sheet.append([cell_text(value) for value in row])
        for index, width in enumerate(WIDTHS[name], start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for cell in sheet[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        sheet.freeze_panes = "A2"
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
    return workbook


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp", required=True, help="experiment directory")
    parser.add_argument("--out", default="", help="target .xlsx (default: <exp>/rounds_export.xlsx)")
    args = parser.parse_args()

    experiment = pathlib.Path(args.exp).expanduser().resolve()
    if not (experiment / "workflows").is_dir():
        raise SystemExit(f"Not an experiment directory: {experiment}")
    out = pathlib.Path(args.out).expanduser() if args.out else experiment / "rounds_export.xlsx"

    workbook = build(experiment)
    workbook.save(out)
    for name in workbook.sheetnames:
        print(f"  {name}: {workbook[name].max_row - 1} 行")
    print(f"written {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
