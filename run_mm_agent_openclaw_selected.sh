#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

MODEL="deepseek/deepseek-v4-flash"
THINKING="high"
TIMEOUT="7200"
OUTPUT_ROOT="${SCRIPT_DIR}/output_workspace_mm_agent_openclaw"
OPENCLAW_COMMAND=""
SKIP_JUDGE=0
PREPARE_ONLY=0

usage() {
    cat <<'EOF'
Run the MM-Agent + OpenClaw baseline on:
  2025_Managing_Sustainable_Tourism
  2003_Aviation_Baggage_Screening

Usage:
  ./run_mm_agent_openclaw_selected.sh [options]

Options:
  --model MODEL              OpenClaw model ID
  --thinking LEVEL           OpenClaw thinking level (default: high)
  --timeout SECONDS          Timeout for each OpenClaw run (default: 7200)
  --output-root PATH         Output directory
  --openclaw-command PATH    Explicit OpenClaw executable
  --skip-judge               Generate reports without ModelingBench evaluation
  --prepare-only             Only prepare prompts and workspaces
  -h, --help                 Show this help
EOF
}

while (($#)); do
    case "$1" in
        --model)
            MODEL="${2:?--model requires a value}"
            shift 2
            ;;
        --thinking)
            THINKING="${2:?--thinking requires a value}"
            shift 2
            ;;
        --timeout)
            TIMEOUT="${2:?--timeout requires a value}"
            shift 2
            ;;
        --output-root)
            OUTPUT_ROOT="${2:?--output-root requires a value}"
            shift 2
            ;;
        --openclaw-command)
            OPENCLAW_COMMAND="${2:?--openclaw-command requires a value}"
            shift 2
            ;;
        --skip-judge)
            SKIP_JUDGE=1
            shift
            ;;
        --prepare-only)
            PREPARE_ONLY=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf 'Unknown argument: %s\n\n' "$1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

PROBLEM_IDS=(
    "2025_Managing_Sustainable_Tourism"
    "2003_Aviation_Baggage_Screening"
)

RUNNER_ARGS=(
    -m src.OpenClaw.run_mm_agent_baseline
    "${PROBLEM_IDS[@]}"
    --model "$MODEL"
    --thinking "$THINKING"
    --timeout "$TIMEOUT"
    --concurrency "${#PROBLEM_IDS[@]}"
    --output-root "$OUTPUT_ROOT"
)

if [[ -n "$OPENCLAW_COMMAND" ]]; then
    RUNNER_ARGS+=(--openclaw-command "$OPENCLAW_COMMAND")
fi
if ((SKIP_JUDGE)); then
    RUNNER_ARGS+=(--skip-judge)
fi
if ((PREPARE_ONLY)); then
    RUNNER_ARGS+=(--prepare-only)
fi

cd "$SCRIPT_DIR"
python "${RUNNER_ARGS[@]}"
