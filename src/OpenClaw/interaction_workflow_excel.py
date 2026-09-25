"""Export every round's evolved interaction policy beside the dialogue it produced.

The workflow-evolution arm rewrites one human-expert *interaction policy* per
round and scores it by what the solver did while reading that policy.  Reading a
run back otherwise means opening ``workflows/round_N/workflow.json`` for the
policy, ``cpe_evaluations/round_N/train_candidate/.../interaction_receipt.json``
for the questions and replies, and ``workflows/round_N/result.json`` for the
verdict -- one file at a time, one round at a time.  This module folds all three
into a single workbook so rounds can be compared side by side.

Three rules shape the rest of the file:

* It never raises.  A round costs hours, so a missing directory, an absent
  field, or an unreadable artifact must degrade to a blank cell rather than take
  the round down with it.
* Every sheet is rebuilt from scratch on each call, and only after the round's
  own artifacts have been persisted.  Resumed rounds and rounds that finished
  while this module was still being written into the engine therefore appear
  without any migration step.
* Round results come off disk, not out of the caller's list.  ``results.json``
  is re-normalized on every persist and old rounds lose their per-run cost and
  utility fields there; ``workflows/round_N/result.json`` and the per-phase
  result files keep them.  The caller's list is only a fallback.

The candidate rollout is the only dialogue recorded, because it is the only one
the round is scored on: the parent re-measures a champion that earlier rounds
already describe, and validation runs the blind split.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from . import run_interaction_rubric_evolution as interaction
except ImportError:  # pragma: no cover - direct-file invocation support
    import run_interaction_rubric_evolution as interaction


WORKBOOK_NAME = "interaction_evolution.xlsx"

CANDIDATE_PHASE = "train_candidate"
PARENT_PHASES = ("initial_train_parent_1", "train_parent_1")
VALIDATION_PHASE = "validation"
SEED_PHASE = "initial_validation_parent_1"

SEED_ROUND = 0
SEED_LABEL = "0 (seed)"
DIFF_LIMIT = 6000
SUMMARY_LIMIT = 200
DIALOGUE_NAME = "human_expert_dialogue.md"

SHEET_STRATEGY = "轮次策略"
SHEET_HISTORY = "交互历史"
SHEET_TIMING = "轮次耗时"

HEADER_FILL = "1F4E78"
HEADER_FONT = "FFFFFF"

# No round in this arm stamps its finish: the MM-Bench judge checkpoint carries
# no completion time and an abandoned run never writes a result at all.  Starts
# come from `meta/run.json`, finishes from the newest artifact the phase left,
# and the label says so rather than implying a recorded interval.
TIMING_SOURCE = "run.json开始时间 + 工件mtime结束时间"


# --------------------------------------------------------------------------- #
# small readers


def read_json(path: Path, default: Any) -> Any:
    """Read one JSON artifact, treating any failure as an absent artifact."""
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return default


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def file_time(path: Path) -> datetime | None:
    try:
        return datetime.fromtimestamp(Path(path).stat().st_mtime)
    except OSError:
        return None


def latest_time_under(directory: Path) -> datetime | None:
    """Newest mtime in a directory, used when no artifact stamps a finish."""
    latest: datetime | None = None
    if not Path(directory).is_dir():
        return None
    for path in Path(directory).rglob("*"):
        stamp = file_time(path)
        if stamp is not None and (latest is None or stamp > latest):
            latest = stamp
    return latest


def earliest_start(directory: Path) -> datetime | None:
    """Earliest ``created_at`` across a phase's run directories."""
    starts = [
        parse_time(read_json(metadata, {}).get("created_at"))
        for metadata in Path(directory).glob("runs/round_*/*/meta/run.json")
    ]
    starts = [start for start in starts if start is not None]
    return min(starts) if starts else None


