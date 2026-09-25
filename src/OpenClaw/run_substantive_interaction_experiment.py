"""Evolve and evaluate substantive expert-interaction rubrics."""

from __future__ import annotations

import argparse
import atexit
import copy
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

try:
    from . import baseline
    from . import record_refinement_changes
    from . import run_evolution as workflow_evolution
    from . import run_interaction_rubric_evolution as interaction
except ImportError:
    import baseline
    import record_refinement_changes
    import run_evolution as workflow_evolution
    import run_interaction_rubric_evolution as interaction


REPO_ROOT = Path(__file__).resolve().parents[2]
RUBRIC_PATH = Path(__file__).with_name("interaction_initial_substantive_v1.json")
BASELINE_REPORT_ROOT = (
    REPO_ROOT / "output_workspace_openclaw_baseline" / "deepseek-deepseek-v4-flash"
)
DEFAULT_PROBLEMS = interaction.VALIDATION_PROBLEMS
DEFAULT_EXPERT_MODEL = "deepseek-v4-pro"
# Temporarily disabled by default. It can be enabled per execution with
# --enforce-substantive-interaction-gate without changing the experiment logic.
ENFORCE_SUBSTANTIVE_INTERACTION_GATE = False
ORIGINAL_PREPARE_VALIDATION_PROBLEM = interaction.prepare_validation_problem
EXPERT_REQUEST_TIMEOUT = 180.0
SECRET_PATTERNS = (
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(
        r'(?i)(["\']?(?:api[_-]?key|authorization|password|secret|token)'
        r'["\']?\s*[:=]\s*["\']?)[^\s,"\'}]+'
    ),
)

SUBSTANTIVE_EXPERT_ROLE_PROMPT = """\
You are an independent human mathematical-modeling expert represented through
an API. You are a non-computational decision adviser, not a calculator or model
implementer.

Read the complete authoritative problem statement appended below before
answering.

Answer only the question you are asked. Do not go beyond it: no extra advice, no
caveats, alternatives, or analysis the question did not ask for, and no
restatement or widening of the question.

Do not calculate results, invent parameters, prescribe code, use tools, or
provide a literature review. Keep the answer under 180 words.
"""

def now() -> str:
    return datetime.now().isoformat()


def redact_session_text(value: str) -> str:
    """Remove common credential forms before persisting a readable transcript."""
    text = str(value)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda match: match.group(1) + "[REDACTED]" if match.lastindex else "[REDACTED]", text)
    return text


def openclaw_session_file(agent_id: str, session_id: str) -> Path:
    state_root = Path(
        os.environ.get("OPENCLAW_STATE_DIR", str(Path.home() / ".openclaw"))
    )
    return state_root / "agents" / agent_id / "sessions" / f"{session_id}.jsonl"


def content_text(block: Any) -> str:
    if isinstance(block, str):
        return block
    if not isinstance(block, dict):
        return json.dumps(block, ensure_ascii=False, indent=2)
    if block.get("type") == "text":
        return str(block.get("text", ""))
    return json.dumps(block, ensure_ascii=False, indent=2)


def render_openclaw_session_log(
    agent_id: str,
    session_id: str,
    request_path: Path,
    log_path: Path,
) -> None:
    """Render OpenClaw's JSONL session as readable request/response events."""
    transcript = openclaw_session_file(agent_id, session_id)
    events: list[str] = [
        "# OpenClaw Session Execution Log",
        "",
        f"- Agent: `{agent_id}`",
        f"- Session: `{session_id}`",
        f"- Source transcript: `{transcript}`",
        "- Internal reasoning blocks are intentionally omitted.",
        "",
    ]
    event_number = 0
    omitted_reasoning = 0
    if transcript.is_file():
        with transcript.open(encoding="utf-8", errors="replace") as source:
            for raw_line in source:
                try:
                    item = json.loads(raw_line)
                except json.JSONDecodeError:
                    continue
                if item.get("type") != "message":
                    continue
                message = item.get("message")
                if not isinstance(message, dict):
                    continue
                role = str(message.get("role", "unknown"))
                content = message.get("content", [])
                blocks = content if isinstance(content, list) else [content]
                visible = []
                tool_calls = []
                for block in blocks:
                    if isinstance(block, dict) and block.get("type") == "thinking":
                        omitted_reasoning += 1
                        continue
                    if isinstance(block, dict) and block.get("type") == "toolCall":
                        tool_calls.append(block)
                        continue
                    rendered = content_text(block).strip()
                    if rendered:
                        visible.append(rendered)
                if not visible and not tool_calls:
                    continue
                event_number += 1
                timestamp = str(item.get("timestamp", ""))
                if role == "user":
                    title = "REQUEST"
                elif role == "assistant":
                    title = "RESPONSE"
                elif role == "toolResult":
                    title = f"TOOL RETURN: {message.get('toolName', 'unknown')}"
                else:
                    title = role.upper()
                events.extend([f"## Event {event_number} — {title}", ""])
                if timestamp:
                    events.extend([f"Timestamp: `{timestamp}`", ""])
                for text_value in visible:
                    events.extend([redact_session_text(text_value), ""])
                for call in tool_calls:
                    name = str(call.get("name", "unknown"))
                    arguments = call.get("arguments", {})
                    rendered_arguments = json.dumps(
                        arguments, ensure_ascii=False, indent=2
                    )
                    events.extend(
                        [
                            f"### Tool request: `{name}`",
                            "",
                            "```json",
                            redact_session_text(rendered_arguments),
                            "```",
                            "",
                        ]
                    )
    else:
        fallback = request_path.read_text(encoding="utf-8", errors="replace")
        events.extend(
            [
                "## Event 1 — REQUEST",
                "",
                redact_session_text(fallback),
                "",
                "## Session transcript unavailable",
                "",
                "OpenClaw did not create the expected JSONL transcript. See "
                "`meta/transport.log` for diagnostic output.",
                "",
            ]
        )
    events.extend(
        [
            "## Log summary",
            "",
            f"- Recorded events: {event_number}",
            f"- Omitted internal reasoning blocks: {omitted_reasoning}",
            "",
        ]
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(events), encoding="utf-8")


def create_substantive_operator_role_prompt(
    output_dir: Path,
    react_role_prompts: dict[str, str] | None = None,
    problem_id: str | None = None,
    problem: dict | None = None,
) -> None:
    """Create only the expert role required by synchronous consultation."""
    del react_role_prompts
    role_dir = output_dir / "logs" / "operator_roles"
    role_dir.mkdir(parents=True, exist_ok=True)
    (role_dir / "human_modeling_expert.md").write_text(
        baseline.human_expert_role_prompt(problem_id, problem), encoding="utf-8"
    )


