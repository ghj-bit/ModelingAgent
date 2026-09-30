#!/bin/bash
# Launch one Claude Code-backed *co-evolution* experiment whose solver starts
# from the problem statement alone.
#
#   bash scripts/launch_claude_coevolution.sh <experiment-name> [max-rounds]
#
# The same pipeline as launch_claude_evolution_from_scratch.sh -- same evidence
# pools, same frozen seed, same prompts, same gates, same concurrency -- with one
# addition: after a round's training-parent runs finish and before the candidate
# is evolved, an LLM critic scores each parent's interaction (policy text +
# recorded expert consultation + recorded post-reply change) against the active
# rubric (src/OpenClaw/interaction_strategy_rubric_v7.md by default -- one
# criterion to start, one appended per round; override
# with CRITIC_RUBRIC), and that review is appended to the workflow-evolution
# prompt as one extra evidence node.  Nothing else the optimizer receives
# changes, and the critic never touches the utility or a gate.
#
# The critic is the only difference between this arm and the from-scratch arm:
# the launcher composes the other arm's hooks rather than copying them, so the
# two stay in step.
#
# The review lands next to the round as workflows/round_N/critic_review.{json,md}.
# The critic endpoint defaults to the MM-Bench judge role; override with
# CRITIC_MODEL / CRITIC_BASE_URL / CRITIC_API_KEY / CRITIC_TIMEOUT.
#
# Nothing precedes the run.  The solver is handed the problem statement and the
# task's pre-gathered data/external_data.md, and owns the modeling plan itself;
# no prompt section, step or policy line refers to a prior plan.  The evidence is
# read out of the planner runs' directories -- that is where it was collected --
# and the engine's own flag for those directories is --planning-draft-root, so
# that flag carries the evidence pools below.  Nothing reads a plan file: only
# <pool>/<run>/output/data/external_data.md is copied.
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
# The local solver/optimizer/judge run on the FP8 build since 2026-09-26, the
# same server the from-scratch arm uses.  Measured with the same benchmark
# harness as bench/RESULTS.md: at TP=2 the single-stream decode rate went
# 23.8 -> 40.2 tok/s and the 8-way rate 116 -> 233 tok/s, because on this SM 8.6
# hardware vLLM keeps FP8 weights 8-bit and streams them through the Marlin
# weight-only kernel -- and this workload is decode/bandwidth bound.  The KV
# pool at equal GPU_UTIL also doubles (83k -> 173k tokens per replica), which is
# what raises how many solving agents fit at once.
#
# The name is deliberately not "qwen3.8-27b": the served name is what lands in
# each run's config.json, so an FP8 run must not be confusable with a bf16 one.
# Override BASE_URL/MODEL in the environment to go back to the bf16 server.
BASE_URL="${BASE_URL:-http://gpu6:18764/v1}"
MODEL="${MODEL:-qwen3.8-27b-fp8}"

# The human expert runs on DeepSeek.  The MM-Bench judge stays on the locally
# served model: a DeepSeek judge was reverted because its reply format broke
# MM-Bench's parser.  The critic is on the local model too -- see below.
DEEPSEEK_BASE_URL="${DEEPSEEK_BASE_URL:-https://api.deepseek.com}"
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:?export DEEPSEEK_API_KEY before running this script}"
EXPERT_MODEL="${EXPERT_MODEL:-deepseek-flash}"
EXPERT_BASE_URL="${EXPERT_BASE_URL:-$DEEPSEEK_BASE_URL}"
EXPERT_API_KEY="${EXPERT_API_KEY:-$DEEPSEEK_API_KEY}"
JUDGE_MODEL="${JUDGE_MODEL:-$MODEL}"
JUDGE_BASE_URL="${JUDGE_BASE_URL:-$BASE_URL}"
JUDGE_API_KEY="${JUDGE_API_KEY:-EMPTY}"

# The optimizer stays on the same local server as the solver.  It used to share
# `--opt-model "$MODEL"` directly; the three names below only make the role
# overridable, so a DeepSeek optimizer can be tried with
# `OPT_MODEL=deepseek-flash OPT_BASE_URL=https://api.deepseek.com OPT_API_KEY=...`
# without editing the launcher.  Note what a weak optimizer costs here: the call
# re-emits the whole ~4.7 KB policy with a targeted patch, and the FP8 build
# answered with the parent text unchanged on 11 of 19 attempts in
# claude_fp8_judgefb_r10 -- which is what killed that run at round 6.
OPT_MODEL="${OPT_MODEL:-$MODEL}"
OPT_BASE_URL="${OPT_BASE_URL:-$BASE_URL}"
OPT_API_KEY="${OPT_API_KEY:-EMPTY}"

# claude_backend takes its endpoint from the environment, not from --model or
# --base-url, so without these the arm would fall back to the backend's own
# defaults rather than to what is configured here.  Same values as the flags
# above, so the solver and the optimizer share one endpoint.
export CLAUDE_MODEL="$MODEL"
export CLAUDE_BASE_URL="$BASE_URL"
export CLAUDE_API_KEY="$JUDGE_API_KEY"

