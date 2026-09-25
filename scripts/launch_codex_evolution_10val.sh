#!/bin/bash
# Codex-only from-scratch validation experiment.
# Runs two validation problems four times each and two more once each: 10 runs.
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
NAME="${1:-codex_val_10}"
LOG="$REPO/.env_setup_logs/$NAME.log"
BASE_URL="${CODEX_BASE_URL:-http://gpu6:18763/v1}"
MODEL="${CODEX_MODEL:-qwen3.8-27b}"
CODEX_BIN="${CODEX_BIN:-/public1/home/stu52275901007/.local/bin/codex}"
mkdir -p "$REPO/.env_setup_logs"

run_batch() {
  local batch_name="$1" validation="$2" repetitions="$3"
  MMBENCH_PIN_VALIDATION="$validation" VALIDATION_REPETITIONS="$repetitions" \
  CODEX_BASE_URL="$BASE_URL" CODEX_MODEL="$MODEL" CODEX_BIN="$CODEX_BIN" \
  EXPECTED_EVIDENCE=35 AGENT_CPUS="${AGENT_CPUS:-4}" \
  bash "$REPO/scripts/launch_codex_evolution_from_scratch.sh" "$batch_name" 0
}

echo "[launch] Codex from-scratch validation batches: 2x4 + 2x1" | tee -a "$LOG"
run_batch "${NAME}_a_2x4" "2020_B,2020_D" 4
run_batch "${NAME}_b_2x1" "2020_E,2020_F" 1
echo "[launch] submitted 10 total validation runs" | tee -a "$LOG"
