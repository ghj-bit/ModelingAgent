"""Run a cost/delay-aware innovation refinement from the Round 6 treatment."""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

try:
    from . import baseline as openclaw_baseline
    from . import run_judge_stability as judge_stability
    from . import run_local_rubric_evolution as local
    from . import run_evolution as workflow_evolution
except ImportError:
    import baseline as openclaw_baseline
    import run_judge_stability as judge_stability
    import run_local_rubric_evolution as local
    import run_evolution as workflow_evolution


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_SOURCE_RESULT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "innovation_round6_20260902_093436"
    / "result.json"
)
BASE_PROMPT = SCRIPT_DIR / "prompt_modelingbench_baseline.md"
WORKFLOW_PATTERN = re.compile(
    r"(?ms)(^## Required Workflow\s*\n)(.*?)(?=^## |\Z)"
)

REFINEMENT_WORKFLOW = """\
1. Read `{{LOGS_DIR}}/inheritance_manifest.json`, every inherited stage summary, `{{RESULTS_DIR}}/parent_solution_report.md`, and the inherited adaptive-staffing code/results. Preserve all validated answers to the original problem; this is a targeted refinement, not a complete restart.
2. Audit the inherited adaptive-policy claim. Treat instantaneous relief activation, cost-free switching, and the selected scalar weight as unresolved limitations. Reproduce the inherited headline points before changing the policy model.
3. Extend the operational model with activation delay, a fixed burden per activation, relief deployment time, and minimum deployment duration. Separate supplied data from explicitly labeled management-preference and stress-test parameters. Do not invent observed costs.
4. Replace selection by one arbitrary scalar weight with constrained multi-objective selection: minimize relief deployment and activation burden subject to conservative confidence-bound compliance with the original waiting-time and queue-length goals. Report a Pareto frontier across delay and switching-burden values so management can select a policy without pretending one unknown cost ratio is authoritative.
5. Implement a reproducible safe policy-search algorithm using common random numbers and sequential confidence-bound elimination. Compare its selected policies, feasibility decisions, simulation budget, and wall time against exhaustive grid search. Include fixed staffing, queue-only, inherited workload-index, and cost/delay-aware policies.
6. Establish one modest technical result: state and justify a structural proposition explaining when zero-delay on-demand relief reproduces fixed-two-teller service, identify precisely which delay/cost assumptions break that equivalence, and test the proposition with deterministic edge cases plus simulation. Do not claim a new queueing theorem beyond what the evidence supports.
7. Validate with repeated simulations, confidence intervals, activation-delay sensitivity, switching-burden sensitivity, demand/service-variability regimes, and ablations. Explicitly test whether workload state provides value over queue length; report a negative result if it does not.
8. Update affected stage summaries and regenerate the complete report. Preserve the management letter and every original deliverable. Add concise sections named `Cost-and-Delay-Aware Contribution`, `Constrained Policy Selection`, `Sequential Safe Search`, `Structural Proposition and Boundary`, and `Regression and Falsification`.

"""

