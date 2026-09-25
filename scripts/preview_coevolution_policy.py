"""Preview the policy the co-evolution arm would evolve from one round.

Solves nothing.  It reads a completed round of an existing experiment, assembles
exactly the evolution prompt the co-evolution arm would assemble -- the
from-scratch solver framing, the parent's rollouts on that batch, and the
critic's rubric review appended as one extra evidence node -- calls the evolver
once, and writes the candidate policy next to a readable rendering of it.

Two properties matter and are why this is a separate script rather than a flag
on ``critic_evolve_dryrun.py``:

* It never writes into the experiment it reads.  A sandbox is built from that
  experiment's state files (the run data is symlinked, not copied), and every
  artifact lands there, so a live run is untouched.
* It renders the *co-evolution* arm's prompt, not the draft arm's: the
  from-scratch launcher's hooks are laid down first, so the prompt's
  ``{solver_source}`` / ``{solver_start}`` sentences say the solver starts from
  the problem statement alone.

    python scripts/preview_coevolution_policy.py \\
        --source-experiment openclaw_experiments/evolve_exp/claude_scratch_evolve_r10 \\
        --round 1 --phase initial_train_parent_1 \\
        --out openclaw_experiments/evolve_exp/_coev_preview_from_r10_r1
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import critic_evolve_dryrun as dryrun  # noqa: E402 - reuses its evidence assembly unchanged

from src.OpenClaw import interaction_strategy_critic as critic  # noqa: E402
from src.OpenClaw import (  # noqa: E402
    run_substantive_interaction_workflow_evolution as shared,
)
from src.OpenClaw import (  # noqa: E402
    run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base,
)
from src.OpenClaw import (  # noqa: E402
    run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch,
)

OPT_MODEL = os.environ.get("PREVIEW_OPT_MODEL", "qwen3.8-27b")
OPT_BASE_URL = os.environ.get("PREVIEW_OPT_BASE_URL", "http://gpu6:18763/v1")
OPT_API_KEY = os.environ.get("PREVIEW_OPT_API_KEY", "EMPTY")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-experiment", required=True, type=Path)
    parser.add_argument("--round", required=True, type=int)
    parser.add_argument("--phase", default="initial_train_parent_1")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--label", default="preview")
    return parser.parse_args()


def build_sandbox(source: Path, out: Path) -> None:
    """Mirror the state files the arm reads; symlink the run data it only reads.

    The critic writes ``critic_review.{json,md}`` under
    ``<experiment>/workflows/round_N/``, so pointing the arm at the source
    experiment would drop files into a round a live run may still own.
    """
    (out / "workflows").mkdir(parents=True, exist_ok=True)
    for name in ("config.json", "initial_interaction_workflows.json"):
        shutil.copy2(source / name, out / name)
    for state in (source / "workflows").glob("*.json"):
        shutil.copy2(state, out / "workflows" / state.name)
    link = out / "cpe_evaluations"
    if not link.exists():
        link.symlink_to(source / "cpe_evaluations")


def readable_candidate(candidate: dict) -> str:
    """The evolver's answer as something a human reads, not a JSON blob."""
    lines = [
        "# 演化出的候选交互策略",
        "",
        f"- **名称**：{candidate.get('name', '')}",
        f"- **目的**：{candidate.get('purpose', '')}",
        f"- **演化模式**：{candidate.get('evolution_mode', '')}",
        f"- **最大交换次数**：{candidate.get('maximum_expert_interactions', '')}",
        f"- **终止条件**：{candidate.get('termination_condition', '')}",
        "",
        "## 改动组件",
        "",
    ]
    for item in candidate.get("changed_components") or []:
        lines.append(f"- {item}")
    lines += [
        "",
        "## 演化理由",
        "",
        str(candidate.get("evolution_rationale") or ""),
        "",
        "## 完整策略文本",
        "",
        "```markdown",
        str(candidate.get("interaction_policy") or "").rstrip(),
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    source = args.source_experiment.resolve()
    out = args.out.resolve()
    build_sandbox(source, out)

    checkpoint = dryrun.read_json(
        out / "cpe_evaluations" / f"round_{args.round}" / args.phase
        / "workflows" / f"round_{args.round}" / "evaluation_checkpoint.json",
        {},
    )
    completed = checkpoint.get("completed") or {}
    if not completed:
        raise SystemExit(f"No completed runs in round {args.round} / {args.phase}")

    seed = dryrun.read_json(out / "initial_interaction_workflows.json", [{}])
    seed = seed[0] if isinstance(seed, list) else seed
    config = dryrun.read_json(out / "config.json", {})
    phase_result = dryrun.read_json(
        out / "cpe_evaluations" / f"round_{args.round}" / args.phase
        / "workflows" / f"round_{args.round}" / "result.json",
        {},
    )
    state = dryrun.read_json(out / "workflows" / "cpe_state.json", {})
    champion = (state.get("initial_parent_validation_results") or [{}])[0]

    # The evidence field is the parent's score *on this batch*, which is what the
    # engine hands the optimizer; the validation utility is a different number on
    # a different split.
    train_utility = phase_result.get("utility")
    validation_utility = (champion or {}).get("utility")

    runs = dryrun.build_training_runs(completed)
    training_parents = [
        {
            "parent_rank": 1,
            "workflow_id": seed.get("workflow_id"),
            "workflow": seed,
            "net_utility_on_current_training_batch": train_utility,
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

    print(f"[preview] round {args.round} / {args.phase}: {len(runs)} run(s), "
          f"train utility {train_utility}, validation utility {validation_utility}", flush=True)

    model, api_key, base_url, timeout = critic.critic_credentials(
        mmbench_judge={
            "model": os.environ.get("CRITIC_MODEL") or "deepseek-flash",
            "base_url": os.environ.get("CRITIC_BASE_URL") or "https://api.deepseek.com",
            "api_key": os.environ.get("CRITIC_API_KEY"),
        }
    )
    print(f"[preview] critic: {model} at {base_url}", flush=True)
    review = critic.review_training_parents(
        training_parents,
        experiment=out,
        model=model,
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
    )
    block = critic.render_critic_block(review)

    shared.CPE_TRAINING_PARENT_COUNT = 1
    # The arm under preview: without these hooks the prompt would describe a
    # solver that was handed a planning draft.
    scratch.patch_sibling_launcher()
    prompt = base.build_initial_draft_cpe_workflow_evolution_prompt(
        training_parents, validation_champion, []
    )
    prompt_with_critic = prompt + "\n\n" + block

    round_dir = out / "workflows" / args.label
    round_dir.mkdir(parents=True, exist_ok=True)
    (round_dir / "evolution_prompt.md").write_text(prompt_with_critic, encoding="utf-8")
    (round_dir / "critic_block.md").write_text(block, encoding="utf-8")

    base.disable_thinking_for_direct_api_calls()

    class OptArgs:
        opt_model = OPT_MODEL
        opt_base_url = OPT_BASE_URL
        opt_api_key = OPT_API_KEY

    print(f"[preview] calling the evolver: {OPT_MODEL} at {OPT_BASE_URL}", flush=True)
    candidate = shared.interaction.local.optimizer_response(
        {
            "model": OPT_MODEL,
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
    (round_dir / "candidate_policy.md").write_text(
        readable_candidate(candidate), encoding="utf-8"
    )

    print("=" * 78)
    print("critic 打分:", json.dumps(
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
    print(readable_candidate(candidate))
    print("=" * 78)
    print("产物:", round_dir)


if __name__ == "__main__":
    main()