def remove_unused_operator_role_prompts(output_dir: Path) -> list[Path]:
    """Remove baseline operator prompts that the substantive workflow never uses."""
    role_dir = Path(output_dir) / "logs" / "operator_roles"
    targets = [role_dir / "ask_expert.md", *role_dir.glob("react_verifier_*.md")]
    removed = []
    for path in targets:
        if path.is_file():
            path.unlink()
            removed.append(path)
    return removed


def load_rubric() -> dict[str, Any]:
    with RUBRIC_PATH.open(encoding="utf-8") as file:
        rubric = json.load(file)
    interaction.validate_rubric(rubric)
    return rubric


def non_full_role_evaluations(judge_result: dict) -> list[dict[str, Any]]:
    """Keep only non-perfect role-level overall scores and feedback."""
    selected = []
    judgements = judge_result.get("judgements", {})
    if not isinstance(judgements, dict):
        return selected
    for dimension in interaction.EVALUATION_DIMENSIONS:
        judgement = judgements.get(dimension, {})
        if not isinstance(judgement, dict):
            continue
        role_evaluations = []
        for role_result in judgement.get("role_based_results") or []:
            if not isinstance(role_result, dict):
                continue
            score = role_result.get("overall_score")
            feedback = str(role_result.get("overall_feedback", "")).strip()
            if (
                isinstance(score, (int, float))
                and float(score) < interaction.JUDGE_FEEDBACK_FULL_SCORE
                and feedback
            ):
                role_evaluations.append(
                    {
                        "overall_score": float(score),
                        "overall_feedback": feedback,
                    }
                )
        if role_evaluations:
            selected.append(
                {"dimension": dimension, "role_evaluations": role_evaluations}
            )
    return selected


def parent_artifacts(run_dir: Path) -> list[dict[str, str]]:
    """Return interaction records plus refined-side report additions."""
    output_dir = Path(run_dir) / "output"
    allowed = (
        ("expert_interaction", "logs/operator_feedback/human_expert_dialogue.md"),
        ("interaction_evidence", "results/interaction_evidence.md"),
        ("interaction_receipt", "results/interaction_receipt.json"),
        ("interaction_added_content", "results/interaction_added_content.md"),
    )
    artifacts = []
    for artifact_type, relative_path in allowed:
        path = output_dir / relative_path
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        if content:
            artifacts.append(
                (
                    path.stat().st_mtime_ns,
                    {"artifact_type": artifact_type, "content": content},
                )
            )
    artifacts.sort(key=lambda item: item[0])
    return [item[1] for item in artifacts]


def optimizer_evidence(results: list[dict], problems: dict) -> list[dict]:
    """Build optimizer evidence with raw non-perfect role evaluations."""
    problem_context = {
        item["problem_id"]: item
        for item in interaction.optimizer_problem_context(problems)
    }
    evidence = []
    for rank, node in enumerate(interaction.top_evolution_nodes(results), start=1):
        validation_runs = []
        for run in node.get("problem_results", []):
            judge_path = Path(str(run.get("judge_result", "")))
            validation_runs.append(
                {
                    **problem_context[run["problem_id"]],
                    "artifacts": parent_artifacts(Path(run["run_dir"])),
                    "non_full_role_evaluations": non_full_role_evaluations(
                        interaction.read_raw_judge_result(judge_path)
                    ),
                }
            )
        evidence.append(
            {
                "rank": rank,
                "round": node["round"],
                "utility": node["utility"],
                "rubric": node["rubric"],
                "validation_runs": validation_runs,
            }
        )
    return evidence


def propose_rubric(
    results: list[dict],
    round_number: int,
    round_dir: Path,
    args,
    problems: dict,
) -> dict:
    """Propose an unrestricted mutation, with crossover when two parents exist."""
    ranked = interaction.top_evolution_nodes(results, limit=len(results))
    primary = ranked[0]
    secondary = ranked[1] if len(ranked) > 1 else None
    evidence = optimizer_evidence(results, problems)
    operator = "crossover_mutation" if secondary else "mutation"
    prompt = f"""Evolve one compact, general rubric for substantive human-expert
interaction during mathematical-modeling work. Optimize the mean final-report
score across the validation tasks. There is no prescribed mutation axis or
evolution direction: use the evidence to decide what interaction mechanism to
retain, remove, combine, or change.

The Judge evidence contains only role evaluations whose overall_score is below
the full score. Use each supplied overall_score and overall_feedback directly;
do not infer missing positive feedback or hidden Judge criteria. Keep the rubric
general and do not copy task-specific facts, parameters, methods, or conclusions.
The interaction history precedes and influences the modeling work and final
report in each validation run. Treat the report as a downstream product of that
interaction: trace which expert input changed, added, removed, or reframed later
analysis, validation, conclusions, confidence, scope, or presentation. Evolve
the interaction mechanism to improve those downstream effects; do not assess
the dialogue and report as unrelated artifacts, and do not assume that merely
mentioning the expert in the report demonstrates useful influence.
Keep the complete consultation trace in interaction_evidence.md. A candidate
rubric must not require an `Expert Interaction Impact` section or another
consultation-process account in the final report; require the substantive
consequences to be integrated into its normal modeling sections instead.
The expert remains a qualitative adviser; calculation, implementation, and
validation remain the modeling agent's responsibility. Return one to four
non-overlapping criteria and an attention budget of one to three exchanges.

Evolution operator: {operator}

Primary parent:
{json.dumps(primary['rubric'], ensure_ascii=False, indent=2)}

Secondary parent:
{json.dumps(secondary['rubric'] if secondary else None, ensure_ascii=False, indent=2)}

Prior validation evidence:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

Every input needed for this proposal has already been read and embedded above by
the Python controller. Artifact inputs are limited to the expert dialogue,
interaction evidence, interaction receipt, and the programmatic
refined-report-versus-original additions artifact. The last of these is the
only report-change input and is computed exclusively from the two reports;
complete reports, code changes, result-file changes, and file-change manifests
are excluded. Do not attempt to open files, resolve paths, call tools, or
request any additional input.

Return only JSON with name, purpose, criteria, attention_budget, success_test,
mutation_rationale, and crossover_rationale. Each criterion must contain name,
rule, positive_example, and negative_example.
"""
    previous_ids = {item["rubric"]["rubric_id"] for item in results}
    last_error = None
    for attempt in range(1, args.optimizer_retries + 1):
        try:
            retry = (
                f"\nThe previous proposal was rejected: {last_error}\n"
                if last_error
                else ""
            )
            attempt_prompt = prompt + retry
            (round_dir / "evolution_prompt.md").write_text(
                attempt_prompt, encoding="utf-8"
            )
            candidate = interaction.local.optimizer_response(
                {
                    "model": args.opt_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Return one concise valid JSON object.",
                        },
                        {"role": "user", "content": attempt_prompt},
                    ],
                    "temperature": min(0.15 * attempt, 0.6),
                    "max_tokens": 2200,
                    "response_format": {"type": "json_object"},
                },
                args,
            )
            workflow_evolution.write_json(
                round_dir / "evolution_response.json", candidate
            )
            candidate.update(
                {
                    "parent_round": primary["round"],
                    "parent_rounds": [
                        primary["round"],
                        *([secondary["round"]] if secondary else []),
                    ],
                    "secondary_parent_round": secondary["round"] if secondary else None,
                    "evolution_operator": operator,
                    "created_round": round_number,
                    "evidence_rounds": [item["round"] for item in evidence],
                }
            )
            candidate["rubric_id"] = interaction.rubric_id(candidate)
            interaction.validate_rubric(candidate)
            if candidate["rubric_id"] in previous_ids:
                raise ValueError("optimizer returned a previously evaluated rubric")
            return candidate
        except Exception as error:
            last_error = error
            print(
                f"Substantive rubric proposal attempt {attempt}/"
                f"{args.optimizer_retries} failed: {error}",
                flush=True,
            )
    raise RuntimeError("Could not produce a valid substantive rubric") from last_error


