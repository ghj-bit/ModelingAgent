#!/bin/bash
# Launch one Claude Code-backed interaction-workflow evolution experiment.
#
#   bash scripts/launch_claude_evolution.sh <experiment-name> [max-rounds]
#
# Mirror of launch_openhands_evolution.sh for the third comparison arm: same
# draft pool, same guard, same model roles, same prompt.  The only difference is
# which executable solves each task, so nothing extra is needed here.
#
# Why the draft root must be passed explicitly: the launcher's own default globs
# `openclaw_experiments/interaction_strategy_clean_baseline_initial_draft_mmbench_*`,
# which finds the old pool (no external_data.md) and a partial run, but not
# `evolve_exp/draft_mmbench`.  The solver prompt is forbidden from searching, so a
# run resolved against the wrong pool would have no factual basis.
#
# Unlike the other two arms this one needs no separate conda environment: the
# Claude backend's task driver is standard-library only.  Each task starts its
# own Anthropic-to-OpenAI translation shim on a free port -- Claude Code cannot
# talk to the local endpoint unaided (see src/OpenClaw/claude_backend/proxy.py).
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
BASE_URL=http://gpu6:18763/v1
MODEL=qwen3.8-27b

# The human expert runs on DeepSeek; the MM-Bench judge stays on the locally
# served model.  A DeepSeek judge was tried and had to be reverted: its replies
# were not in the tagged format MM-Bench's parser requires (unclosed <reason>,
# markdown headers inside the answer), so a dimension came back empty and the
# whole round aborted.  The solver and the optimizer are local in both cases.
# Override any of these to point a role somewhere else.
DEEPSEEK_BASE_URL="${DEEPSEEK_BASE_URL:-https://api.deepseek.com}"
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:?export DEEPSEEK_API_KEY before running this script}"
EXPERT_MODEL="${EXPERT_MODEL:-deepseek-flash}"
EXPERT_BASE_URL="${EXPERT_BASE_URL:-$DEEPSEEK_BASE_URL}"
EXPERT_API_KEY="${EXPERT_API_KEY:-$DEEPSEEK_API_KEY}"
JUDGE_MODEL="${JUDGE_MODEL:-$MODEL}"
JUDGE_BASE_URL="${JUDGE_BASE_URL:-$BASE_URL}"
JUDGE_API_KEY="${JUDGE_API_KEY:-EMPTY}"

# Optional: pin the CPE sampling seed.  Reusing another experiment's seed makes
# every round draw the same training batches in the same order, which is what
# turns a re-run into a paired replay of the original.
SAMPLING_SEED="${SAMPLING_SEED:-}"
SAMPLING_SEED_ARG=""
if [ -n "$SAMPLING_SEED" ]; then
  SAMPLING_SEED_ARG="--sampling-seed $SAMPLING_SEED"
fi

DRAFT_ROOT="${DRAFT_ROOT:-$REPO/openclaw_experiments/evolve_exp/draft_mmbench}"
EXPECTED_DRAFTS="${EXPECTED_DRAFTS:-35}"
# Roots that exist only to satisfy the launcher's start-up existence check, for
# runs that exercise part of the split.  Drafts here carry no external_data.md,
# so a solver must never actually read one; the resolver takes the newest draft
# per problem, and every problem in DRAFT_ROOT is newer.
EXTRA_DRAFT_ROOTS="${EXTRA_DRAFT_ROOTS:-}"

NAME="${1:?usage: launch_claude_evolution.sh <experiment-name> [max-rounds]}"
ROUNDS="${2:-5}"
# 0 means "round 0 only": the launcher's private --round0-only stops the run once
# the round-0 initial-parent validation is done, before the initial training
# parents and every evolved round.  --max-rounds is pinned to 1 alongside it
# purely because the shared parser rejects a value below 1.
ROUND0_ONLY=""
if [ "$ROUNDS" -eq 0 ]; then
  ROUND0_ONLY="--round0-only"
  ROUNDS=1
fi

# Score each problem three times and average, so a per-problem score carries a
# spread instead of being one sample.  Trials are independent and the judge runs
# them concurrently, so this costs concurrency on the endpoint, not wall clock.
# It matters more here than in the baseline arm: CPE compares candidates against
# an incumbent by a margin, and that comparison is meaningless without knowing
# how much the score moves on its own.
JUDGE_REPEATS="${JUDGE_REPEATS:-3}"
# Score the four judge dimensions on concurrent calls instead of one after the
# other.  They are independent, so this only shortens the judge.  It is set here
# and not in the evaluator because it changes how hard a run leans on the shared
# judge endpoint: runs judged under different regimes are not comparable, so
# every arm must opt in deliberately.
export MMBENCH_JUDGE_PARALLEL_DIMENSIONS="${MMBENCH_JUDGE_PARALLEL_DIMENSIONS:-1}"

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

setsid nohup "$PY" -m src.OpenClaw.run_substantive_interaction_workflow_evolution_from_initial_draft_claude \
  --exp "$EXP" \
  --benchmark mmbench \
  --mmbench-root "$REPO/data/MMBench" \
  --planning-draft-root "$DRAFT_ROOT" $EXTRA_DRAFT_ROOTS \
  --fixed-rubric "$REPO/src/OpenClaw/interaction_initial_substantive_v1.json" \
  --baseline-report-root "$REPO" \
  --model "$MODEL" \
  --opt-model "$MODEL"      --opt-base-url "$BASE_URL"      --opt-api-key EMPTY \
  --expert-model "$EXPERT_MODEL" --expert-base-url "$EXPERT_BASE_URL" --expert-api-key "$EXPERT_API_KEY" \
  --judge-feedback-model "$MODEL" \
  --mmbench-judge-model "$JUDGE_MODEL" --mmbench-judge-base-url "$JUDGE_BASE_URL" --mmbench-judge-api-key "$JUDGE_API_KEY" \
  --max-rounds "$ROUNDS" $ROUND0_ONLY $SAMPLING_SEED_ARG \
  --judge-repeats "$JUDGE_REPEATS" \
  --train-batch-size 2 \
  --validation-size "${VALIDATION_SIZE:-4}" \
  --thinking off \
  >> "$LOG" 2>&1 &

echo "launcher pid=$!  experiment=$EXP  max_rounds=$ROUNDS  log=$LOG"
