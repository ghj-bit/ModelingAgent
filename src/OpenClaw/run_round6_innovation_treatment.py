"""Run one innovation-focused refinement from the 2013 bank Round 6 node."""

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
except ImportError:
    import baseline as openclaw_baseline
    import run_judge_stability as judge_stability
    import run_local_rubric_evolution as local


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
SOURCE_EXPERIMENT = (
    REPO_ROOT / "openclaw_experiments" / "mlevolve_rubric_20260830_225420"
)
SOURCE_RESULT = SOURCE_EXPERIMENT / "workflows" / "round_6" / "result.json"
BASE_PROMPT = SCRIPT_DIR / "prompt_modelingbench_baseline.md"
WORKFLOW_PATTERN = re.compile(
    r"(?ms)(^## Required Workflow\s*\n)(.*?)(?=^## |\Z)"
)

INNOVATION_WORKFLOW = """\
1. Read the inheritance manifest, all inherited stage summaries, executable artifacts, and `{{RESULTS_DIR}}/parent_solution_report.md`. Preserve every validated parent result and original deliverable.
2. Identify the fixed-staffing baseline's decision limitation: it chooses one teller count for all states and does not trade service risk against relief-teller usage.
3. Formulate one state-responsive relief-teller policy with activation and release thresholds, hysteresis, a minimum deployment duration, and an explicit objective using service-target violations and teller utilization. Clearly distinguish supplied data from stress-test assumptions.
4. Implement and execute a compact, reproducible simulation-optimization experiment. Compare at least fixed two tellers, fixed three tellers, a queue-only threshold rule, and the proposed risk-aware policy under common random numbers. Search a documented finite policy grid; do not select thresholds by narrative judgment alone.
5. Validate the contribution using repeated runs, confidence intervals, tail/SLA violation measures, and ablations for state feedback and hysteresis. Report both successful and failed cases. The contribution is valid only if it offers a measurable Pareto improvement or a clearly quantified new trade-off over the fixed baselines.
6. Update affected stage summaries and regenerate the complete final report. Preserve answers to every original subproblem and the management letter. Add concise sections named `Novel Contribution`, `Adaptive Policy and Objective`, `Baseline Comparison`, `Ablation and Falsification`, and `Transferability`; do not claim invention of new queueing theory.

"""

EVIDENCE_CONTRACT = """## Innovation Evidence Contract

Create and actually use these authoritative artifacts:

- `{{CODE_DIR}}/adaptive_staffing.py`: executable policy search and evaluation.
- `{{RESULTS_DIR}}/adaptive_staffing_results.json`: parameters, seeds, baseline and policy metrics, uncertainty, and ablations.
- `{{RESULTS_DIR}}/innovation_comparison.md`: the novelty gap, mathematical mechanism, fair baseline comparison, falsification outcome, limitations, and transferability.

The final report must cite quantitative values from these generated artifacts. A new assumption, extra scenario, or longer discussion without an implemented decision mechanism and baseline comparison does not satisfy this experiment.

"""


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_prompt_template(destination: Path) -> None:
    base = BASE_PROMPT.read_text(encoding="utf-8")
    rendered, count = WORKFLOW_PATTERN.subn(
        lambda match: match.group(1) + INNOVATION_WORKFLOW,
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
        description="Refine the bank-service Round 6 report with one fixed innovation treatment."
    )
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--judge-trials", type=int, default=3)
    parser.add_argument("--agent")
    parser.add_argument("--openclaw-command")
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--source-result", type=Path, default=SOURCE_RESULT)
    parser.add_argument("--exp", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.judge_trials < 1:
        raise ValueError("--judge-trials must be positive")
    source = read_json(args.source_result.resolve())
    parent_output = Path(source["output_dir"]).resolve()
    parent_report = Path(source["final_report"]).resolve()
    parent_judge = Path(source["judge_result"]).resolve()
    for label, path in (
        ("Round 6 output", parent_output),
        ("Round 6 report", parent_report),
        ("Round 6 Judge result", parent_judge),
    ):
        if not path.exists():
            raise FileNotFoundError(f"{label} is missing: {path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment = (
        args.exp.resolve()
        if args.exp
        else REPO_ROOT / "openclaw_experiments" / f"innovation_round6_{timestamp}"
    )
    experiment.mkdir(parents=True, exist_ok=False)
    prompt_template = experiment / "prompt.md"
    build_prompt_template(prompt_template)

    problems = openclaw_baseline.load_problems()
    problem_id = str(source.get("problem_id") or "2013_Bank_Service_Problem")
    if problem_id not in problems:
        raise ValueError(f"Unknown problem ID: {problem_id}")

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

    summary = {
        "experiment_type": "round6_fixed_innovation_treatment",
        "problem_id": problem_id,
        "created_at": datetime.now().isoformat(),
        "source_result": str(args.source_result.resolve()),
        "source_report": str(parent_report),
        "source_score": source.get("offline_score"),
        "source_dimension_scores": source.get("offline_dimension_scores"),
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
            reports={"round6": parent_report, "treatment": Path(result["final_report"])},
            repeats=args.judge_trials,
            judge_label="innovation-treatment-deepseek-v4-flash",
            output=comparison_path,
            runs_parent=experiment,
            experiment=experiment,
            seed_results={
                "round6": parent_judge,
                "treatment": Path(result["judge_result"]),
            },
        )
        summary["judge_comparison"] = str(comparison_path)
        summary["average_scores"] = comparison.get("average_scores")
        result_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(f"Innovation treatment experiment: {experiment}")
    print(f"Summary: {result_path}")


if __name__ == "__main__":
    main()