def build_refinement_prompt(rubric: dict[str, Any]) -> str:
    """Build the complete Agent prompt for expert-guided draft refinement."""
    purpose = re.sub(
        r"that this change is explicitly traced to the reply in the final report",
        "that this change is explicitly documented in interaction_evidence.md",
        str(rubric["purpose"]),
        flags=re.IGNORECASE,
    )

    def execution_rule(criterion: dict[str, Any]) -> str:
        rule = str(criterion["rule"])
        normalized = rule.lower()
        if "expert interaction impact" in normalized or (
            "dedicated section" in normalized and "final report" in normalized
        ):
            return (
                "The interaction_evidence.md artifact must identify the expert's "
                "recommendation, the resulting analytical changes, and their "
                "effect on conclusions, confidence, scope, or presentation. "
                "Integrate the substantive changes into the final report's normal "
                "sections without adding a consultation-process section."
            )
        return rule

    criteria = "\n".join(
        f"{index}. **{criterion['name']}**: {execution_rule(criterion)}"
        for index, criterion in enumerate(rubric["criteria"], start=1)
    )
    return f"""# Expert-Guided Modeling Report Refinement

Refine the supplied no-interaction draft; do not solve the task again from
scratch.

## Problem Metadata

- Problem ID: `{{{{PROBLEM_ID}}}}`
- Title: {{{{TITLE}}}}
- Source: {{{{SOURCE}}}}
- Year: {{{{YEAR}}}}

## Authoritative Problem Statement

{{{{QUESTION}}}}

## Files

- Original draft (read-only): `{{{{RESULTS_DIR}}}}/original_report.md`
- Refined standalone report: `{{{{FINAL_REPORT}}}}`
- Interaction evidence: `{{{{RESULTS_DIR}}}}/interaction_evidence.md`
- Expert request/reply/dialogue: `{{{{OPERATOR_FEEDBACK_DIR}}}}`
- The rest of the baseline modeling workspace has been inherited at the same
  relative paths under `{{{{OUTPUT_DIR}}}}`, including reusable code, data,
  numerical results, and figures.

Read the original draft first. Preserve correct, unaffected material. Modify
the inherited files only where the expert interaction or necessary downstream
analysis justifies a change. If you modify executable code, model parameters,
or data-processing logic, execute the affected code again and regenerate every
dependent numerical result, table, and figure before updating the report. Do
not cite stale inherited outputs produced by an older version of the code.
Ensure that the refined report still answers the complete authoritative
problem.

## Interaction Rubric

**{rubric['name']}**: {purpose}

{criteria}

Artifact boundary: keep the complete consultation process, expert advice, and
trace from advice to analytical changes in
`{{{{RESULTS_DIR}}}}/interaction_evidence.md`. This boundary overrides any
rubric wording that asks for an expert-interaction section or consultation
trace in the final report. Incorporate the resulting substantive assumptions,
methods, validation, results, limitations, and conclusions into their normal
report sections without identifying them as expert-generated. The final report
must not contain a section titled `Expert Interaction Impact`.

Expert-attention budget: {rubric['attention_budget']}

Success test: {rubric['success_test']}

## Expert Interaction

- Before implementation, write only the qualitative question body to
  `{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_question_1.md`, then execute once in the
  foreground:
  `python "{{{{OUTPUT_DIR}}}}/code/wait_for_expert_reply.py" --request "{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_request_1.json" --reply "{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_reply_1.json" --timeout {EXPERT_REQUEST_TIMEOUT:.0f}`.
  The Python controller creates the fixed-schema request. Do not create or edit
  request/reply JSON and do not start process-poll or command-retry loops. Use a
  second numbered question only if the same decision remains unresolved.
- The controller writes `{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_reply_N.json` and
  `{{{{OPERATOR_FEEDBACK_DIR}}}}/human_expert_dialogue.md`; do not edit them.
- After the reply, write one concise
  `{{{{RESULTS_DIR}}}}/interaction_evidence.md` containing the baseline plan,
  the reply-triggered analytical change, paths to affected evidence, and the
  effect on the conclusion, confidence, scope, or presentation.
- Keep that process account in `interaction_evidence.md`. In the final report,
  include only its substantive modeling consequences in the relevant standard
  sections, without an expert-interaction section.

## Refinement Output

Write the complete refined Markdown report to `{{{{FINAL_REPORT}}}}`. Do not
edit `original_report.md`. The Python controller will compute the added or
revised content, file-change record, and one consolidated consistency check
after the run. Run affected Python programs directly; do not use shell output
redirection or Git. Do not expose private chain-of-thought.
"""


def append_expert_bridge_log(prepared: dict, message: str) -> None:
    """Persist concise request/reply lifecycle events for one run."""
    path = Path(prepared["run_dir"]) / "meta" / "expert_bridge.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{now()} {message}\n")


def configured_interaction_stages(prepared: dict) -> list[int]:
    """Read controller-authored workflow stages for sequential expert exchanges."""
    run_dir = Path(prepared["run_dir"])
    strategy = workflow_evolution.read_json(run_dir / "strategy.json", {})
    if not strategy:
        strategy = workflow_evolution.read_json(run_dir / "workflow.json", {})
    stages = []
    for action in strategy.get("actions", []):
        if action.get("action_type") != "expert_exchange":
            continue
        value = action.get("interaction_stage")
        if isinstance(value, int) and 1 <= value <= 6:
            stages.append(value)
    return stages or [2]


