"""Generate an offline preview of the workflow optimizer prompt for inspection."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import run_substantive_interaction_workflow_evolution as evolution


DEFAULT_EXPERIMENT = (
    evolution.REPO_ROOT
    / "openclaw_experiments"
    / "interaction_workflow_substantive_20260909_214301"
)


def short_preview(content: str) -> str:
    """Use a deterministic offline stand-in for the runtime LLM summary."""
    return re.sub(r"\s+", " ", content).strip()[:50]


def preview_evidence(parents: list[dict], problems: dict) -> list[dict]:
    context = {
        item["problem_id"]: item
        for item in evolution.interaction.optimizer_problem_context(problems)
    }
    evidence = []
    for rank, node in enumerate(parents, 1):
        validation_runs = []
        for run in node.get("problem_results", []):
            artifacts = evolution.optimizer_parent_artifacts(Path(run["run_dir"]))
            for artifact in artifacts:
                if artifact["artifact_type"] == "interaction_added_content":
                    artifact["content"] = short_preview(artifact["content"])
                    artifact["artifact_type"] = "interaction_added_content_summary"
            judge = evolution.interaction.read_raw_judge_result(
                Path(str(run.get("judge_result", "")))
            )
            validation_runs.append(
                {
                    **context[run["problem_id"]],
                    "artifacts": artifacts,
                    "non_full_role_evaluations": (
                        evolution.substantive.non_full_role_evaluations(judge)
                    ),
                }
            )
        evidence.append(
            {
                "rank": rank,
                "round": node["round"],
                "utility": node["utility"],
                "workflow": evolution.optimizer_workflow(node["workflow"]),
                "validation_runs": validation_runs,
            }
        )
    return evidence


def json_after(prompt: str, label: str):
    value, _ = json.JSONDecoder().raw_decode(prompt.split(label, 1)[1].lstrip())
    return value


def validate_filtered_prompt(prompt: str) -> None:
    if "Fixed interaction rubric:" in prompt or "Interaction Rubric" in prompt:
        raise AssertionError("Interaction rubric leaked into optimizer input")
    if "Evolve one new human-expert dialogue operator" in prompt:
        raise AssertionError("Operator-evolution prompt leaked into workflow prompt")
    if "five consecutive" in prompt or "historical_best_utility" in prompt:
        raise AssertionError("Programmatic stagnation rule leaked into workflow prompt")
    primary = json_after(prompt, "Primary parent workflow:")
    secondary = json_after(prompt, "Secondary parent workflow:")
    evidence = json_after(prompt, "Prior validation evidence:")
    for candidate in (primary, secondary):
        if candidate is None:
            continue
        for key in (
            "purpose",
            "changed_components",
            "mutation_rationale",
            "crossover_rationale",
        ):
            if key in candidate:
                raise AssertionError(f"Workflow field leaked into optimizer input: {key}")
    for node in evidence:
        for key in (
            "purpose",
            "changed_components",
            "mutation_rationale",
            "crossover_rationale",
        ):
            if key in node["workflow"]:
                raise AssertionError(f"Evidence workflow field leaked into input: {key}")
        for run in node["validation_runs"]:
            artifact_types = {
                artifact["artifact_type"] for artifact in run["artifacts"]
            }
            unexpected = artifact_types - {
                "expert_interaction",
                "interaction_added_content_summary",
            }
            if unexpected:
                raise AssertionError(
                    "Redundant interaction artifacts leaked into optimizer input: "
                    + ", ".join(sorted(unexpected))
                )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, default=DEFAULT_EXPERIMENT)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--parent-similarity-threshold",
        type=float,
        default=evolution.DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD,
    )
    args = parser.parse_args()
    experiment = args.experiment.resolve()
    results = evolution.workflow_evolution.read_json(
        experiment / "workflows" / "results.json", []
    )
    parents = evolution.select_diverse_workflow_nodes(
        results, 2, args.parent_similarity_threshold
    )
    if not parents:
        raise ValueError("No evaluated workflow is available for prompt preview")
    problems = evolution.baseline.load_problems()
    evidence = preview_evidence(parents, problems)
    secondary = parents[1] if len(parents) > 1 else None
    operator = "workflow_crossover_mutation" if secondary else "workflow_mutation"
    prompt = evolution.build_workflow_evolution_prompt(
        parents[0], secondary, evidence, operator
    )
    validate_filtered_prompt(prompt)
    output = (
        args.output.resolve()
        if args.output
        else experiment / "workflows" / "evolution_prompt_preview.md"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(prompt, encoding="utf-8")
    metadata = {
        "preview_only": True,
        "optimizer_called": False,
        "parent_rounds": [item["round"] for item in parents],
        "output": str(output),
        "note": "interaction_added_content uses a deterministic 50-character preview; runtime uses its configured LLM summarizer.",
    }
    output.with_suffix(".json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Prompt preview: {output}")
    print("Parent rounds: " + ", ".join(map(str, metadata["parent_rounds"])))
    print("Filter validation passed; no optimizer or Judge API was called.")


if __name__ == "__main__":
    main()
