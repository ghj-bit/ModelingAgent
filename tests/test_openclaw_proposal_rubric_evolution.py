from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.OpenClaw import baseline
from src.OpenClaw import run_local_rubric_evolution as local
from src.OpenClaw import run_proposal_checkpoint_evolution as checkpoint
from src.OpenClaw import run_proposal_rubric_evolution as proposal


def proposal_args(**overrides):
    values = {
        "disable_proposal_operator": False,
        "enable_react_operator": True,
        "proposal_plateau_window": 3,
        "proposal_min_improvement": 0.005,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_proposal_operator_activates_for_innovation_plateau():
    results = [
        {"offline_score": score}
        for score in (0.70, 0.701, 0.702, 0.702)
    ]
    best = {
        "node_id": "node_4",
        "dimension_scores": {
            "innovativeness": 0.40,
            "modeling_groundedness": 0.75,
        },
    }
    with patch.object(local, "best_mcts_node", return_value=best):
        decision = proposal.proposal_operator_decision(
            results, {"nodes": {}}, proposal_args()
        )
    assert decision["active"] is True
    assert decision["selected_operator"] == "proposal"
    assert decision["target_dimension"] == "innovativeness"


def test_proposal_operator_stays_off_while_score_improves():
    results = [
        {"offline_score": score}
        for score in (0.70, 0.71, 0.72, 0.73)
    ]
    best = {
        "node_id": "node_4",
        "dimension_scores": {
            "innovativeness": 0.40,
            "modeling_groundedness": 0.75,
        },
    }
    with patch.object(local, "best_mcts_node", return_value=best):
        decision = proposal.proposal_operator_decision(
            results, {"nodes": {}}, proposal_args()
        )
    assert decision["active"] is False
    assert decision["selected_operator"] == "react"
    assert decision["reason"] == "recent best score is still improving"


def test_react_is_disabled_by_default_mode():
    decision = proposal.proposal_operator_decision(
        [],
        {"nodes": {}},
        proposal_args(enable_react_operator=False),
    )
    assert decision["active"] is True
    assert decision["selected_operator"] == "proposal"
    assert decision["target_dimension"] == "innovativeness"
    assert decision["reason"] == "React operator disabled by command line"


def test_proposal_prompt_skips_react_and_uses_feedback_as_patch():
    seed = local.DEFAULT_SEED_WORKFLOW.read_text(encoding="utf-8")
    candidate = {
        "rubric_id": "rubric_test",
        "stage": "modeling",
        "criterion": "Compare a distinct hypothesis against the baseline.",
    }
    prompt = proposal.refinement_prompt(
        seed,
        "modeling",
        candidate,
        "node_parent",
        proposal_operator=True,
    )
    assert "2. **Proposal:**" in prompt
    assert "**ReAct:**" not in prompt
    assert "do not launch ReAct" in prompt
    assert "proposal_1.md` as the proposal patch" in prompt
    assert "proposal_1.md" in prompt
    assert "proposal_used" in prompt
    assert "proposal_agent_context.md" in prompt
    assert "## Generated files" in prompt
    assert "paths to the relevant generated files" in prompt


def test_proposal_role_is_materialized_without_changing_baseline(tmp_path: Path):
    prompts = proposal.build_node_role_prompts(
        local.new_rubric_bank(),
        "modeling",
        {
            "rubric_id": "rubric_test",
            "stage": "modeling",
            "criterion": "Test one distinct hypothesis.",
            "status": "candidate",
        },
        True,
    )
    baseline.create_operator_role_prompts(tmp_path, prompts)
    role_path = (
        tmp_path
        / "logs"
        / "operator_roles"
        / proposal.PROPOSAL_ROLE_FILENAME
    )
    assert role_path.is_file()
    assert set(prompts) == {proposal.PROPOSAL_ROLE_KEY}
    role = role_path.read_text(encoding="utf-8")
    assert "independent proposal subagent" in role
    assert "Use the supplied proposal rubric" in role
    assert "main-Agent state" in role
    assert "## Evidence reviewed" in role


def test_checkpoint_wrapper_imports_best_node_into_new_experiment(tmp_path: Path):
    source = (
        proposal.REPO_ROOT
        / "openclaw_experiments"
        / "mlevolve_rubric_20260830_225420"
    )
    problem_id, seed = checkpoint.load_best_checkpoint(
        source, "2013_Bank_Service_Problem"
    )
    destination = tmp_path / "new_proposal_experiment"
    checkpoint.initialize_destination(destination, source, problem_id, seed)
    config = proposal.workflow_evolution.read_json(
        destination / "config.json", {}
    )
    results = proposal.workflow_evolution.read_json(
        destination / "workflows" / "results.json", []
    )
    assert destination.is_dir()
    assert config["source_experiment"] == str(source.resolve())
    assert config["react_operator_enabled"] is False
    assert results[0]["source_node_id"] == "node_r6_e1"
    assert results[0]["offline_score"] == 0.7687499999999999


def test_checkpoint_wrapper_normalizes_agent_and_optimizer_models():
    normalized = checkpoint.normalize_forwarded_models(
        [
            "--model",
            "deepseek-v4-flash",
            "--opt-model",
            "deepseek/deepseek-v4-flash",
            "--thinking=high",
        ]
    )
    assert normalized == [
        "--model",
        "deepseek/deepseek-v4-flash",
        "--opt-model",
        "deepseek-v4-flash",
        "--thinking=high",
    ]


def test_checkpoint_wrapper_normalizes_equals_model_arguments():
    assert checkpoint.normalize_forwarded_models(
        [
            "--model=deepseek-v4-pro",
            "--opt-model=deepseek/deepseek-v4-flash",
        ]
    ) == [
        "--model=deepseek/deepseek-v4-pro",
        "--opt-model=deepseek-v4-flash",
    ]


def test_checkpoint_wrapper_repairs_transient_optimizer_exhaustion(tmp_path: Path):
    destination = tmp_path / "experiment"
    workflows = destination / "workflows"
    (workflows / "round_2").mkdir(parents=True)
    proposal.workflow_evolution.write_json(
        workflows / "results.json", [{"round": 1}]
    )
    proposal.workflow_evolution.write_json(
        workflows / proposal.SEMANTIC_MEMORY_FILENAME,
        {"entries": [], "rejections": []},
    )
    graph_path = workflows / proposal.SEARCH_GRAPH_FILENAME
    proposal.workflow_evolution.write_json(
        graph_path,
        {
            "nodes": {
                "root": {
                    "node_id": "root",
                    "semantic_exhausted": True,
                    "semantic_exhausted_at": "temporary",
                    "semantic_exhausted_round": 2,
                }
            }
        },
    )
    assert checkpoint.repair_transient_semantic_exhaustion(destination) == [
        "root"
    ]
    repaired = proposal.workflow_evolution.read_json(graph_path, {})
    assert "semantic_exhausted" not in repaired["nodes"]["root"]
