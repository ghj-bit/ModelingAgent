import argparse
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


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = REPO_ROOT / "data" / "modeling_data_final.json"
PROMPT_TEMPLATE_PATH = SCRIPT_DIR / "prompt.md"
BASELINE_PROMPT_TEMPLATE_PATH = SCRIPT_DIR / "prompt_modelingbench_baseline.md"
JUDGER_DIR = REPO_ROOT / "src" / "judger"
EXPECTED_JUDGERS = (
    "structural_coherency",
    "scoring_decomposition",
    "modeling_groundedness",
    "data_groundedness",
    "analysis_groundedness",
    "innovativeness",
)
WORKFLOW_SECTION_PATTERN = re.compile(
    r"(?ms)^## Required Workflow\s*\n(.*?)(?=^## |\Z)"
)
WORKFLOW_STEP_PATTERN = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")
WORKFLOW_OPERATOR_PATTERN = re.compile(
    r"^\*\*(AskExpert|ScEnsemble|Review|ReAct):\*\*"
)
EVIDENCE_FILE_PATTERN = re.compile(
    r"evidence file(?:\s+now)?:\s*`([^`]+)`",
    re.IGNORECASE,
)
EVIDENCE_FIELDS = {
    "AskExpert": (
        "question_strategy",
        "runtime_issue",
        "question",
        "advice",
        "expert_feedback_file",
        "refine_plan",
        "refined_files",
        "verification",
        "applied_changes",
        "downstream_handoff",
    ),
    "ScEnsemble": ("candidates", "selected", "rationale"),
    "Review": ("reviewed", "issues", "corrections"),
    "ReAct": (
        "stage_artifacts_reviewed",
        "questions",
        "verifier_rubric",
        "verifier_feedback",
        "verifier_feedback_file",
        "defects",
        "revision_plan",
        "revised_files",
        "verification",
        "downstream_handoff",
    ),
}
ASK_EXPERT_ROLE_PROMPT = """\
You are an expert subagent supporting a mathematical-modeling workflow.

The parent agent will provide a narrow stage-specific question, the relevant
artifact paths, and a required feedback-file path. Inspect only the supplied
artifacts and task facts. Return concise, actionable feedback about uncertainty,
defects, missing evidence, or decision-relevant improvements. Do not solve later
workflow stages, do not invent data, and do not write the final report. Do not
edit any artifact, execute commands or code, use network tools, or launch another
agent. Only the parent agent may implement and verify refinements.

Write the feedback to the exact requested UTF-8 file path before replying to the
parent. The feedback must state the question reviewed, findings, recommended
changes, and any limits on the advice. Keep the complete feedback under 1,200
words.
"""
HUMAN_MODELING_EXPERT_ROLE_PROMPT = """\
You are a human mathematical-modeling expert represented by an independent
subagent acting only as a non-computational decision adviser. Give a brief
answer about one consequential qualitative uncertainty in the parent's current
work. If the request bundles several issues, address only the single
highest-impact qualitative decision.

Before answering, read the complete Authoritative Problem Statement appended
to this role prompt. Base the recommendation on the actual task and all of its
required deliverables, not only on the parent agent's summary or question.

Your responsibilities are limited to clarifying ambiguity in the problem,
identifying stakeholder preferences, prioritizing policy objectives, choosing
a defensible decision or reporting frame, identifying value judgments that the
problem cannot determine, and highlighting real-world meaning or decision risk.

Stay strictly within that qualitative advisory scope. If a request falls
outside it, do not perform the out-of-scope work; answer only the nearest
legitimate qualitative decision. Do not edit artifacts, execute commands, use
network tools, or launch another agent.

Keep each response under 160 words. Use only: (1) one qualitative
recommendation, (2) up to three short reasons tagged as fact, judgment, or
assumption, and (3) one decision caveat or boundary. Do not add a literature
review or extra suggestions.
"""
REACT_VERIFIER_ROLE_PROMPTS = {
    "problem_data": """\
You are a strict verifier subagent for a problem and data understanding stage.
Do not score the work. Inspect the artifacts named in the parent brief and answer
only the parent's one to three questions. Apply this rubric:
- Use all material facts, supplied tables, attachments, and data descriptions.
- Separate requested subproblems from background and submission requirements.
- Identify objectives, hard constraints, data fields, ambiguities, dependencies,
  and assumptions; state each assumption's impact and boundary.

Write concise findings, missing evidence, and executable revisions to the exact
UTF-8 feedback file path requested by the parent before replying. Do not modify
the inspected artifacts or launch another agent. Keep the feedback under 1,200
words.
""",
    "modeling": """\
You are a strict verifier subagent for a mathematical modeling stage. Do not
score the work. Inspect the artifacts named in the parent brief and answer only
the parent's one to three questions. Apply this rubric:
- Define variables, parameters, objective functions, and constraints for every
  applicable subproblem.
- Check that the selected model actually implements the stated requirements.
- Check assumptions, units, feasibility, and consistency with supplied data.
- Distinguish exact, constrained, and approximate formulations and their scope.

Write concise findings, missing evidence, and executable revisions to the exact
UTF-8 feedback file path requested by the parent before replying. Do not modify
the inspected artifacts or launch another agent. Keep the feedback under 1,200
words.
""",
    "implementation_analysis": """\
You are a strict verifier subagent for an implementation and analysis stage. Do
not score the work. Inspect the artifacts named in the parent brief and answer
only the parent's one to three questions. Apply this rubric:
- Cover all required calculations and constraints with reproducible code or
  auditable calculations.
- Require independent checks, preserved intermediate outputs, and clear limits
  for infeasible, incomplete, or approximate results.
- Ensure numerical claims are traceable to executed artifacts and uncertainty,
  feasibility, and optimality claims are properly qualified.

Write concise findings, missing evidence, and executable revisions to the exact
UTF-8 feedback file path requested by the parent before replying. Do not modify
the inspected artifacts or launch another agent. Keep the feedback under 1,200
words.
""",
}
STEP_RECEIPT_FIELDS = (
    "step_number",
    "step_name",
    "status",
    "input_files",
    "output_files",
    "authoritative_outputs",
    "summary",
    "next_step",
)
AGENT_COMPLETION_PATTERN = re.compile(
    r"\[agent\]\s+run\s+\S+\s+ended with stopReason="
)
AGENT_COMPLETION_GRACE_SECONDS = 60.0
PROCESS_TERMINATION_GRACE_SECONDS = 10.0
JUDGE_MAX_ATTEMPTS = 3
JUDGE_RETRY_DELAY_SECONDS = 5.0


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
    return value or "openclaw"


