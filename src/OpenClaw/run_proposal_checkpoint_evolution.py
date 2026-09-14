"""Branch Proposal evolution from the best checkpoint of another experiment."""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from . import baseline as openclaw_baseline
    from . import run_evolution as workflow_evolution
    from . import run_local_rubric_evolution as local
    from . import run_proposal_rubric_evolution as proposal
except ImportError:
    import baseline as openclaw_baseline
    import run_evolution as workflow_evolution
    import run_local_rubric_evolution as local
    import run_proposal_rubric_evolution as proposal


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEEPSEEK_API_MODELS = {
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "deepseek-v4-flash-vision-exp",
}


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE entries without overriding the current process."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def normalize_forwarded_models(arguments: list[str]) -> list[str]:
    """Keep OpenClaw provider IDs separate from direct API model IDs."""
    normalized = list(arguments)
    index = 0
    while index < len(normalized):
        token = normalized[index]
        if token in {"--model", "--opt-model"}:
            if index + 1 >= len(normalized):
                raise ValueError(f"{token} requires a value")
            value = normalized[index + 1]
            if token == "--model" and value in DEEPSEEK_API_MODELS:
                normalized[index + 1] = f"deepseek/{value}"
            elif token == "--opt-model" and value.startswith("deepseek/"):
                normalized[index + 1] = value.split("/", 1)[1]
            index += 2
            continue
        if token.startswith("--model="):
            value = token.split("=", 1)[1]
            if value in DEEPSEEK_API_MODELS:
                normalized[index] = f"--model=deepseek/{value}"
        elif token.startswith("--opt-model="):
            value = token.split("=", 1)[1]
            if value.startswith("deepseek/"):
                normalized[index] = f"--opt-model={value.split('/', 1)[1]}"
        index += 1
    return normalized


def load_best_checkpoint(source_exp: Path, problem_id: str | None) -> tuple[str, dict]:
    source_exp = source_exp.resolve()
    config = workflow_evolution.read_json(source_exp / "config.json", {})
    source_problem = config.get("problem_id")
    resolved_problem = problem_id or source_problem
    if not resolved_problem:
        raise ValueError("Could not determine problem ID from --source-exp")
    if source_problem not in (None, resolved_problem):
        raise ValueError(
            f"Source experiment contains {source_problem}, not {resolved_problem}"
        )
    results_path = source_exp / "workflows" / "results.json"
    results = workflow_evolution.read_json(results_path, [])
    candidates = []
    for item in results:
        score = item.get("offline_score")
        report_value = item.get("selected_report")
        if not isinstance(score, (int, float)) or not report_value:
            continue
        report = Path(report_value).resolve()
        if report.is_file():
            candidates.append((float(score), int(item.get("round", 0)), item, report))
    if not candidates:
        raise RuntimeError(f"No scored checkpoint found in {results_path}")
    _, source_round, source, report = min(
        candidates, key=lambda value: (-value[0], value[1])
    )
    run_dir = report.parents[2]
    metadata = workflow_evolution.read_json(run_dir / "meta" / "run.json", {})
    if metadata.get("problem_id") not in (None, resolved_problem):
        raise ValueError("Best checkpoint metadata has a different problem ID")
    seed = {
        "round": 1,
        "problem_id": resolved_problem,
        "seed_reused": True,
        "seed_source": str(source_exp),
        "source_results": str(results_path.resolve()),
        "source_round": source_round,
        "source_node_id": source.get("best_node_id"),
        "selected_run_dir": str(run_dir),
        "selected_output_dir": str(run_dir / "output"),
        "selected_report": str(report),
        "offline_score": source.get("offline_score"),
        "offline_dimension_scores": source.get("offline_dimension_scores", {}),
        "candidate_promoted": None,
        "time": proposal.now(),
    }
    return resolved_problem, seed


def initialize_destination(
    destination: Path,
    source_exp: Path,
    problem_id: str,
    seed: dict,
) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    workflows = destination / "workflows"
    round_one = workflows / "round_1"
    round_one.mkdir(parents=True)
    shutil.copy2(local.DEFAULT_SEED_WORKFLOW, round_one / "prompt.md")
    local.save_rubric_bank(
        workflows / local.RUBRIC_BANK_FILENAME, local.new_rubric_bank()
    )
    proposal.save_semantic_memory(
        workflows / proposal.SEMANTIC_MEMORY_FILENAME,
        proposal.new_semantic_memory(),
    )
    workflow_evolution.write_json(workflows / "results.json", [seed])
    workflow_evolution.write_json(
        destination / "config.json",
        {
            "experiment_type": "proposal_mlevolve_rubric_search",
            "problem_id": problem_id,
            "source_experiment": str(source_exp.resolve()),
            "source_round": seed.get("source_round"),
            "source_node_id": seed.get("source_node_id"),
            "execute_seed_root": False,
            "semantic_deduplication": True,
            "progressive_widening": True,
            "top_k_exploitation": True,
            "patch_fusion": False,
            "proposal_operator_enabled": True,
            "react_operator_enabled": False,
            "operator_selection_before_rubric_evolution": True,
            "proposal_requires_react": False,
            "created_at": proposal.now(),
        },
    )