def format_time(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value is not None else ""


def minutes_between(start: datetime | None, end: datetime | None) -> float | None:
    if start is None or end is None or end < start:
        return None
    return (end - start).total_seconds() / 60.0


def first_number(*values: Any) -> float | None:
    """First value that parses as a number.

    Spelled out rather than chained with ``or`` because a real score of 0.0 is
    falsy, and a missing field must stay missing instead of collapsing to it.
    """
    for value in values:
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def first_value(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return ""


def yes_no(value: Any) -> str:
    if value is None:
        return ""
    return "是" if value else "否"


def join_lines(values: Any, separator: str = "\n") -> str:
    if not isinstance(values, (list, tuple)):
        return str(values or "")
    return separator.join(str(value) for value in values if str(value).strip())


def summarize(text: Any, limit: int = SUMMARY_LIMIT) -> str:
    """One scannable line: the sheet is unreadable if every row starts with a 10k cell."""
    collapsed = " ".join(str(text or "").split())
    return collapsed[:limit] + ("…" if len(collapsed) > limit else "")


# --------------------------------------------------------------------------- #
# strategies


def policy_diff(candidate: str, parent: str) -> str:
    """Report the policy lines a mutation added or rewrote, not a line-by-line diff.

    Multiset comparison rather than a positional diff: the steps are prose, and a
    paragraph inserted mid-step would otherwise mark every following line as
    changed, burying the one line the round actually moved.
    """
    if not parent:
        return "（无父代策略可比对）"
    before = Counter(line.strip() for line in str(parent).splitlines() if line.strip())
    after = Counter(line.strip() for line in str(candidate).splitlines() if line.strip())
    added = [
        line
        for line in (value.strip() for value in str(candidate).splitlines())
        if line and after[line] > before.get(line, 0)
    ]
    removed = [
        line
        for line in (value.strip() for value in str(parent).splitlines())
        if line and before[line] > after.get(line, 0)
    ]
    blocks = []
    if added:
        blocks.append("【新增/改写后】\n" + "\n".join(f"+ {line}" for line in added))
    if removed:
        blocks.append("【改写前】\n" + "\n".join(f"- {line}" for line in removed))
    if not blocks:
        return "（与父代逐行一致）"
    return "\n".join(blocks)[:DIFF_LIMIT]


def render_actions(workflow: dict[str, Any]) -> str:
    actions = workflow.get("actions")
    if not isinstance(actions, list):
        return ""
    rendered = []
    for index, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            continue
        rendered.append(
            f"{index}. [{action.get('action_type', '')}] {action.get('action_id', '')}\n"
            f"{action.get('rule', '')}"
        )
    return "\n\n".join(rendered)


def round_results(experiment: Path, results: list[dict]) -> dict[int, dict]:
    """Round number -> result, preferring the per-round file over the caller's list."""
    by_round: dict[int, dict] = {}
    for result in results:
        number = result.get("round")
        if isinstance(number, int):
            by_round[number] = result
    for path in sorted(experiment.glob("workflows/round_*/result.json")):
        name = path.parent.name.replace("round_", "")
        if not name.isdigit():
            continue
        stored = read_json(path, {})
        if isinstance(stored, dict) and stored:
            by_round[int(name)] = stored
    return by_round


def policy_index(
    experiment: Path, by_round: dict[int, dict]
) -> dict[str, dict[str, Any]]:
    """Map workflow id -> the round and policy that minted it.

    Parents are always either the frozen seed or an earlier round's candidate, so
    the seed file plus the round results cover every lineage the workbook has to
    draw.  The per-round ``workflow.json`` on disk is folded in as well: a round
    that was resumed from state may carry its policy on disk before the results
    list is rewritten.
    """
    index: dict[str, dict[str, Any]] = {}

    seed_workflows = read_json(experiment / "initial_interaction_workflows.json", [])
    if isinstance(seed_workflows, dict):
        seed_workflows = [seed_workflows]
    for seed in seed_workflows or []:
        workflow_id = str(seed.get("workflow_id", ""))
        if workflow_id:
            index[workflow_id] = {
                "round": SEED_ROUND,
                "workflow": seed,
            }

    for number, result in by_round.items():
        workflow = result.get("workflow")
        if not isinstance(workflow, dict):
            continue
        workflow_id = str(result.get("workflow_id") or workflow.get("workflow_id") or "")
        if workflow_id:
            index[workflow_id] = {"round": number, "workflow": workflow}

    for path in sorted(experiment.glob("workflows/round_*/workflow.json")):
        workflow = read_json(path, {})
        if not isinstance(workflow, dict):
            continue
        workflow_id = str(workflow.get("workflow_id", ""))
        if workflow_id and workflow_id not in index:
            index[workflow_id] = {
                "round": path.parent.name.replace("round_", ""),
                "workflow": workflow,
            }
    return index


def seed_result(experiment: Path) -> dict[str, Any]:
    """The seed's own validation rollout, which sets the first champion bar."""
    path = (
        experiment
        / "cpe_evaluations"
        / f"round_{SEED_ROUND}"
        / SEED_PHASE
        / "workflows"
        / f"round_{SEED_ROUND}"
        / "result.json"
    )
    return read_json(path, {})


def strategy_rows(
    experiment: Path, by_round: dict[int, dict]
) -> tuple[list[list[Any]], list[str]]:
    """One row per round: what the policy is, what it changed, and how it scored."""
    headers = [
        "轮次",
        "策略名",
        "工作流ID",
        "父代工作流ID",
        "父代轮次",
        "演化模式",
        "改动组件",
        "与父代的策略差异",
        "演化理由",
        "训练批次",
        "train父代效用",
        "train候选效用",
        "Δ(候选-父代)",
        "训练是否接受",
        "验证效用",
        "验证是否接受",
        "是否当前冠军",
        "策略字数",
        "最大交换次数",
        "终止条件",
        "完整策略全文",
        "完整步骤(actions)",
    ]
    index = policy_index(experiment, by_round)
    champion = read_json(experiment / "workflows" / "best_workflow.json", {}) or {}
    champion_id = str(champion.get("workflow_id", ""))

    rows: list[list[Any]] = []

    seed_entry = next(
        (entry for entry in index.values() if entry["round"] == SEED_ROUND), None
    )
    if seed_entry is not None:
        seed = seed_entry["workflow"]
        seed_validation = seed_result(experiment)
        rows.append(
            [
                SEED_LABEL,
                seed.get("name", ""),
                seed.get("workflow_id", ""),
                "",
                "",
                "初始种子(冻结)",
                "",
                "",
                "",
                "",
                None,
                None,
                None,
                "",
                first_number(seed_validation.get("utility")),
                yes_no(True) if seed_validation else "",
                yes_no(str(seed.get("workflow_id", "")) == champion_id),
                len(str(seed.get("policy_text", ""))),
                seed.get("max_exchanges", ""),
                seed.get("stop_condition", ""),
                seed.get("policy_text", ""),
                render_actions(seed),
            ]
        )

    for number in sorted(by_round):
        result = by_round[number]
        workflow = result.get("workflow") or {}
        parents = [
            str(parent) for parent in (result.get("training_parent_workflow_ids") or [])
        ]
        parent_entry = index.get(parents[0]) if parents else None
        parent_policy = ""
        parent_label = ""
        if parent_entry is not None:
            parent_label = str(parent_entry.get("round", ""))
            parent_policy = str(parent_entry["workflow"].get("policy_text", ""))
        pre = first_number(result.get("train_pre_utility"))
        post = first_number(result.get("train_post_utility"))
        rows.append(
            [
                number,
                workflow.get("name", ""),
                result.get("workflow_id", ""),
                join_lines(parents, "; "),
                parent_label,
                first_value(workflow.get("evolution_mode"), result.get("evolution_operator")),
                join_lines(workflow.get("changed_components"), "\n"),
                policy_diff(str(workflow.get("policy_text", "")), parent_policy),
                workflow.get("evolution_rationale", ""),
                join_lines(result.get("training_batch"), ", "),
                pre,
                post,
                None if pre is None or post is None else post - pre,
                yes_no(result.get("train_accepted")),
                first_number(result.get("validation_utility")),
                yes_no(result.get("validation_accepted")),
                yes_no(str(result.get("workflow_id", "")) == champion_id),
                len(str(workflow.get("policy_text", ""))),
                workflow.get("max_exchanges", ""),
                workflow.get("stop_condition", ""),
                workflow.get("policy_text", ""),
                render_actions(workflow),
            ]
        )
    return rows, headers


# --------------------------------------------------------------------------- #
# interaction history


def dialogue_text(run_dir: Path) -> str:
    path = Path(run_dir) / "output" / "logs" / "operator_feedback" / DIALOGUE_NAME
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def repetition_cost(
    problem: dict[str, Any], repetition: dict[str, Any]
) -> dict[str, Any] | None:
    """The cost record of one repetition, or ``None`` when it cannot be isolated.

    ``problem["interaction_cost_runs"]`` carries one entry per repetition, in the
    same order as ``problem["repetitions"]``, because the engine builds it by
    walking that list and calling ``cpe_interaction_cost`` on each ``run_dir``.
    The repetition itself does not carry the record.

    Summing the whole list -- which this used to do -- reports the problem's
    total as every one of its repetitions' cost, so each rep row overstated its
    own run and a column total double-counted.  When the entry cannot be matched
    the cell is left blank: an absent number is better than a wrong one.
    """
    own = [
        cost
        for cost in repetition.get("interaction_cost_runs") or []
        if isinstance(cost, dict)
    ]
    if own:
        return own[0]
    problem_costs = [
        cost for cost in problem.get("interaction_cost_runs") or [] if isinstance(cost, dict)
    ]
    if not problem_costs:
        return None
    repetitions = problem.get("repetitions") or []
    index = next((i for i, item in enumerate(repetitions) if item is repetition), None)
    if index is None:
        # A caller that passed a copy still identifies the repetition by number.
        wanted = repetition.get("repetition")
        if wanted is not None:
            index = next(
                (
                    i
                    for i, item in enumerate(repetitions)
                    if item.get("repetition") == wanted
                ),
                None,
            )
    if index is None or index >= len(problem_costs):
        return None
    return problem_costs[index]


def history_row(
    round_label: Any,
    workflow: dict[str, Any],
    workflow_id: str,
    problem: dict[str, Any],
    receipt: dict[str, Any],
    repetition: dict[str, Any],
) -> list[Any]:
    """One problem repetition: the questions asked, the replies, and what it cost.

    Cost is this repetition's own run, matched out of the problem's per-run list;
    the score is per-repetition too, since repetitions of the same problem are
    scored separately.  Net utility stays on the problem aggregate, which is the
    mean over repetitions -- there is no per-run figure to read and recomputing
    one here would have to duplicate the engine's cost weights.
    """
    questions = receipt.get("questions_asked") or []
    answers = receipt.get("expert_answers") or []
    run_dir = str(first_value(repetition.get("run_dir"), problem.get("run_dir")))
    cost = repetition_cost(problem, repetition)
    tokens = int(cost.get("total_tokens_approx", 0) or 0) if cost else 0
    latency = (
        float(cost.get("total_expert_latency_seconds", 0.0) or 0.0) if cost else 0.0
    )
    return [
        round_label,
        workflow.get("name", ""),
        workflow_id,
        first_value(problem.get("problem_id"), repetition.get("problem_id")),
        first_value(repetition.get("repetition"), problem.get("repetition")),
        first_value(receipt.get("exchange_count"), len(questions)),
        first_value(receipt.get("workflow_max_exchanges"), workflow.get("max_exchanges")),
        summarize(questions[0] if questions else ""),
        "\n\n".join(
            f"Q{index}: {question}" for index, question in enumerate(questions, start=1)
        ),
        "\n\n".join(
            f"A{index}: {answer}" for index, answer in enumerate(answers, start=1)
        ),
        dialogue_text(run_dir) if run_dir else "",
        tokens or None,
        round(latency, 2) if latency else None,
        first_number(repetition.get("average_score"), problem.get("average_score")),
        first_number(repetition.get("net_utility"), problem.get("net_utility")),
        run_dir,
        str(first_value(repetition.get("final_report"), problem.get("final_report"))),
    ]


def history_rows(
    experiment: Path, by_round: dict[int, dict]
) -> tuple[list[list[Any]], list[str]]:
    """One row per problem repetition the round's own policy ran."""
    headers = [
        "轮次",
        "策略名",
        "工作流ID",
        "题目ID",
        "重复号",
        "交互次数",
        "上限",
        "首问摘要",
        "提问(Q1..Qn)",
        "专家回复",
        "完整对话",
        "交互tokens",
        "专家延迟(秒)",
        "平均得分",
        "净效用",
        "运行目录",
        "最终报告",
    ]
    rows: list[list[Any]] = []
    for number in sorted(by_round):
        result = by_round[number]
        workflow = result.get("workflow") or {}
        workflow_id = str(result.get("workflow_id", ""))
        phase_dir = experiment / "cpe_evaluations" / f"round_{number}" / CANDIDATE_PHASE
        phase_result = read_json(
            phase_dir / "workflows" / f"round_{number}" / "result.json", {}
        )
        if phase_result.get("problem_results"):
            for problem in phase_result["problem_results"]:
                for repetition in problem.get("repetitions") or [problem]:
                    rows.append(
                        history_row(
                            number,
                            workflow,
                            workflow_id,
                            problem,
                            repetition.get("interaction_receipt") or {},
                            repetition,
                        )
                    )
            continue
        # No phase result yet: a round still running has run directories whose
        # receipts are already on disk, and a partial row beats no row.
        for run_dir in sorted((phase_dir / "runs" / f"round_{number}").glob("*")):
            metadata = read_json(run_dir / "meta" / "run.json", {})
            if not metadata:
                # Stray partial directories (an interrupted launch) hold no run
                # metadata and would otherwise enter the sheet as blank rows.
                continue
            judge = read_json(
                run_dir / "meta" / "mmbench_judge" / "judge_stability.json", {}
            )
            rows.append(
                history_row(
                    number,
                    workflow,
                    workflow_id,
                    {
                        "problem_id": metadata.get("problem_id", ""),
                        "repetition": metadata.get("repetition", ""),
                        "run_dir": str(run_dir),
                        "average_score": judge.get("average_score"),
                    },
                    read_json(
                        run_dir / "output" / "results" / "interaction_receipt.json", {}
                    ),
                    {"run_dir": str(run_dir)},
                )
            )
    return rows, headers


# --------------------------------------------------------------------------- #
# round timing


def round_timing(
    experiment: Path, round_number: int, result: dict | None
) -> list[Any]:
    """Wall-clock of one full round, split by the phase that consumed it.

    A round is not just its candidate evaluation: the parent re-measurement, the
    policy rewrite and -- when the candidate is accepted -- the validation batch
    all sit inside the same round.  Each phase's problems run concurrently, so
    every phase is a wall interval, never a sum.
    """
    round_dir = experiment / "workflows" / f"round_{round_number}"
    phase_dir = experiment / "cpe_evaluations" / f"round_{round_number}"

    if round_number == SEED_ROUND:
        # The seed round evolves nothing; it only has a blind-split rollout. The
        # start comes from run metadata, so it is reported without an inference
        # marker even here.
        seed_start = earliest_start(phase_dir / SEED_PHASE)
        seed_end = latest_time_under(phase_dir / SEED_PHASE)
        return [
            SEED_LABEL,
            "",
            format_time(seed_start),
            format_time(seed_end),
            minutes_between(seed_start, seed_end),
            None,
            None,
            None,
            minutes_between(seed_start, seed_end),
            "基线(非演化轮)" if seed_end else "未开始",
            TIMING_SOURCE,
        ]

    parent_start = None
    for phase in PARENT_PHASES:
        parent_start = earliest_start(phase_dir / phase) or parent_start
    # The evidence file is the phase's own end marker; a phase still judging has
    # one only when it is finished, so fall back to the newest artifact it left.
    parent_done = file_time(round_dir / "training_parent_evidence.json") or (
        latest_time_under(phase_dir / PARENT_PHASES[0])
        or latest_time_under(phase_dir / PARENT_PHASES[1])
    )
    evolution_done = file_time(round_dir / "evolution_response.json")
    candidate_start = earliest_start(phase_dir / CANDIDATE_PHASE)
    result_time = file_time(round_dir / "result.json")
    validation_start = earliest_start(phase_dir / VALIDATION_PHASE)
    validation_end = latest_time_under(phase_dir / VALIDATION_PHASE)

    # ``completed_at`` is stamped the moment the candidate phase ends, before the
    # champion gate launches, so it -- not the result file, which is rewritten
    # after validation -- is what bounds the candidate evaluation.
    candidate_done = parse_time((result or {}).get("completed_at"))
    if candidate_done is None:
        candidate_done = validation_start or result_time

    start = parent_start or candidate_start
    end = max(
        [value for value in (result_time, validation_end) if value is not None],
        default=None,
    )
    return [
        round_number,
        (result or {}).get("workflow", {}).get("name", ""),
        format_time(start),
        format_time(end),
        minutes_between(start, end),
        minutes_between(parent_start, parent_done),
        minutes_between(parent_done, evolution_done),
        minutes_between(candidate_start, candidate_done),
        minutes_between(validation_start, validation_end),
        "完成" if result_time is not None else "进行中",
        TIMING_SOURCE,
    ]


def timing_rows(
    experiment: Path, by_round: dict[int, dict]
) -> tuple[list[list[Any]], list[str]]:
    headers = [
        "轮次",
        "策略名",
        "轮次开始",
        "轮次结束",
        "轮次总耗时(分钟)",
        "父代评估(分钟)",
        "进化改写(分钟)",
        "候选评估(分钟)",
        "验证(分钟)",
        "状态",
        "计时来源",
    ]
    discovered = {
        int(path.name.replace("round_", ""))
        for path in (experiment / "cpe_evaluations").glob("round_*")
        if path.name.replace("round_", "").isdigit()
    }
    rounds = sorted(discovered | set(by_round) | {SEED_ROUND})
    return (
        [round_timing(experiment, number, by_round.get(number)) for number in rounds],
        headers,
    )


# --------------------------------------------------------------------------- #
# workbook


def write_interaction_evolution_workbook(
    output_path: Path,
    experiment: Path,
    results: list[dict] | None = None,
) -> Path:
    """Rewrite the strategy, history and timing sheets from the experiment's artifacts."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
    except ImportError as error:  # pragma: no cover - depends on the environment
        raise RuntimeError(
            "Excel interaction export requires openpyxl; install project requirements first"
        ) from error

    output_path = Path(output_path)
    experiment = Path(experiment)
    if results is None:
        results = read_json(experiment / "workflows" / "results.json", [])
    if not isinstance(results, list):
        results = []
    by_round = round_results(experiment, results)

    strategies, strategy_headers = strategy_rows(experiment, by_round)
    history, history_headers = history_rows(experiment, by_round)
    timings, timing_headers = timing_rows(experiment, by_round)

    # Long text stays on one line: wrapped, a 10k-character question inflates its
    # row height until the sheet is unusable, and the cell is still fully readable
    # in the formula bar.  Everything else is centred, numbers included.
    text_columns = {
        SHEET_STRATEGY: {2, 4, 7, 8, 9, 20, 21, 22},
        SHEET_HISTORY: {2, 8, 9, 10, 11, 16, 17},
        SHEET_TIMING: {2},
    }
    numeric_columns = {
        SHEET_STRATEGY: {11: "0.0000", 12: "0.0000", 13: "0.0000", 15: "0.0000", 18: "0"},
        SHEET_HISTORY: {6: "0", 7: "0", 12: "0", 13: "0.00", 14: "0.0000", 15: "0.0000"},
        SHEET_TIMING: {5: "0.0", 6: "0.0", 7: "0.0", 8: "0.0", 9: "0.0"},
    }
    widths = {
        SHEET_STRATEGY: [
            8, 34, 30, 30, 10, 16, 55, 55, 60, 16,
            12, 12, 14, 11, 12, 11, 11, 10, 12, 45, 80, 60,
        ],
        SHEET_HISTORY: [8, 30, 30, 12, 8, 10, 8, 60, 90, 60, 80, 11, 12, 10, 10, 55, 55],
        SHEET_TIMING: [8, 34, 21, 21, 16, 14, 14, 14, 12, 10, 32],
    }

    workbook = Workbook()
    header_fill = PatternFill("solid", fgColor=HEADER_FILL)
    for title, headers, rows in (
        (SHEET_STRATEGY, strategy_headers, strategies),
        (SHEET_HISTORY, history_headers, history),
        (SHEET_TIMING, timing_headers, timings),
    ):
        sheet = workbook.active if title == SHEET_STRATEGY else workbook.create_sheet(title)
        sheet.title = title
        sheet.append(headers)
        for row in rows:
            # Every text cell, long or short, goes through the shared guard: it
            # truncates at Excel's cell limit and stops a question that opens with
            # "=" or "-" from being read as a formula.
            sheet.append([interaction.excel_cell_text(value) for value in row])
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(color=HEADER_FONT, bold=True)
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        for index, width in enumerate(widths[title], start=1):
            sheet.column_dimensions[sheet.cell(1, index).column_letter].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(
                    horizontal="left" if cell.column in text_columns[title] else "center",
                    vertical="center",
                )
                number_format = numeric_columns[title].get(cell.column)
                if number_format and isinstance(cell.value, (int, float)):
                    cell.number_format = number_format

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)
    return output_path