def wait_for_expert_question(
    question_path: Path,
    stop_event: threading.Event,
    final_report: Path,
    timeout: float | None,
) -> str | None:
    """Wait for a plain-text question until the run ends or a deadline expires."""
    deadline = time.monotonic() + timeout if timeout is not None else None
    while not stop_event.is_set():
        try:
            if question_path.is_file():
                question = question_path.read_text(encoding="utf-8").strip()
                if question:
                    return question
            if final_report.is_file() and final_report.read_text(
                encoding="utf-8"
            ).strip():
                return None
        except (OSError, UnicodeDecodeError):
            pass
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError(
                f"No expert question received within {timeout:.0f}s: {question_path}"
            )
        stop_event.wait(0.1)
    return None


def serve_substantive_expert_requests(
    prepared: dict,
    rubric: dict,
    args,
    stop_event: threading.Event,
    errors: list[Exception],
) -> None:
    """Convert plain questions into fixed requests and synchronously serve them."""
    feedback_dir = Path(prepared["output_dir"]) / "logs" / "operator_feedback"
    dialogue_path = feedback_dir / "human_expert_dialogue.md"
    role_path = (
        Path(prepared["output_dir"])
        / "logs"
        / "operator_roles"
        / "human_modeling_expert.md"
    )
    exchange = 0
    interaction_stages = configured_interaction_stages(prepared)
    try:
        if not role_path.is_file():
            raise FileNotFoundError(f"Human expert role prompt not found: {role_path}")
        role_prompt = role_path.read_text(encoding="utf-8")
        append_expert_bridge_log(prepared, "waiting for exchange 1 plain-text question")
        for exchange in range(1, 4):
            question_path = feedback_dir / f"expert_question_{exchange}.md"
            question = wait_for_expert_question(
                question_path,
                stop_event,
                Path(prepared["final_report"]),
                None,
            )
            if question is None:
                append_expert_bridge_log(prepared, "bridge stopped; no further question")
                return
            request_path = feedback_dir / f"expert_request_{exchange}.json"
            request = {
                "rubric_id": rubric["rubric_id"],
                "interaction_stage": interaction_stages[
                    min(exchange - 1, len(interaction_stages) - 1)
                ],
                "question": question,
            }
            interaction.write_json_atomic(request_path, request)
            append_expert_bridge_log(
                prepared,
                f"received exchange {exchange} question; wrote fixed request "
                f"({len(question)} chars; reply deadline="
                f"{args.expert_request_timeout:.0f}s)",
            )
            prior_dialogue = (
                dialogue_path.read_text(encoding="utf-8")
                if dialogue_path.is_file()
                else ""
            )
            # Keep the complete retry sequence within the same 180-second
            # handshake budget used by the blocking helper.
            expert_args = copy.copy(args)
            retry_sleep_budget = 5.0 * sum(
                range(1, max(1, expert_args.expert_attempts))
            )
            per_attempt_budget = max(
                1.0,
                (args.expert_request_timeout - retry_sleep_budget)
                / max(1, expert_args.expert_attempts),
            )
            expert_args.expert_timeout = min(
                expert_args.expert_timeout, per_attempt_budget
            )
            request_started = time.monotonic()
            answer = interaction.call_direct_human_expert(
                role_prompt, question, prior_dialogue, expert_args
            )
            request_elapsed = time.monotonic() - request_started
            if request_elapsed > args.expert_request_timeout:
                raise TimeoutError(
                    "Expert request/reply handshake exceeded "
                    f"{args.expert_request_timeout:.0f}s"
                )
            interaction.append_expert_dialogue(
                dialogue_path, exchange, question, answer
            )
            interaction.write_json_atomic(
                feedback_dir / f"expert_reply_{exchange}.json",
                {
                    "ok": True,
                    "exchange": exchange,
                    "question": question,
                    "answer": answer,
                    "rubric_id": rubric["rubric_id"],
                },
            )
            append_expert_bridge_log(
                prepared,
                f"completed exchange {exchange} reply ({len(answer)} chars; "
                f"{request_elapsed:.2f}s)",
            )
    except Exception as error:
        append_expert_bridge_log(
            prepared, f"bridge failed at exchange {exchange or 1}: {error!r}"
        )
        if exchange:
            reply_path = feedback_dir / f"expert_reply_{exchange}.json"
            if not reply_path.is_file():
                interaction.write_json_atomic(
                    reply_path,
                    {"ok": False, "exchange": exchange, "error": repr(error)},
                )
        errors.append(error)


def resolve_workspace_path(output_dir: Path, value: str) -> Path:
    candidate = (output_dir / value).resolve()
    try:
        candidate.relative_to(output_dir.resolve())
    except ValueError as error:
        raise ValueError(f"Artifact escapes the run workspace: {value}") from error
    return candidate


def has_expert_interaction_impact_section(report: str) -> bool:
    """Accept Markdown section headings with optional numeric numbering."""
    return re.search(
        r"^ {0,3}#{2,6}[ \t]+(?:\d+(?:\.\d+)*[.)]?[ \t]+)?"
        r"Expert[ \t]+Interaction[ \t]+Impact[ \t]*(?:#+[ \t]*)?\r?$",
        report,
        flags=re.MULTILINE | re.IGNORECASE,
    ) is not None


def validate_substantive_interaction(run_dir: Path) -> dict[str, Any]:
    """Check that the reply caused traceable post-reply analytical work."""
    output_dir = run_dir / "output"
    feedback_dir = output_dir / "logs" / "operator_feedback"
    results_dir = output_dir / "results"
    replies = []
    for path in sorted(feedback_dir.glob("expert_reply_*.json")):
        payload = workflow_evolution.read_json(path, {})
        if payload.get("ok") is True and str(payload.get("answer", "")).strip():
            replies.append(path)
    if not replies:
        raise RuntimeError("No successful expert reply exists")
    reply_path = replies[0]
    request_path = feedback_dir / reply_path.name.replace("reply", "request")
    request = workflow_evolution.read_json(request_path, {})
    if request.get("interaction_stage") not in range(1, 7):
        raise RuntimeError(
            "Expert consultation must occur before final-report assembly in "
            "Required Workflow stages 1 through 6; got "
            f"{request.get('interaction_stage')!r}"
        )

    evidence_path = results_dir / "interaction_evidence.md"
    if not evidence_path.is_file() or not evidence_path.read_text(
        encoding="utf-8", errors="replace"
    ).strip():
        raise FileNotFoundError(f"Interaction evidence is missing: {evidence_path}")
    if evidence_path.stat().st_mtime < reply_path.stat().st_mtime:
        raise RuntimeError(
            "Interaction evidence predates the expert reply and was not refreshed: "
            f"{evidence_path}"
        )

    final_report = results_dir / "solution_report.md"
    if not final_report.is_file():
        raise FileNotFoundError(f"Refined report is missing: {final_report}")
    final_report_text = final_report.read_text(encoding="utf-8", errors="replace")
    if has_expert_interaction_impact_section(final_report_text):
        raise RuntimeError(
            f"Refined report must not contain an 'Expert Interaction Impact' "
            f"section: {final_report}"
        )
    return {
        "passed": True,
        "request": str(request_path),
        "reply": str(reply_path),
        "interaction_stage": request["interaction_stage"],
        "post_reply_artifacts": [str(evidence_path)],
        "checked_at": now(),
    }