# The critic runs on the same local FP8 server as the solver and the optimizer.
# It used to sit on DeepSeek, on the grounds that its output is parsed by our own
# tolerant reader and a failure is never fatal, so it did not need the stability
# the judge requires.  Keeping it local instead makes the arm one endpoint
# lighter and puts the review on the model that also writes the policies, which
# is what the rubric is meant to measure.  Set CRITIC_MODEL/CRITIC_BASE_URL to
# point it somewhere else; the module's own fallback is the same local role.
export CRITIC_MODEL="${CRITIC_MODEL:-$MODEL}"
export CRITIC_BASE_URL="${CRITIC_BASE_URL:-$BASE_URL}"
export CRITIC_API_KEY="${CRITIC_API_KEY:-EMPTY}"

# The rubric proposer runs on the optimizer endpoint: revising the measuring
# stick is an optimization step, not a review step, so it stays on the model
# that also writes the policies.  It only runs for rounds that reached the
# validation split -- see src/OpenClaw/interaction_rubric_proposer.py.
export RUBRIC_MODEL="${RUBRIC_MODEL:-$MODEL}"
export RUBRIC_BASE_URL="${RUBRIC_BASE_URL:-$BASE_URL}"
export RUBRIC_API_KEY="${RUBRIC_API_KEY:-EMPTY}"

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

# The arm's seed, as a policy file rather than the built-in seed the launcher
# carries.  Both claude arms read this one knob, so this script and
# launch_claude_evolution_from_scratch.sh can start from the same policy; the
# file here is the information-gap policy, whose strategy section admits a gap
# only if it cannot be derived, would branch the work, and has a landing place.
# Point it at another workflow JSON to seed from that, or set it explicitly
# empty to fall back to the built-in OPERATOR_DRIVEN_CONSULTATION seed.  A
# resumed experiment ignores it: the seed already written into the experiment
# directory wins.
export INTERACTION_INITIAL_WORKFLOW_JSON="${INTERACTION_INITIAL_WORKFLOW_JSON-$REPO/openclaw_experiments/exp_prompt/initial_interaction_workflow_info_first.json}"

# Foreground command budget, lowered from the 30 minutes run_claude_task.py
# defaults to.  Trial, not a settled setting -- the value it replaces was itself
# chosen against evidence: run_claude_task.py records that a 5-minute default
# was tried before and killed a `sleep 420 && tail progress.log` poll at 300 s,
# because the solver treats the default as its own budget (49 of 50 Bash calls
# leave the timeout unset).  Lower it only while chasing a specific runaway:
# this run spent 30 minutes and ~180 GB on an array that gained an axis per loop
# pass, and the point of the shorter cap is that the agent is handed control at
# the moment the command turns expensive instead of half an hour later.
# Raise it back to 1800000 to restore the default.
export BASH_DEFAULT_TIMEOUT_MS="${BASH_DEFAULT_TIMEOUT_MS:-300000}"
export BASH_MAX_TIMEOUT_MS="${BASH_MAX_TIMEOUT_MS:-300000}"

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

NAME="${1:?usage: launch_claude_coevolution.sh <experiment-name> [max-rounds]}"
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
echo "[launch] $(date)  (co-evolution from scratch: critic in the loop)" | tee -a "$LOG"

setsid nohup "$PY" -m src.OpenClaw.run_substantive_interaction_workflow_evolution_from_initial_draft_claude_critic \
  --exp "$EXP" \
  --benchmark mmbench \
  --mmbench-root "$REPO/data/MMBench" \
  --planning-draft-root $EVIDENCE_ROOTS \
  --fixed-rubric "$REPO/src/OpenClaw/interaction_initial_substantive_v1.json" \
  --baseline-report-root "$REPO" \
  --model "$MODEL" \
  --opt-model "$OPT_MODEL"  --opt-base-url "$OPT_BASE_URL"  --opt-api-key "$OPT_API_KEY" \
  --expert-model "$EXPERT_MODEL" --expert-base-url "$EXPERT_BASE_URL" --expert-api-key "$EXPERT_API_KEY" \
  --judge-feedback-model "$MODEL" \
  --mmbench-judge-model "$JUDGE_MODEL" --mmbench-judge-base-url "$JUDGE_BASE_URL" --mmbench-judge-api-key "$JUDGE_API_KEY" \
  --max-rounds "$ROUNDS" $ROUND0_ONLY $SAMPLING_SEED_ARG \
  --judge-repeats "$JUDGE_REPEATS" \
  --train-batch-size 3 \
  --validation-size "${VALIDATION_SIZE:-8}" \
  --validation-repetitions "${VALIDATION_REPETITIONS:-1}" \
  --thinking off \
  >> "$LOG" 2>&1 &

echo "launcher pid=$!  experiment=$EXP  max_rounds=$ROUNDS  log=$LOG"
