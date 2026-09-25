#!/bin/bash
# Launch one OpenClaw-backed interaction-workflow evolution experiment.
#
#   bash scripts/launch_openclaw_evolution.sh <experiment-name> [max-rounds]
#
# The engine's own defaults point at DeepSeek and at the original author's
# Windows checkout, so every model role and every path has to be supplied here;
# what is not passed stays at whatever the shared parser defaults to.  All four
# model roles run against the local vLLM endpoint, which is the only reachable
# one on this cluster.
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
BASE_URL=http://gpu6:18763/v1
MODEL=qwen3.8-27b
# Draft pool generated with the empirical-lookup planner prompt.  Each draft
# carries data/external_data.md, which prepare_from_planning_draft stages into
# the solver workspace; the solver prompt forbids searching, so a pool from
# another root would leave every run without its factual basis.
DRAFT_ROOT="${DRAFT_ROOT:-$REPO/openclaw_experiments/evolve_exp/draft_mmbench}"
# The pool the evolution split draws from: MMBENCH_TRAIN_PROBLEMS (30) plus
# MMBENCH_VALIDATION_PROBLEMS (5).  Every one of them needs a draft, because the
# solver prompt forbids searching and reads the draft's own external_data.md.
EXPECTED_DRAFTS="${EXPECTED_DRAFTS:-35}"
# Extra roots passed to the launcher so its start-up existence check passes, for
# runs that exercise only part of the split (round 0 touches the validation pool
# alone).  Drafts here are picked only if a problem has no draft in DRAFT_ROOT,
# and they carry no external_data.md, so they must never be the ones a solver
# actually reads.
EXTRA_DRAFT_ROOTS="${EXTRA_DRAFT_ROOTS:-}"

NAME="${1:?usage: launch_openclaw_evolution.sh <experiment-name> [max-rounds]}"
ROUNDS="${2:-5}"

EXP="$REPO/openclaw_experiments/evolve_exp/$NAME"
LOG="$REPO/.env_setup_logs/$NAME.log"
mkdir -p "$REPO/.env_setup_logs"

if [ ! -d "$DRAFT_ROOT" ]; then
  echo "Draft root does not exist: $DRAFT_ROOT" >&2
  exit 2
fi
drafts=$(find "$DRAFT_ROOT" -path "*/results/draft.md" | wc -l)
missing=$(find "$DRAFT_ROOT" -path "*/results/draft.md" -printf '%h\n' \
          | while read -r d; do [ -s "$d/../data/external_data.md" ] || echo x; done | wc -l)
echo "Draft pool: $drafts drafts, $missing without external_data.md" | tee -a "$LOG"
# A count check is required as well as the per-draft one: against a pool that is
# still being written, every draft present is complete, so the missing count is
# 0 and the run would start against the handful of tasks finished so far.
if [ "$drafts" -lt "$EXPECTED_DRAFTS" ]; then
  echo "Refusing to start: draft pool has $drafts of $EXPECTED_DRAFTS drafts; the generator is still running." >&2
  exit 3
fi
if [ "$missing" -gt 0 ]; then
  echo "Refusing to start: $missing draft(s) lack the pre-gathered evidence the solver is told to read." >&2
  exit 4
fi

cd "$REPO"
echo "[launch] $(date)" | tee -a "$LOG"

setsid nohup "$PY" -m src.OpenClaw.run_substantive_interaction_workflow_evolution_from_initial_draft \
  --exp "$EXP" \
  --benchmark mmbench \
  --mmbench-root "$REPO/data/MMBench" \
  --planning-draft-root "$DRAFT_ROOT" $EXTRA_DRAFT_ROOTS \
  --fixed-rubric "$REPO/src/OpenClaw/interaction_initial_substantive_v1.json" \
  --baseline-report-root "$REPO" \
  --model "$MODEL" \
  --opt-model "$MODEL"      --opt-base-url "$BASE_URL"      --opt-api-key EMPTY \
  --expert-model "$MODEL"   --expert-base-url "$BASE_URL"   --expert-api-key EMPTY \
  --judge-feedback-model "$MODEL" \
  --mmbench-judge-model "$MODEL" --mmbench-judge-base-url "$BASE_URL" --mmbench-judge-api-key EMPTY \
  --max-rounds "$ROUNDS" \
  --train-batch-size 2 \
  --validation-size "${VALIDATION_SIZE:-4}" \
  --thinking off \
  >> "$LOG" 2>&1 &

echo "launcher pid=$!  experiment=$EXP  max_rounds=$ROUNDS  log=$LOG"
