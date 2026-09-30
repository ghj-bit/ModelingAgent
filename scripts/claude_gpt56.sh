#!/bin/bash
# One command: a Claude Code session on rightapi's gpt-5.6-sol (reasoning high).
#
#   bash scripts/claude_gpt56.sh                  # 交互式会话
#   bash scripts/claude_gpt56.sh -p "问题"        # 非交互，同一套环境
#
# Arguments are passed straight through to ``claude``.  Everything else is
# automatic: the key is read from codex's own credential file, the
# Anthropic-to-OpenAI shim is started on a free port, Claude Code is pointed at
# it, and the shim is stopped again when the session ends.
#
# Overridable: MODEL, EFFORT, BASE_URL, CLAUDE_BIN, CLAUDE_GPT56_LOG.
# The upstream facts behind this (which channel answers, what carries "high")
# are recorded in scripts/launch_claude_gpt56.sh.
set -euo pipefail

REPO=/public1/home/stu52275901007/workspace/ghj_workspace/ModelingAgent
PY=/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python
MODEL="${MODEL:-gpt-5.6-sol}"
EFFORT="${EFFORT:-high}"
BASE_URL="${BASE_URL:-https://rightapi.ai/v1}"
CLAUDE_BIN="${CLAUDE_BIN:-$HOME/.local/bin/claude}"

OPENCLAW_UPSTREAM_API_KEY="$(
  "$PY" -c "import json,pathlib;print(json.loads((pathlib.Path.home()/'.codex/auth.json').read_text())['OPENAI_API_KEY'])"
)"
if [ -z "$OPENCLAW_UPSTREAM_API_KEY" ]; then
  echo "No key in ~/.codex/auth.json (OPENAI_API_KEY) -- log codex in first." >&2
  exit 2
fi
export OPENCLAW_UPSTREAM_API_KEY

port="$("$PY" -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1]);s.close()')"
log="${CLAUDE_GPT56_LOG:-/tmp/claude_gpt56_shim_${port}.log}"

"$PY" "$REPO/src/OpenClaw/claude_backend/proxy.py" \
  --upstream "$BASE_URL" --port "$port" --model "$MODEL" \
  --reasoning-effort "$EFFORT" > "$log" 2>&1 &
shim_pid=$!
trap 'kill "$shim_pid" 2>/dev/null || true' EXIT INT TERM

for _ in $(seq 1 60); do
  if curl -sf -m 1 "http://127.0.0.1:$port/v1/models" > /dev/null 2>&1; then
    break
  fi
  sleep 0.2
done

echo "[claude-gpt56] model=$MODEL effort=$EFFORT shim=127.0.0.1:$port (log $log)" >&2

ANTHROPIC_BASE_URL="http://127.0.0.1:$port" \
ANTHROPIC_AUTH_TOKEN="EMPTY" \
ANTHROPIC_API_KEY="EMPTY" \
ANTHROPIC_MODEL="$MODEL" \
ANTHROPIC_SMALL_FAST_MODEL="$MODEL" \
ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL" \
"$CLAUDE_BIN" "$@"
