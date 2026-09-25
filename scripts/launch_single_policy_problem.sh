#!/bin/bash
# Replay ONE (evolved policy, problem) pair in its own experiment directory.
#
#   bash scripts/launch_single_policy_problem.sh <experiment-name> <problem-id> [guard|noguard]
#
# The experiment directory must already hold `initial_interaction_workflows.json`
# (the policy to replay) — see the runaway_guard_* directories for the format.
# Round 0 only: the initial parent validation runs the policy once on the one
# pinned problem and stops, so this costs a single agent run.
#
# Differences from launch_claude_evolution.sh, and why:
#   * --validation-size 1 + MMBENCH_PIN_VALIDATION=<problem>: the shared CPE state
#     requires the validation size to equal the whole pool, so the pool is pinned
#     to the single problem instead of shrinking the size.
#   * --round0-only: stop after the initial validation instead of evolving.
#   * INTERACTION_RUNAWAY_GUARD=1 (default): append the search-scope / background
#     rules to the solver prompt.  "noguard" replays without them, which is the
#     A/B control for the same policy and problem.
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
BASE_URL=http://gpu6:18763/v1
MODEL=qwen3.8-27b

NAME="${1:?usage: launch_single_policy_problem.sh <experiment-name> <problem-id> [guard|noguard]}"
PROBLEM="${2:?usage: launch_single_policy_problem.sh <experiment-name> <problem-id> [guard|noguard]}"
MODE="${3:-guard}"

EXP="$REPO/openclaw_experiments/evolve_exp/$NAME"
LOG="$REPO/.env_setup_logs/$NAME.log"
mkdir -p "$REPO/.env_setup_logs"
if [ ! -f "$EXP/initial_interaction_workflows.json" ]; then
  echo "Missing $EXP/initial_interaction_workflows.json (the policy to replay)" >&2
  exit 2
fi

export MMBENCH_JUDGE_PARALLEL_DIMENSIONS="${MMBENCH_JUDGE_PARALLEL_DIMENSIONS:-1}"
export MMBENCH_PIN_VALIDATION="$PROBLEM"
export DISABLE_AUTOUPDATER=1
if [ "$MODE" = "guard" ]; then
  export INTERACTION_RUNAWAY_GUARD=1
else
  unset INTERACTION_RUNAWAY_GUARD || true
fi

cd "$REPO"
echo "[launch] $(date) problem=$PROBLEM mode=$MODE" | tee -a "$LOG"

setsid nohup "$PY" -m src.OpenClaw.run_substantive_interaction_workflow_evolution_from_initial_draft_claude \
  --exp "$EXP" \
  --benchmark mmbench \
  --mmbench-root "$REPO/data/MMBench" \
  --planning-draft-root "$REPO/openclaw_experiments/evolve_exp/draft_mmbench" \
                        "$REPO/openclaw_experiments/evolve_exp/draft_mmbench_train" \
  --fixed-rubric "$REPO/src/OpenClaw/interaction_initial_substantive_v1.json" \
  --baseline-report-root "$REPO" \
  --model "$MODEL" \
  --opt-model "$MODEL"      --opt-base-url "$BASE_URL"      --opt-api-key EMPTY \
  --expert-model "$MODEL"   --expert-base-url "$BASE_URL"   --expert-api-key EMPTY \
  --judge-feedback-model "$MODEL" \
  --mmbench-judge-model "$MODEL" --mmbench-judge-base-url "$BASE_URL" --mmbench-judge-api-key EMPTY \
  --max-rounds 1 --round0-only \
  --judge-repeats 3 \
  --train-batch-size 2 \
  --validation-size 1 \
  --thinking off \
  >> "$LOG" 2>&1 &

echo "launcher pid=$!  experiment=$EXP  problem=$PROBLEM  mode=$MODE  log=$LOG"
