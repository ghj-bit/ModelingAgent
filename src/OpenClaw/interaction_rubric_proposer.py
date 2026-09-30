"""Evolve the critic's interaction rubric once per round.

The co-evolution arm scores each round's consultation against a rubric and feeds
that review to the policy optimizer.  Nothing in the pipeline ever revises the
rubric itself: in CPE mode the engine loads it once and passes it by value, so a
rubric that mis-measures one round mis-measures every round after it.

This module adds the missing step.  Every round whose parent and candidate both
finished revises the rubric.  Which evidence the revision is made from is chosen
here, in code, and never by the proposer:

* the candidate beat its parent on the training batch, so validation ran -- the
  revision is made from the parent's training record and the candidate's held-out
  record;
* the candidate did not beat its parent, so validation never ran -- the revision
  is made from the parent's and the candidate's training records alone, and the
  proposer is told there is no held-out evidence to lean on.

Each version **appends one new criterion** -- a concise rule plus a short example
-- and leaves every earlier line byte-identical.  The protocol that could reword,
split and retire spent all five edits of the one run that used it on the same
criterion, each version longer than the last; appending keeps the rubric monotone
and two consecutive versions comparable.

Three deliberate properties:

* **The rubric file is markdown with ``[N]`` weights**, because that is the only
  shape ``interaction_strategy_critic`` can read (``rubric_criteria`` parses
  ``^\\[N\\] name:``).  The proposer answers in JSON, which is validated and then
  rendered into that markdown here, so a malformed reply cannot reach the critic.
* **One appended criterion per version.**  Nothing is reworded, split, retired or
  reweighted, so every earlier criterion is byte-identical in the next version.
* **Versions land in the experiment, not in ``src/``.**  A run's rubric lineage is
  part of that run's record; the hand-maintained ``v1..v4`` files stay the
  starting point.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

try:
    from . import interaction_strategy_critic as critic
    from . import run_interaction_rubric_evolution as interaction
    from . import run_evolution as workflow_evolution
except ImportError:  # pragma: no cover - direct-file invocation support
    import interaction_strategy_critic as critic
    import run_interaction_rubric_evolution as interaction
    import run_evolution as workflow_evolution


RUBRIC_FILENAME = re.compile(r"^interaction_strategy_rubric_v(\d+)\.md$")
MAX_RUNS_IN_PROMPT = 8
MAX_DIALOGUE_CHARS = 4000
MAX_POLICY_CHARS = 6000
# Per run, and per field of the submission: the four fields are what the Judge
# reads, and the point of showing them is which numbers appear in them and
# whether an exchange accounts for them -- not their full text.
MAX_SOLUTION_CHARS = 1800
SOLUTION_FIELDS = (
    ("task_description", 300),
    ("task_analysis", 400),
    ("mathematical_modeling_process", 500),
    ("subtask_outcome_analysis", 400),
)

SYSTEM_PROMPT = """\
You are a methodologist who maintains the rubric that scores expert-consultation
practice in a mathematical-modeling pipeline. You are given the rubric in force
together with the incumbent policy's and this round's candidate's records on the
training batch: the consultation each produced, its questions and replies, and its
scores. Each version of the rubric adds exactly one new criterion; a criterion
already in the rubric is never reworded, split, retired or reweighted. Reply with
one JSON object and nothing else."""


def current_rubric_path() -> Path:
    """The rubric the critic is using right now (``CRITIC_RUBRIC`` wins)."""
    return critic.rubric_path()


def next_rubric_path(experiment: Path, round_number: int) -> Path:
    """Where this round's version lands, numbered after the rubric it revises."""
    stem = current_rubric_path().stem
    match = RUBRIC_FILENAME.match(current_rubric_path().name)
    version = int(match.group(1)) + 1 if match else 1
    return (
        Path(experiment) / "workflows" / "rubric_evolution"
        / f"round_{round_number}" / f"interaction_strategy_rubric_v{version}.md"
    )


def held_out_result(result: dict) -> dict:
    """The round's validation result, or ``{}`` when the round never reached it.

    The engine runs validation inside the round, so by the time a round is
    persisted the file is either there or the round never got that far.
    """
    path = result.get("validation_result_path")
    if not path or not Path(str(path)).is_file():
        return {}
    return workflow_evolution.read_json(Path(str(path)), {})


