"""Score one round's interaction strategy with an LLM critic, for the evolver.

The co-evolution launcher calls :func:`review_training_parents` immediately after
a round's training-parent evaluation and before the candidate is evolved.  The
critic reads the active rubric (``interaction_strategy_rubric_v6.md`` by
default; override with ``CRITIC_RUBRIC``) and, for
every training run of every parent, scores the interaction policy together with
the consultation it produced: the policy text, the expert dialogue recorded in
the run's evidence, and what the run reports the reply changed.

The result is appended to the workflow-evolution prompt as one extra evidence
node.  Nothing else about the evolution inputs changes, and the critic never
touches the task score -- it scores only the interaction.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUBRIC = Path(__file__).resolve().parent / "interaction_strategy_rubric_v6.md"
CRITIC_REPEATS = 1
CRITIC_MAX_TOKENS = 2600


def rubric_path() -> Path:
    """Rubric in force for this run; override with CRITIC_RUBRIC."""
    override = os.environ.get("CRITIC_RUBRIC")
    return Path(override).resolve() if override else DEFAULT_RUBRIC

SYSTEM_PROMPT = """\
You are an exacting reviewer of expert-consultation practice in a mathematical
modeling pipeline. You score one interaction policy together with the
consultation it actually produced, against a fixed rubric.

Rules:
- Score only the interaction: the policy text, the expert question, the expert
  reply, and what the run records the reply changed. Do not score the modeling
  result itself.
- Every non-zero score needs a verbatim quote or a named artifact from the
  material provided. If the material cannot decide a criterion, score it 0 and
  say so in the justification.
- Score EVERY criterion in the rubric, in the rubric's order, including the ones
  a run fails outright.  Give each one a reason.  A review that omits a
  criterion is incomplete and will be sent back.
- Do not reward record-keeping: how well a run wrote about the exchange is not
  evidence about the exchange.  Judge the question and the reply themselves.
- Do not invent facts about the run beyond the material given.
- Reply with one JSON object and nothing else.
"""

OUTPUT_SCHEMA_HINT = """\
Return exactly this JSON shape, with one "criteria" entry for EVERY rubric
criterion, in the rubric's order:
{"criteria": [{"name": "<criterion name>", "max": <bracketed max>,
               "score": <0..max>, "evidence": "<quote or artifact>",
               "justification": "<one sentence>",
               "fix": "<one concrete edit to the interaction policy text>"}],
 "total": <sum of scores>,
 "top_fix": "<the single edit with the largest expected gain>"}
"""


def rubric_text() -> str:
    return rubric_path().read_text(encoding="utf-8")


def rubric_criteria() -> list[str]:
    """The rubric's criterion names, in order, from its ``[N] Name:`` lines."""
    return [
        match.group(2).strip()
        for match in re.finditer(
            r"^\[(\d+(?:\.\d+)?)\]\s*([^:]+):", rubric_text(), re.M
        )
    ]


def rubric_maxima() -> dict[str, float]:
    """Criterion name -> its bracketed maximum, from the rubric itself."""
    return {
        match.group(2).strip(): float(match.group(1))
        for match in re.finditer(
            r"^\[(\d+(?:\.\d+)?)\]\s*([^:]+):", rubric_text(), re.M
        )
    }


def rubric_max_total() -> float:
    """The rubric's theoretical maximum, read off its bracketed values."""
    values = [float(v) for v in re.findall(r"^\[(\d+(?:\.\d+)?)\]", rubric_text(), re.M)]
    return sum(values) if values else 100.0


def _dialogue_from_evidence(training_run: dict[str, Any]) -> str:
    """Pull the recorded expert dialogue out of one training run's evidence."""
    parts = []
    for artifact in training_run.get("artifacts") or []:
        content = str(artifact.get("content") or "").strip()
        if content:
            parts.append(content)
    return "\n\n".join(parts)


def _draft_from_evidence(training_run: dict[str, Any]) -> str:
    """The plan the run started from: the default the movement criterion scores against."""
    direct = str(training_run.get("draft") or "").strip()
    if direct:
        return direct
    for artifact in training_run.get("artifacts") or []:
        if "draft" in str(artifact.get("artifact_type") or "").lower():
            return str(artifact.get("content") or "").strip()
    return ""


