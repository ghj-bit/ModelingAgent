#!/bin/bash
# Launch the non-coevolution, from-scratch Codex solver arm.
#
#   bash scripts/launch_codex_evolution_from_scratch.sh <experiment-name> [max-rounds]
#
# The workflow, prompt, CPE, expert bridge, judge, and validation settings are
# the same as the Claude from-scratch arm.  Only the solver process changes to
# Codex CLI, with model reasoning fixed to the server's lowest accepted level
# (model_reasoning_effort=low -- the endpoint rejects "none" outright).
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
BASE_URL="${CODEX_BASE_URL:-http://gpu6:18763/v1}"
MODEL="${CODEX_MODEL:-qwen3.8-27b}"
CODEX_BIN="${CODEX_BIN:-/public1/home/stu52275901007/.local/bin/codex}"

AGENT_CPUS="${AGENT_CPUS:-4}"
export CODEX_AGENT_CPUS="$AGENT_CPUS"
if [ "$AGENT_CPUS" -gt 0 ]; then
  export OMP_NUM_THREADS="$AGENT_CPUS"
  export OPENBLAS_NUM_THREADS="$AGENT_CPUS"
  export MKL_NUM_THREADS="$AGENT_CPUS"
  export NUMEXPR_NUM_THREADS="$AGENT_CPUS"
  export LOKY_MAX_CPU_COUNT="$AGENT_CPUS"
fi

DEEPSEEK_BASE_URL="${DEEPSEEK_BASE_URL:-https://api.deepseek.com}"
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:?export DEEPSEEK_API_KEY before running this script}"
EXPERT_MODEL="${EXPERT_MODEL:-deepseek-flash}"
EXPERT_BASE_URL="${EXPERT_BASE_URL:-$DEEPSEEK_BASE_URL}"
EXPERT_API_KEY="${EXPERT_API_KEY:-$DEEPSEEK_API_KEY}"
JUDGE_MODEL="${JUDGE_MODEL:-$MODEL}"
JUDGE_BASE_URL="${JUDGE_BASE_URL:-$BASE_URL}"
JUDGE_API_KEY="${JUDGE_API_KEY:-EMPTY}"

export INTERACTION_RUNAWAY_GUARD="${INTERACTION_RUNAWAY_GUARD:-1}"
export CODEX_MODEL="$MODEL"
export CODEX_BASE_URL="$BASE_URL"
export CODEX_BIN
export CODEX_REASONING_EFFORT="${CODEX_REASONING_EFFORT:-low}"
export CODEX_MODEL_VERBOSITY=low
export CODEX_JSON_LOG="${CODEX_JSON_LOG:-0}"

SAMPLING_SEED="${SAMPLING_SEED:-}"
SAMPLING_SEED_ARG=""
if [ -n "$SAMPLING_SEED" ]; then
  SAMPLING_SEED_ARG="--sampling-seed $SAMPLING_SEED"
fi

EVIDENCE_ROOT="${EVIDENCE_ROOT:-$REPO/openclaw_experiments/evolve_exp/draft_mmbench}"
TRAIN_EVIDENCE_ROOT="${TRAIN_EVIDENCE_ROOT:-$REPO/openclaw_experiments/evolve_exp/draft_mmbench_train}"
EVIDENCE_ROOTS="$EVIDENCE_ROOT $TRAIN_EVIDENCE_ROOT"
EXPECTED_EVIDENCE="${EXPECTED_EVIDENCE:-35}"

NAME="${1:?usage: launch_codex_evolution_from_scratch.sh <experiment-name> [max-rounds]}"
ROUNDS="${2:-5}"
ROUND0_ONLY=""
if [ "$ROUNDS" -eq 0 ]; then
  ROUND0_ONLY="--round0-only"
  ROUNDS=1
fi

JUDGE_REPEATS="${JUDGE_REPEATS:-3}"
export MMBENCH_JUDGE_PARALLEL_DIMENSIONS="${MMBENCH_JUDGE_PARALLEL_DIMENSIONS:-1}"

# Validation-only replay: four pinned validation problems, four repetitions,
# hence sixteen independent Codex solver runs in the round-0 phase.
export MMBENCH_PIN_VALIDATION="${MMBENCH_PIN_VALIDATION:-2020_B,2020_D,2020_E,2020_F}"
VALIDATION_REPETITIONS="${VALIDATION_REPETITIONS:-4}"

EXP="$REPO/openclaw_experiments/evolve_exp/$NAME"
LOG="$REPO/.env_setup_logs/$NAME.log"
mkdir -p "$REPO/.env_setup_logs"

entries=0
missing=0
for root in $EVIDENCE_ROOTS; do
  if [ ! -d "$root" ]; then
    echo "Evidence root does not exist: $root" >&2
    exit 2
  fi
  entries=$((entries + $(find "$root" -path "*/output/data/external_data.md" -size +0c | wc -l)))
  missing=$((missing + $(find "$root" -path "*/output/data/external_data.md" -type f -empty | wc -l)))
done
echo "Evidence pools: $entries tasks, $missing without external_data.md" | tee -a "$LOG"
if [ "$entries" -lt "$EXPECTED_EVIDENCE" ]; then
  echo "Refusing to start: evidence pools hold $entries of $EXPECTED_EVIDENCE tasks." >&2
  exit 3
fi
if [ "$missing" -gt 0 ]; then
  echo "Refusing to start: $missing task(s) have no evidence to reuse." >&2
  exit 4
fi

cd "$REPO"
echo "[launch] $(date) (Codex evolution from scratch; reasoning=${CODEX_REASONING_EFFORT})" | tee -a "$LOG"

setsid nohup "$PY" -m src.OpenClaw.run_substantive_interaction_workflow_evolution_from_scratch_codex \
  --exp "$EXP" \
  --benchmark mmbench \
  --mmbench-root "$REPO/data/MMBench" \
  --planning-draft-root $EVIDENCE_ROOTS \
  --fixed-rubric "$REPO/src/OpenClaw/interaction_initial_substantive_v1.json" \
  --baseline-report-root "$REPO" \
  --model "$MODEL" \
  --opt-model "$MODEL" --opt-base-url "$BASE_URL" --opt-api-key EMPTY \
  --expert-model "$EXPERT_MODEL" --expert-base-url "$EXPERT_BASE_URL" --expert-api-key "$EXPERT_API_KEY" \
  --judge-feedback-model "$MODEL" \
  --mmbench-judge-model "$JUDGE_MODEL" --mmbench-judge-base-url "$JUDGE_BASE_URL" --mmbench-judge-api-key "$JUDGE_API_KEY" \
  --max-rounds "$ROUNDS" $ROUND0_ONLY $SAMPLING_SEED_ARG \
  --judge-repeats "$JUDGE_REPEATS" \
  --train-batch-size 2 \
  --validation-size "${VALIDATION_SIZE:-4}" \
  --validation-repetitions "$VALIDATION_REPETITIONS" \
  --thinking off \
  >> "$LOG" 2>&1 &

echo "launcher pid=$! experiment=$EXP max_rounds=$ROUNDS log=$LOG"
