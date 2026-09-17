import json
import math
import re
import statistics
from pathlib import Path


EXPERIMENT = Path(
    "openclaw_experiments/interaction_workflow_clean_baseline_refinement_20260914_140527"
)
OUTPUT = EXPERIMENT / "workflows" / "expert_interaction_token_statistics.json"
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

RESULTS = json.loads(
    (EXPERIMENT / "workflows" / "results.json").read_text(encoding="utf-8")
)
CANONICAL_RUNS = {}
for node in RESULTS:
    for problem in node.get("problem_results", []):
        repetitions = problem.get("repetitions") or [problem]
        for repetition in repetitions:
            run_dir = Path(str(repetition["run_dir"])).resolve()
            CANONICAL_RUNS[run_dir] = int(node["round"])


def approximate_tokens(text: str) -> int:
    """Approximate DeepSeek-family tokens without downloading a tokenizer."""
    cjk_count = len(CJK.findall(text))
    other_non_ascii = sum(
        1 for char in text if ord(char) >= 128 and not CJK.fullmatch(char)
    )
    ascii_count = sum(1 for char in text if ord(char) < 128)
    return math.ceil(cjk_count + other_non_ascii + ascii_count / 4)


def percentile(values: list[int], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def summary(values: list[int]) -> dict:
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "p75": percentile(values, 0.75),
        "p90": percentile(values, 0.90),
        "p95": percentile(values, 0.95),
        "max": max(values),
        "min": min(values),
    }


runs = []
for feedback_dir in sorted(
    EXPERIMENT.glob("runs/round_*/*/output/logs/operator_feedback")
):
    run_dir = feedback_dir.parents[2]
    if run_dir.resolve() not in CANONICAL_RUNS:
        continue
    round_number = CANONICAL_RUNS[run_dir.resolve()]
    metadata_path = run_dir / "meta" / "run.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    exchanges = []
    for request_path in sorted(feedback_dir.glob("expert_request_*.json")):
        exchange = int(request_path.stem.rsplit("_", 1)[1])
        reply_path = feedback_dir / f"expert_reply_{exchange}.json"
        if not reply_path.is_file():
            continue
        request = json.loads(request_path.read_text(encoding="utf-8"))
        reply = json.loads(reply_path.read_text(encoding="utf-8"))
        question = str(request.get("question", ""))
        answer = str(reply.get("answer", ""))
        request_tokens = approximate_tokens(question)
        reply_tokens = approximate_tokens(answer)
        exchanges.append(
            {
                "exchange": exchange,
                "request_characters": len(question),
                "reply_characters": len(answer),
                "request_tokens_approx": request_tokens,
                "reply_tokens_approx": reply_tokens,
                "total_tokens_approx": request_tokens + reply_tokens,
            }
        )
    if not exchanges:
        continue
    runs.append(
        {
            "round": round_number,
            "problem_id": metadata.get("problem_id"),
            "run_dir": str(run_dir.resolve()),
            "exchange_count": len(exchanges),
            "request_tokens_approx": sum(
                item["request_tokens_approx"] for item in exchanges
            ),
            "reply_tokens_approx": sum(
                item["reply_tokens_approx"] for item in exchanges
            ),
            "total_tokens_approx": sum(
                item["total_tokens_approx"] for item in exchanges
            ),
            "exchanges": exchanges,
        }
    )

runs.sort(key=lambda item: (item["round"], str(item["problem_id"])))
rounds = []
for round_number in sorted({item["round"] for item in runs}):
    selected = [item for item in runs if item["round"] == round_number]
    rounds.append(
        {
            "round": round_number,
            "run_count": len(selected),
            "mean_exchanges_per_run": statistics.fmean(
                item["exchange_count"] for item in selected
            ),
            "mean_request_tokens_per_run_approx": statistics.fmean(
                item["request_tokens_approx"] for item in selected
            ),
            "mean_reply_tokens_per_run_approx": statistics.fmean(
                item["reply_tokens_approx"] for item in selected
            ),
            "mean_total_tokens_per_run_approx": statistics.fmean(
                item["total_tokens_approx"] for item in selected
            ),
            "round_request_tokens_approx": sum(
                item["request_tokens_approx"] for item in selected
            ),
            "round_reply_tokens_approx": sum(
                item["reply_tokens_approx"] for item in selected
            ),
            "round_total_tokens_approx": sum(
                item["total_tokens_approx"] for item in selected
            ),
        }
    )

exchange_rows = [exchange for run in runs for exchange in run["exchanges"]]
payload = {
    "experiment": str(EXPERIMENT.resolve()),
    "method": {
        "exact_usage_available": False,
        "fields_counted": {
            "expert_input": "expert_request_N.json.question",
            "expert_reply": "expert_reply_N.json.answer",
        },
        "approximation": (
            "ceil(CJK characters + other non-ASCII characters + ASCII characters / 4)"
        ),
        "excludes": "The duplicated question field stored in expert_reply_N.json.",
    },
    "coverage": {
        "round_count": len(rounds),
        "run_count": len(runs),
        "exchange_count": len(exchange_rows),
    },
    "per_exchange": {
        "request_tokens_approx": summary(
            [item["request_tokens_approx"] for item in exchange_rows]
        ),
        "reply_tokens_approx": summary(
            [item["reply_tokens_approx"] for item in exchange_rows]
        ),
        "total_tokens_approx": summary(
            [item["total_tokens_approx"] for item in exchange_rows]
        ),
    },
    "per_problem_run": {
        "exchange_count": summary([item["exchange_count"] for item in runs]),
        "request_tokens_approx": summary(
            [item["request_tokens_approx"] for item in runs]
        ),
        "reply_tokens_approx": summary(
            [item["reply_tokens_approx"] for item in runs]
        ),
        "total_tokens_approx": summary(
            [item["total_tokens_approx"] for item in runs]
        ),
    },
    "rounds": rounds,
    "runs": runs,
}
OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(OUTPUT)
print(json.dumps(payload["coverage"], ensure_ascii=False))
print(json.dumps(payload["per_exchange"], ensure_ascii=False))
print(json.dumps(payload["per_problem_run"], ensure_ascii=False))
