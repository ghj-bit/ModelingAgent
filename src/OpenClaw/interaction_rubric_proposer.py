"""Evolve the critic's interaction rubric once per round.

The co-evolution arm scores each round's consultation against a rubric and feeds
that review to the policy optimizer.  Nothing in the pipeline ever revises the
rubric itself: in CPE mode the engine loads it once and passes it by value, so a
rubric that mis-measures one round mis-measures every round after it.

This module adds the missing step.  Every round whose parent and candidate both
finished revises the rubric.  Which evidence the revision is made from is decided
here, in code, and never by the proposer:

* the candidate beat its parent on the training batch, so validation ran -- the
  revision is made from the parent's training record and the candidate's
  held-out record;
* the candidate did not beat its parent, so validation never ran -- the revision
  is made from the parent's and the candidate's training records alone, and the
  proposer is told there is no held-out evidence to lean on.

Both branches activate the new version for the rounds that follow.

Three deliberate properties:

* **The rubric file is markdown with ``[N]`` weights**, because that is the only
  shape ``interaction_strategy_critic`` can read (``rubric_criteria`` parses
  ``^\\[N\\] name:``).  The proposer answers in JSON, which is validated and then
  rendered into that markdown here, so a malformed reply cannot reach the critic.
* **One structural change per version.**  That is the protocol the rubric files
  themselves state, and it is what keeps consecutive versions comparable.
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
MAX_CRITERIA = 6
MAX_RUNS_IN_PROMPT = 8
MAX_DIALOGUE_CHARS = 4000
MAX_POLICY_CHARS = 6000

SYSTEM_PROMPT = """\
You are a methodologist who maintains the rubric that scores expert-consultation
practice in a mathematical-modeling pipeline. You are given the rubric in force,
the incumbent policy's record on the training batch, and the record of the policy
this round produced. That record is held-out when the round reached validation and
training-only when it did not; the evidence section says which. You return one
revised rubric. Reply with one JSON object and nothing else."""


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


def run_record(run: dict, run_dir: Path | None = None) -> str:
    """One run: its score, the questions asked, and the replies received.

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
        return "\n".join(lines)
    dialogue = dialogue_from_artifacts(run)
    if not dialogue and run_dir is not None:
        dialogue = dialogue_of(run_dir)
    if dialogue:
        lines.append(clip(dialogue, MAX_DIALOGUE_CHARS))
    summary = str(run.get("interaction_report_change_summary") or "").strip()
    if summary:
        lines.append(f"  （该 run 自述回复带来的改动：{summary}）")
    return "\n".join(lines)