def finalize_substantive_receipt(result: dict, rubric: dict) -> dict:
    """Generate a compact receipt from the dialogue and single evidence note."""
    run_dir = Path(result["run_dir"])
    output_dir = run_dir / "output"
    feedback_dir = output_dir / "logs" / "operator_feedback"
    evidence_path = output_dir / "results" / "interaction_evidence.md"
    receipt_path = output_dir / "results" / "interaction_receipt.json"
    if not evidence_path.is_file() or not evidence_path.read_text(
        encoding="utf-8", errors="replace"
    ).strip():
        raise FileNotFoundError(f"Interaction evidence is missing: {evidence_path}")

    completed = interaction.completed_expert_exchanges(run_dir)
    questions = [item["question"] for item in completed]
    answers = [item["answer"] for item in completed]
    stages = []
    for item in completed:
        request = workflow_evolution.read_json(
            feedback_dir / f"expert_request_{item['exchange']}.json", {}
        )
        stages.append(request.get("interaction_stage"))
    receipt = {
        "rubric_id": rubric["rubric_id"],
        "interaction_stage": stages[0] if stages else None,
        "questions_asked": questions,
        "expert_answers": answers,
        "exchange_count": len(completed),
        "evidence_file": "results/interaction_evidence.md",
        "dialogue_file": "logs/operator_feedback/human_expert_dialogue.md",
        "interaction_complete": bool(completed),
        "generated_by": "python_controller",
    }
    interaction.write_json_atomic(receipt_path, receipt)
    return receipt


def resolve_baseline_report(problem_id: str, report_root: Path) -> Path:
    """Select the newest completed baseline report for one problem."""
    candidates = [
        path
        for path in Path(report_root).glob(
            f"{problem_id}_*/output/results/solution_report.md"
        )
        if path.is_file()
        and path.read_text(encoding="utf-8", errors="replace").strip()
    ]
    if not candidates:
        raise FileNotFoundError(
            f"No baseline report found for {problem_id} under {report_root}"
        )
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, str(path)))


BASELINE_RUNTIME_ROOT_FILES = {
    "AGENTS.md",
    "HEARTBEAT.md",
    "IDENTITY.md",
    "SOUL.md",
    "TOOLS.md",
    "USER.md",
    "openclaw-workspace-state.json",
    ".gitignore",
}


def inherit_baseline_workspace(
    source_report: Path, target_output: Path, *, overwrite: bool
) -> list[str]:
    """Copy reusable baseline workspace files while isolating old run state."""
    source_report = Path(source_report).resolve()
    source_output = source_report.parent.parent
    if source_report.parent.name != "results" or source_output.name != "output":
        raise ValueError(
            "Baseline report must be located at output/results/solution_report.md: "
            f"{source_report}"
        )

    copied = []
    for source in sorted(source_output.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(source_output)
        if relative.parts[0] in {"logs", ".git"}:
            continue
        if len(relative.parts) == 1 and relative.name in BASELINE_RUNTIME_ROOT_FILES:
            continue
        if relative.as_posix() == "code/wait_for_expert_reply.py":
            continue
        destination_relative = (
            Path("results/original_report.md")
            if relative.as_posix() == "results/solution_report.md"
            else relative
        )
        destination = Path(target_output) / destination_relative
        if destination.exists() and not overwrite:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(destination_relative.as_posix())
    return copied


def remove_run_git_metadata(output_dir: Path) -> list[str]:
    """Remove generated Git state so the refinement Agent cannot manage it."""
    output_dir = Path(output_dir).resolve()
    removed = []
    git_dir = output_dir / ".git"
    if git_dir.is_dir():
        shutil.rmtree(git_dir)
        removed.append(".git/")
    gitignore = output_dir / ".gitignore"
    if gitignore.is_file():
        gitignore.unlink()
        removed.append(".gitignore")
    return removed


def prepare_refinement_validation_problem(
    problem_id: str,
    problem: dict,
    prompt_path: Path,
    round_number: int,
    repetition: int,
    experiment: Path,
    args,
) -> dict:
    """Prepare a normal interaction run, then install its fixed baseline draft."""
    prepared = ORIGINAL_PREPARE_VALIDATION_PROBLEM(
        problem_id,
        problem,
        prompt_path,
        round_number,
        repetition,
        experiment,
        args,
    )
    output_dir = Path(prepared["output_dir"])
    source_report = Path(args.baseline_reports[problem_id])
    inherited_files = inherit_baseline_workspace(
        source_report,
        output_dir,
        overwrite=not prepared["recovered"],
    )
    removed_git_metadata = remove_run_git_metadata(output_dir)
    original_report = output_dir / "results" / "original_report.md"
    if not original_report.is_file():
        raise FileNotFoundError(
            f"Baseline inheritance did not create the original draft: {original_report}"
        )
    manifest_path = output_dir / "results" / "baseline_workspace_manifest.json"
    if not prepared["recovered"] or not manifest_path.is_file():
        record_refinement_changes.write_manifest(output_dir, manifest_path)
    metadata_path = Path(prepared["run_dir"]) / "meta" / "run.json"
    metadata = workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "baseline_report_source": str(source_report),
            "baseline_workspace_source": str(source_report.parent.parent),
            "baseline_workspace_inherited_files": inherited_files,
            "removed_git_metadata": removed_git_metadata,
            "baseline_workspace_manifest": str(manifest_path),
            "refinement_change_record": str(
                output_dir / "results" / "refinement_changed_files.json"
            ),
            "original_report": str(original_report),
            "execution_mode": "expert_guided_baseline_report_refinement",
        }
    )
    workflow_evolution.write_json(metadata_path, metadata)
    if prepared["recovered"]:
        write_interaction_added_content(prepared["run_dir"])
        record_refinement_changes.write_changes(
            output_dir,
            manifest_path,
            output_dir / "results" / "refinement_changed_files.json",
        )
    return prepared


