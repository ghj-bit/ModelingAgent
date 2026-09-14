"""Run one fixed, innovation-focused OpenClaw benchmark experiment."""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from baseline import PROMPT_TEMPLATE_PATH, REPO_ROOT, load_problems, run_problem


WORKFLOW_PATTERN = re.compile(
    r"(?ms)(^## Required Workflow\s*\n)(.*?)(?=^## |\Z)"
)
INNOVATION_WORKFLOW = """\
1. Understand the complete problem, preserve every supplied table value, identify all requested deliverables, and write a problem-understanding artifact.
2. Build and execute a reproducible G/G/c baseline from the supplied empirical distributions. Report fixed-two-teller and fixed-three-teller performance, assumptions, uncertainty, and validation checks.
3. Reframe the decision from choosing a fixed teller count to controlling a cross-trained relief teller under uncertain demand. Define a state-responsive hysteresis policy with activation threshold h, release threshold l, minimum deployment time, switching cost, and an explicit labor-waiting-abandonment objective.
4. Implement a reproducible simulation-optimization experiment. Optimize the policy over plausible uncertainty scenarios derived from the supplied data, clearly labeling perturbations as stress tests rather than observations. Compare fixed two tellers, fixed three tellers, a scheduled lunch floater, a queue-only policy, and the combined time-and-state robust policy.
5. Validate the proposed contribution with repeated simulations, confidence intervals, SLA violation probabilities, sensitivity analysis, and ablations that remove uncertainty handling, hysteresis, and state feedback. Save the formulation, executable code, machine-readable results, and baseline comparison as authoritative artifacts.
6. Answer every original subproblem and translate the optimized policy into operational recommendations. Explain the contribution without claiming new queueing theory, and discuss limitations and transferability to other service systems.
7. Produce the final report at the required path. Include dedicated sections named Novel Contribution, Baseline Limitation, Proposed Adaptive Policy, Simulation-Optimization Algorithm, Ablation Study, and Robustness and Transferability; incorporate the quantitative evidence from the authoritative experiment artifacts.

"""


def build_prompt_template(destination: Path) -> None:
    base_prompt = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
    rendered, count = WORKFLOW_PATTERN.subn(
        lambda match: match.group(1) + INNOVATION_WORKFLOW,
        base_prompt,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Base prompt has no unique Required Workflow section")
    destination.write_text(rendered, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a fixed adaptive-staffing innovation experiment and judge its "
            "final report; no workflow evolution is performed."
        )
    )
    parser.add_argument(
        "problem_id", nargs="?", default="2013_Bank_Service_Problem"
    )
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--agent")
    parser.add_argument("--openclaw-command")
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument(
        "--exp",
        help=(
            "Experiment directory. Defaults to "
            "openclaw_experiments/innovation_<timestamp>."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    problems = load_problems()
    if args.problem_id not in problems:
        raise ValueError(f"Unknown problem ID: {args.problem_id}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment = (
        Path(args.exp).resolve()
        if args.exp
        else REPO_ROOT / "openclaw_experiments" / f"innovation_{timestamp}"
    )
    experiment.mkdir(parents=True, exist_ok=False)
    prompt_template = experiment / "prompt.md"
    build_prompt_template(prompt_template)

    run_args = SimpleNamespace(
        output_root=str(experiment / "runs"),
        model=args.model,
        prompt_template=str(prompt_template),
        prepare_only=args.prepare_only,
        openclaw_command=args.openclaw_command,
        agent=args.agent,
        thinking=args.thinking,
        timeout=args.timeout,
        skip_judge=args.skip_judge,
    )
    result = run_problem(args.problem_id, problems[args.problem_id], run_args)
    summary = {
        "experiment_type": "fixed_innovation_treatment",
        "problem_id": args.problem_id,
        "model": args.model,
        "created_at": datetime.now().isoformat(),
        "prompt_template": str(prompt_template),
        "run_dir": str(result["run_dir"]),
        "final_report": str(result["final_report"]),
        "judge_result": (
            str(result["judge_result"]) if result["judge_result"] else None
        ),
        "average_score": result["average_score"],
    }
    (experiment / "result.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Innovation experiment: {experiment}")
    print(f"Experiment summary: {experiment / 'result.json'}")


if __name__ == "__main__":
    main()