EVIDENCE_CONTRACT = """## Cost-Aware Innovation Evidence Contract

Create and use all of the following authoritative artifacts:

- `{{CODE_DIR}}/cost_aware_adaptive_staffing.py`: executable constrained search and validation.
- `{{RESULTS_DIR}}/cost_delay_policy_results.json`: seeds, parameter grids, confidence bounds, feasibility decisions, baselines, selected policies, ablations, and regime tests.
- `{{RESULTS_DIR}}/policy_frontier.csv`: non-dominated service/resource policies across delay and switching burden.
- `{{RESULTS_DIR}}/safe_search_comparison.json`: sequential elimination versus exhaustive-grid agreement, simulation budget, and runtime.
- `{{RESULTS_DIR}}/technical_contribution.md`: proposition, assumptions, proof or justification, deterministic tests, empirical checks, failure boundary, and restrained novelty claim.

Acceptance conditions:

1. No policy may be called feasible merely because a point estimate passes. Use a stated one-sided confidence rule for both original service goals.
2. Do not convert an invented switching burden into dollars or present it as observed data. Show decisions over a range.
3. The sequential search must be executable and compared against exhaustive search; renaming grid search is insufficient.
4. The final report must quote generated numerical evidence and explain whether the new mechanism survives realistic activation delay and switching burden.
5. Preserve or explicitly retract the inherited 58% labor-reduction claim after including activation burden and delay.

"""


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_prompt_template(destination: Path) -> None:
    base = BASE_PROMPT.read_text(encoding="utf-8")
    rendered, count = WORKFLOW_PATTERN.subn(
        lambda match: match.group(1) + REFINEMENT_WORKFLOW,
        base,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Base prompt has no unique Required Workflow section")
    rendered = rendered.replace(
        "## Final Report Contract", EVIDENCE_CONTRACT + "## Final Report Contract", 1
    )
    destination.write_text(rendered, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Refine the Round 6 adaptive-staffing treatment with switching cost, "
            "activation delay, constrained selection, and safe sequential search."
        )
    )
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--judge-trials", type=int, default=3)
    parser.add_argument("--agent")
    parser.add_argument("--openclaw-command")
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--source-result", type=Path, default=DEFAULT_SOURCE_RESULT)
    parser.add_argument("--exp", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.judge_trials < 1:
        raise ValueError("--judge-trials must be positive")

    source_result_path = args.source_result.resolve()
    source = read_json(source_result_path)
    parent_report = Path(source["final_report"]).resolve()
    parent_run = Path(source["run_dir"]).resolve()
    parent_output = parent_run / "output"
    parent_judge_value = source.get("judge_result")
    parent_judge = Path(parent_judge_value).resolve() if parent_judge_value else None
    for label, path in (
        ("Source output", parent_output),
        ("Source report", parent_report),
    ):
        if not path.exists():
            raise FileNotFoundError(f"{label} is missing: {path}")
    if not args.skip_judge and not args.prepare_only:
        if parent_judge is None or not parent_judge.is_file():
            raise FileNotFoundError(f"Source Judge result is missing: {parent_judge}")

    problem_id = str(source.get("problem_id") or "2013_Bank_Service_Problem")
    problems = openclaw_baseline.load_problems()
    if problem_id not in problems:
        raise ValueError(f"Unknown problem ID: {problem_id}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment = (
        args.exp.resolve()
        if args.exp
        else REPO_ROOT / "openclaw_experiments" / f"cost_aware_innovation_{timestamp}"
    )
    experiment.mkdir(parents=True, exist_ok=False)
    prompt_template = experiment / "prompt.md"
    build_prompt_template(prompt_template)

    run_args = SimpleNamespace(
        output_root=str(experiment / "runs"),
        model=args.model,
        prompt_template=str(prompt_template),
        react_role_prompts={},
        inherit_output_dir=str(parent_output),
        openclaw_command=args.openclaw_command,
        agent=args.agent,
        thinking=args.thinking,
        timeout=args.timeout,
        skip_judge=args.skip_judge or args.prepare_only,
        external_verifier=False,
    )
    if args.prepare_only:
        run_dir, output_dir, prompt_path = local.prepare_inherited_run(
            problem_id,
            problems[problem_id],
            Path(run_args.output_root),
            args.model,
            prompt_template,
            {},
            parent_output,
        )
        result = {
            "run_dir": run_dir,
            "prompt": prompt_path,
            "final_report": output_dir / "results" / "solution_report.md",
            "judge_result": None,
            "average_score": None,
        }
    else:
        result = local.run_inherited_problem(problem_id, problems[problem_id], run_args)

    parent_dimensions = None
    parent_score = source.get("average_score")
    if parent_judge and parent_judge.is_file():
        parent_dimensions = workflow_evolution.judge_dimension_scores(parent_judge)
        parent_score = sum(parent_dimensions.values()) / len(parent_dimensions)
    summary = {
        "experiment_type": "cost_delay_aware_innovation_treatment",
        "problem_id": problem_id,
        "created_at": datetime.now().isoformat(),
        "source_result": str(source_result_path),
        "source_report": str(parent_report),
        "source_score": parent_score,
        "source_dimension_scores": parent_dimensions,
        "prompt_template": str(prompt_template),
        "run_dir": str(result["run_dir"]),
        "final_report": str(result["final_report"]),
        "judge_result": str(result["judge_result"]) if result["judge_result"] else None,
        "average_score": result["average_score"],
        "prepare_only": args.prepare_only,
    }
    result_path = experiment / "result.json"
    result_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if not args.prepare_only and not args.skip_judge:
        comparison_path = experiment / "judge_comparison.json"
        comparison = judge_stability.evaluate_reports_repeated(
            problem_id=problem_id,
            reports={"parent": parent_report, "cost_aware": Path(result["final_report"])},
            repeats=args.judge_trials,
            judge_label="cost-aware-innovation-deepseek-v4-flash",
            output=comparison_path,
            runs_parent=experiment,
            experiment=experiment,
            seed_results={
                "parent": parent_judge,
                "cost_aware": Path(result["judge_result"]),
            },
        )
        summary["judge_comparison"] = str(comparison_path)
        summary["average_scores"] = comparison.get("average_scores")
        result_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(f"Cost-aware innovation experiment: {experiment}")
    print(f"Summary: {result_path}")


if __name__ == "__main__":
    main()
