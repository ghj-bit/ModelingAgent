#!/bin/bash
# Launch one Claude Code-backed interaction-workflow evolution whose solver
# starts from the problem statement alone.
#
#   bash scripts/launch_claude_evolution_from_scratch.sh <experiment-name> [max-rounds]
#
# Same engine, gates, utility, judge and evolution prompt as
# launch_claude_evolution.sh, with two differences:
#
#   * Nothing precedes the run.  The solver is handed the problem statement and
#     the task's pre-gathered data/external_data.md, and owns the modeling plan
#     itself; no prompt section, step or policy line refers to a prior plan.
#   * The initial interaction policy is the arm's own seed,
#     interaction_policy.STRATEGIC_DECISION_CONSULTATION, plus one paragraph
#     telling the solver to keep the consultation proportionate: the expert
#     settles at most one strategic decision and the modeling work is still
#     owed in full.  The paragraph lives in the from-scratch module, not in the
#     policy text, so the optimizer cannot rewrite it away.
#
# The evidence is read out of the planner runs' directories -- that is where it
# was collected -- and the engine's own flag for those directories is
# --planning-draft-root, so that flag carries the evidence pools below.  Nothing
# reads a plan file: only <pool>/<run>/output/data/external_data.md is copied.
#
# Everything downstream -- training/validation split, acceptance margins,
# judge repeats, the evolution prompt -- is the other arm's default.  Override
# the pools with MMBENCH_TRAIN_POOL / MMBENCH_PIN_VALIDATION, and note that
# MMBENCH_PIN_VALIDATION must be paired with --validation-size equal to its
# length (the engine checks the two).
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python

# Solver, optimizer, judge-feedback and MM-Bench judge are served locally; the
# human expert is the only model on DeepSeek.  Everything was pointed at DeepSeek
# for the night of 2026-09-25 and rolled back within the hour: the per-token
# cost of 16-20 concurrent agent sessions is real, and the judge's reply format
# had already been the reason a DeepSeek judge was reverted once before.
#
# The agent CPU budget below is what actually fixed the saturation that started
# the experiment -- the model's location never was the cause.
DEEPSEEK_BASE_URL="${DEEPSEEK_BASE_URL:-https://api.deepseek.com}"
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:?export DEEPSEEK_API_KEY before running this script}"
# The local solver/optimizer/judge run on the FP8 build since 2026-09-26.
# Measured with the same benchmark harness as bench/RESULTS.md: at TP=2 the
# single-stream decode rate went 23.8 -> 40.2 tok/s and the 8-way rate
# 116 -> 233 tok/s, because on this SM 8.6 hardware vLLM keeps FP8 weights
# 8-bit and streams them through the Marlin weight-only kernel -- and this
# workload is decode/bandwidth bound.  The KV pool at equal GPU_UTIL also
# doubles (83k -> 173k tokens per replica), which is what raises how many
# solving agents fit at once.
#
# The name is deliberately not "qwen3.8-27b": the served name is what lands in
# each run's config.json, so an FP8 run must not be confusable with a bf16 one.
# Override BASE_URL/MODEL in the environment to go back to the bf16 server.
BASE_URL="${BASE_URL:-http://gpu6:18764/v1}"
MODEL="${MODEL:-qwen3.8-27b-fp8}"
EXPERT_MODEL="${EXPERT_MODEL:-deepseek-flash}"
EXPERT_BASE_URL="${EXPERT_BASE_URL:-$DEEPSEEK_BASE_URL}"
EXPERT_API_KEY="${EXPERT_API_KEY:-$DEEPSEEK_API_KEY}"
JUDGE_MODEL="${JUDGE_MODEL:-$MODEL}"
JUDGE_BASE_URL="${JUDGE_BASE_URL:-$BASE_URL}"
JUDGE_API_KEY="${JUDGE_API_KEY:-EMPTY}"

# claude_backend takes its endpoint from the environment, not from --model or
# --base-url, so without these the arm would fall back to the backend's own
# defaults rather than to what is configured here.  Same values as the flags
# above, so the solver and the optimizer share one endpoint.
export CLAUDE_MODEL="$MODEL"
export CLAUDE_BASE_URL="$BASE_URL"
export CLAUDE_API_KEY="$JUDGE_API_KEY"

