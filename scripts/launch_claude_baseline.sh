#!/bin/bash
# Launch the Claude Code no-interaction baseline.
#
#   bash scripts/launch_claude_baseline.sh <experiment-name>
#
# This is the comparison arm for launch_claude_evolution.sh: same draft pool,
# same solver prompt, same submission contract, one round, and the only
# difference is that the prompt has no `# Human Expert Interaction` section.  The
# harness side of that is not a prompt edit alone -- the clean-baseline module
# already runs the solver without starting the expert bridge and without the
# interaction gate, which is why this is built on it rather than on the evolution
# launcher.
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
BASE_URL=http://gpu6:18763/v1
MODEL=qwen3.8-27b

# The MM-Bench judge stays on the locally served model, matching the interactive
# arm (a DeepSeek judge was reverted: its reply format broke MM-Bench's parser).
# The solver is local as well.
JUDGE_MODEL="${JUDGE_MODEL:-$MODEL}"
JUDGE_BASE_URL="${JUDGE_BASE_URL:-$BASE_URL}"
JUDGE_API_KEY="${JUDGE_API_KEY:-EMPTY}"

DRAFT_ROOT="${DRAFT_ROOT:-$REPO/openclaw_experiments/evolve_exp/draft_mmbench}"
EXPECTED_DRAFTS="${EXPECTED_DRAFTS:-5}"
# Satisfies the launcher's start-up existence check only: the clean-baseline
# module resolves drafts for the requested problems alone, so this stays empty
# unless the split is being exercised only in part.
EXTRA_DRAFT_ROOTS="${EXTRA_DRAFT_ROOTS:-}"
# MMBENCH_VALIDATION_PROBLEMS.
PROBLEMS="${PROBLEMS:-2020_B 2020_C 2020_D 2020_E 2020_F}"

NAME="${1:?usage: launch_claude_baseline.sh <experiment-name>}"

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

if [ ! -d "$DRAFT_ROOT" ]; then
  echo "Draft root does not exist: $DRAFT_ROOT" >&2
  exit 2
fi
# A draft directory is named after its run, not its problem, so the problem is
# read from meta/run.json -- the same field the launcher's resolver uses.
# shellcheck disable=SC2086 -- the problem list is deliberately word-split
missing=$("$PY" - "$DRAFT_ROOT" $PROBLEMS <<'PY'
import json, pathlib, sys
root, wanted = pathlib.Path(sys.argv[1]), sys.argv[2:]
found = {}
for meta in root.glob("**/meta/run.json"):
    try:
        problem_id = json.loads(meta.read_text(encoding="utf-8")).get("problem_id")
    except (OSError, ValueError):
        continue
    if not isinstance(problem_id, str):
        continue
    output = meta.parent.parent / "output"
    draft = output / "results" / "draft.md"
    evidence = output / "data" / "external_data.md"
    if draft.is_file() and draft.read_text(encoding="utf-8", errors="replace").strip():
        found[problem_id] = evidence.is_file() and bool(
            evidence.read_text(encoding="utf-8", errors="replace").strip()
        )
bad = 0
for problem in wanted:
    if problem not in found:
        print(f"No draft for {problem} under {root}", file=sys.stderr)
        bad += 1
    elif not found[problem]:
        print(f"Draft for {problem} has no data/external_data.md", file=sys.stderr)
        bad += 1
print(bad)
PY
)
echo "Draft pool: $(echo $PROBLEMS | wc -w) requested, $missing unusable" | tee -a "$LOG"
if [ "$missing" -gt 0 ]; then
  echo "Refusing to start: $missing requested problem(s) lack a usable draft." >&2
  exit 3
fi
if [ "$(echo $PROBLEMS | wc -w)" -lt "$EXPECTED_DRAFTS" ]; then
  echo "Refusing to start: run covers $(echo $PROBLEMS | wc -w) of $EXPECTED_DRAFTS problems." >&2
  exit 4
fi

cd "$REPO"
echo "[launch] $(date)" | tee -a "$LOG"

# shellcheck disable=SC2086 -- problem list and extra roots are word-split
setsid nohup "$PY" -m src.OpenClaw.run_substantive_interaction_strategy_clean_baseline \
  --exp "$EXP" \
  --max-rounds 1 \
  --benchmark mmbench \
  --mmbench-root "$REPO/data/MMBench" \
  --agent-backend claude \
  --planning-draft-root "$DRAFT_ROOT" $EXTRA_DRAFT_ROOTS \
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