def clip(text: Any, limit: int) -> str:
    body = str(text or "").strip()
    return body if len(body) <= limit else body[:limit] + "\n…（截断）"


# --------------------------------------------------------------------------- #
# evidence


def dialogue_of(run_dir: Path) -> str:
    for relative in (
        "output/logs/operator_feedback/human_expert_dialogue.md",
        "output/results/interaction_evidence.md",
    ):
        path = Path(run_dir) / relative
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="replace")
    return ""


def dialogue_from_artifacts(run: dict) -> str:
    """The dialogue a training-evidence run carries inline.

    The optimizer's evidence bundle inlines each run's consultation as an
    ``expert_interaction`` artifact and keeps no ``run_dir``, so this is the only
    way to read the parent's dialogue out of that file.
    """
    parts = [
        str(artifact.get("content") or "")
        for artifact in run.get("artifacts") or []
        if isinstance(artifact, dict)
        and artifact.get("artifact_type") == "expert_interaction"
    ]
    return "\n\n".join(part for part in parts if part.strip())


def solution_block(run_dir: Path | None) -> str:
    """The run's submitted ``solution.json``, showing the four fields the Judge scores.

    The Judge scores that container, not the report: ``task_analysis`` carries the
    rigor dimension, ``mathematical_modeling_process`` the practicality and
    scientificity one, ``subtask_outcome_analysis`` the result-and-bias one.  A
    criterion about what a consultation was worth cannot be written without seeing
    what the work ended up asserting -- which numbers it used, and whether any of
    them is traceable to an exchange or just appears.
    """
    if run_dir is None:
        return ""
    payload = workflow_evolution.read_json(
        Path(run_dir) / "output" / "results" / "solution.json", {}
    )
    tasks = payload.get("tasks") if isinstance(payload, dict) else None
    if not isinstance(tasks, list) or not tasks:
        return ""
    lines = ["  提交的 solution.json（MM-Bench 判分读的就是这四个字段）："]
    for index, task in enumerate(tasks[:2], start=1):
        if not isinstance(task, dict):
            continue
        lines.append(f"    Task {index}/{len(tasks)}：")
        for field, limit in SOLUTION_FIELDS:
            value = " ".join(str(task.get(field) or "").split())
            if value:
                lines.append(f"      {field}: {clip(value, limit)}")
    return clip("\n".join(lines), MAX_SOLUTION_CHARS) if len(lines) > 1 else ""


def run_record(run: dict, run_dir: Path | None = None) -> str:
    """One run: its score, the questions asked, the replies, and the submission.

    A validation run carries a receipt and a run directory; a training-evidence
    run carries the dialogue inline.  Both shapes reach this function, so it
    takes whichever is present.
    """
    receipt = run.get("interaction_receipt") or {}
    scores = run.get("scores") or {}
    score = run.get("average_score")
    if score is None:
        score = scores.get("report_score")
    exchanges = receipt.get("exchange_count")
    if exchanges is None:
        exchanges = len(receipt.get("questions_asked") or [])
    lines = [
        f"- **{run.get('problem_id', '')}** 重复 {run.get('repetition', '')}："
        f"得分 {score}，交互 {exchanges} 次",
    ]
    questions = receipt.get("questions_asked") or []
    answers = receipt.get("expert_answers") or []
    if questions or answers:
        for index, question in enumerate(questions, start=1):
            lines.append(f"  提问 {index}：\n{clip(question, MAX_DIALOGUE_CHARS)}")
        for index, answer in enumerate(answers, start=1):
            lines.append(f"  专家回复 {index}：{clip(answer, 1000)}")
    else:
        dialogue = dialogue_from_artifacts(run)
        if not dialogue and run_dir is not None:
            dialogue = dialogue_of(run_dir)
        if dialogue:
            lines.append(clip(dialogue, MAX_DIALOGUE_CHARS))
        summary = str(run.get("interaction_report_change_summary") or "").strip()
        if summary:
            lines.append(f"  （该 run 自述回复带来的改动：{summary}）")
    solution = solution_block(run_dir)
    if solution:
        lines.append(solution)
    return "\n".join(lines)