def build_critic_prompt(
    *,
    parent_rank: Any,
    policy_text: str,
    problem_id: str,
    title: str,
    dialogue: str,
    change_summary: str,
    scores: dict[str, Any] | None,
    interaction_cost: Any = None,
    draft: str = "",
) -> str:
    scores = scores or {}
    criteria = rubric_criteria()
    return "\n".join(
        [
            "# Rubric to score against",
            "",
            rubric_text().strip(),
            "",
            "# Interaction policy under review",
            "",
            f"(parent rank {parent_rank})",
            "",
            str(policy_text).strip(),
            "",
            "# The consultation this policy produced",
            "",
            f"Task: {problem_id} — {title}",
            "",
            "## Recorded expert dialogue (question, reply, and the run's own record)",
            "",
            (dialogue.strip() or "(no dialogue was recorded for this run)"),
            "",
            "# The plan the consultation started from",
            "",
            "(The plan the agent had before the exchange, when the run had one; the"
            " movement criterion compares the expert's answer against the default it"
            " already had.)",
            "",
            (draft.strip()[:9000] or "(no plan was supplied)"),
            "",
            "## What the run says the reply changed (self-reported — context only)",
            "",
            (str(change_summary).strip() or "(nothing recorded)"),
            "",
            "## Cost and task-side context (context only, do not score it)",
            "",
            f"task report score: {scores.get('report_score')}",
            f"interaction cost: {interaction_cost}",
            f"interaction penalty: {scores.get('interaction_penalty')}",
            "",
            "# Your task",
            "",
            f"The rubric has {len(criteria)} criteria.  Score ALL {len(criteria)} of"
            " them for THIS consultation, in the order listed below, and give a"
            " reason for each one -- including a criterion this consultation fails"
            " outright (score it 0 and say why).  Then give the per-criterion fix"
            " that would raise it.  Do not omit a criterion, do not merge two"
            " criteria into one entry, and do not add criteria of your own.",
            "",
            "The complete set you must return, one entry each:",
            *(f"  {index}. {name}" for index, name in enumerate(criteria, start=1)),
            "",
            f"A reply that does not cover all {len(criteria)} is incomplete and will"
            " be sent back to be redone.",
            "",
            OUTPUT_SCHEMA_HINT,
        ]
    )