def run_consolidated_refinement_check(prepared: dict) -> Path:
    """Run exactly one controller-owned report/result consistency check."""
    output_dir = Path(prepared["output_dir"])
    results_dir = output_dir / "results"
    checks: list[dict[str, Any]] = []

    def require_text(relative: str) -> str:
        path = output_dir / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise RuntimeError(f"Cannot read UTF-8 artifact {relative}: {error}") from error
        if not text.strip():
            raise RuntimeError(f"Required artifact is empty: {relative}")
        if "\x00" in text:
            raise RuntimeError(f"NUL bytes detected in text artifact: {relative}")
        checks.append({"check": "utf8_nonempty", "path": relative, "passed": True})
        return text

    original = require_text("results/original_report.md")
    refined = require_text("results/solution_report.md")
    evidence = require_text("results/interaction_evidence.md")
    if original == refined:
        raise RuntimeError("Refined report is byte-for-byte identical to the original")
    checks.append({"check": "report_changed", "passed": True})
    if has_expert_interaction_impact_section(refined):
        raise RuntimeError(
            "Refined report must not contain an 'Expert Interaction Impact' section"
        )
    checks.append({"check": "expert_impact_section_absent", "passed": True})
    if not any(
        payload.get("ok") is True and str(payload.get("answer", "")).strip()
        for payload in (
            workflow_evolution.read_json(path, {})
            for path in sorted(
                (output_dir / "logs" / "operator_feedback").glob(
                    "expert_reply_*.json"
                )
            )
        )
    ):
        raise RuntimeError("No successful expert reply is available")
    checks.append({"check": "successful_expert_reply", "passed": True})
    if not evidence.strip():
        raise RuntimeError("Interaction evidence is empty")

    verifier = output_dir / "code" / "verify_report.py"
    verifier_result = None
    if verifier.is_file():
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "utf-8"
        completed = subprocess.run(
            [sys.executable, str(verifier)],
            cwd=output_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            env=environment,
            check=False,
        )
        verifier_result = {
            "path": "code/verify_report.py",
            "returncode": completed.returncode,
            "stdout": completed.stdout[-20000:],
            "stderr": completed.stderr[-20000:],
        }
        if completed.returncode != 0:
            raise RuntimeError(
                "The consolidated code/verify_report.py check failed with "
                f"exit code {completed.returncode}"
            )
        checks.append(
            {"check": "task_verify_report", "path": "code/verify_report.py", "passed": True}
        )

    output_path = results_dir / "refinement_validation.json"
    workflow_evolution.write_json(
        output_path,
        {
            "generated_at": now(),
            "generated_by": "python_controller",
            "execution_count": 1,
            "checks": checks,
            "task_verifier": verifier_result,
            "passed": True,
        },
    )
    return output_path


def write_interaction_added_content(run_dir: Path) -> Path:
    """Record only new-side inserted/revised lines relative to the baseline draft."""
    results_dir = Path(run_dir) / "output" / "results"
    original_path = results_dir / "original_report.md"
    refined_path = results_dir / "solution_report.md"
    if not original_path.is_file() or not refined_path.is_file():
        raise FileNotFoundError(
            f"Cannot compare missing original/refined report under {results_dir}"
        )
    original = original_path.read_text(encoding="utf-8", errors="replace").splitlines()
    refined = refined_path.read_text(encoding="utf-8", errors="replace").splitlines()
    blocks = []
    for tag, _, _, start, end in difflib.SequenceMatcher(
        None, original, refined, autojunk=False
    ).get_opcodes():
        if tag in {"insert", "replace"} and start != end:
            blocks.append((tag, refined[start:end]))
    lines = [
        "# Interaction-Attributed Added Content",
        "",
        "Generated programmatically by comparing `original_report.md` with the ",
        "refined `solution_report.md`. Only new-side inserted or revised content ",
        "is retained; unchanged and deleted original content is excluded.",
        "",
    ]
    if not blocks:
        lines.extend(["No added or revised content was detected.", ""])
    for index, (change_type, content) in enumerate(blocks, start=1):
        lines.extend(
            [
                f"## Change {index} ({change_type})",
                "",
                *content,
                "",
            ]
        )
    output_path = results_dir / "interaction_added_content.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evolve and evaluate substantive expert-interaction rubrics."
    )
    parser.add_argument("--max-rounds", type=int, default=10)
    parser.add_argument("--problem-id", nargs="+", default=list(DEFAULT_PROBLEMS))
    parser.add_argument("--exp")
    parser.add_argument("--baseline-report-root", default=str(BASELINE_REPORT_ROOT))
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--opt-model", default="deepseek-v4-pro")
    parser.add_argument("--opt-api-key")
    parser.add_argument("--opt-base-url")
    parser.add_argument("--optimizer-retries", type=int, default=5)
    parser.add_argument("--expert-model", default=DEFAULT_EXPERT_MODEL)
    parser.add_argument("--expert-api-key")
    parser.add_argument("--expert-base-url")
    parser.add_argument("--expert-timeout", type=float, default=600.0)
    parser.add_argument(
        "--expert-request-timeout",
        type=float,
        default=EXPERT_REQUEST_TIMEOUT,
        help="Maximum seconds for one request/reply handshake after submission.",
    )
    parser.add_argument("--expert-attempts", type=int, default=3)
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--completion-grace", type=float, default=60.0)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--judge-repeats", type=int, default=1)
    parser.add_argument("--judge-concurrency", type=int, default=1)
    parser.add_argument("--validation-repetitions", type=int, default=1)
    parser.add_argument("--validation-attempts", type=int, default=3)
    parser.add_argument("--retry-concurrency", type=int, default=1)
    parser.add_argument("--validation-retry-delay", type=float, default=10.0)
    parser.add_argument("--openclaw-command")
    parser.add_argument("--initialize-only", action="store_true")
    parser.add_argument(
        "--enforce-substantive-interaction-gate",
        action="store_true",
        default=ENFORCE_SUBSTANTIVE_INTERACTION_GATE,
        help=(
            "Run the post-execution substantive-interaction checks and fail "
            "the command when they do not pass (disabled by default)."
        ),
    )
    return parser.parse_args()