def parent_run_dirs(round_dir: Path) -> dict[tuple[int, str], Path]:
    """``(parent rank, problem id)`` -> run directory, for this round's parents.

    The evidence bundle inlines each parent's dialogue and carries no run
    directory, so the submissions are resolved from the phase results on disk.
    """
    experiment = round_dir.parent.parent
    round_name = round_dir.name
    mapping: dict[tuple[int, str], Path] = {}
    for phase_dir in sorted((experiment / "cpe_evaluations" / round_name).glob("train_parent_*")):
        try:
            rank = int(phase_dir.name.rsplit("_", 1)[-1])
        except ValueError:
            continue
        payload = workflow_evolution.read_json(
            phase_dir / "workflows" / round_name / "result.json", {}
        ) or {}
        for problem in payload.get("problem_results") or []:
            repetitions = problem.get("repetitions") or [problem]
            run_dir = str(repetitions[0].get("run_dir") or "")
            if run_dir:
                mapping[(rank, str(problem.get("problem_id")))] = Path(run_dir)
    return mapping


def training_evidence_block(round_dir: Path) -> str:
    """The incumbent's record on this round's training batch.

    Read from the evidence file the engine already wrote for the optimizer, so
    the rubric sees the same rollouts the policy evolution saw; the submissions
    come from the round's parent phase, which the bundle does not point at.
    """
    evidence = workflow_evolution.read_json(
        round_dir / "training_parent_evidence.json", []
    )
    parents = evidence if isinstance(evidence, list) else evidence.get("training_parents") or []
    if not parents:
        return "（本轮没有母代训练证据）"
    run_dirs = parent_run_dirs(round_dir)
    blocks = []
    for parent in parents:
        training = parent.get("training_evidence") or {}
        rank = int(parent.get("parent_rank") or 1)
        blocks.append(
            "\n".join(
                [
                    f"### 母代 {parent.get('workflow_id', '')}"
                    f"（训练批次净效用 {parent.get('net_utility_on_current_training_batch')}）",
                    "",
                    clip((parent.get("workflow") or {}).get("policy_text"), MAX_POLICY_CHARS),
                    "",
                    *(
                        run_record(run, run_dirs.get((rank, str(run.get("problem_id")))))
                        for run in (training.get("training_runs") or [])[:MAX_RUNS_IN_PROMPT]
                    ),
                ]
            )
        )
    return "\n\n".join(blocks)


def candidate_evidence_block(result: dict, split_label: str) -> str:
    """The candidate's record on ``split_label``: 分数、交互策略、交互历史.

    Reached with the held-out result when the round was validated and with the
    candidate's own training result when it was not, so the label is a parameter
    rather than a constant.
    """
    if not result:
        return f"（本轮没有{split_label}结果）"
    workflow = result.get("workflow") or {}
    lines = [
        f"- **效用**：{result.get('utility')}",
        f"- **四维均分**：{json.dumps(result.get('average_dimension_scores') or {}, ensure_ascii=False)}",
        "",
        "#### 候选交互策略全文",
        "",
        clip(workflow.get("policy_text"), MAX_POLICY_CHARS),
        "",
        "#### 逐题交互历史",
        "",
    ]
    for problem in (result.get("problem_results") or [])[:MAX_RUNS_IN_PROMPT]:
        for repetition in problem.get("repetitions") or [problem]:
            lines.append(run_record(repetition, Path(str(repetition.get("run_dir", "")))))
    return "\n".join(lines)


def decision_block(result: dict, validated: bool) -> str:
    lines = [
        f"- 母代训练净效用：{result.get('train_pre_utility')}",
        f"- 候选训练净效用：{result.get('train_post_utility')}",
        f"- 训练门（候选须高于母代 0.005 才进验证）：{'通过' if result.get('train_accepted') else '未通过'}",
    ]
    if validated:
        lines += [
            f"- 验证效用：{result.get('validation_utility')}",
            f"- 验证门（须高于现任冠军 +0.005）：{result.get('validation_accepted')}",
        ]
    else:
        lines.append("- 验证：未运行（候选未通过训练门，本轮没有 held-out 证据）")
    return "\n".join(lines)