def validate_resume_destination(
    destination: Path, source_exp: Path, problem_id: str
) -> None:
    config = workflow_evolution.read_json(destination / "config.json", {})
    if config.get("experiment_type") != "proposal_mlevolve_rubric_search":
        raise ValueError("--exp is not a Proposal checkpoint experiment")
    if config.get("problem_id") != problem_id:
        raise ValueError("--exp problem ID does not match the source experiment")
    configured_source = Path(config.get("source_experiment", "")).resolve()
    if configured_source != source_exp.resolve():
        raise ValueError("--exp was initialized from a different source experiment")


def repair_transient_semantic_exhaustion(destination: Path) -> list[str]:
    """Unlock parents exhausted only because every optimizer API call failed."""
    workflows = destination / "workflows"
    graph_path = workflows / proposal.SEARCH_GRAPH_FILENAME
    graph = workflow_evolution.read_json(graph_path, {})
    if not graph:
        return []
    results = workflow_evolution.read_json(workflows / "results.json", [])
    completed_rounds = {
        int(item["round"])
        for item in results
        if isinstance(item.get("round"), int)
    }
    memory = workflow_evolution.read_json(
        workflows / proposal.SEMANTIC_MEMORY_FILENAME, {}
    )
    rejection_rounds = {
        int(item["round"])
        for item in memory.get("rejections", [])
        if isinstance(item.get("round"), int)
    }
    repaired = []
    for node in graph.get("nodes", {}).values():
        exhausted_round = node.get("semantic_exhausted_round")
        if not isinstance(exhausted_round, int):
            continue
        round_dir = workflows / f"round_{exhausted_round}"
        has_candidate = (round_dir / "candidate.json").is_file() or (
            round_dir / "semantic_signature.json"
        ).is_file()
        if (
            exhausted_round in completed_rounds
            or exhausted_round in rejection_rounds
            or has_candidate
        ):
            continue
        node.pop("semantic_exhausted", None)
        node.pop("semantic_exhausted_at", None)
        node.pop("semantic_exhausted_round", None)
        repaired.append(str(node.get("node_id")))
    if repaired:
        workflow_evolution.write_json(graph_path, graph)
    return repaired


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-exp", type=Path, required=True)
    parser.add_argument("--exp", type=Path)
    parser.add_argument("--problem_id")
    args, forwarded = parser.parse_known_args()
    if "--seed-root" in forwarded:
        raise ValueError("This wrapper selects the source checkpoint automatically")
    return args, forwarded


def main() -> None:
    args, forwarded = parse_args()
    load_env_file(REPO_ROOT / ".env")
    load_env_file(SCRIPT_DIR / ".env")
    forwarded = normalize_forwarded_models(forwarded)
    source_exp = args.source_exp.resolve()
    if not source_exp.is_dir():
        raise FileNotFoundError(f"Source experiment not found: {source_exp}")
    problem_id, seed = load_best_checkpoint(source_exp, args.problem_id)
    destination = (
        args.exp.resolve()
        if args.exp
        else REPO_ROOT
        / "openclaw_experiments"
        / (
            f"proposal_checkpoint_{openclaw_baseline.safe_path_component(problem_id)}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    )
    try:
        destination.relative_to(source_exp)
    except ValueError:
        pass
    else:
        raise ValueError("The new experiment must not be inside --source-exp")

    if destination.exists():
        validate_resume_destination(destination, source_exp, problem_id)
        print(f"Resuming Proposal checkpoint experiment: {destination}", flush=True)
    else:
        initialize_destination(destination, source_exp, problem_id, seed)
        print(f"Created Proposal checkpoint experiment: {destination}", flush=True)
        print(
            f"Imported source round {seed['source_round']} / "
            f"{seed.get('source_node_id')} with score {seed['offline_score']}",
            flush=True,
        )

    repaired = repair_transient_semantic_exhaustion(destination)
    if repaired:
        print(
            "Cleared transient optimizer-failure exhaustion for: "
            + ", ".join(repaired),
            flush=True,
        )

    command = [
        sys.executable,
        str(SCRIPT_DIR / "run_proposal_rubric_evolution.py"),
        "--problem_id",
        problem_id,
        "--exp",
        str(destination),
        *forwarded,
    ]
    subprocess.run(command, cwd=SCRIPT_DIR, check=True)


if __name__ == "__main__":
    main()