def runtime_args(
    args: argparse.Namespace, baseline_reports: dict[str, str]
) -> SimpleNamespace:
    return SimpleNamespace(
        model=args.model,
        openclaw_command=args.openclaw_command,
        expert_model=args.expert_model,
        expert_api_key=args.expert_api_key,
        expert_base_url=args.expert_base_url,
        expert_timeout=args.expert_timeout,
        expert_request_timeout=args.expert_request_timeout,
        expert_attempts=args.expert_attempts,
        opt_model=args.opt_model,
        opt_api_key=args.opt_api_key,
        opt_base_url=args.opt_base_url,
        optimizer_retries=args.optimizer_retries,
        baseline_reports=baseline_reports,
        thinking=args.thinking,
        timeout=args.timeout,
        concurrency=args.concurrency,
        judge_repeats=args.judge_repeats,
        judge_concurrency=args.judge_concurrency,
        validation_repetitions=args.validation_repetitions,
        validation_attempts=args.validation_attempts,
        retry_concurrency=args.retry_concurrency,
        validation_retry_delay=args.validation_retry_delay,
        skip_interaction_receipt_validation=True,
    )


def run_substantive_modeling_phase(
    prepared: dict,
    session_id: str,
    message_file: Path,
    args,
    completion_artifact: Path | None,
) -> None:
    """Run OpenClaw while separating transport noise from session content."""
    meta_dir = prepared["run_dir"] / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    transport_log = meta_dir / "transport.log"
    solve_log = meta_dir / "solve.log"
    metadata_path = meta_dir / "run.json"
    metadata = workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "session_id": session_id,
            "session_transcript": str(
                openclaw_session_file(prepared["agent_id"], session_id)
            ),
            "solve_log": str(solve_log),
            "transport_log": str(transport_log),
        }
    )
    workflow_evolution.write_json(metadata_path, metadata)

    def run_agent(current_message_file: Path) -> None:
        baseline.stream_command(
            [
                prepared["openclaw"],
                "agent",
                "--local",
                "--agent",
                prepared["agent_id"],
                "--session-id",
                session_id,
                "--message-file",
                str(current_message_file),
                "--thinking",
                args.thinking,
                "--timeout",
                str(args.timeout),
            ],
            prepared["run_dir"],
            transport_log,
            completion_artifact=completion_artifact,
        )

    def artifact_ready() -> bool:
        if completion_artifact is None:
            return True
        try:
            return bool(
                completion_artifact.is_file()
                and completion_artifact.read_text(encoding="utf-8").strip()
            )
        except (OSError, UnicodeDecodeError):
            return False

    try:
        run_agent(message_file)
        if not artifact_ready():
            recovery_prompt = meta_dir / "final_report_recovery_prompt.md"
            recovery_prompt.write_text(
                "# Submission recovery\n\n"
                "The previous turn completed without creating the required "
                "submission for this task. Resume the existing work in this same "
                "workspace and session. Do not restart completed analysis, repeat "
                "web research, or request another expert interaction. Inspect the "
                "existing draft, code, data, computed results, and expert "
                "feedback, then write the complete submission in the exact format "
                "the task prompt specifies, at this exact path:\n\n"
                f"`{completion_artifact}`\n\n"
                "Answer every original task, include the necessary assumptions, "
                "model, results, validation, and limitations, and do not generate "
                "images. Verify that the file exists, is non-empty, and is in the "
                "required format before ending.\n",
                encoding="utf-8",
            )
            print(
                "OpenClaw exited before writing the required submission; resuming "
                "the same session once to complete the artifact.",
                flush=True,
            )
            run_agent(recovery_prompt)
    finally:
        render_openclaw_session_log(
            prepared["agent_id"], session_id, message_file, solve_log
        )
    if not artifact_ready():
        raise RuntimeError(
            "OpenClaw did not produce the required non-empty completion artifact "
            f"after one same-session recovery attempt: {completion_artifact}"
        )
    write_interaction_added_content(prepared["run_dir"])
    output_dir = Path(prepared.get("output_dir", prepared["run_dir"] / "output"))
    manifest_path = output_dir / "results" / "baseline_workspace_manifest.json"
    if manifest_path.is_file():
        record_refinement_changes.write_changes(
            output_dir,
            manifest_path,
            output_dir / "results" / "refinement_changed_files.json",
        )
    run_consolidated_refinement_check(prepared)


def experiment_path(value: str | None) -> tuple[Path, bool]:
    if value:
        path = Path(value).resolve()
        return path, path.is_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = (
        REPO_ROOT
        / "openclaw_experiments"
        / f"interaction_rubric_substantive_{timestamp}"
    )
    return path, False