def build_prompt(
    result: dict,
    round_dir: Path,
    evidence: dict,
    split_label: str,
    *,
    validated: bool,
) -> str:
    """One of two evidence variants, chosen from the round's gate outcome in code.

    * the candidate beat its parent on the training batch, so validation ran --
      the proposer sees the parent's training record and the candidate's
      held-out record, the only record that says whether a policy generalises;
    * it did not, so validation never ran -- both records come from the training
      batch, and the prompt says there is no held-out evidence to lean on.

    The protocol is the same in both variants: exactly one new criterion,
    appended, with a rule and a short example.
    """
    rubric_text = critic.rubric_text()
    if validated:
        task = [
            "为上面这份 rubric **新增一条子项**，使它更能分辨「这次咨询是否真的产生了价值」——",
            "依据只能是上面的证据：母代在训练集上的表现，以及候选在验证集上的分数、策略与交互历史。",
            "验证集是 held-out，它的结果比训练集更能说明策略是否真的变好；如果验证没有通过，",
            "要考虑是否有一类「看起来成功、实际没有」的咨询没有被现行 rubric 罚到。",
        ]
    else:
        task = [
            "为上面这份 rubric **新增一条子项**，使它更能分辨「这次咨询是否真的产生了价值」——",
            "依据只能是上面的证据：母代和候选在同一训练批次上的分数、策略与交互历史。",
            "本轮候选没有赢过母代，因此没有 held-out 证据：不要把「候选更差」当成前提，",
            "两个策略在训练批次上都没被现行 rubric 罚到的地方，才是要找的盲区。",
        ]
    return "\n".join(
        [
            "# 现行 rubric",
            "",
            rubric_text.strip(),
            "",
            "# 本轮母代在训练集上的表现",
            "",
            training_evidence_block(round_dir),
            "",
            f"# 本轮候选在{split_label}上的表现",
            "",
            candidate_evidence_block(evidence, split_label),
            "",
            "# 本轮的判定",
            "",
            decision_block(result, validated),
            "",
            "# 你的任务",
            "",
            *task,
            "",
            "先在上面证据里定位一类**信息层面的交互失败**，再把它写成一条可判定的子项。要看的是：",
            "",
            "- **该问没问**：报告或结果依赖某个量、约束或读法，而三次交换都没为它问过。",
            "- **问了没用**：答案本可从题面/数据/标准推导得到，或它没有落到任何计算、结构、假设、局限里。",
            "- **问得不合理**：题头声明的算子类型与问题正文不符，或一次交换塞进多个独立决策，使回复无法被采用。",
            "- **只有 held-out 才暴露**（有验证证据时）：训练集上分不低、验证掉下来的那类咨询 ——「看起来成功、实际没有」的形态。",
            "",
            "新子项要能用上面的证据**直接核对**（能判「符合/不符合」），并在 `predicted_effect` 里点名它在哪类题、哪一维上应把分压下来；",
            "不要复述已有子项已经罚过的行为。",
            "",
            "硬性要求：",
            "",
            "- **只新增一条子项**：不改写、不废止、不拆分任何已有子项，也不调整任何已有子项的权重。",
            "- 新子项自带权重 `max`（5–20 的整数）；已有子项那一行必须原样保留。",
            "- 规则要**简洁**：一到两句、能判「符合/不符合」的行为要求（≤ 60 词），不要写成对模型的整体评价。",
            "- **必须附一个短例子** `example`：一句话说明满足与不满足分别长什么样。",
            "- 不要针对某一轮的具体题目、数值或实体写规则。",
            "",
            "只输出一个 JSON 对象：",
            "",
            '{"criterion": {"name": "<子项名，≤ 8 词>", "max": 10,',
            '  "rule": "<简洁规则，含 Deduct when…>", "example": "<一句话例子>"},',
            ' "evolution_rationale": "为什么新增这一条（引用上面的证据，直接给结论，不要写推理过程）",',
            ' "predicted_effect": "预期哪些行为会被这条罚到、在哪类问题上"}',
            "",
        ]
    )


CRITERION_LINE = re.compile(r"^\[([\d.]+)\]\s*([^:]+):\s*(.+)$")


def parse_criteria(rubric_text: str) -> list[dict[str, Any]]:
    """``{name, max, rule}`` per criterion, in the order the rubric states them."""
    parsed = []
    for line in str(rubric_text or "").splitlines():
        match = CRITERION_LINE.match(line.strip())
        if not match:
            continue
        parsed.append(
            {
                "name": " ".join(match.group(2).split()),
                "max": float(match.group(1)),
                "rule": " ".join(match.group(3).split()),
            }
        )
    return parsed


def find_criterion(criteria: list[dict], name: str) -> int:
    wanted = " ".join(str(name or "").split()).lower()
    for index, criterion in enumerate(criteria):
        if criterion["name"].lower() == wanted:
            return index
    raise ValueError(f"target {name!r} is not a criterion in the rubric in force")


