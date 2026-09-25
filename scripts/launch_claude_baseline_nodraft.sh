#!/bin/bash
# Launch the Claude Code clean baseline WITHOUT a planning draft.
#
#   bash scripts/launch_claude_baseline_nodraft.sh <experiment-name>
#
# Same arm as launch_claude_baseline.sh -- one round, no expert interaction, the
# same MM-Bench judge wiring -- except that no draft is staged and the solver is
# handed the problem statement alone.  That is the behaviour the openclaw
# backend has always had; the claude runner insisted on a draft root until the
# clean-baseline module grew the draft-free path, so this launcher drops the
# draft pool entirely and pins the task list with --problem-id instead.
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
BASE_URL=http://gpu6:18763/v1
MODEL=qwen3.8-27b

# claude_backend takes its endpoint from the environment, not from --model or
# --base-url: claude_command() only falls back to DEFAULT_MODEL/DEFAULT_BASE_URL
# when CLAUDE_MODEL/CLAUDE_BASE_URL are unset, so without these the arm would
# quietly ignore MODEL/BASE_URL above.  Set here so the solver is the same local
# model the other baselines run.
export CLAUDE_MODEL="$MODEL"
export CLAUDE_BASE_URL="$BASE_URL"
# A failed auto-update has deleted this CLI's own binary twice in one day, and a
# claude session cannot be started while that is true.  A long run should not
# depend on it not happening again.
export DISABLE_AUTOUPDATER=1

# The MM-Bench judge stays on the locally served model, matching the interactive
# and draft-based arms (a DeepSeek judge was reverted: its reply format broke
# MM-Bench's parser).
JUDGE_MODEL="${JUDGE_MODEL:-$MODEL}"
JUDGE_BASE_URL="${JUDGE_BASE_URL:-$BASE_URL}"
JUDGE_API_KEY="${JUDGE_API_KEY:-EMPTY}"

# MMBENCH_VALIDATION_PROBLEMS.
PROBLEMS="${PROBLEMS:-2020_B 2020_C 2020_D 2020_E 2020_F}"
# Read for its evidence only: the solver is handed each problem's pre-gathered
# data/external_data.md, never the draft's own proposed solution, and is told not
# to search for anything else.
DRAFT_ROOT="${DRAFT_ROOT:-$REPO/openclaw_experiments/evolve_exp/draft_mmbench}"

NAME="${1:?usage: launch_claude_baseline_nodraft.sh <experiment-name>}"

# Score each problem three times and average, so a per-problem score carries a
# spread instead of being one sample.  Trials are independent and the judge runs
# them concurrently, so this costs concurrency on the endpoint, not wall clock.
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

# This arm is meant to start clean.  The runner only checks a resumed
# --exp directory for a matching experiment type, benchmark and task list, so an
# accidental reuse would silently continue an older run instead of measuring a
# fresh one.
if [ -f "$EXP/config.json" ] || [ -f "$EXP/runs/config.json" ]; then
  echo "Refusing to start: $EXP already holds a clean baseline; use a new name." >&2
  exit 2
fi

if [ ! -d "$DRAFT_ROOT" ]; then
  echo "Draft root does not exist: $DRAFT_ROOT" >&2
  exit 3
fi
# The prompt tells the solver to read data/external_data.md and forbids searching,
# so a problem missing it would be scored on evidence it never received.  The
# runner raises on the same condition; failing here names the problem first.
# shellcheck disable=SC2086 -- the problem list is deliberately word-split
missing=$("$PY" - "$DRAFT_ROOT" $PROBLEMS <<'PY'
import json, pathlib, sys
root, wanted = pathlib.Path(sys.argv[1]), sys.argv[2:]
found = set()
for meta in root.glob("**/meta/run.json"):
    try:
        problem_id = json.loads(meta.read_text(encoding="utf-8")).get("problem_id")
    except (OSError, ValueError):
        continue
    if not isinstance(problem_id, str) or problem_id not in wanted:
        continue
    evidence = meta.parent.parent / "output" / "data" / "external_data.md"
    if evidence.is_file() and evidence.read_text(encoding="utf-8", errors="replace").strip():
        found.add(problem_id)
for problem in wanted:
    if problem not in found:
        print(f"No usable data/external_data.md for {problem} under {root}", file=sys.stderr)
print(len(set(wanted) - found))
PY
)
if [ "$missing" -gt 0 ]; then
  echo "Refusing to start: $missing requested problem(s) have no evidence to reuse." >&2
  exit 4
fi

cd "$REPO"
echo "[launch] $(date)" | tee -a "$LOG"

# shellcheck disable=SC2086 -- the problem list is deliberately word-split
setsid nohup "$PY" -m src.OpenClaw.run_substantive_interaction_strategy_clean_baseline \
  --exp "$EXP" \
  --max-rounds 1 \
  --benchmark mmbench \
  --mmbench-root "$REPO/data/MMBench" \
  --agent-backend claude \
  --planning-draft-root "$DRAFT_ROOT" \
  --reuse-draft-data \
  --problem-id $PROBLEMS \
  --model "$MODEL" \
  --mmbench-judge-model "$JUDGE_MODEL" \
  --mmbench-judge-base-url "$JUDGE_BASE_URL" \
  --mmbench-judge-api-key "$JUDGE_API_KEY" \
  --judge-repeats "$JUDGE_REPEATS" \
  --thinking off \
  --concurrency 5 \
  >> "$LOG" 2>&1 &

echo "launcher pid=$!  experiment=$EXP  log=$LOG"