def safe_path_component(value: str) -> str:
    """Keep an identifier readable while removing Windows-forbidden characters."""
    value = value.replace("?", "")
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value).rstrip(" .")
    return value or "problem"


def find_openclaw_command(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    candidates = ["openclaw.cmd", "openclaw"] if os.name == "nt" else ["openclaw"]
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise FileNotFoundError(
        "OpenClaw CLI was not found. Install it or pass --openclaw-command."
    )


def load_problems() -> dict:
    with open(DATA_PATH, encoding="utf-8") as file:
        return json.load(file)


def render_prompt(
    problem_id: str,
    problem: dict,
    output_dir: Path,
    template_path: Path | None = None,
) -> str:
    template_path = template_path or BASELINE_PROMPT_TEMPLATE_PATH
    template = template_path.read_text(encoding="utf-8")
    replacements = {
        "PROBLEM_ID": problem_id,
        "TITLE": str(problem.get("title", "")),
        "SOURCE": str(problem.get("source", "")),
        "YEAR": str(problem.get("year", "")),
        "QUESTION": str(problem.get("question", "")),
        "OUTPUT_DIR": str(output_dir.resolve()),
        "FINAL_REPORT": str((output_dir / "results" / "solution_report.md").resolve()),
        "CODE_DIR": str((output_dir / "code").resolve()),
        "RESULTS_DIR": str((output_dir / "results").resolve()),
        "DATA_DIR": str((output_dir / "data").resolve()),
        "LOGS_DIR": str((output_dir / "logs").resolve()),
        "EVIDENCE_DIR": str(
            (output_dir / "logs" / "workflow_evidence").resolve()
        ),
        "OPERATOR_ROLE_DIR": str((output_dir / "logs" / "operator_roles").resolve()),
        "OPERATOR_FEEDBACK_DIR": str(
            (output_dir / "logs" / "operator_feedback").resolve()
        ),
    }
    for key, value in replacements.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def human_expert_role_prompt(
    problem_id: str | None = None, problem: dict | None = None
) -> str:
    """Build the expert role prompt, including the run's complete problem text."""
    if problem_id is None or problem is None:
        return HUMAN_MODELING_EXPERT_ROLE_PROMPT

    return (
        HUMAN_MODELING_EXPERT_ROLE_PROMPT.rstrip()
        + "\n\n## Authoritative Problem Statement\n\n"
        + f"Problem ID: {problem_id}\n"
        + f"Title: {problem.get('title', '')}\n"
        + f"Source: {problem.get('source', '')}\n"
        + f"Year: {problem.get('year', '')}\n\n"
        + str(problem.get("question", "")).strip()
        + "\n"
    )


def create_operator_role_prompts(
    output_dir: Path,
    react_role_prompts: dict[str, str] | None = None,
    problem_id: str | None = None,
    problem: dict | None = None,
) -> None:
    """Materialize subagent role prompts inside the run workspace, not prompt.md."""
    role_dir = output_dir / "logs" / "operator_roles"
    role_dir.mkdir(parents=True, exist_ok=True)
    (role_dir / "ask_expert.md").write_text(
        ASK_EXPERT_ROLE_PROMPT, encoding="utf-8"
    )
    (role_dir / "human_modeling_expert.md").write_text(
        human_expert_role_prompt(problem_id, problem), encoding="utf-8"
    )
    role_prompts = react_role_prompts or REACT_VERIFIER_ROLE_PROMPTS
    for rubric_kind, prompt in role_prompts.items():
        (role_dir / f"react_verifier_{rubric_kind}.md").write_text(
            prompt, encoding="utf-8"
        )


def _has_evidence_value(value) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return value is not None


def _matches_descriptive_next_step(value: str, expected_name: str) -> bool:
    """Accept legacy receipts that used a recognizable next-step name."""
    ignored = {"a", "an", "and", "at", "for", "in", "of", "the", "to"}

    def tokens(text: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9]+", text.lower())
            if token not in ignored
        }

    actual = tokens(value)
    expected = tokens(expected_name)
    if not actual or not expected:
        return False
    overlap = 2.0 * len(actual & expected) / (len(actual) + len(expected))
    return overlap >= 0.5


