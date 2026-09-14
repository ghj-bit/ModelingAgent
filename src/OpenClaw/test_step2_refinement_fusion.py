"""Focused smoke test for fusing Step 2 assumptions with an expert reply."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_substantive_20260912_124353"
    / "runs"
    / "round_1"
    / "r1p2_20260912_124428"
)


def credentials(args: argparse.Namespace) -> tuple[str, str]:
    api_key = args.api_key
    base_url = args.base_url
    secret_path = REPO_ROOT / "secret.json"
    if secret_path.is_file():
        secret = json.loads(secret_path.read_text(encoding="utf-8"))
        api_key = api_key or secret.get("api_key")
        base_url = base_url or secret.get("base_url")
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL")
    if not api_key or not base_url:
        raise ValueError("Missing API credentials")
    return str(api_key), str(base_url)


def response_text(message: object) -> str:
    for value in (
        getattr(message, "content", None),
        getattr(message, "reasoning_content", None),
    ):
        if isinstance(value, str) and value.strip():
            text = value.strip()
            fenced = re.fullmatch(r"```(?:markdown|md)?\s*(.*?)\s*```", text, re.DOTALL)
            return fenced.group(1).strip() if fenced else text
    raise ValueError("Model returned no refinement text")


def build_prompt(original: str, expert_reply: str) -> str:
    return f"""Reconstruct the intermediate report below using the expert advice.

Adopt the advice and convert each recommendation into explicit, executable
technical definitions and formulas. Define every symbol, unit, resource, and
model dependency; fix the formula structure here, leaving only unavailable
numerical inputs for later evidence. Each formula term may charge only the
resource it represents; express alternative resource paths as mutually exclusive
formulas. Propagate each change through affected
assumptions, methods, and conclusions, resolve conflicts, separate incompatible
alternatives, and prevent duplicate effects. Preserve unaffected content. State
accepted advice directly and omit consultation or change history. Return only
the reconstructed Markdown report.

<original_intermediate_report>
{original}
</original_intermediate_report>

<expert_advice>
{expert_reply}
</expert_advice>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--api-key")
    parser.add_argument("--base-url")
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Send the injected Step 2 and expert reply to the configured external API.",
    )
    args = parser.parse_args()

    run = args.run.resolve()
    original_path = run / "output" / "results" / "step_02_modeling_assumptions.md"
    expert_path = run / "output" / "logs" / "operator_feedback" / "expert_reply_1.json"
    original = original_path.read_text(encoding="utf-8")
    expert_payload = json.loads(expert_path.read_text(encoding="utf-8"))
    expert_reply = str(expert_payload.get("answer", "")).strip()
    if not expert_reply:
        raise ValueError(f"No expert answer in {expert_path}")

    prompt = build_prompt(original, expert_reply)
    output_dir = run.parents[2] / "workflows" / "step2_refinement_fusion_test"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    if not args.execute:
        checks = {
            "source_run": str(run),
            "model": args.model,
            "executed": False,
            "contains_obsolete_authority_label": "authoritative" in prompt.lower(),
            "injects_original_report": "<original_intermediate_report>" in prompt,
            "injects_expert_advice": "<expert_advice>" in prompt,
            "requires_executable_formulas": "explicit, executable" in prompt,
            "fixes_formula_structure": "fix the formula structure here" in prompt,
        }
        (output_dir / "test_result.json").write_text(
            json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(output_dir)
        return

    api_key, base_url = credentials(args)
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=args.timeout)
    options = {
        "model": args.model,
        "messages": [
            {
                "role": "system",
                "content": "Reconstruct mathematical-modeling reports for internal consistency.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,
        "max_tokens": 8192,
    }
    if "deepseek.com" in base_url.lower():
        options["extra_body"] = {"thinking": {"type": "disabled"}}
    response = client.chat.completions.create(**options)
    refined = response_text(response.choices[0].message)

    (output_dir / "step_02_modeling_assumptions_refined.md").write_text(
        refined + "\n", encoding="utf-8"
    )
    checks = {
        "source_run": str(run),
        "model": args.model,
        "executed": True,
        "contains_obsolete_authority_label": "authoritative" in refined.lower(),
        "mentions_M1": "M1" in refined,
        "mentions_M2": "M2" in refined,
        "mentions_EDS": "EDS" in refined,
        "mentions_ETD": "ETD" in refined,
        "output_chars": len(refined),
    }
    (output_dir / "test_result.json").write_text(
        json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(output_dir)


if __name__ == "__main__":
    main()
