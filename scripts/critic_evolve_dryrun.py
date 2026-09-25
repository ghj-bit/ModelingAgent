"""Score one round's interactions with the rubric and run ONLY the evolver.

No task is solved here.  The script takes an experiment's completed evaluation
round, rebuilds the training-parent evidence bundle the engine would hand to the
optimizer, scores every run's interaction with the active rubric, appends that
review to the workflow-evolution prompt, and calls the optimizer once -- so the
candidate policy it prints is what the evolver produces when the rubric review
is the extra evidence.

    python scripts/critic_evolve_dryrun.py \\
        --experiment openclaw_experiments/evolve_exp/claude_evolve_r1_from_round0 \\
        --round 0 --phase initial_validation_parent_1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import interaction_strategy_critic as critic  # noqa: E402
from src.OpenClaw import (  # noqa: E402
    run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base,
)
from src.OpenClaw import (  # noqa: E402
    run_substantive_interaction_workflow_evolution as shared,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True, type=Path)
    parser.add_argument("--round", required=True, type=int)
    parser.add_argument("--phase", default="initial_validation_parent_1")
    parser.add_argument("--label", default=None, help="output folder name")
    return parser.parse_args()


def read_json(path: Path, default=None):
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def load_dialogue(run_dir: Path) -> str:
    for relative in (
        "output/logs/operator_feedback/human_expert_dialogue.md",
        "output/results/interaction_evidence.md",
    ):
        path = run_dir / relative
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="replace")
    return ""


def load_change_summary(run_dir: Path) -> str:
    """The run's own record of what the reply changed, if it wrote one."""
    path = run_dir / "output/results/interaction_evidence.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(
        r"(?is)(modeling decision derived|decision derived|how this affected the work)"
        r"(.*?)(?=\n#{1,3} |\Z)",
        text,
    )
    return match.group(0).strip()[:2500] if match else ""


def build_training_runs(completed: dict) -> list[dict]:
    runs = []
    for problem_id, by_rep in sorted(completed.items()):
        for repetition, entry in sorted(by_rep.items(), key=lambda kv: int(kv[0])):
            run_dir = Path(str(entry.get("run_dir", "")))
            dialogue = load_dialogue(run_dir)
            receipt = entry.get("interaction_receipt") or {}
            if not dialogue and receipt:
                dialogue = json.dumps(receipt, ensure_ascii=False)[:20000]
            draft_path = run_dir / "output/results/draft.md"
            draft = (
                draft_path.read_text(encoding="utf-8", errors="replace")[:9000]
                if draft_path.is_file()
                else ""
            )
            artifacts = []
            if dialogue:
                artifacts.append({"artifact_type": "expert_interaction", "content": dialogue})
            if draft:
                artifacts.append({"artifact_type": "planning_draft", "content": draft})
            runs.append(
                {
                    "problem_id": problem_id,
                    "title": f"MM-Bench {problem_id}",
                    "question": "",
                    "artifacts": artifacts,
                    "scores": {
                        "report_score": entry.get("average_score"),
                        "dimension_scores": entry.get("dimension_scores") or {},
                        "interaction_cost": entry.get("interaction_cost"),
                        "interaction_penalty": entry.get("interaction_penalty"),
                    },
                    "interaction_report_change_summary": load_change_summary(run_dir),
                }
            )
    return runs


def main() -> None:
    args = parse_args()
    experiment = args.experiment.resolve()
    label = args.label or f"round_{args.round}_critic_dryrun"
    round_dir = experiment / "workflows" / label
    round_dir.mkdir(parents=True, exist_ok=True)

    checkpoint = read_json(
        experiment
        / "cpe_evaluations"
        / f"round_{args.round}"
        / args.phase
        / "workflows"
        / f"round_{args.round}"
        / "evaluation_checkpoint.json",
        {},
    )
    completed = checkpoint.get("completed") or {}
    if not completed:
        raise SystemExit(f"No completed runs in {experiment} round {args.round}")

    seed = read_json(experiment / "initial_interaction_workflows.json", [{}])
    seed = seed[0] if isinstance(seed, list) else seed
    config = read_json(experiment / "config.json", {})
    validation_utility = None
    state = read_json(experiment / "workflows/cpe_state.json", {})
    initial = (state.get("initial_parent_validation_results") or [{}])[0]
    validation_utility = (initial or {}).get("utility")

    runs = build_training_runs(completed)
    training_parents = [
        {
            "parent_rank": 1,
            "workflow_id": seed.get("workflow_id"),
            "workflow": seed,
            "net_utility_on_current_training_batch": validation_utility,
            "training_evidence": {
                "round": args.round,
                "training_runs": runs,
                "average_interaction_cost": None,
                "average_interaction_penalty": None,
                "interaction_cost_parameters": (config.get("cpe") or {}).get(
                    "interaction_cost", {}
                ),
            },
        }
    ]
    validation_champion = {
        "workflow_id": seed.get("workflow_id"),
        "workflow": seed,
        "utility": validation_utility,
    }

    # 1) critic review of every interaction in the round
    model, api_key, base_url, timeout = critic.critic_credentials(
        mmbench_judge={
            "model": os.environ.get("CRITIC_MODEL") or "deepseek-flash",
            "base_url": os.environ.get("CRITIC_BASE_URL") or "https://api.deepseek.com",
            "api_key": os.environ.get("CRITIC_API_KEY")
            or os.environ.get("ANTHROPIC_AUTH_TOKEN"),
        }
    )
    review = critic.review_training_parents(
        training_parents,
        experiment=experiment,
        model=model,
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
    )
    block = critic.render_critic_block(review)

    # 2) the usual evolution prompt, plus the review.  The launcher runs with a
    # single live policy, so the engine's parent count has to match here too.
    shared.CPE_TRAINING_PARENT_COUNT = 1
    prompt = base.build_initial_draft_cpe_workflow_evolution_prompt(
        training_parents, validation_champion, []
    )
    prompt_with_critic = prompt + "\n\n" + block
    (round_dir / "evolution_prompt.md").write_text(prompt_with_critic, encoding="utf-8")
    (round_dir / "critic_block.md").write_text(block, encoding="utf-8")

    # 3) run the evolver only
    base.disable_thinking_for_direct_api_calls()

    class OptArgs:
        opt_model = "qwen3.8-27b"
        opt_base_url = "http://gpu6:18763/v1"
        opt_api_key = "EMPTY"

    candidate = shared.interaction.local.optimizer_response(
        {
            "model": OptArgs.opt_model,
            "messages": [
                {"role": "system", "content": "Return one concise valid JSON workflow object."},
                {"role": "user", "content": prompt_with_critic},
            ],
            "temperature": 0.5,
            "max_tokens": 3000,
            "response_format": {"type": "json_object"},
        },
        OptArgs(),
    )
    (round_dir / "evolution_response.json").write_text(
        json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("\n" + "=" * 78)
    print("归一化分数:", json.dumps(
        {
            "rubric": review.get("rubric_id"),
            "max": review.get("rubric_max_total"),
            "parents": [
                {
                    "workflow_id": p.get("workflow_id"),
                    "mean_total": p.get("mean_total"),
                    "mean_normalized": p.get("mean_normalized"),
                }
                for p in review.get("parents") or []
            ],
        },
        ensure_ascii=False,
    ))
    print("=" * 78)
    print(json.dumps(candidate, ensure_ascii=False, indent=2)[:4000])
    print("=" * 78)
    print("产物:", round_dir)


if __name__ == "__main__":
    main()
