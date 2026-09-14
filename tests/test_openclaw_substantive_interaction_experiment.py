import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import run_substantive_interaction_experiment as substantive  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_refinement_prompt_directly_contains_rubric_without_baseline_workflow() -> None:
    rubric = substantive.load_rubric()
    prompt = substantive.build_refinement_prompt(rubric)

    assert "Expert-Guided Modeling Report Refinement" in prompt
    assert "Traceable substantive consultation" in prompt
    assert prompt.count("**Post-reply causal change**") == 1
    assert "Concise task-balanced consultation" not in prompt
    assert "controller creates the fixed-schema request" in prompt
    assert "interaction_evidence.md" in prompt
    assert "must not contain a section titled `Expert Interaction Impact`" in prompt
    assert "## Workflow Summary Contract" not in prompt
    assert "## Substantive Interaction Evidence Contract" not in prompt
    assert "technical_translations" not in prompt
    assert "step_01_problem_understanding.md" not in prompt
    assert "step_05_validation_analysis.md" not in prompt
    assert "Solve the complete problem below autonomously" not in prompt
    assert "## Required Workflow" not in prompt
    assert "{{RESULTS_DIR}}/original_report.md" in prompt
    assert "{{FINAL_REPORT}}" in prompt
    assert "{{QUESTION}}" in prompt
    assert "execute the affected code again" in prompt
    assert "stale inherited outputs" in prompt
    assert "refinement_changed_files.json" not in prompt
    assert "record_refinement_changes.py" not in prompt


def test_substantive_gate_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.setattr(
        sys, "argv", ["run_substantive_interaction_experiment.py"]
    )
    args = substantive.parse_args()

    assert args.enforce_substantive_interaction_gate is False
    assert args.opt_model == "deepseek-v4-pro"


def test_substantive_role_setup_keeps_only_required_expert_prompt(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        substantive.baseline,
        "HUMAN_MODELING_EXPERT_ROLE_PROMPT",
        "Qualitative expert role.",
    )

    substantive.create_substantive_operator_role_prompt(
        tmp_path,
        problem_id="problem",
        problem={"question": "Question text"},
    )

    files = sorted(
        path.name
        for path in (tmp_path / "logs" / "operator_roles").iterdir()
    )
    assert files == ["human_modeling_expert.md"]


def test_unused_role_cleanup_preserves_feedback_and_required_prompt(
    tmp_path: Path,
) -> None:
    roles = tmp_path / "logs" / "operator_roles"
    feedback = tmp_path / "logs" / "operator_feedback"
    roles.mkdir(parents=True)
    feedback.mkdir(parents=True)
    for name in (
        "ask_expert.md",
        "react_verifier_modeling.md",
        "react_verifier_problem_data.md",
        "human_modeling_expert.md",
    ):
        (roles / name).write_text(name, encoding="utf-8")
    dialogue = feedback / "human_expert_dialogue.md"
    dialogue.write_text("dialogue", encoding="utf-8")

    removed = substantive.remove_unused_operator_role_prompts(tmp_path)

    assert {path.name for path in removed} == {
        "ask_expert.md",
        "react_verifier_modeling.md",
        "react_verifier_problem_data.md",
    }
    assert (roles / "human_modeling_expert.md").is_file()
    assert dialogue.is_file()


def test_substantive_gate_can_be_enabled(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_substantive_interaction_experiment.py",
            "--enforce-substantive-interaction-gate",
        ],
    )
    args = substantive.parse_args()

    assert args.enforce_substantive_interaction_gate is True