def _post(client, model: str, base_url: str, prompt: str) -> str:
    options: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": CRITIC_MAX_TOKENS,
    }
    # DeepSeek reasons by default and would spend the budget on reasoning; it
    # also has no chat_template_kwargs.  Setting extra_body here keeps the
    # launcher's vLLM-only injection off a DeepSeek request.
    if "deepseek.com" in str(base_url).lower():
        options["extra_body"] = {"thinking": {"type": "disabled"}}
    response = client.chat.completions.create(**options)
    choice = response.choices[0]
    return str(choice.message.content or "")


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|```$", "", text).strip()
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        try:
            value = json.loads(text[start : end + 1])
            return value if isinstance(value, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _missing_criteria(parsed: dict[str, Any]) -> list[str]:
    """Rubric criteria the review did not score, matched case-insensitively."""
    expected = rubric_criteria()
    if not expected or "criteria" not in parsed:
        return []
    got = [
        str(entry.get("name") or "").strip().lower()
        for entry in parsed.get("criteria") or []
        if isinstance(entry, dict)
    ]
    return [name for name in expected if not any(name.lower() in g for g in got)]


def score_one(
    client, model: str, base_url: str, prompt: str, *, attempts: int = 3
) -> dict[str, Any]:
    last_error = "no attempt"
    follow_up = ""
    for _ in range(attempts):
        try:
            raw = _post(client, model, base_url, prompt + follow_up)
        except Exception as error:  # noqa: BLE001 - report, never abort the round
            last_error = f"{type(error).__name__}: {error}"
            continue
        parsed = _extract_json(raw)
        if parsed is None:
            last_error = "critic reply was not JSON"
            follow_up = "\n\nYour previous reply was not parseable JSON. Return only the JSON object."
            continue
        missing = _missing_criteria(parsed)
        if not missing:
            parsed["_raw"] = raw
            return parsed
        last_error = "critic reply omitted criteria: " + ", ".join(missing)
        follow_up = (
            "\n\nYour previous reply omitted these rubric criteria: "
            + ", ".join(missing)
            + ". Return the complete set: one entry per criterion, in the rubric's order,"
            " each with its score, evidence, justification and fix."
        )
    return {"error": last_error}


def critic_credentials(args: Any = None, mmbench_judge: dict | None = None):
    """Critic endpoint: explicit overrides, else the MM-Bench judge role."""
    model = os.environ.get("CRITIC_MODEL")
    base_url = os.environ.get("CRITIC_BASE_URL")
    api_key = os.environ.get("CRITIC_API_KEY")
    judge = mmbench_judge or {}
    model = model or str(judge.get("model") or "")
    base_url = base_url or str(judge.get("base_url") or "")
    api_key = api_key or str(judge.get("api_key") or "")
    if args is not None:
        model = model or str(getattr(args, "judge_feedback_model", "") or "")
        base_url = base_url or str(getattr(args, "opt_base_url", "") or "")
        api_key = api_key or str(getattr(args, "opt_api_key", "") or "")
    timeout = float(os.environ.get("CRITIC_TIMEOUT") or judge.get("timeout") or 600.0)
    return model, api_key, base_url, timeout


def review_training_parents(
    training_parents: list[dict[str, Any]],
    *,
    experiment: Path,
    model: str,
    api_key: str,
    base_url: str,
    timeout: float,
) -> dict[str, Any]:
    """Score every training run of every parent; return the round's review."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout, max_retries=0)
    max_total = rubric_max_total()
    expected_criteria = rubric_criteria()
    reviews: list[dict[str, Any]] = []
    for parent in training_parents:
        evidence = parent.get("training_evidence") or {}
        runs = evidence.get("training_runs") or []
        policy_text = str((parent.get("workflow") or {}).get("policy_text") or "")
        entries = []
        for run in runs:
            prompt = build_critic_prompt(
                parent_rank=parent.get("parent_rank"),
                policy_text=policy_text,
                problem_id=str(run.get("problem_id") or ""),
                title=str(run.get("title") or ""),
                dialogue=_dialogue_from_evidence(run),
                draft=_draft_from_evidence(run),
                change_summary=str(run.get("interaction_report_change_summary") or ""),
                scores=run.get("scores") or {},
                interaction_cost=(run.get("scores") or {}).get("interaction_cost"),
            )
            result = score_one(client, model, base_url, prompt)
            result.pop("_raw", None)
            returned = len(result.get("criteria") or [])
            entries.append(
                {
                    "problem_id": run.get("problem_id"),
                    "criteria_expected": len(expected_criteria),
                    "criteria_returned": returned,
                    # A review that skipped a criterion has a total the rubric
                    # cannot compare with a complete one, so it is flagged here
                    # and left out of the parent's mean.
                    "complete": "criteria" in result
                    and returned >= len(expected_criteria),
                    "result": result,
                }
            )
        scored = [e["result"] for e in entries if "criteria" in e["result"]]
        complete = [e["result"] for e in entries if e["complete"]]
        basis = complete or scored
        reviews.append(
            {
                "parent_rank": parent.get("parent_rank"),
                "workflow_id": parent.get("workflow_id"),
                "net_utility_on_current_training_batch": parent.get(
                    "net_utility_on_current_training_batch"
                ),
                "per_problem": entries,
                "mean_total": (
                    round(sum(float(s.get("total") or 0) for s in basis) / len(basis), 2)
                    if basis
                    else None
                ),
                "mean_normalized": (
                    round(
                        sum(float(s.get("total") or 0) for s in basis)
                        / len(basis)
                        / max_total,
                        4,
                    )
                    if basis
                    else None
                ),
                "scored_problems": len(scored),
                "mean_total_basis": (
                    "complete" if complete else ("all_scored" if scored else None)
                ),
                "incomplete_problems": [
                    e["problem_id"] for e in entries if not e["complete"]
                ],
            }
        )
    review = {
        "rubric_path": str(rubric_path()),
        "rubric_id": rubric_path().stem,
        "rubric_max_total": max_total,
        "critic_model": model,
        "critic_base_url": base_url,
        "round": (training_parents[0].get("training_evidence") or {}).get("round")
        if training_parents
        else None,
        "parents": reviews,
    }
    round_number = review.get("round")
    target_dir = Path(experiment) / "workflows" / f"round_{round_number}"
    if round_number is not None:
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "critic_review.json").write_text(
            json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (target_dir / "critic_review.md").write_text(
            render_critic_block(review), encoding="utf-8"
        )
    return review


def render_critic_block(review: dict[str, Any]) -> str:
    """Compact, prompt-ready feedback derived from one round's review."""
    lines = [
        "## Interaction-strategy critic review",
        "",
        f"Rubric: `{Path(str(review.get('rubric_path'))).name}` "
        f"(max {review.get('rubric_max_total')}, scored by {review.get('critic_model')}), "
        f"round {review.get('round')}. Normalized score = total / max.",
        "Each criterion is scored out of its bracketed maximum. Treat this as",
        "diagnostic feedback about the interaction itself: repair the policy text",
        "where a fix is named, and keep what already scores full marks.",
        "",
    ]
    declared = rubric_maxima()
    for parent in review.get("parents") or []:
        mean_total = parent.get("mean_total")
        mean_norm = parent.get("mean_normalized")
        lines.append(
            f"### Parent rank {parent.get('parent_rank')} "
            f"(`{parent.get('workflow_id')}`) — mean total "
            f"{mean_total if mean_total is not None else 'n/a'}"
            f"/{review.get('rubric_max_total')} "
            f"(normalized {mean_norm if mean_norm is not None else 'n/a'})"
        )
        incomplete = parent.get("incomplete_problems") or []
        if incomplete:
            fate = (
                "those runs are all that was scored, so this mean averages"
                " incomplete reviews and understates the score"
                if parent.get("mean_total_basis") == "all_scored"
                else "those runs are excluded from the mean above"
            )
            lines.append(
                "- note: the critic did not score every criterion for "
                + ", ".join(str(p) for p in incomplete)
                + f"; {fate}."
            )
        lines.append("")
        aggregated: dict[str, list[dict[str, Any]]] = {}
        for entry in parent.get("per_problem") or []:
            result = entry.get("result") or {}
            if result.get("error"):
                lines.append(
                    f"- ({entry.get('problem_id')}) critic failed: {result['error']}"
                )
                continue
            for criterion in result.get("criteria") or []:
                aggregated.setdefault(str(criterion.get("name")), []).append(
                    {**criterion, "problem_id": entry.get("problem_id")}
                )
        for name, items in aggregated.items():
            scores = [float(i.get("score") or 0) for i in items]
            maximum = max(
                [float(i.get("max") or 0) for i in items]
                + [declared.get(name, 0.0)]
            )
            mean = round(sum(scores) / len(scores), 2)
            if len(items) < len(parent.get("per_problem") or []):
                mean_caveat = (
                    f" (mean over {len(items)} of "
                    f"{len(parent.get('per_problem') or [])} runs)"
                )
            else:
                mean_caveat = ""
            worst = min(items, key=lambda i: float(i.get("score") or 0))
            norm = round(mean / maximum, 3) if maximum else 0.0
            lines.append(
                f"- **{name}**: {mean}/{maximum:.0f} (normalized {norm})"
                f"{mean_caveat} — {worst.get('justification')}"
            )
            lines.append(f"  - fix: {worst.get('fix')}")
        top = next(
            (
                (entry.get("result") or {}).get("top_fix")
                for entry in parent.get("per_problem") or []
                if (entry.get("result") or {}).get("top_fix")
            ),
            None,
        )
        if top:
            lines.append(f"- **Top fix**: {top}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
