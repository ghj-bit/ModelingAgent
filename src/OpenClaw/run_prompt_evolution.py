"""Preview OpenClaw workflow evolution without running the benchmark or judge."""

import argparse
import shutil
from datetime import datetime
from pathlib import Path

try:
    from .baseline import PROMPT_TEMPLATE_PATH, REPO_ROOT
    from .run_evolution import (
        ALLOWED_OPERATORS,
        MAX_OPERATORS_PER_MUTATION,
        apply_operator_insertions,
        append_question_strategies,
        assert_only_workflow_changed,
        existing_workflow_signatures,
        load_question_bank,
        new_experiment_path,
        previous_experiences,
        propose_insertion,
        read_json,
        split_required_workflow,
        write_json,
    )
except ImportError:
    from baseline import PROMPT_TEMPLATE_PATH, REPO_ROOT
    from run_evolution import (
        ALLOWED_OPERATORS,
        MAX_OPERATORS_PER_MUTATION,
        apply_operator_insertions,
        append_question_strategies,
        assert_only_workflow_changed,
        existing_workflow_signatures,
        load_question_bank,
        new_experiment_path,
        previous_experiences,
        propose_insertion,
        read_json,
        split_required_workflow,
        write_json,
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evolve only prompt.md's Required Workflow without benchmarking."
    )
    parser.add_argument("--max-rounds", "--max_rounds", type=int, default=5)
    parser.add_argument("--exp", help="Resume a specific prompt-preview experiment.")
    parser.add_argument("--opt-model", default="deepseek-v4-flash")
    parser.add_argument("--opt-api-key")
    parser.add_argument("--opt-base-url")
    return parser.parse_args()


def resolve_experiment(requested: str | None) -> tuple[Path, bool]:
    if requested:
        path = Path(requested).resolve()
        if (path / "workflows").is_dir():
            return path, True
        return new_experiment_path(str(path)), False
    prefix = REPO_ROOT / "openclaw_prompt_experiments" / "run"
    return new_experiment_path(str(prefix)), False


def initialize_experiment(experiment: Path, args) -> None:
    round_one = experiment / "workflows" / "round_1"
    round_one.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROMPT_TEMPLATE_PATH, round_one / "prompt.md")
    write_json(
        experiment / "config.json",
        {
            "max_rounds": args.max_rounds,
            "operators": list(ALLOWED_OPERATORS),
            "max_operators_per_mutation": MAX_OPERATORS_PER_MUTATION,
            "question_evolution": "incremental_deduplicated",
            "opt_model": args.opt_model,
            "benchmark_executed": False,
            "created_at": datetime.now().isoformat(),
        },
    )
    write_json(experiment / "workflows" / "question_bank.json", [])


def main() -> None:
    args = parse_args()
    if args.max_rounds < 1:
        raise ValueError("--max-rounds must be at least 1")

    experiment, resumed = resolve_experiment(args.exp)
    if not resumed:
        initialize_experiment(experiment, args)
        print(f"Created prompt-only evolution experiment: {experiment}")
    else:
        print(f"Resuming prompt-only evolution experiment: {experiment}")

    workflows = experiment / "workflows"
    for round_number in range(2, args.max_rounds + 1):
        round_dir = workflows / f"round_{round_number}"
        prompt_path = round_dir / "prompt.md"
        if prompt_path.is_file():
            print(f"Round {round_number} already exists; skipping")
            continue

        parent_round = round_number - 1
        parent_path = workflows / f"round_{parent_round}" / "prompt.md"
        if not parent_path.is_file():
            raise FileNotFoundError(f"Missing parent prompt: {parent_path}")
        parent_prompt = parent_path.read_text(encoding="utf-8")
        proposal = propose_insertion(
            parent_prompt,
            "Prompt-only preview: benchmark execution and judging were skipped.",
            None,
            previous_experiences(workflows),
            args,
            existing_workflow_signatures(workflows),
            None,
            load_question_bank(workflows),
        )
        evolved_prompt = apply_operator_insertions(
            parent_prompt, proposal["insertions"]
        )
        assert_only_workflow_changed(parent_prompt, evolved_prompt)

        round_dir.mkdir(parents=True, exist_ok=True)
        append_question_strategies(
            workflows,
            [item["question_strategy"] for item in proposal["insertions"]],
            round_number,
            parent_round,
        )
        prompt_path.write_text(evolved_prompt, encoding="utf-8")
        write_json(
            round_dir / "modification.json",
            {
                **proposal,
                "father_node": parent_round,
                "score": None,
                "benchmark_executed": False,
                "created_at": datetime.now().isoformat(),
            },
        )
        insertion_summary = ", ".join(
            f"{item['operator']} after step {item['after_step']}"
            for item in proposal["insertions"]
        )
        print(f"Round {round_number}: inserted {insertion_summary}")

    print("\nGenerated Required Workflows:")
    for prompt_path in sorted(workflows.glob("round_*/prompt.md")):
        prompt = prompt_path.read_text(encoding="utf-8")
        _, workflow, _ = split_required_workflow(prompt)
        print(f"\n[{prompt_path.parent.name}]\n{workflow.strip()}")
    print(f"\nExperiment: {experiment}")
    print("Benchmark and judge were not executed.")


if __name__ == "__main__":
    main()