def test_evolution_feedback_keeps_only_non_full_role_overalls() -> None:
    judge = {
        "judgements": {
            "analysis_groundedness": {
                "role_based_results": [
                    {
                        "overall_score": 0.75,
                        "overall_feedback": "The uncertainty analysis is incomplete.",
                        "role": {"name": "Analyst"},
                        "detail": {"score": 0.25, "explanation": "Do not pass this."},
                    },
                    {
                        "overall_score": 1.0,
                        "overall_feedback": "Full-score feedback must be excluded.",
                    },
                ]
            },
            "modeling_groundedness": {
                "role_based_results": [
                    {
                        "overall_score": 0.5,
                        "overall_feedback": "Model assumptions need stronger support.",
                    }
                ]
            },
        }
    }

    selected = substantive.non_full_role_evaluations(judge)

    assert selected == [
        {
            "dimension": "modeling_groundedness",
            "role_evaluations": [
                {
                    "overall_score": 0.5,
                    "overall_feedback": "Model assumptions need stronger support.",
                }
            ],
        },
        {
            "dimension": "analysis_groundedness",
            "role_evaluations": [
                {
                    "overall_score": 0.75,
                    "overall_feedback": "The uncertainty analysis is incomplete.",
                }
            ],
        },
    ]


def test_substantive_evolution_has_no_assigned_mutation_axis(
    tmp_path: Path, monkeypatch
) -> None:
    rubric = substantive.load_rubric()
    results = [{"round": 1, "utility": 0.8, "rubric": rubric}]
    captured = {}

    def fake_optimizer(payload, args):
        captured["prompt"] = payload["messages"][1]["content"]
        return {
            "name": "Evidence-directed consultation",
            "purpose": "Improve substantive expert interaction using observed evaluation evidence.",
            "criteria": [
                {
                    "name": "Decision impact",
                    "rule": "Ask for one qualitative decision and trace its downstream analytical impact.",
                    "positive_example": "The reply changes a later decision-relevant analysis.",
                    "negative_example": "The reply is merely copied into the report.",
                }
            ],
            "attention_budget": "Use one exchange unless the same decision remains unresolved.",
            "success_test": "A downstream artifact identifies a reply-triggered analytical change.",
            "mutation_rationale": "Respond to the supplied non-full role evaluations.",
            "crossover_rationale": "Only one parent is currently available.",
        }

    monkeypatch.setattr(substantive, "optimizer_evidence", lambda *_: [])
    monkeypatch.setattr(substantive.interaction.local, "optimizer_response", fake_optimizer)
    args = type(
        "Args",
        (),
        {
            "optimizer_retries": 1,
            "opt_model": "test-model",
            "opt_api_key": None,
            "opt_base_url": None,
        },
    )()

    candidate = substantive.propose_rubric(results, 2, tmp_path, args, {})

    assert "There is no prescribed mutation axis or" in captured["prompt"]
    assert "judge_weakness_summary" not in captured["prompt"]
    assert "overall_score and overall_feedback directly" in captured["prompt"]
    assert "report as a downstream product of that" in captured["prompt"]
    assert "dialogue and report as unrelated artifacts" in captured["prompt"]
    assert "already been read and embedded above by" in captured["prompt"]
    assert "request any additional" in captured["prompt"]
    assert "expert dialogue" in captured["prompt"]
    assert "only report-change input" in captured["prompt"]
    assert "code changes" in captured["prompt"]
    assert "mutation_axis" not in candidate
    assert candidate["parent_rounds"] == [1]
    assert (tmp_path / "evolution_prompt.md").read_text(encoding="utf-8") == (
        captured["prompt"]
    )
    response = json.loads(
        (tmp_path / "evolution_response.json").read_text(encoding="utf-8")
    )
    assert response["name"] == "Evidence-directed consultation"