def append_criterion(criteria: list[dict], payload: dict) -> list[dict]:
    """Append the one new criterion this proposal asks for.

    Add-only is enforced by construction rather than by asking nicely: the
    proposer returns a criterion, and this function is what turns it into the
    next version.  Reword, split and retire are gone from the protocol because
    the run that had them spent every edit on the same criterion -- five versions
    of one rule, each longer than the last, none of them measuring anything new.
    """
    item = payload.get("criterion")
    if not isinstance(item, dict):
        raise ValueError("proposal needs exactly one `criterion` object")
    name = " ".join(str(item.get("name") or "").split())
    rule = " ".join(str(item.get("rule") or "").split())
    example = " ".join(str(item.get("example") or "").split())
    if len(name) < 8:
        raise ValueError("criterion name is too short")
    if len(rule) < 40:
        raise ValueError("criterion rule is too short to be judgeable")
    if len(example) < 20:
        raise ValueError("criterion example is missing or too short")
    if any(str(existing["name"]).lower() == name.lower() for existing in criteria):
        raise ValueError(f"criterion {name!r} is already in the rubric")
    try:
        maximum = float(item["max"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("criterion needs a numeric max") from None
    if not 1 <= maximum <= 25:
        raise ValueError(f"criterion max must be between 1 and 25, got {maximum:g}")
    return [*criteria, {"name": name, "max": maximum, "rule": rule, "example": example}]


def proposal_errors(payload: Any, current: list[dict]) -> list[str]:
    """Everything that must hold before a proposal is allowed to reach the critic."""
    if not isinstance(payload, dict):
        return ["response is not a JSON object"]
    try:
        append_criterion(current, payload)
    except (TypeError, ValueError) as error:
        return [str(error)]
    if len(str(payload.get("evolution_rationale") or "").strip()) < 24:
        return ["evolution_rationale is missing or too short"]
    return []


def rubric_title(rubric_text: str) -> str:
    match = re.search(r"(?m)^\s*Interaction Strategy:\s*(.+)$", str(rubric_text or ""))
    return match.group(1).strip() if match else "Expert Consultation"


def render_rubric_markdown(criteria: list[dict], template: str | None = None) -> str:
    """Render the criteria into the ``[N] name: rule`` markdown the critic parses.

    Before the criteria the file into whose line they go, so only what changed is
    the appended line; the title and the scoring footer are carried over, with the
    footer's normalization basis restated as the criteria's actual total (an
    appended criterion raises it above 100, and a footer that still said 100 would
    misstate how a total is normalized).
    """
    source = template if template is not None else critic.rubric_text()
    lines = [f"Interaction Strategy: {rubric_title(source)}", ""]
    for criterion in criteria:
        maximum = float(criterion["max"])
        weight = int(maximum) if maximum.is_integer() else maximum
        rule = str(criterion["rule"]).strip()
        example = str(criterion.get("example") or "").strip()
        if example:
            rule = f"{rule} Example: {example}"
        lines.append(f"[{weight}] {str(criterion['name']).strip()}: {rule}")
        lines.append("")
    footer = rubric_footer(source)
    if footer:
        lines.append(with_total(footer, sum(float(item["max"]) for item in criteria)))
    return "\n".join(lines).rstrip() + "\n"


def with_total(footer: str, total: float) -> str:
    """Restate a scoring footer's normalization basis as ``total``."""
    number = int(total) if float(total).is_integer() else total
    text = re.sub(r"theoretical maximum \([\d.]+\)", f"theoretical maximum ({number})", footer)
    return re.sub(r"total / [\d.]+", f"total / {number}", text)


def rubric_footer(rubric_text: str) -> str:
    """The scoring paragraph that follows the weighted criteria, if any."""
    body = str(rubric_text or "")
    match = re.search(r"(?ms)^(Scores are summed.*)$", body)
    return match.group(1).strip() if match else ""


def ensure_usable_direct_calls() -> None:
    """Turn provider thinking off before asking the local model for JSON.

    The shared client only disables thinking for DeepSeek base URLs.  Against the
    locally served model a thinking reply spends the whole token budget on
    reasoning and comes back with an empty body, which surfaces here as "no JSON
    object" rather than as the empty answer it is.  The launcher already does
    this at start-up; a stand-alone backfill would not, and would fail the same
    silent way, so the proposer makes sure of it itself.
    """
    try:
        from . import (
            run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base,
        )
    except ImportError:  # pragma: no cover - direct-file invocation support
        import run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base
    base.disable_thinking_for_direct_api_calls()


def evolve_rubric(
    experiment: Path,
    round_number: int,
    result: dict[str, Any],
    *,
    model: str,
    base_url: str,
    api_key: str,
    args: Any = None,
    retries: int = 2,
) -> Path | None:
    """Append this round's criterion, and point later rounds at the new version.

    Every round whose parent and candidate both finished reaches this point, and
    each of them produces a version.  Which evidence the criterion is proposed
    from is chosen here, in code:

    * the candidate beat its parent, so validation ran -- the proposer sees the
      parent's training record and the candidate's held-out record;
    * the candidate did not beat its parent, so validation never ran -- both
      records are the training batch's, and the prompt says so.

    ``None`` only when no proposal ever became valid; the round itself is never
    lost.
    """
    held_out = held_out_result(result)
    validated = bool(result.get("train_accepted")) and bool(held_out)
    if result.get("train_accepted") and not held_out:
        # Validation runs inside the round, so a missing file means it is absent
        # rather than pending.  Fall through to the training-only evidence and
        # say so, rather than losing the round.
        print(
            "[rubric] train-accepted round has no validation result on disk; "
            "appending from training evidence only",
            flush=True,
        )
    evidence = held_out if validated else result
    split_label = "验证集（held-out）" if validated else "训练集"
    print(
        f"[rubric] round {round_number} appending one criterion from "
        f"{'held-out validation' if validated else 'training evidence only'}",
        flush=True,
    )
    out_path = next_rubric_path(experiment, round_number)
    if out_path.is_file():
        # The round-end hook also runs on the resume path, so a version that was
        # already written for this round is left alone.
        print(f"[rubric] round {round_number} already evolved: {out_path.name}", flush=True)
        _activate(out_path)
        return out_path

    round_dir = Path(experiment) / "workflows" / f"round_{round_number}"
    prompt = build_prompt(
        result, round_dir, evidence, split_label, validated=validated
    )
    current_rubric_text = critic.rubric_text()
    current = parse_criteria(current_rubric_text)
    ensure_usable_direct_calls()

    class OptArgs:
        opt_model = model
        opt_base_url = base_url
        opt_api_key = api_key

    payload: dict[str, Any] = {}
    errors = ["not attempted"]
    for attempt in range(1, retries + 1):
        attempt_prompt = prompt
        if attempt > 1:
            attempt_prompt += (
                "\n上一次的回复被拒绝，原因：\n- " + "\n- ".join(errors)
                + "\n请修正后重新输出一个 JSON 对象。\n"
            )
        print(f"[rubric] proposing round {round_number} rubric (attempt {attempt})", flush=True)
        try:
            payload = interaction.local.optimizer_response(
                {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": attempt_prompt},
                    ],
                    "temperature": min(0.15 * attempt, 0.6),
                    "max_tokens": 4000,
                    "response_format": {"type": "json_object"},
                },
                OptArgs(),
            )
        except Exception as error:  # noqa: BLE001 - a bad reply is a retryable attempt
            errors = [f"{type(error).__name__}: {error}"]
            print(f"[rubric] attempt {attempt} unusable: {errors[0]}", flush=True)
            continue
        errors = proposal_errors(payload, current)
        if not errors:
            break
    if errors:
        print(f"[rubric] proposal rejected: {errors}", flush=True)
        return None

    out_path.parent.mkdir(parents=True, exist_ok=True)
    updated = append_criterion(current, payload)
    out_path.write_text(
        render_rubric_markdown(updated, template=current_rubric_text), encoding="utf-8"
    )
    workflow_evolution.write_json(
        out_path.with_suffix(".json"), {**payload, "applied_criteria": updated}
    )
    (out_path.parent / "evolution_prompt.md").write_text(prompt, encoding="utf-8")
    print(f"[rubric] round {round_number} rubric evolved: {out_path}", flush=True)
    _activate(out_path)
    return out_path


def _activate(path: Path) -> None:
    """Point the critic at the new version for every later round in this process.

    ``interaction_strategy_critic.rubric_path`` reads the environment on each
    call, so this takes effect from the next review on with no rebinding.
    """
    os.environ["CRITIC_RUBRIC"] = str(Path(path).resolve())
