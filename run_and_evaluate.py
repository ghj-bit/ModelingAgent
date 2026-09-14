import argparse
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent
MODELTOOL_DIR = REPO_ROOT / "src" / "ModelTool"
JUDGER_DIR = REPO_ROOT / "src" / "judger"


def run_command(command, workdir):
    print(f"\nRunning: {' '.join(str(part) for part in command)}")
    subprocess.run(command, cwd=workdir, check=True)


def find_new_workspace(output_root, problem_id, previous_directories):
    candidates = [
        path
        for path in output_root.glob(f"{problem_id}_*")
        if path.is_dir() and path.resolve() not in previous_directories
    ]
    if not candidates:
        raise RuntimeError(
            f"No new workspace was created for {problem_id} under {output_root}"
        )

    workspace = max(candidates, key=lambda path: path.stat().st_mtime_ns)
    reports = sorted(workspace.glob("*.md"))
    if not reports:
        raise RuntimeError(
            f"Task finished without a Markdown report in the new workspace: {workspace}"
        )
    return workspace, reports


def main():
    parser = argparse.ArgumentParser(
        description="Run one Tool Agent problem and evaluate its generated reports."
    )
    parser.add_argument("problem_id", help="ModelingBench problem ID to run.")
    args = parser.parse_args()

    config_path = MODELTOOL_DIR / "model_config.yaml"
    with open(config_path, encoding="utf-8") as config_file:
        model_name = yaml.safe_load(config_file)["model_name"]

    output_root = REPO_ROOT / "output_workspace_modeltool" / model_name
    output_root.mkdir(parents=True, exist_ok=True)
    previous_directories = {
        path.resolve() for path in output_root.glob(f"{args.problem_id}_*")
    }

    run_command(
        [sys.executable, "baseline.py", args.problem_id],
        MODELTOOL_DIR,
    )

    workspace, reports = find_new_workspace(
        output_root, args.problem_id, previous_directories
    )
    print(f"\nNew workspace: {workspace}")
    print("Reports: " + ", ".join(path.name for path in reports))

    run_command(
        [
            sys.executable,
            "main_judge.py",
            args.problem_id,
            "--workspace",
            str(workspace),
        ],
        JUDGER_DIR,
    )

    result_path = (
        REPO_ROOT
        / "output_judge"
        / "ModelTool"
        / model_name
        / workspace.name
        / f"{args.problem_id}.json"
    )
    if not result_path.is_file():
        raise RuntimeError(f"Judge completed without producing: {result_path}")
    print(f"\nRun and evaluation completed: {result_path}")


if __name__ == "__main__":
    main()