# CPU budget per solving agent.  Agents write numpy/sklearn/pandas pipelines,
# and those default to every core on the box: measured 2026-09-25, one run's
# text-sentiment script opened 127 threads and held 59 of 104 cores, which
# starved the other 19 runs of the same phase and every other user of the shared
# login node.  Two independent limits, because neither is sufficient alone:
#
#   * CLAUDE_AGENT_CPUS makes run_claude_task.py pin the session -- and every
#     process it spawns, since children inherit the affinity mask -- to that many
#     CPUs.  This is the hard cap: it holds even for multiprocessing pools, which
#     thread-count variables cannot touch.
#   * The thread-count variables size the libraries' pools to the pinned CPUs, so
#     work inside the lane runs at full speed instead of thrashing; BLAS and
#     joblib both read them, and joblib is what sklearn's n_jobs=-1 ends up in.
#
# Raise AGENT_CPUS for faster single runs, lower it to fit more runs side by side;
# 0 disables the pin entirely.
AGENT_CPUS="${AGENT_CPUS:-4}"
export CLAUDE_AGENT_CPUS="$AGENT_CPUS"
if [ "$AGENT_CPUS" -gt 0 ]; then
  export OMP_NUM_THREADS="$AGENT_CPUS"
  export OPENBLAS_NUM_THREADS="$AGENT_CPUS"
  export MKL_NUM_THREADS="$AGENT_CPUS"
  export NUMEXPR_NUM_THREADS="$AGENT_CPUS"
  export LOKY_MAX_CPU_COUNT="$AGENT_CPUS"
fi

# This arm's policy no longer carries the "keep every run bounded" clause (the
# seed text is the plain one), so the solver-side guard against whole-disk
# searches and 30-minute foreground commands is on by default here.  Set to 0 to
# drop that paragraph from the prompt.
export INTERACTION_RUNAWAY_GUARD="${INTERACTION_RUNAWAY_GUARD:-1}"

# Optional: pin the CPE sampling seed, so a re-run draws the same training
# batches in the same order as the run it is compared against.
SAMPLING_SEED="${SAMPLING_SEED:-}"
SAMPLING_SEED_ARG=""
if [ -n "$SAMPLING_SEED" ]; then
  SAMPLING_SEED_ARG="--sampling-seed $SAMPLING_SEED"
fi

# The evidence pools: the planner runs' directories, where each task's
# data/external_data.md was collected.  Every problem the run may sample needs a
# non-empty one in one of these roots; nothing else in them is read.  The
# validation and train pools were generated separately, so both are listed.
EVIDENCE_ROOT="${EVIDENCE_ROOT:-$REPO/openclaw_experiments/evolve_exp/draft_mmbench}"
TRAIN_EVIDENCE_ROOT="${TRAIN_EVIDENCE_ROOT:-$REPO/openclaw_experiments/evolve_exp/draft_mmbench_train}"
EVIDENCE_ROOTS="$EVIDENCE_ROOT $TRAIN_EVIDENCE_ROOT"
EXPECTED_EVIDENCE="${EXPECTED_EVIDENCE:-35}"

NAME="${1:?usage: launch_claude_evolution_from_scratch.sh <experiment-name> [max-rounds]}"
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

# Score each problem three times and average: CPE compares candidates against an
# incumbent by a margin, and that comparison is meaningless without knowing how
# much the score moves on its own.
JUDGE_REPEATS="${JUDGE_REPEATS:-3}"
export MMBENCH_JUDGE_PARALLEL_DIMENSIONS="${MMBENCH_JUDGE_PARALLEL_DIMENSIONS:-1}"

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
echo "[launch] $(date)  (evolution from scratch)" | tee -a "$LOG"

setsid nohup "$PY" -m src.OpenClaw.run_substantive_interaction_workflow_evolution_from_scratch_claude \
  --exp "$EXP" \
  --benchmark mmbench \
  --mmbench-root "$REPO/data/MMBench" \
  --planning-draft-root $EVIDENCE_ROOTS \
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
  --validation-repetitions "${VALIDATION_REPETITIONS:-1}" \
  --thinking off \
  >> "$LOG" 2>&1 &

echo "launcher pid=$!  experiment=$EXP  max_rounds=$ROUNDS  log=$LOG"