def test_parent_artifacts_keep_interaction_files_but_exclude_change_manifest(
    tmp_path: Path,
) -> None:
    output = tmp_path / "output"
    evidence = output / "results" / "interaction_evidence.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text(
        "The expert reply caused a new decision-relevant validation scenario.",
        encoding="utf-8",
    )
    dialogue = output / "logs" / "operator_feedback" / "human_expert_dialogue.md"
    dialogue.parent.mkdir(parents=True)
    dialogue.write_text("Question and expert answer.", encoding="utf-8")
    receipt = output / "results" / "interaction_receipt.json"
    receipt.write_text('{"interaction_complete": true}', encoding="utf-8")
    (output / "results" / "refinement_changed_files.json").write_text(
        '{"modified": ["code/model.py"]}', encoding="utf-8"
    )
    (output / "code").mkdir()
    (output / "code" / "model.py").write_text("print(2)", encoding="utf-8")

    artifacts = substantive.parent_artifacts(tmp_path)

    by_type = {item["artifact_type"]: item["content"] for item in artifacts}
    assert by_type == {
        "expert_interaction": "Question and expert answer.",
        "interaction_evidence": (
            "The expert reply caused a new decision-relevant validation scenario."
        ),
        "interaction_receipt": '{"interaction_complete": true}',
    }


def test_parent_artifacts_exclude_complete_report(tmp_path: Path) -> None:
    results = tmp_path / "output" / "results"
    results.mkdir(parents=True)
    (results / "original_report.md").write_text(
        "# Complete original report\n\nThis must not reach the optimizer.",
        encoding="utf-8",
    )
    (results / "solution_report.md").write_text(
        "# Complete refined report\n\nThis must not reach the optimizer.",
        encoding="utf-8",
    )

    assert substantive.parent_artifacts(tmp_path) == []


def test_programmatic_report_diff_becomes_optimizer_artifact(
    tmp_path: Path,
) -> None:
    results = tmp_path / "output" / "results"
    results.mkdir(parents=True)
    (results / "original_report.md").write_text(
        "# Report\n\nUnchanged.\n\nOld conclusion.\n", encoding="utf-8"
    )
    (results / "solution_report.md").write_text(
        "# Report\n\nUnchanged.\n\nRevised conclusion.\n\nNew validation.\n",
        encoding="utf-8",
    )

    output = substantive.write_interaction_added_content(tmp_path)
    content = output.read_text(encoding="utf-8")
    artifacts = substantive.parent_artifacts(tmp_path)

    assert "Revised conclusion." in content
    assert "New validation." in content
    assert "Old conclusion." not in content
    assert "Unchanged." not in content
    assert artifacts == [
        {"artifact_type": "interaction_added_content", "content": content}
    ]


def test_baseline_report_resolution_selects_newest_matching_run(
    tmp_path: Path,
) -> None:
    older = (
        tmp_path
        / "2013_Bank_Service_Problem_20260101_000000"
        / "output"
        / "results"
        / "solution_report.md"
    )
    newer = (
        tmp_path
        / "2013_Bank_Service_Problem_20260102_000000"
        / "output"
        / "results"
        / "solution_report.md"
    )
    for path, text in ((older, "old"), (newer, "new")):
        path.parent.mkdir(parents=True)
        path.write_text(text, encoding="utf-8")
    older.touch()
    newer.touch()

    assert substantive.resolve_baseline_report(
        "2013_Bank_Service_Problem", tmp_path
    ) == newer