def check_workflow_execution(
    prompt_path: Path, output_dir: Path, check_path: Path
) -> Path:
    prompt = prompt_path.read_text(encoding="utf-8")
    section_match = WORKFLOW_SECTION_PATTERN.search(prompt)
    errors = []
    warnings = []
    requirements = []
    workflow_steps = []
    previous_operator = None

    if not section_match:
        errors.append("Rendered prompt has no Required Workflow section")
    else:
        for line in section_match.group(1).splitlines():
            step_match = WORKFLOW_STEP_PATTERN.match(line)
            if not step_match:
                continue
            step_number = int(step_match.group(1))
            step = step_match.group(2).strip()
            workflow_steps.append({"number": step_number, "name": step})
            operator_match = WORKFLOW_OPERATOR_PATTERN.match(step)
            operator = operator_match.group(1) if operator_match else None
            if operator and operator == previous_operator:
                errors.append(f"Adjacent duplicate operator: {operator}")
            previous_operator = operator
            if not operator:
                continue
            evidence_match = EVIDENCE_FILE_PATTERN.search(step)
            if not evidence_match:
                errors.append(f"{operator} step has no evidence file declaration")
                continue
            requirements.append(
                {
                    "step_number": step_number,
                    "operator": operator,
                    "path": evidence_match.group(1),
                }
            )

    evidence_root = (output_dir / "logs" / "workflow_evidence").resolve()
    checked_files = []
    operator_evidence_by_step = {}
    for requirement in requirements:
        operator = requirement["operator"]
        evidence_path = Path(requirement["path"])
        if not evidence_path.is_absolute():
            evidence_path = output_dir / evidence_path
        evidence_path = evidence_path.resolve()
        try:
            evidence_path.relative_to(evidence_root)
        except ValueError:
            errors.append(
                f"{operator} evidence path is outside {evidence_root}: {evidence_path}"
            )
            continue
        item = {"operator": operator, "path": str(evidence_path), "valid": False}
        checked_files.append(item)
        if not evidence_path.is_file():
            errors.append(f"Missing {operator} evidence file: {evidence_path}")
            continue
        try:
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            errors.append(f"Invalid {operator} evidence JSON at {evidence_path}: {error}")
            continue
        if not isinstance(evidence, dict):
            errors.append(f"{operator} evidence must be a JSON object: {evidence_path}")
            continue
        operator_evidence_by_step[requirement["step_number"]] = (
            evidence_path,
            evidence,
        )
        if evidence.get("operator") != operator:
            errors.append(
                f"Evidence operator mismatch at {evidence_path}: "
                f"expected {operator!r}, got {evidence.get('operator')!r}"
            )
        missing_fields = [
            field
            for field in EVIDENCE_FIELDS[operator]
            if not _has_evidence_value(evidence.get(field))
        ]
        if missing_fields:
            errors.append(
                f"Empty or missing fields in {evidence_path}: "
                + ", ".join(missing_fields)
            )
        if operator == "AskExpert" and not missing_fields:
            refined_files = evidence.get("refined_files")
            if not isinstance(refined_files, list) or not refined_files:
                errors.append(
                    f"AskExpert refined_files must be a non-empty list: {evidence_path}"
                )
            else:
                for refined_file in refined_files:
                    refined_path = Path(str(refined_file))
                    if not refined_path.is_absolute():
                        refined_path = output_dir / refined_path
                    refined_path = refined_path.resolve()
                    try:
                        refined_path.relative_to(output_dir.resolve())
                    except ValueError:
                        errors.append(
                            f"AskExpert refined file is outside the workspace: "
                            f"{refined_path}"
                        )
                        continue
                    if not refined_path.is_file():
                        errors.append(
                            f"AskExpert refined file does not exist: {refined_path}"
                        )
        if operator == "ScEnsemble":
            candidates = evidence.get("candidates")
            if (
                not isinstance(candidates, list)
                or len(candidates) < 3
                or any(not _has_evidence_value(candidate) for candidate in candidates)
            ):
                errors.append(
                    f"ScEnsemble evidence requires at least three non-empty candidates: "
                    f"{evidence_path}"
                )
        item["valid"] = not any(str(evidence_path) in error for error in errors)

    def resolve_workspace_file(value, receipt_path: Path) -> Path | None:
        path = Path(str(value))
        if not path.is_absolute():
            path = output_dir / path
        path = path.resolve()
        try:
            path.relative_to(output_dir.resolve())
        except ValueError:
            errors.append(f"Receipt path is outside the workspace: {path}")
            return None
        if path == receipt_path:
            errors.append(f"A step receipt cannot declare itself as an output: {path}")
            return None
        if not path.is_file():
            errors.append(f"Receipt-declared file does not exist: {path}")
            return None
        return path

    step_receipts = []
    previous_receipt_path = None
    previous_authoritative = set()
    refinement_step_by_path = {}
    for refinement_step, (_, operator_evidence) in operator_evidence_by_step.items():
        if operator_evidence.get("operator") != "AskExpert":
            continue
        for value in operator_evidence.get("refined_files", []):
            path = Path(str(value))
            if not path.is_absolute():
                path = output_dir / path
            refinement_step_by_path[path.resolve()] = refinement_step

    def file_created_ns(path: Path) -> int:
        stat = path.stat()
        if os.name == "nt":
            return stat.st_ctime_ns
        birthtime = getattr(stat, "st_birthtime", None)
        return int(birthtime * 1_000_000_000) if birthtime is not None else stat.st_mtime_ns

    for expected_index, workflow_step in enumerate(workflow_steps, start=1):
        step_number = workflow_step["number"]
        if step_number != expected_index:
            errors.append(
                f"Workflow step numbering is not continuous: expected "
                f"{expected_index}, got {step_number}"
            )
        receipt_path = evidence_root / f"step_{step_number:02d}.json"
        receipt_item = {
            "step_number": step_number,
            "path": str(receipt_path),
            "valid": False,
        }
        step_receipts.append(receipt_item)
        if not receipt_path.is_file():
            errors.append(f"Missing step receipt: {receipt_path}")
            continue
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            errors.append(f"Invalid step receipt JSON at {receipt_path}: {error}")
            continue
        if not isinstance(receipt, dict):
            errors.append(f"Step receipt must be a JSON object: {receipt_path}")
            continue
        missing_fields = [
            field for field in STEP_RECEIPT_FIELDS if field not in receipt
        ]
        if missing_fields:
            errors.append(
                f"Missing fields in {receipt_path}: " + ", ".join(missing_fields)
            )
            continue
        if receipt.get("step_number") != step_number:
            errors.append(
                f"Step number mismatch in {receipt_path}: expected {step_number}, "
                f"got {receipt.get('step_number')!r}"
            )
        if not _has_evidence_value(receipt.get("step_name")):
            errors.append(f"Empty step_name in {receipt_path}")
        if receipt.get("status") != "completed":
            errors.append(f"Step receipt is not completed: {receipt_path}")
        expected_next = step_number + 1 if step_number < len(workflow_steps) else None
        next_step = receipt.get("next_step")
        descriptive_next = False
        if expected_next is not None and isinstance(next_step, str):
            expected_name = workflow_steps[expected_next - 1]["name"]
            descriptive_next = _matches_descriptive_next_step(
                next_step, expected_name
            )
            if descriptive_next:
                warnings.append(
                    f"Legacy descriptive next_step accepted in {receipt_path}; "
                    f"use integer {expected_next} in future receipts"
                )
        if next_step != expected_next and not descriptive_next:
            errors.append(
                f"Invalid next_step in {receipt_path}: expected {expected_next!r}, "
                f"got {next_step!r}"
            )
        if not _has_evidence_value(receipt.get("summary")):
            errors.append(f"Empty summary in {receipt_path}")

        resolved_lists = {}
        for field in ("input_files", "output_files", "authoritative_outputs"):
            values = receipt.get(field)
            if not isinstance(values, list):
                errors.append(f"{field} must be a list in {receipt_path}")
                resolved_lists[field] = set()
                continue
            if field != "input_files" and not values:
                errors.append(f"{field} must be non-empty in {receipt_path}")
            if field == "input_files" and step_number > 1 and not values:
                errors.append(f"input_files must be non-empty in {receipt_path}")
            resolved = {
                path
                for value in values
                if (path := resolve_workspace_file(value, receipt_path)) is not None
            }
            resolved_lists[field] = resolved

        inputs = resolved_lists.get("input_files", set())
        outputs = resolved_lists.get("output_files", set())
        authoritative = resolved_lists.get("authoritative_outputs", set())
        operator_record = operator_evidence_by_step.get(step_number)
        refined = set()
        if operator_record and operator_record[1].get("operator") == "AskExpert":
            refined = {
                path
                for value in operator_record[1].get("refined_files", [])
                if (path := resolve_workspace_file(value, receipt_path)) is not None
            }
        undeclared_refinements = refined - outputs
        if undeclared_refinements:
            warnings.append(
                f"AskExpert step {step_number} omitted refined files from "
                f"output_files; accepted for compatibility: "
                f"{sorted(map(str, undeclared_refinements))}"
            )
        effective_outputs = outputs | refined
        if not authoritative.issubset(effective_outputs):
            errors.append(
                f"authoritative_outputs must be included in output_files: {receipt_path}"
            )
        if step_number > 1 and not previous_authoritative.issubset(inputs):
            missing_inputs = sorted(map(str, previous_authoritative - inputs))
            errors.append(
                f"Step {step_number} does not consume all authoritative outputs "
                f"from step {step_number - 1}: {missing_inputs}"
            )
        if previous_receipt_path is not None:
            previous_time = previous_receipt_path.stat().st_mtime_ns
            for output_path in effective_outputs:
                if output_path in refined and output_path in inputs:
                    continue
                if file_created_ns(output_path) < previous_time:
                    errors.append(
                        f"Step {step_number} output was created before the previous "
                        f"step completed: "
                        f"{output_path}"
                    )
        receipt_time = receipt_path.stat().st_mtime_ns
        for output_path in effective_outputs:
            if output_path.stat().st_mtime_ns > receipt_time:
                refinement_step = refinement_step_by_path.get(output_path)
                refinement_receipt = (
                    evidence_root / f"step_{refinement_step:02d}.json"
                    if refinement_step is not None
                    else None
                )
                if (
                    refinement_step != step_number + 1
                    or refinement_receipt is None
                    or not refinement_receipt.is_file()
                    or output_path.stat().st_mtime_ns
                    > refinement_receipt.stat().st_mtime_ns
                ):
                    errors.append(
                        f"Step {step_number} output was modified after its receipt "
                        f"without an immediately following declared refinement: "
                        f"{output_path}"
                    )

        if operator_record:
            operator_path, operator_evidence = operator_record
            if operator_path not in outputs:
                errors.append(
                    f"Operator evidence is not declared in step {step_number} "
                    f"output_files: {operator_path}"
                )
            if operator_evidence.get("operator") == "AskExpert":
                if not refined.issubset(authoritative):
                    errors.append(
                        f"AskExpert refined files are not authoritative outputs of "
                        f"step {step_number}: {sorted(map(str, refined - authoritative))}"
                    )

        receipt_item["valid"] = not any(
            str(receipt_path) in error or f"Step {step_number} " in error
            for error in errors
        )
        previous_receipt_path = receipt_path
        previous_authoritative = authoritative

    check_result = {
        "passed": not errors,
        "operator_steps": len(requirements),
        "checked_files": checked_files,
        "step_receipts": step_receipts,
        "errors": errors,
        "warnings": warnings,
        "checked_at": datetime.now().isoformat(),
    }
    check_path.parent.mkdir(parents=True, exist_ok=True)
    check_path.write_text(
        json.dumps(check_result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if errors:
        raise RuntimeError(
            "Workflow execution check failed: " + "; ".join(errors) +
            f". See {check_path}."
        )
    return check_path


def record_disabled_workflow_check(check_path: Path) -> Path:
    """Preserve the result-file interface while final workflow checks are disabled."""
    check_path.parent.mkdir(parents=True, exist_ok=True)
    check_path.write_text(
        json.dumps(
            {
                "passed": None,
                "skipped": True,
                "reason": "Post-run workflow checker is disabled",
                "checked_at": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return check_path


def print_console(value: str, *, end: str = "\n") -> None:
    """Print model output without letting a legacy Windows code page abort a run."""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    safe_value = value.encode(encoding, errors="replace").decode(encoding)
    print(safe_value, end=end, flush=True)


def stream_command(
    command: list[str],
    cwd: Path,
    log_path: Path,
    completion_grace_seconds: float = AGENT_COMPLETION_GRACE_SECONDS,
    completion_artifact: Path | None = None,
    fatal_output_markers: tuple[str, ...] = (),
) -> None:
    print(f"Running: {' '.join(command[:4])} ...", flush=True)
    with open(log_path, "a", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert process.stdout is not None
        agent_completed = False
        fatal_output_line = None
        for line in process.stdout:
            print_console(line, end="")
            log_file.write(line)
            log_file.flush()
            if any(marker in line for marker in fatal_output_markers):
                fatal_output_line = line.strip()
                break
            if AGENT_COMPLETION_PATTERN.search(line):
                artifact_ready = completion_artifact is None
                if completion_artifact is not None:
                    try:
                        artifact_ready = (
                            completion_artifact.is_file()
                            and bool(
                                completion_artifact.read_text(
                                    encoding="utf-8"
                                ).strip()
                            )
                        )
                    except (OSError, UnicodeDecodeError):
                        artifact_ready = False
                if artifact_ready:
                    agent_completed = True
                    break
                ignored_notice = (
                    "Ignoring agent completion marker because the final report "
                    "is not ready; this is likely a sub-agent completion.\n"
                )
                print_console(ignored_notice, end="")
                log_file.write(ignored_notice)
                log_file.flush()

        if fatal_output_line is not None:
            process.terminate()
            try:
                return_code = process.wait(timeout=PROCESS_TERMINATION_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                process.kill()
                return_code = process.wait()
        elif not agent_completed:
            return_code = process.wait()
        else:
            notice = (
                "OpenClaw reported agent completion; waiting up to "
                f"{completion_grace_seconds:g} seconds for the CLI to exit.\n"
            )
            print_console(notice, end="")
            log_file.write(notice)
            log_file.flush()

            def drain_remaining_output() -> None:
                try:
                    for remaining_line in process.stdout:
                        print_console(remaining_line, end="")
                        log_file.write(remaining_line)
                        log_file.flush()
                except (OSError, ValueError):
                    return

            output_drainer = threading.Thread(
                target=drain_remaining_output,
                name="openclaw-output-drainer",
                daemon=True,
            )
            output_drainer.start()
            try:
                return_code = process.wait(timeout=completion_grace_seconds)
            except subprocess.TimeoutExpired:
                timeout_notice = (
                    "OpenClaw CLI did not exit within the completion grace period; "
                    "terminating the completed CLI process and continuing.\n"
                )
                print_console(timeout_notice, end="")
                log_file.write(timeout_notice)
                log_file.flush()
                process.terminate()
                try:
                    return_code = process.wait(
                        timeout=PROCESS_TERMINATION_GRACE_SECONDS
                    )
                except subprocess.TimeoutExpired:
                    process.kill()
                    return_code = process.wait()
            output_drainer.join(timeout=PROCESS_TERMINATION_GRACE_SECONDS)

    if fatal_output_line is not None:
        raise RuntimeError(
            "OpenClaw reported a terminal session failure: " + fatal_output_line
        )
    if return_code != 0 and not agent_completed:
        raise subprocess.CalledProcessError(return_code, command)


def run_checked(command: list[str], cwd: Path, log_path: Path) -> None:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(result.stdout or "")
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, command, output=result.stdout
        )


def judge_final_report(
    problem_id: str,
    final_report: Path,
    model_slug: str,
    run_dir: Path,
    judgers: tuple[str, ...] | None = None,
) -> Path:
    submission_dir = run_dir / "final_submission"
    submission_dir.mkdir(parents=True, exist_ok=True)
    submitted_report = submission_dir / "solution_report.md"
    shutil.copy2(final_report, submitted_report)

    judge_output = (
        REPO_ROOT
        / "output_judge"
        / "OpenClaw"
        / model_slug
        / run_dir.name
    )
    command = [
        sys.executable,
        "main_judge.py",
        problem_id,
        "--workspace",
        str(submission_dir),
        "--output-dir",
        str(judge_output),
    ]
    if judgers:
        command.extend(["--judgers", *judgers])
    result_path = judge_output / f"{safe_path_component(problem_id)}.json"
    for attempt in range(1, JUDGE_MAX_ATTEMPTS + 1):
        judge_env = os.environ.copy()
        judge_env["PYTHONIOENCODING"] = "utf-8"
        subprocess.run(command, cwd=JUDGER_DIR, check=True, env=judge_env)
        if not result_path.is_file():
            raise RuntimeError(
                f"Judge did not produce the expected result: {result_path}"
            )

        try:
            calculate_average_score(result_path, judgers)
            return result_path
        except RuntimeError as error:
            if attempt == JUDGE_MAX_ATTEMPTS:
                raise
            print(
                f"Judge attempt {attempt}/{JUDGE_MAX_ATTEMPTS} produced an "
                f"incomplete result ({error}). Retrying failed or missing "
                f"metrics in {JUDGE_RETRY_DELAY_SECONDS:g}s...",
                flush=True,
            )
            time.sleep(JUDGE_RETRY_DELAY_SECONDS)

    raise RuntimeError("Judge retries ended without a complete result")


def calculate_dimension_scores(
    result_path: Path, expected_judgers: tuple[str, ...] | None = None
) -> dict[str, float]:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    judgements = result.get("judgements", {})
    scores = {}
    missing = []
    for name in expected_judgers or EXPECTED_JUDGERS:
        judgement = judgements.get(name, {})
        score = judgement.get("aggregated_score")
        if score is None:
            score = judgement.get("calculated_overall")
        if not isinstance(score, (int, float)):
            missing.append(name)
        else:
            scores[name] = float(score)
    if missing:
        raise RuntimeError(
            "Cannot calculate the requested-metric average; missing successful scores for: "
            + ", ".join(missing)
        )
    return scores


def calculate_average_score(
    result_path: Path, expected_judgers: tuple[str, ...] | None = None
) -> float:
    scores = calculate_dimension_scores(result_path, expected_judgers)
    return sum(scores.values()) / len(scores)


def prepare_run(
    problem_id: str,
    problem: dict,
    output_root: Path,
    model: str,
    template_path: Path | None = None,
    react_role_prompts: dict[str, str] | None = None,
    skills_source: Path | None = None,
    selected_skills: list[str] | None = None,
    run_directory_prefix: str | None = None,
    flat_run_layout: bool = False,
) -> tuple[Path, Path, Path]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_slug = slugify(model)
    safe_problem_id = safe_path_component(problem_id)
    directory_prefix = safe_path_component(run_directory_prefix or safe_problem_id)
    run_name = f"{directory_prefix}_{timestamp}"
    run_dir = output_root / run_name if flat_run_layout else output_root / model_slug / run_name
    output_dir = run_dir / "output"
    for path in (
        run_dir / "meta",
        output_dir / "code",
        output_dir / "data",
        output_dir / "results",
        output_dir / "logs",
        output_dir / "logs" / "workflow_evidence",
        output_dir / "logs" / "operator_feedback",
    ):
        path.mkdir(parents=True, exist_ok=True)

    create_operator_role_prompts(
        output_dir,
        react_role_prompts,
        problem_id=problem_id,
        problem=problem,
    )

    installed_skills = []
    if skills_source is not None:
        skills_source = Path(skills_source).resolve()
        if not skills_source.is_dir():
            raise FileNotFoundError(f"Skills source not found: {skills_source}")
        selected_skill_names = (
            set(selected_skills) if selected_skills is not None else None
        )
        workspace_skills = output_dir / "skills"
        for source in sorted(skills_source.iterdir()):
            if not source.is_dir() or not (source / "SKILL.md").is_file():
                continue
            if (
                selected_skill_names is not None
                and source.name not in selected_skill_names
            ):
                continue
            shutil.copytree(source, workspace_skills / source.name)
            installed_skills.append(source.name)

    prompt_path = run_dir / "prompt.md"
    prompt_path.write_text(
        render_prompt(problem_id, problem, output_dir, template_path),
        encoding="utf-8",
    )
    metadata = {
        "problem_id": problem_id,
        "model": model,
        "created_at": datetime.now().isoformat(),
        "prompt_template": str(
            (template_path or BASELINE_PROMPT_TEMPLATE_PATH).resolve()
        ),
        "prompt": str(prompt_path),
        "output_dir": str(output_dir),
        "final_report": str(output_dir / "results" / "solution_report.md"),
        "installed_skills": installed_skills,
    }
    (run_dir / "meta" / "run.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return run_dir, output_dir, prompt_path


def run_problem(problem_id: str, problem: dict, args) -> dict:
    output_root = Path(args.output_root).resolve()
    template_path = (
        Path(args.prompt_template).resolve()
        if getattr(args, "prompt_template", None)
        else None
    )
    run_dir, output_dir, prompt_path = prepare_run(
        problem_id,
        problem,
        output_root,
        args.model,
        template_path,
        getattr(args, "react_role_prompts", None),
        getattr(args, "skills_source", None),
        getattr(args, "selected_skills", None),
        getattr(args, "run_directory_prefix", None),
        getattr(args, "flat_run_layout", False),
    )
    print(f"Prepared OpenClaw run: {run_dir}")
    print(f"Prompt: {prompt_path}")
    if args.prepare_only:
        return {
            "run_dir": run_dir,
            "prompt": prompt_path,
            "final_report": output_dir / "results" / "solution_report.md",
            "judge_result": None,
            "average_score": None,
            "workflow_check": None,
        }

    openclaw = find_openclaw_command(args.openclaw_command)
    agent_id = args.agent or slugify(
        f"modelingbench-{problem_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    log_path = run_dir / "meta" / "solve.log"

    if not args.agent:
        run_checked(
            [
                openclaw,
                "agents",
                "add",
                agent_id,
                "--workspace",
                str(output_dir),
                "--model",
                args.model,
                "--non-interactive",
                "--json",
            ],
            run_dir,
            log_path,
        )

    session_id = f"{slugify(problem_id)}-{datetime.now().strftime('%m%d%H%M%S')}"
    stream_command(
        [
            openclaw,
            "agent",
            "--local",
            "--agent",
            agent_id,
            "--session-id",
            session_id,
            "--message-file",
            str(prompt_path),
            "--thinking",
            args.thinking,
            "--timeout",
            str(args.timeout),
        ],
        run_dir,
        log_path,
        completion_artifact=output_dir / "results" / "solution_report.md",
    )

    final_report = output_dir / "results" / "solution_report.md"
    if not final_report.is_file() or not final_report.read_text(
        encoding="utf-8"
    ).strip():
        raise RuntimeError(
            "OpenClaw completed without a non-empty final report at "
            f"{final_report}. See {log_path}."
        )

    workflow_check = record_disabled_workflow_check(
        run_dir / "meta" / "workflow_check.json"
    )
    print(f"Post-run workflow checker is disabled: {workflow_check}")
    print(f"Final OpenClaw report: {final_report}")
    result_path = None
    average_score = None
    if not args.skip_judge:
        result_path = judge_final_report(
            problem_id, final_report, slugify(args.model), run_dir
        )
        average_score = calculate_average_score(result_path)
        print(f"Judge result: {result_path}")
        print(f"Average benchmark score: {average_score:.6f}")
    return {
        "run_dir": run_dir,
        "prompt": prompt_path,
        "final_report": final_report,
        "judge_result": result_path,
        "average_score": average_score,
        "workflow_check": workflow_check,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run OpenClaw on ModelingBench and judge only its final report."
    )
    parser.add_argument(
        "problem_id", nargs="?", help="Problem ID; omit only when using --all."
    )
    parser.add_argument("--all", action="store_true", help="Run all benchmark problems.")
    parser.add_argument("--agent", help="Use an existing OpenClaw agent ID.")
    parser.add_argument(
        "--model", default="deepseek/deepseek-v4-flash", help="OpenClaw model ID."
    )
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--openclaw-command")
    parser.add_argument(
        "--prompt-template",
        help=(
            "Optional prompt template; defaults to "
            "src/OpenClaw/prompt_modelingbench_baseline.md."
        ),
    )
    parser.add_argument(
        "--output-root", default=str(REPO_ROOT / "output_workspace_openclaw")
    )
    parser.add_argument(
        "--skills-source",
        help="Optional directory containing workspace skill folders.",
    )
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Create the run directory and rendered prompt without calling OpenClaw.",
    )
    args = parser.parse_args()

    if bool(args.problem_id) == bool(args.all):
        parser.error("provide exactly one problem_id or --all")

    problems = load_problems()
    if args.problem_id:
        if args.problem_id not in problems:
            parser.error(f"unknown problem ID: {args.problem_id}")
        selected = [(args.problem_id, problems[args.problem_id])]
    else:
        selected = list(problems.items())

    for problem_id, problem in selected:
        run_problem(problem_id, problem, args)


if __name__ == "__main__":
    main()
