import json
import os
import ast
import argparse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, Set

from structural_coherency import StructuralCoherencyJudger
from scoring_decomposition import ScoringDecompositionJudger
from modeling_groundedness import ModelingGroundednessJudger
from data_groundedness import DataGroundednessJudger
from analysis_groundedness import AnalysisGroundednessJudger
from innovativeness import InnovativenessJudger

AVAILABLE_JUDGERS = (
    "structural_coherency",
    "scoring_decomposition",
    "modeling_groundedness",
    "data_groundedness",
    "analysis_groundedness",
    "innovativeness",
)


def result_file_path(output_dir: str | Path, gold_id: str) -> Path:
    gold_id = gold_id.replace("?", "")
    safe_id = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", gold_id).rstrip(" .")
    return Path(output_dir) / f"{safe_id or 'problem'}.json"

class MainJudger:
    def __init__(self, judger_names=None):
        judger_types = {
            "structural_coherency": StructuralCoherencyJudger,
            "scoring_decomposition": ScoringDecompositionJudger,
            "modeling_groundedness": ModelingGroundednessJudger,
            "data_groundedness": DataGroundednessJudger,
            "analysis_groundedness": AnalysisGroundednessJudger,
            "innovativeness": InnovativenessJudger,
        }
        selected = tuple(judger_names or AVAILABLE_JUDGERS)
        unknown = sorted(set(selected) - set(AVAILABLE_JUDGERS))
        if unknown:
            raise ValueError("Unknown judgers: " + ", ".join(unknown))
        self.judgers = {name: judger_types[name]() for name in selected}
        
        # Judgers that use role-based evaluation
        self.role_based_judgers = {
            "modeling_groundedness",
            "data_groundedness", 
            "analysis_groundedness",
            "innovativeness"
        }
        
    def run_judger(self, judger_name: str, writing: str, roles: list = None, grading_points: list = None) -> Dict[str, Any]:
        try:
            judger = self.judgers[judger_name]
            print(f"[Judge] Starting {judger_name}", flush=True)
            
            # Handle role-based judgers
            if judger_name in self.role_based_judgers and roles:
                results = [None] * len(roles)

                def run_role(index: int, role: dict):
                    print(
                        f"[Judge] {judger_name}: role {index + 1}/{len(roles)} "
                        f"({role.get('name', 'unknown')})",
                        flush=True,
                    )
                    result = judger.run(writing, role=role)
                    result["role"] = role
                    return index, result

                with ThreadPoolExecutor(max_workers=len(roles)) as executor:
                    futures = [
                        executor.submit(run_role, index, role)
                        for index, role in enumerate(roles)
                    ]
                    for future in as_completed(futures):
                        index, result = future.result()
                        results[index] = result

                return {
                    "role_based_results": results,
                    "aggregated_score": sum(r.get("calculated_overall", 0) for r in results) / len(results)
                }
            
            # Handle non-role-based judgers
            if judger_name == "scoring_decomposition":
                return judger.run(writing, grading_points)
            return judger.run(writing)
            
        except Exception as e:
            print(f"Error in {judger_name}: {str(e)}")
            return {
                "error": str(e),
                "status": "failed",
                "judger": judger_name
            }
    
    def get_existing_results(self, output_dir: str, gold_id: str) -> Dict[str, Any]:
        """Read existing judgement results if they exist"""
        output_file = result_file_path(output_dir, gold_id)
        if output_file.exists():
            try:
                with open(output_file, encoding="utf-8") as f:
                    results = json.load(f)
                return results.get("judgements", {})
            except (OSError, UnicodeError, json.JSONDecodeError):
                return {}
        return {}

    def get_missing_judgers(self, existing_results: Dict[str, Any]) -> Set[str]:
        """Determine which judgers need to be run"""
        missing = set(self.judgers.keys())
        for judger_name, result in existing_results.items():
            # Only consider result valid if it exists and has no error
            if judger_name in self.judgers and result and "error" not in result:
                missing.remove(judger_name)
        return missing
    
    def judge(self, output_dir: str, gold_id: str, writing: str, grading_points: list, roles: list = None) -> Dict[str, Any]:
        # Initialize results structure
        results = {
            "gold_id": gold_id,
            "judgements": {},
            "metadata": {
                "success_count": 0,
                "failed_count": 0,
                "failed_judgers": [],
                "skipped_count": 0,
                "skipped_judgers": []
            }
        }
        
        # Get existing results
        existing_results = self.get_existing_results(output_dir, gold_id)
        missing_judgers = self.get_missing_judgers(existing_results)
        
        print(f"Missing judgers for {gold_id}: {missing_judgers}")
        
        # Add existing valid results to our results
        for judger_name, result in existing_results.items():
            if judger_name in self.judgers and judger_name not in missing_judgers:
                results["judgements"][judger_name] = result
                results["metadata"]["skipped_count"] += 1
                results["metadata"]["skipped_judgers"].append(judger_name)
        
        if not missing_judgers:
            print(f"All judgements already exist for {gold_id}")
            return results
        
        # Run only missing judgers in parallel
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_judger = {
                executor.submit(
                    self.run_judger, 
                    name, 
                    writing, 
                    roles if name in self.role_based_judgers else None,
                    grading_points if name == "scoring_decomposition" else None
                ): name
                for name in missing_judgers
            }
            
            for future in as_completed(future_to_judger):
                name = future_to_judger[future]
                try:
                    result = future.result()
                    if "error" in result:
                        results["metadata"]["failed_count"] += 1
                        results["metadata"]["failed_judgers"].append(name)
                    else:
                        results["metadata"]["success_count"] += 1
                    results["judgements"][name] = result
                except Exception as e:
                    print(f"Error in {name}: {str(e)}")
                    results["judgements"][name] = {"error": str(e)}
                    results["metadata"]["failed_count"] += 1
                    results["metadata"]["failed_judgers"].append(name)

                with open(result_file_path(output_dir, gold_id), "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)
                print(
                    f"[Judge] Finished {name}; checkpoint saved "
                    f"({len(results['judgements'])}/{len(self.judgers)})",
                    flush=True,
                )
        
        with open(result_file_path(output_dir, gold_id), "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        return results

def process_gold_id(args):
    gold_id, data, output_dir, judger = args
    if "writing" not in data:  # Skip if no writing to evaluate
        return
    
    writing = data["writing"]
    criteria = data["criteria"]
    grading_points = criteria.get("decomposition", {}).get("grading_points", [])
    roles = criteria.get("eval_roles", [])
    
    print(f"Evaluating {gold_id}...")
    results = judger.judge(output_dir, gold_id, writing, grading_points, roles)
    print(f"Completed {gold_id} - Success: {results['metadata']['success_count']}, "
          f"Failed: {results['metadata']['failed_count']}, "
          f"Skipped: {results['metadata']['skipped_count']}")
    return gold_id, results

def evaluate_workspace(
    problem_id: str, workspace: str, output_dir: str = None, judger_names=None
) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    workspace_path = Path(workspace).resolve()
    if not workspace_path.is_dir():
        raise ValueError(f"Workspace directory not found: {workspace_path}")

    report_files = sorted(workspace_path.glob("*.md"))
    if not report_files:
        raise ValueError(f"No Markdown reports found in: {workspace_path}")

    with open(repo_root / "data" / "modeling_data_final.json", encoding="utf-8") as f:
        criterias = json.load(f)
    if problem_id not in criterias:
        raise ValueError(f"Unknown problem ID: {problem_id}")

    writing_parts = []
    for report_file in report_files:
        writing_parts.append(
            f"# Submitted file: {report_file.name}\n\n"
            + report_file.read_text(encoding="utf-8")
        )
    writing = "\n\n---\n\n".join(writing_parts)

    if output_dir:
        output_path = Path(output_dir).resolve()
    else:
        model_name = workspace_path.parent.name
        output_path = (
            repo_root
            / "output_judge"
            / "ModelTool"
            / model_name
            / workspace_path.name
        )
    output_path.mkdir(parents=True, exist_ok=True)

    criteria = criterias[problem_id]
    grading_points = criteria.get("decomposition", {}).get("grading_points", [])
    roles = criteria.get("eval_roles", [])

    print(f"Evaluating {problem_id} from {workspace_path}")
    print("Submitted reports: " + ", ".join(path.name for path in report_files))
    results = MainJudger(judger_names).judge(
        str(output_path), problem_id, writing, grading_points, roles
    )
    result_path = result_file_path(output_path, problem_id)
    print(
        f"Completed {problem_id} - Success: {results['metadata']['success_count']}, "
        f"Failed: {results['metadata']['failed_count']}, "
        f"Skipped: {results['metadata']['skipped_count']}"
    )
    print(f"Judgement saved to: {result_path}")


def run_batch():
    for model, level in zip(["deepseek-v4-flash"], ["ModelAgent"]):
        try:
            # Load problem data
            with open("../../data/modeling_data_final.json") as f:
                criterias = json.load(f)
            with open(f"../../output_writings/{level}/{model}/solutions_metadata.json") as f:
                writings = json.load(f)
            
            output_dir = f"../../output_judge/{level}/{model}"
            os.makedirs(output_dir, exist_ok=True)
            all_data = {}
            for gold_id, criteria in criterias.items():
                    all_data[gold_id] = {
                        "criteria": criteria,
                    }
            for gold_id, writing in writings.items():
                    if "writing" not in writing:
                        continue
                    all_data[gold_id]["writing"] = writing
            
            print(len(all_data))
            
            judger = MainJudger()
            
            # Process problems in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                args = [(gold_id, data, output_dir, judger) for gold_id, data in all_data.items()]
                results = list(executor.map(process_gold_id, args))
        except:
            continue


def main():
    parser = argparse.ArgumentParser(description="Evaluate ModelingBench reports.")
    parser.add_argument(
        "problem_id", nargs="?", help="Evaluate only this problem ID."
    )
    parser.add_argument(
        "--workspace",
        help="Tool Agent run directory containing one or more Markdown reports.",
    )
    parser.add_argument(
        "--output-dir",
        help="Optional directory for the judgement JSON output.",
    )
    parser.add_argument(
        "--judgers",
        nargs="+",
        choices=AVAILABLE_JUDGERS,
        help="Run only the selected evaluation dimensions.",
    )
    args = parser.parse_args()

    if args.problem_id or args.workspace or args.output_dir:
        if not args.problem_id or not args.workspace:
            parser.error("problem_id and --workspace must be provided together")
        evaluate_workspace(
            args.problem_id, args.workspace, args.output_dir, args.judgers
        )
        return

    run_batch()

if __name__ == "__main__":
    main()