def test_refinement_preparation_inherits_workspace_without_appending_prompt(
    tmp_path: Path, monkeypatch
) -> None:
    source_output = tmp_path / "baseline_run" / "output"
    source = source_output / "results" / "solution_report.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Fixed baseline draft", encoding="utf-8")
    (source_output / "code").mkdir()
    (source_output / "code" / "model.py").write_text(
        "print('baseline result')", encoding="utf-8"
    )
    (source_output / "data").mkdir()
    (source_output / "data" / "inputs.csv").write_text(
        "x,y\n1,2\n", encoding="utf-8"
    )
    (source_output / "results" / "numbers.json").write_text(
        '{"value": 2}', encoding="utf-8"
    )
    (source_output / "logs" / "operator_feedback").mkdir(parents=True)
    (source_output / "logs" / "operator_feedback" / "expert_reply_1.json").write_text(
        '{"ok": true}', encoding="utf-8"
    )
    (source_output / "openclaw-workspace-state.json").write_text(
        "old runtime state", encoding="utf-8"
    )
    run_dir = tmp_path / "run"
    output = run_dir / "output"
    (output / "results").mkdir(parents=True)
    prompt = run_dir / "prompt.md"
    prompt.write_text("Already rendered refinement prompt.", encoding="utf-8")
    write_json(run_dir / "meta" / "run.json", {"problem_id": "problem"})

    monkeypatch.setattr(
        substantive,
        "ORIGINAL_PREPARE_VALIDATION_PROBLEM",
        lambda *args: {
            "problem_id": "problem",
            "run_dir": run_dir,
            "output_dir": output,
            "prompt": prompt,
            "recovered": False,
        },
    )
    args = type(
        "Args", (), {"baseline_reports": {"problem": str(source)}}
    )()

    substantive.prepare_refinement_validation_problem(
        "problem", {}, prompt, 1, 1, tmp_path, args
    )

    original = output / "results" / "original_report.md"
    assert original.read_text(encoding="utf-8") == "# Fixed baseline draft"
    assert (output / "code" / "model.py").is_file()
    assert (output / "data" / "inputs.csv").is_file()
    assert (output / "results" / "numbers.json").is_file()
    assert (output / "code" / "record_refinement_changes.py").is_file()
    assert (output / "results" / "baseline_workspace_manifest.json").is_file()
    assert not (output / "results" / "solution_report.md").exists()
    assert not (output / "logs" / "operator_feedback" / "expert_reply_1.json").exists()
    assert not (output / "openclaw-workspace-state.json").exists()
    rendered = prompt.read_text(encoding="utf-8")
    assert rendered == "Already rendered refinement prompt."
    metadata = json.loads((run_dir / "meta" / "run.json").read_text())
    assert metadata["baseline_report_source"] == str(source)
    assert metadata["baseline_workspace_source"] == str(source_output)
    assert set(metadata["baseline_workspace_inherited_files"]) == {
        "code/model.py",
        "data/inputs.csv",
        "results/numbers.json",
        "results/original_report.md",
    }


