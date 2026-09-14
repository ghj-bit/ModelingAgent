"""Reweight saved workflow scores without rerunning reports or Judge."""

from __future__ import annotations

import argparse
import copy
import json
import shutil
from datetime import datetime
from pathlib import Path

try:
    from . import run_substantive_interaction_workflow_evolution as workflow
except ImportError:
    import run_substantive_interaction_workflow_evolution as workflow


WEIGHTS = {
    "analysis_groundedness": 1.0,
    "modeling_groundedness": 1.0,
    "scoring_decomposition": 1.0,
    "structural_coherency": 1.0,
}


def reweight_run(run: dict) -> None:
    for repetition in run.get("repetitions", []):
        reweight_run(repetition)
    run["average_score"] = workflow.interaction.objective_score(run["dimension_scores"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp", required=True, type=Path)
    args = parser.parse_args()
    experiment = args.exp.resolve()
    workdir = experiment / "workflows"
    results_path = workdir / "results.json"
    original = results_path.read_bytes()
    results = json.loads(original)
    config_path = experiment / "config.json"
    config = workflow.workflow_evolution.read_json(config_path, {})
    workflow.interaction.OBJECTIVE_WEIGHTS = dict(WEIGHTS)
    updated = copy.deepcopy(results)
    comparison = []
    for node in updated:
        old = node["utility"]
        for run in node["problem_results"]:
            reweight_run(run)
        node["utility"] = sum(run["average_score"] for run in node["problem_results"]) / len(node["problem_results"])
        comparison.append({
            "round": node["round"],
            "previous_utility": old,
            "weighted_utility": node["utility"],
            "average_dimension_scores": node["average_dimension_scores"],
        })
    by_round = {node["round"]: node for node in updated}
    for node in updated:
        if "utility_delta" in node:
            reference = by_round.get(node.get("parent_round"))
            node["utility_delta"] = node["utility"] - reference["utility"] if reference else None

    backup = experiment / "utility_recalculation_backups" / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    targets = [config_path, results_path,
               workdir / "round_problem_dimension_scores.json",
               workdir / "round_problem_dimension_scores.xlsx",
               workdir / "weighted_utility_recalculation.json"]
    targets += [workdir / f"round_{node['round']}" / "result.json" for node in updated]
    for path in targets:
        if path.is_file():
            target = backup / path.relative_to(experiment)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    if results_path.read_bytes() != original:
        raise RuntimeError("Results changed during recalculation; rerun using the latest results")
    config["utility_weights"] = dict(WEIGHTS)
    config["utility_normalization"] = "sum(weight * dimension_score) / sum(weights); mean across problems"
    write_json = workflow.workflow_evolution.write_json
    write_json(config_path, config)
    write_json(results_path, updated)
    for node in updated:
        write_json(workdir / f"round_{node['round']}" / "result.json", node)
    workflow.interaction.write_score_summary(workdir / "round_problem_dimension_scores.json", experiment, updated)
    workflow.interaction.write_score_workbook(workdir / "round_problem_dimension_scores.xlsx", experiment, updated)
    write_json(workdir / "weighted_utility_recalculation.json", {
        "generated_at": datetime.now().isoformat(),
        "weights": WEIGHTS,
        "weight_sum": sum(WEIGHTS.values()),
        "backup": str(backup),
        "rounds": comparison,
    })
    print(json.dumps({"rounds": comparison, "backup": str(backup)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
