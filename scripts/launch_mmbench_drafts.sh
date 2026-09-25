#!/bin/bash
# Generate MM-Bench planning drafts that carry their own empirical evidence.
#
#   bash scripts/launch_mmbench_drafts.sh <experiment-path> [concurrency] [problem-id...]
#
# With no problem IDs this runs the five MM-Bench validation tasks, which is the
# pool the CPE validation phase draws from.  Pass IDs explicitly to cover the
# training pool instead.
#
# The planner prompt looks up 1-2 verifiable empirical data items and writes them
# to `data/external_data.md` next to the draft.  The evolution launcher stages
# that file into each solver workspace and forbids the solver from searching, so
# the lookup happens once per problem instead of once per solver run.
#
# The problem list is always explicit: the runner's own default is "every
# MM-Bench task that ships a dataset directory" (8 tasks), which is neither pool.
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
# The locally served model; the runner's own default is deepseek.
MODEL=qwen3.8-27b
# MMBENCH_VALIDATION_PROBLEMS in the evolution launcher.
VAL_PROBLEMS="2020_B 2020_C 2020_D 2020_E 2020_F"

EXP_ARG="${1:?usage: launch_mmbench_drafts.sh <experiment-path> [concurrency] [problem-id...]}"
CONC="${2:-5}"
shift 2 2>/dev/null || shift 1
PROBLEMS="${*:-$VAL_PROBLEMS}"

LOG="$REPO/.env_setup_logs/$(basename "$EXP_ARG").log"
mkdir -p "$REPO/.env_setup_logs"

cd "$REPO"
echo "[launch] $(date)" | tee -a "$LOG"

# shellcheck disable=SC2086 -- the problem list is deliberately word-split
setsid nohup "$PY" scripts/run_clean_baseline_initial_draft_mmbench.py \
  --exp "$EXP_ARG" \
  --mmbench-root "$REPO/data/MMBench" \
  --problem-id $PROBLEMS \
  --model "$MODEL" \
  --thinking off \
  --concurrency "$CONC" \
  --validation-attempts 3 \
  >> "$LOG" 2>&1 &

echo "draft runner pid=$!  experiment=$EXP_ARG  concurrency=$CONC  tasks=[$(echo $PROBLEMS | wc -w)]  log=$LOG"