def main() -> None:
    args = parse_args()
    numeric = (
        args.max_rounds,
        args.optimizer_retries,
        args.concurrency,
        args.judge_repeats,
        args.judge_concurrency,
        args.validation_repetitions,
        args.validation_attempts,
        args.retry_concurrency,
        args.expert_attempts,
    )
    if (
        min(numeric) < 1
        or args.timeout < 1
        or args.expert_timeout <= 0
        or args.expert_request_timeout <= 0
    ):
        raise ValueError("Concurrency, retry, timeout, and repetition values must be positive")
    if args.validation_retry_delay < 0:
        raise ValueError("validation retry delay must be non-negative")
    if len(args.problem_id) != len(set(args.problem_id)):
        raise ValueError("problem IDs must be unique")

    problems = baseline.load_problems()
    unknown = [problem_id for problem_id in args.problem_id if problem_id not in problems]
    if unknown:
        raise ValueError("Unknown problem ID(s): " + ", ".join(unknown))
    initial_rubric = load_rubric()
    experiment, resumed = experiment_path(args.exp)
    workflows = experiment / "workflows"
    results_path = workflows / "results.json"
    previous_config = {}
    if not resumed:
        workflows.mkdir(parents=True, exist_ok=False)
        workflow_evolution.write_json(results_path, [])
    else:
        previous_config = workflow_evolution.read_json(experiment / "config.json", {})
        if previous_config.get("experiment_type") not in {
            "fixed_substantive_interaction",
            "substantive_interaction_rubric_evolution",
        }:
            raise ValueError("--exp is not a substantive-interaction experiment")
        if (
            workflow_evolution.read_json(results_path, [])
            and previous_config.get("execution_mode")
            != "expert_guided_baseline_report_refinement"
        ):
            raise ValueError(
                "Existing rounds were not generated by baseline-report refinement. "
                "Start a new experiment without --exp so Round 1 also refines the "
                "fixed original report."
            )
    configured_reports = previous_config.get("baseline_reports", {})
    if not isinstance(configured_reports, dict):
        configured_reports = {}
    baseline_reports = {}
    for problem_id in args.problem_id:
        configured_path = Path(str(configured_reports.get(problem_id, "")))
        source = (
            configured_path
            if configured_path.is_file()
            else resolve_baseline_report(problem_id, Path(args.baseline_report_root))
        )
        baseline_reports[problem_id] = str(source.resolve())

    # evaluate_round currently reads its fixed validation set from this module
    # global. Restrict it process-locally to the user's selected problems.
    interaction.VALIDATION_PROBLEMS = tuple(args.problem_id)
    interaction.INITIAL_RUBRIC = initial_rubric
    interaction.finalize_interaction_receipt = finalize_substantive_receipt
    interaction.run_local_modeling_phase = run_substantive_modeling_phase
    interaction.prepare_validation_problem = prepare_refinement_validation_problem
    interaction.serve_expert_requests = serve_substantive_expert_requests
    baseline.HUMAN_MODELING_EXPERT_ROLE_PROMPT = SUBSTANTIVE_EXPERT_ROLE_PROMPT
    baseline.create_operator_role_prompts = create_substantive_operator_role_prompt

    removed_prompts = []
    for output_dir in (experiment / "runs").glob("round_*/*/output"):
        removed_prompts.extend(remove_unused_operator_role_prompts(output_dir))
    if removed_prompts:
        print(
            f"Removed {len(removed_prompts)} unused operator-role prompt file(s).",
            flush=True,
        )

    config = {
        "experiment_type": "substantive_interaction_rubric_evolution",
        "rubric_evolution": True,
        "max_rounds": args.max_rounds,
        "execution_mode": "expert_guided_baseline_report_refinement",
        "baseline_report_root": str(Path(args.baseline_report_root).resolve()),
        "baseline_reports": baseline_reports,
        "validation_problems": args.problem_id,
        "model": args.model,
        "opt_model": args.opt_model,
        "optimizer_judge_feedback": "non_full_role_overall_score_and_overall_feedback",
        "evolution_direction": "unrestricted",
        "expert_model": args.expert_model,
        "expert_request_timeout": args.expert_request_timeout,
        "interaction_transport": "single_openclaw_run_synchronous_expert_api",
        "judge_repeats": args.judge_repeats,
        "validation_repetitions": args.validation_repetitions,
        "substantive_interaction_gate": args.enforce_substantive_interaction_gate,
        "updated_at": now(),
    }
    workflow_evolution.write_json(experiment / "config.json", config)
    print(f"Experiment: {experiment}")
    print(f"Initial rubric: {RUBRIC_PATH}")
    print("Problems: " + ", ".join(args.problem_id))
    print(f"Expert model: {args.expert_model}")
    print(
        "Substantive-interaction gate: "
        + ("enabled" if args.enforce_substantive_interaction_gate else "disabled")
    )
    if args.initialize_only:
        round_dir = workflows / "round_1"
        round_dir.mkdir(parents=True, exist_ok=True)
        rubric_target = round_dir / "rubric.json"
        workflow_evolution.write_json(rubric_target, initial_rubric)
        prompt_path = round_dir / "prompt.md"
        prompt_path.write_text(
            build_refinement_prompt(initial_rubric), encoding="utf-8"
        )
        print(f"Initialization complete; prompt: {prompt_path}")
        return

    workflow_evolution.configure_completion_grace(
        baseline.run_problem, args.completion_grace
    )
    openclaw = baseline.find_openclaw_command(args.openclaw_command)
    atexit.register(
        interaction.cleanup_experiment_agents_at_exit, openclaw, experiment
    )
    run_args = runtime_args(args, baseline_reports)
    for round_number in range(1, args.max_rounds + 1):
        results = interaction.normalize_results(
            workflow_evolution.read_json(results_path, [])
        )
        existing = next(
            (item for item in results if item.get("round") == round_number), None
        )
        if (
            existing
            and len(existing.get("problem_results", [])) == len(args.problem_id)
            and all(
                item.get("repetition_count", 1) >= args.validation_repetitions
                for item in existing["problem_results"]
            )
        ):
            print(f"Round {round_number} is complete; skipping", flush=True)
            continue
        round_dir = workflows / f"round_{round_number}"
        round_dir.mkdir(parents=True, exist_ok=True)
        rubric_target = round_dir / "rubric.json"
        rubric = workflow_evolution.read_json(rubric_target, {})
        if not rubric:
            rubric = (
                copy.deepcopy(initial_rubric)
                if round_number == 1
                else propose_rubric(
                    results, round_number, round_dir, run_args, problems
                )
            )
            workflow_evolution.write_json(rubric_target, rubric)
        interaction.validate_rubric(rubric)
        prompt_path = round_dir / "prompt.md"
        prompt_path.write_text(
            build_refinement_prompt(rubric), encoding="utf-8"
        )
        result = interaction.evaluate_round(
            experiment,
            round_number,
            rubric,
            problems,
            prompt_path,
            run_args,
            existing,
        )
        checks = []
        failures = []
        if args.enforce_substantive_interaction_gate:
            for aggregate in result["problem_results"]:
                repetitions = aggregate.get("repetitions") or [aggregate]
                for repetition in repetitions:
                    run_dir = Path(repetition["run_dir"])
                    try:
                        check = validate_substantive_interaction(run_dir)
                    except Exception as error:
                        check = {
                            "passed": False,
                            "run_dir": str(run_dir),
                            "error": repr(error),
                            "checked_at": now(),
                        }
                        failures.append(check)
                    else:
                        check["run_dir"] = str(run_dir)
                    repetition["substantive_interaction_check"] = check
                    checks.append(check)
                aggregate["substantive_interaction_passed"] = all(
                    item.get("substantive_interaction_check", {}).get("passed")
                    for item in repetitions
                )
        result.update(
            {
                "parent_round": rubric.get("parent_round"),
                "parent_rounds": rubric.get("parent_rounds", []),
                "secondary_parent_round": rubric.get("secondary_parent_round"),
                "evolution_operator": rubric.get("evolution_operator", "initial"),
                "substantive_interaction_checks": checks,
                "substantive_interaction_gate_enabled": args.enforce_substantive_interaction_gate,
                "substantive_interaction_passed": (
                    not failures if args.enforce_substantive_interaction_gate else None
                ),
            }
        )
        results = [item for item in results if item.get("round") != round_number]
        results.append(result)
        results = interaction.normalize_results(
            sorted(results, key=lambda item: item["round"])
        )
        result = next(item for item in results if item["round"] == round_number)
        workflow_evolution.write_json(round_dir / "result.json", result)
        workflow_evolution.write_json(results_path, results)
        interaction.write_score_outputs(
            workflows / "round_problem_dimension_scores.json",
            workflows / "round_problem_dimension_scores.xlsx",
            workflows / "round_problem_interactions.xlsx",
            experiment,
            results,
        )
        print(f"Round {round_number} utility: {result['utility']:.6f}")
        if failures:
            raise RuntimeError(
                f"{len(failures)} run(s) failed the substantive-interaction gate; "
                f"see {round_dir / 'result.json'}"
            )
    print(f"Results: {results_path}")


if __name__ == "__main__":
    main()
