"""Run the Judge-feedback weakness summarizer against an existing score file.

This is an opt-in integration test because it calls the configured LLM API.
"""

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import run_interaction_rubric_evolution as interaction  # noqa: E402


DEFAULT_JUDGE_FILE = (
    REPO_ROOT
    / "output_judge"
    / "OpenClaw"
    / "interaction-rubric-interaction_rubric_20260907_200447-r1"
    / "j_88abe790c8_report_1"
    / "2013_Bank_Service_Problem.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize low-scoring Judge subdimension feedback into abstract, "
            "weakness-only aspects."
        )
    )
    parser.add_argument("--judge-file", type=Path, default=DEFAULT_JUDGE_FILE)
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--api-key")
    parser.add_argument("--base-url")
    return parser.parse_args()


def main() -> None:
    cli = parse_args()
    judge_file = cli.judge_file.resolve()
    judge_result = interaction.read_raw_judge_result(judge_file)
    selected = interaction.low_scoring_judge_feedback(judge_result)
    if not selected:
        raise RuntimeError(f"No low-scoring Judge subdimensions found in {judge_file}")

    llm_args = SimpleNamespace(
        opt_model=cli.model,
        judge_summary_model=cli.model,
        opt_api_key=cli.api_key,
        opt_base_url=cli.base_url,
    )
    summary = interaction.summarize_judge_feedback_file(judge_file, llm_args)
    diagnostic = {
        "judge_file": str(judge_file),
        "selected_low_subdimensions": [
            {
                "dimension": item["dimension"],
                "subdimensions": [
                    subdimension["name"]
                    for subdimension in item["low_subdimensions"]
                ],
            }
            for item in selected
        ],
        "llm_weakness_summary": summary,
    }
    print(json.dumps(diagnostic, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