def training_evidence_block(round_dir: Path) -> str:
    """The incumbent's record on this round's training batch.

    Read from the evidence file the engine already wrote for the optimizer, so
    the rubric sees the same rollouts the policy evolution saw.
    """
    evidence = workflow_evolution.read_json(
        round_dir / "training_parent_evidence.json", []
    )
    parents = evidence if isinstance(evidence, list) else evidence.get("training_parents") or []
    if not parents:
        return "（本轮没有母代训练证据）"
    blocks = []
    for parent in parents:
        training = parent.get("training_evidence") or {}
        blocks.append(
            "\n".join(
                [
                    f"### 母代 {parent.get('workflow_id', '')}"
                    f"（训练批次净效用 {parent.get('net_utility_on_current_training_batch')}）",
                    "",
                    clip((parent.get("workflow") or {}).get("policy_text"), MAX_POLICY_CHARS),
                    "",
                    *(
                        run_record(run)
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
    rubric_text = critic.rubric_text()
    if validated:
        task = [
            "修订上面这份 rubric，使它更能分辨「这次咨询是否真的产生了价值」——",
            "依据只能是上面的证据：母代在训练集上的表现，以及候选在验证集上的分数、策略与交互历史。",
            "验证集是 held-out，它的结果比训练集更能说明策略是否真的变好；如果验证没有通过，",
            "要考虑是否有一类「看起来成功、实际没有」的咨询没有被现行 rubric 罚到。",
        ]
    else:
        task = [
            "修订上面这份 rubric，使它更能分辨「这次咨询是否真的产生了价值」——",
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
            "硬性要求：",
            "",
            "- **只做一处结构性改动**：新增、拆分、改写或废止**一条**准则（这是这套 rubric 自己的演化协议）。",
            "- 保持 `[N] 准则名: 规则` 的 markdown 形态与「Deduct when…」句式；权重合计必须为 100。",
            "- 准则总数 2–6 条，彼此不重叠；每条都必须能在对话或产物里被观察到。",
            "- 每条准则的规则要写成可判定的行为要求，不要写成对模型整体的评价。",
            "- 不要针对某一轮的具体题目、数值或实体写规则。",
            "",
            "只输出一个 JSON 对象，描述**一处**编辑即可（不要复述整份 rubric，其余准则保持原样）：",
            "",
            '{"op": "reword | add | retire | split",',
            ' "target": "被改动的准则名（add 时为 null）",',
            ' "new_criteria": [{"name": "准则名", "max": 25, "rule": "规则文本，含 Deduct when…"}],',
            ' "weights": {"需要调权的准则名": 20},',
            ' "name": "新的 rubric 名称（可选，不要带 Interaction Strategy: 前缀）",',
            ' "evolution_rationale": "为什么这样改（引用上面的证据，直接给结论，不要写推理过程）",',
            ' "predicted_effect": "预期哪些准则的分数会移动、朝哪个方向、在哪一题上"}',
            "",
            "`op` 的含义：reword 改写 target（`new_criteria` 给 1 条改写后的）、"
            "add 新增（`new_criteria` 给 1 条、`target` 为 null）、"
            "retire 废止 target（`new_criteria` 留空）、"
            "split 把 target 拆成两条（`new_criteria` 给 2 条）。",
            "`weights` 只写你改动权重的准则；改动后所有准则权重合计必须恰好 100，不够或超出要在这里补平。",
            "",
        ]
    )


# --------------------------------------------------------------------------- #
# proposal


CRITERION_LINE = re.compile(r"^\[([\d.]+)\]\s*([^:]+):\s*(.+)$")
OPS = ("reword", "add", "retire", "split")


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


def apply_edit(criteria: list[dict], payload: dict) -> list[dict]:
    """Apply one edit to the criteria in force and return the new list.

    The edit is applied here rather than accepted as a rewritten rubric so the
    protocol holds by construction: exactly one criterion can move, and every
    other line is the same characters it was before.  A proposer that has to
    reproduce the whole rubric verbatim tends to hand back the rubric it was
    shown, which is an evolution that silently did not happen.
    """
    op = str(payload.get("op") or "").strip().lower()
    if op not in OPS:
        raise ValueError(f"op must be one of {OPS}, got {payload.get('op')!r}")
    replacements = [dict(item) for item in payload.get("new_criteria") or []]
    expected = {"reword": 1, "add": 1, "split": 2, "retire": 0}[op]
    if len(replacements) != expected:
        raise ValueError(f"{op} needs {expected} new_criteria, got {len(replacements)}")
    for item in replacements:
        for key in ("name", "rule"):
            text = str(item.get(key) or "").strip()
            if len(text) < 12:
                raise ValueError(f"new criterion {key} is too short to be a rule")
            item[key] = " ".join(text.split())
        try:
            item["max"] = float(item["max"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("new criterion needs a numeric max") from None

    if op == "add":
        updated = [*criteria, *replacements]
    else:
        index = find_criterion(criteria, payload.get("target"))
        if op == "reword":
            updated = [
                *criteria[:index],
                {**replacements[0], "max": replacements[0].get("max", criteria[index]["max"])},
                *criteria[index + 1:],
            ]
        elif op == "retire":
            updated = [*criteria[:index], *criteria[index + 1:]]
        else:  # split
            updated = [*criteria[:index], *replacements, *criteria[index + 1:]]

    for name, weight in (payload.get("weights") or {}).items():
        updated[find_criterion(updated, name)]["max"] = float(weight)
    return updated


def proposal_errors(payload: Any, current: list[dict]) -> list[str]:
    """Everything that must hold before a proposal is allowed to reach the critic."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["response is not a JSON object"]
    try:
        updated = apply_edit(current, payload)
    except (TypeError, ValueError) as error:
        return [str(error)]
    if not 2 <= len(updated) <= MAX_CRITERIA:
        errors.append(f"the rubric must keep 2..{MAX_CRITERIA} criteria, got {len(updated)}")
    total = sum(float(criterion["max"]) for criterion in updated)
    if abs(total - 100.0) > 0.01:
        errors.append(
            f"weights would sum to {total:g}, not 100; adjust them with the "
            "`weights` field"
        )
    if not payload.get("new_criteria") and not payload.get("weights"):
        errors.append("the edit changes nothing (no new_criteria and no weights)")
    if len(str(payload.get("evolution_rationale") or "").strip()) < 24:
        errors.append("evolution_rationale is missing or too short")
    return errors


def rubric_title(rubric_text: str) -> str:
    match = re.search(r"(?m)^\s*Interaction Strategy:\s*(.+)$", str(rubric_text or ""))
    return match.group(1).strip() if match else "Expert Consultation"


def render_rubric_markdown(
    criteria: list[dict], payload: dict, template: str | None = None
) -> str:
    """Render the applied criteria into the ``[N] name: rule`` markdown the critic parses.

    The scoring footer is carried over from the rubric being revised, because it
    is the instruction the critic reads about how to apply the criteria; dropping
    it on evolution would silently change a second thing per version.
    """
    # The file already states the heading; a name that repeats it would render as
    # "Interaction Strategy: Interaction Strategy: …".
    given = re.sub(
        r"(?i)^\s*interaction\s+strategy\s*:\s*", "", str(payload.get("name") or "").strip()
    )
    source = template if template is not None else critic.rubric_text()
    lines = [f"Interaction Strategy: {given or rubric_title(source)}", ""]
    for criterion in criteria:
        maximum = float(criterion["max"])
        weight = int(maximum) if maximum.is_integer() else maximum
        lines.append(f"[{weight}] {criterion['name'].strip()}: {criterion['rule'].strip()}")
        lines.append("")
    footer = rubric_footer(source)
    if footer:
        lines.append(footer)
    return "\n".join(lines).rstrip() + "\n"


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
    """Write this round's rubric version, and point later rounds at it.

    Every round whose parent and candidate both finished reaches this point, so
    every such round produces a version.  The branch is chosen here, in code:

    * the candidate beat its parent, so validation ran -- revise from the
      candidate's held-out record;
    * the candidate did not beat its parent, so validation never ran -- revise
      from both training records and say so in the prompt.

    ``None`` only when no rubric could be produced (a proposal that never became
    valid); the round itself is never lost.
    """
    held_out = held_out_result(result)
    validated = bool(result.get("train_accepted")) and bool(held_out)
    if result.get("train_accepted") and not held_out:
        # The engine runs validation inside the round, so this means the file is
        # missing rather than pending.  Fall through to the training-only
        # evidence rather than skipping the round, but say so.
        print(
            "[rubric] train-accepted round has no validation result on disk; "
            "revising from training evidence only",
            flush=True,
        )
    evidence = held_out if validated else result
    split_label = "验证集（held-out）" if validated else "训练集"
    print(
        f"[rubric] round {round_number} revising from "
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
            # The endpoint occasionally answers without a JSON object at all;
            # that is a rejected attempt, not a failed round.
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
    updated = apply_edit(current, payload)
    out_path.write_text(
        render_rubric_markdown(updated, payload, template=current_rubric_text),
        encoding="utf-8",
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
