#!/bin/bash
# Run one Claude Code task against rightapi's gpt-5.6-sol, in the background.
#
#   bash scripts/launch_claude_gpt56.sh <workspace-dir> "<prompt text>" [model] [effort]
#
# Same chain as every other claude-backend run -- run_claude_task.py starts the
# Anthropic-to-OpenAI shim on a free port, points Claude Code at it inside a
# throwaway CLAUDE_CONFIG_DIR, and streams the session to a log -- with the
# upstream switched to the codex key's chat-completions channel.
#
# Why this channel: codex's own config (``~/.codex/config.toml``) uses
# ``gpt-5.6-sol`` with ``model_reasoning_effort = "high"`` over the Responses
# wire API at ``https://rightapi.ai/codex/v1``.  Claude Code cannot speak that
# shape, but the same key answers on ``https://rightapi.ai/v1`` chat completions
# with tools and streaming (measured 2026-09-30), so the existing shim reaches
# the same model; ``--reasoning-effort high`` is what carries the "high" half of
# the codex setting, on the field the OpenAI shape defines for it.
#
# The key is read from ``~/.codex/auth.json`` and exported, not passed as an
# argument: arguments are readable by every user on the box.
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
CLAUDE_BIN="${CLAUDE_BIN:-$HOME/.local/bin/claude}"

WS_RAW="${1:?usage: launch_claude_gpt56.sh <workspace-dir> \"<prompt text>\" [model] [effort]}"
PROMPT_TEXT="${2:?usage: launch_claude_gpt56.sh <workspace-dir> \"<prompt text>\" [model] [effort]}"
MODEL="${3:-gpt-5.6-sol}"
EFFORT="${4:-high}"
BASE_URL="${GPT56_BASE_URL:-https://rightapi.ai/v1}"

WS="$(realpath -m "$WS_RAW")"
mkdir -p "$WS/meta/claude"
printf '%s\n' "$PROMPT_TEXT" > "$WS/prompt.md"

OPENCLAW_UPSTREAM_API_KEY="$(
  "$PY" -c "import json,pathlib;print(json.loads((pathlib.Path.home()/'.codex/auth.json').read_text())['OPENAI_API_KEY'])"
)"
if [ -z "$OPENCLAW_UPSTREAM_API_KEY" ]; then
  echo "No key in ~/.codex/auth.json (OPENAI_API_KEY) -- codex must be logged in first." >&2
  exit 2
fi
export OPENCLAW_UPSTREAM_API_KEY

# Agents here write numpy/sklearn pipelines that default to every core; the pin
# keeps one task from starving the box (same reasoning as the evolution
# launchers, and the same numbers).
AGENT_CPUS="${AGENT_CPUS:-4}"
export CLAUDE_AGENT_CPUS="$AGENT_CPUS"
export OMP_NUM_THREADS="$AGENT_CPUS" OPENBLAS_NUM_THREADS="$AGENT_CPUS" \
       MKL_NUM_THREADS="$AGENT_CPUS" NUMEXPR_NUM_THREADS="$AGENT_CPUS" \
       LOKY_MAX_CPU_COUNT="$AGENT_CPUS"

echo "[launch] $(date)  model=$MODEL effort=$EFFORT upstream=$BASE_URL" > "$WS/run.log"

setsid nohup "$PY" "$REPO/src/OpenClaw/claude_backend/run_claude_task.py" \
  --prompt-file "$WS/prompt.md" \
  --workspace "$WS" \
  --persistence-dir "$WS/meta/claude" \
  --model "$MODEL" \
  --upstream-model "$MODEL" \
  --base-url "$BASE_URL" \
  --reasoning-effort "$EFFORT" \
  --claude-bin "$CLAUDE_BIN" \
  --timeout "${TIMEOUT:-3600}" \
  --permission-mode acceptEdits \
  --allowed-tools Bash,Read,Write,Edit,MultiEdit,Glob,Grep,LS,WebFetch,WebSearch,NotebookEdit,TodoWrite \
  --autocompact "${AUTOCOMPACT:-180k}" \
  >> "$WS/run.log" 2>&1 &

echo "pid=$!  workspace=$WS  log=$WS/run.log"
echo "tail -f $WS/run.log"
