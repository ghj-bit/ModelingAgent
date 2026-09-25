#!/bin/bash
# Launch one OpenHands-backed interaction-workflow evolution experiment.
#
#   bash scripts/launch_openhands_evolution.sh <experiment-name> [max-rounds]
#
# Mirror of launch_openclaw_evolution.sh for the comparison arm: same draft pool,
# same guard, same model roles.  The only differences are the launcher module and
# that the OpenHands backend already treats solution.json as the submission and
# renders the Markdown report from it, so nothing extra is needed here for that.
#
# Why the draft root must be passed explicitly: the launcher's own default globs
# `openclaw_experiments/interaction_strategy_clean_baseline_initial_draft_mmbench_*`,
# which finds the old pool (no external_data.md) and a partial run, but not
# `evolve_exp/draft_mmbench`.  The solver prompt is forbidden from searching, so a
# run resolved against the wrong pool would have no factual basis.
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
BASE_URL=http://gpu6:18763/v1
MODEL=qwen3.8-27b

DRAFT_ROOT="${DRAFT_ROOT:-$REPO/openclaw_experiments/evolve_exp/draft_mmbench}"
EXPECTED_DRAFTS="${EXPECTED_DRAFTS:-35}"
# Roots that exist only to satisfy the launcher's start-up existence check, for
# runs that exercise part of the split.  Drafts here carry no external_data.md,
# so a solver must never actually read one; the resolver takes the newest draft
# per problem, and every problem in DRAFT_ROOT is newer.
EXTRA_DRAFT_ROOTS="${EXTRA_DRAFT_ROOTS:-}"

NAME="${1:?usage: launch_openhands_evolution.sh <experiment-name> [max-rounds]}"
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

setsid nohup "$PY" -m src.OpenClaw.run_substantive_interaction_workflow_evolution_from_initial_draft_openhands \
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