def test_refinement_change_record_tracks_modified_added_and_deleted_files(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "output"
    (workspace / "code").mkdir(parents=True)
    (workspace / "results").mkdir()
    model = workspace / "code" / "model.py"
    obsolete = workspace / "results" / "obsolete.txt"
    model.write_text("print(1)", encoding="utf-8")
    obsolete.write_text("old", encoding="utf-8")
    manifest = workspace / "results" / "baseline_workspace_manifest.json"
    substantive.record_refinement_changes.write_manifest(workspace, manifest)

    model.write_text("print(2)", encoding="utf-8")
    obsolete.unlink()
    (workspace / "results" / "fresh.txt").write_text("new", encoding="utf-8")
    record_path = workspace / "results" / "refinement_changed_files.json"
    record = substantive.record_refinement_changes.write_changes(
        workspace, manifest, record_path
    )

    assert record["modified"] == ["code/model.py"]
    assert record["added"] == ["results/fresh.txt"]
    assert record["deleted"] == ["results/obsolete.txt"]
    assert json.loads(record_path.read_text(encoding="utf-8")) == record


def test_substantive_gate_accepts_post_reply_evidence(tmp_path: Path) -> None:
    output = tmp_path / "output"
    feedback = output / "logs" / "operator_feedback"
    results = output / "results"
    write_json(
        feedback / "expert_request_1.json",
        {"interaction_stage": 2, "question": "Which objective should govern?"},
    )
    write_json(
        feedback / "expert_reply_1.json",
        {"ok": True, "answer": "Prioritize the safety objective."},
    )
    results.mkdir(parents=True, exist_ok=True)
    (results / "interaction_evidence.md").write_text(
        "Baseline: average performance.\n\nChange: added a tail-risk test.",
        encoding="utf-8",
    )
    (results / "solution_report.md").write_text(
        "## Results\n\nThe tail-risk test changes the robust recommendation.",
        encoding="utf-8",
    )

    check = substantive.validate_substantive_interaction(tmp_path)

    assert check["passed"] is True
    assert check["interaction_stage"] == 2
    assert len(check["post_reply_artifacts"]) == 1


def test_session_log_contains_content_without_transport_noise(
    tmp_path: Path, monkeypatch
) -> None:
    state = tmp_path / "state"
    agent_id = "test-agent"
    session_id = "test-session"
    session_file = state / "agents" / agent_id / "sessions" / f"{session_id}.jsonl"
    session_file.parent.mkdir(parents=True)
    messages = [
        {
            "type": "message",
            "timestamp": "2026-09-08T00:00:00Z",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "Solve this task."}],
            },
        },
        {
            "type": "message",
            "timestamp": "2026-09-08T00:00:01Z",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "private reasoning"},
                    {"type": "text", "text": "I will inspect the data."},
                    {
                        "type": "toolCall",
                        "name": "exec",
                        "arguments": {"command": "python check.py", "api_key": "sk-secret123"},
                    },
                ],
            },
        },
        {
            "type": "message",
            "timestamp": "2026-09-08T00:00:02Z",
            "message": {
                "role": "toolResult",
                "toolName": "exec",
                "content": [{"type": "text", "text": "validation passed"}],
            },
        },
    ]
    session_file.write_text(
        "".join(json.dumps(item) + "\n" for item in messages), encoding="utf-8"
    )
    request = tmp_path / "prompt.md"
    request.write_text("fallback request", encoding="utf-8")
    log = tmp_path / "solve.log"
    monkeypatch.setenv("OPENCLAW_STATE_DIR", str(state))

    substantive.render_openclaw_session_log(agent_id, session_id, request, log)

    text = log.read_text(encoding="utf-8")
    assert "Event 1 — REQUEST" in text
    assert "Solve this task." in text
    assert "Event 2 — RESPONSE" in text
    assert "I will inspect the data." in text
    assert "Tool request: `exec`" in text
    assert "TOOL RETURN: exec" in text
    assert "validation passed" in text
    assert "private reasoning" not in text
    assert "sk-secret123" not in text
    assert "[REDACTED]" in text
    assert "provider-transport-fetch" not in text


def test_substantive_modeling_phase_separates_transport_and_session_logs(
    tmp_path: Path, monkeypatch
) -> None:
    state = tmp_path / "state"
    agent_id = "phase-agent"
    session_id = "phase-session"
    session_file = state / "agents" / agent_id / "sessions" / f"{session_id}.jsonl"
    session_file.parent.mkdir(parents=True)
    session_file.write_text(
        json.dumps(
            {
                "type": "message",
                "timestamp": "2026-09-08T00:00:00Z",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Completed report."}],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    request = tmp_path / "prompt.md"
    request.write_text("Do the work.", encoding="utf-8")
    monkeypatch.setenv("OPENCLAW_STATE_DIR", str(state))

    def fake_stream(command, cwd, log_path, **kwargs):
        assert Path(log_path).name == "transport.log"
        Path(log_path).write_text("provider-transport-fetch", encoding="utf-8")

    monkeypatch.setattr(substantive.baseline, "stream_command", fake_stream)
    monkeypatch.setattr(
        substantive, "write_interaction_added_content", lambda *_: None
    )
    prepared = {
        "openclaw": "openclaw",
        "agent_id": agent_id,
        "run_dir": tmp_path,
    }
    args = type("Args", (), {"thinking": "high", "timeout": 60})()

    substantive.run_substantive_modeling_phase(
        prepared, session_id, request, args, None
    )

    assert (tmp_path / "meta" / "transport.log").read_text() == (
        "provider-transport-fetch"
    )
    solve = (tmp_path / "meta" / "solve.log").read_text(encoding="utf-8")
    assert "Completed report." in solve
    assert "provider-transport-fetch" not in solve
