"""Run ONLY the interaction-policy evolver over one completed round.

No task is solved and no rubric is involved: this script takes an experiment's
completed evaluation round, rebuilds the training-parent evidence bundle the
engine would hand the optimizer, builds the evolution prompt exactly as the
launcher builds it, and calls the optimizer once.  The policy it prints is what
the evolver produces from that round's evidence alone.

    python scripts/evolver_dryrun.py \
        --experiment openclaw_experiments/evolve_exp/claude_evolve_round0 \
        --round 0 --phase initial_validation_parent_1

The sibling ``critic_evolve_dryrun.py`` does the same but appends the critic's
rubric-based review to the prompt.  This one deliberately does not import the
critic module at all, so nothing rubric-shaped can reach the optimizer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import run_substantive_interaction_workflow_evolution as shared  # noqa: E402
from src.OpenClaw import (  # noqa: E402
    run_substantive_interaction_workflow_evolution_from_initial_draft_claude as launcher,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True, type=Path)
    parser.add_argument("--round", required=True, type=int)
    parser.add_argument("--phase", default="initial_validation_parent_1")
    parser.add_argument("--label", default=None, help="output folder name")
    parser.add_argument(
        "--attempts",
        type=int,
        default=3,
        help="optimizer calls allowed before giving up (the engine retries too)",
    )
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
    """One evidence entry per completed run, dialogue first."""
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
    round_dir = experiment / "workflows" / (
        args.label or f"round_{args.round}_evolver_dryrun"
    )
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
    state = read_json(experiment / "workflows/cpe_state.json", {})
    initial = (state.get("initial_parent_validation_results") or [{}])[0]
    utility = (initial or {}).get("utility")

    training_parents = [
        {
            "parent_rank": 1,
            "workflow_id": seed.get("workflow_id"),
            "workflow": seed,
            "net_utility_on_current_training_batch": utility,
            "training_evidence": {"round": args.round, "training_runs": build_training_runs(completed)},
        }
    ]
    validation_champion = {
        "workflow_id": seed.get("workflow_id"),
        "workflow": seed,
        "utility": utility,
    }

    # The engine's own prompt builder, exactly as the launcher wires it: no
    # rubric, no critic review, nothing but this round's evidence.
    shared.CPE_TRAINING_PARENT_COUNT = 1
    prompt = launcher.build_initial_draft_cpe_workflow_evolution_prompt(
        training_parents, validation_champion, []
    )
    (round_dir / "evolution_prompt.md").write_text(prompt, encoding="utf-8")

    launcher.disable_thinking_for_direct_api_calls()

    class OptArgs:
        opt_model = "qwen3.8-27b"
        opt_base_url = "http://gpu6:18763/v1"
        opt_api_key = "EMPTY"

    # The engine rejects a candidate whose solver-visible text reproduces the
    # parent's and re-asks, so the dry run does the same: keep the first response
    # that actually carries a different policy.
    parent_text = str(seed.get("policy_text") or "").strip()
    candidate = None
    for attempt in range(1, args.attempts + 1):
        response = shared.interaction.local.optimizer_response(
            {
                "model": OptArgs.opt_model,
                "messages": [
                    {"role": "system", "content": "Return one concise valid JSON workflow object."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.5,
                "max_tokens": 3000,
                "response_format": {"type": "json_object"},
            },
            OptArgs(),
        )
        (round_dir / f"evolution_response_attempt_{attempt}.json").write_text(
            json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        text = str(
            response.get("interaction_policy") or response.get("policy_text") or ""
        ).strip()
        print(f"[attempt {attempt}] 策略 {len(text)} 字符，与父代相同: {text == parent_text}")
        if text and text != parent_text:
            candidate = response
            break
    if candidate is None:
        raise SystemExit(
            f"optimizer reproduced the parent policy in all {args.attempts} attempts"
        )
    (round_dir / "evolution_response.json").write_text(
        json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    policy = str(candidate.get("interaction_policy") or candidate.get("policy_text") or "")
    (round_dir / "policy.md").write_text(policy.strip() + "\n", encoding="utf-8")

    print("=" * 78)
    print("演化产物:", round_dir)
    print("=" * 78)
    print(policy)
    print("=" * 78)


if __name__ == "__main__":
    main()
