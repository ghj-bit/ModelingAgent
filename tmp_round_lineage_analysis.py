import json
import pathlib
import re

b = pathlib.Path(r"D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_workflow_clean_baseline_refinement_20260914_140527")
results = json.loads((b / "workflows/results.json").read_text(encoding="utf-8"))

print("ROUNDS")
for node in results:
    n = int(node["round"])
    workflow = json.loads((b / "workflows" / f"round_{n}" / "workflow.json").read_text(encoding="utf-8"))
    changed = workflow.get("changed_components") or []
    rationale = re.sub(r"\s+", " ", str(workflow.get("evolution_rationale", ""))).strip()
    problem_scores = {
        item["problem_id"]: item["average_score"]
        for item in node.get("problem_results", [])
    }
    exchanges = {
        item["problem_id"]: item.get("interaction_receipt", {}).get("exchange_count")
        for item in node.get("problem_results", [])
    }
    print(json.dumps({
        "round": n,
        "utility": node["utility"],
        "name": workflow.get("name"),
        "evolution_operator": workflow.get("evolution_operator", node.get("evolution_operator")),
        "seed_operator": workflow.get("seed_operator"),
        "evidence_rounds": workflow.get("evidence_rounds"),
        "max_exchanges": workflow.get("max_exchanges"),
        "action_types": [action.get("action_type") for action in workflow.get("actions", [])],
        "changed_components": changed,
        "rationale": rationale[:700],
        "problem_scores": problem_scores,
        "actual_exchanges": exchanges,
    }, ensure_ascii=True))

print("TOP")
for node in sorted(results, key=lambda item: (-float(item["utility"]), int(item["round"])))[:8]:
    print(node["round"], node["utility"])
print("BOTTOM")
for node in sorted(results, key=lambda item: (float(item["utility"]), int(item["round"])))[:8]:
    print(node["round"], node["utility"])
