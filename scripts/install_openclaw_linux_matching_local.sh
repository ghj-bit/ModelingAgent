#!/usr/bin/env bash
set -Eeuo pipefail

OPENCLAW_VERSION="2026.6.33"
OPENCLAW_BUILD="7af0cfc"
NODE_VERSION="22.22.2"
NPM_VERSION="10.9.7"
NVM_VERSION="0.40.7"
GATEWAY_PORT="18789"
START_GATEWAY=1
NON_INTERACTIVE=0

log() {
  printf '\n[%s] %s\n' "openclaw-install" "$*"
}

die() {
  printf '\n[openclaw-install] ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Install the same OpenClaw environment used by the local ModelingAgent setup.

Usage:
  bash scripts/install_openclaw_linux_matching_local.sh [options]

Options:
  --non-interactive  Read DEEPSEEK_API_KEY and TAVILY_API_KEY from the environment.
  --skip-gateway     Install and configure OpenClaw without starting the Gateway.
  -h, --help         Show this help.

The script never accepts secrets as command-line arguments. In interactive mode
it prompts for missing keys without echoing them.
EOF
}

while (($#)); do
  case "$1" in
    --non-interactive)
      NON_INTERACTIVE=1
      ;;
    --skip-gateway)
      START_GATEWAY=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
  shift
done

[[ "$(uname -s)" == "Linux" ]] || die "This installer supports Linux only."

install_system_dependencies() {
  local missing=()
  local command_name
  for command_name in curl git; do
    command -v "$command_name" >/dev/null 2>&1 || missing+=("$command_name")
  done
  ((${#missing[@]} == 0)) && return

  command -v apt-get >/dev/null 2>&1 || {
    die "Missing ${missing[*]}. Install curl, git, and CA certificates, then rerun."
  }

  local privilege=()
  if ((EUID != 0)); then
    command -v sudo >/dev/null 2>&1 || {
      die "Missing ${missing[*]} and sudo is unavailable. Ask the administrator to install them."
    }
    privilege=(sudo)
  fi

  log "Installing required system packages"
  "${privilege[@]}" apt-get update
  "${privilege[@]}" apt-get install -y curl git ca-certificates build-essential
}

install_nvm_and_node() {
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  if [[ ! -s "$NVM_DIR/nvm.sh" ]]; then
    log "Installing nvm v${NVM_VERSION}"
    curl -fsSL \
      "https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh" |
      bash
  fi

  # shellcheck source=/dev/null
  . "$NVM_DIR/nvm.sh"
  command -v nvm >/dev/null 2>&1 || die "nvm installation did not complete."

  log "Installing Node.js v${NODE_VERSION}"
  nvm install "$NODE_VERSION"
  nvm use "$NODE_VERSION"
  nvm alias default "$NODE_VERSION"

  log "Installing npm ${NPM_VERSION}"
  npm install -g "npm@${NPM_VERSION}"
  hash -r

  [[ "$(node --version)" == "v${NODE_VERSION}" ]] || {
    die "Expected Node.js v${NODE_VERSION}, got $(node --version)."
  }
  [[ "$(npm --version)" == "$NPM_VERSION" ]] || {
    die "Expected npm ${NPM_VERSION}, got $(npm --version)."
  }
}

install_openclaw() {
  log "Installing OpenClaw ${OPENCLAW_VERSION}"
  npm install -g "openclaw@${OPENCLAW_VERSION}"
  hash -r
  command -v openclaw >/dev/null 2>&1 || die "OpenClaw executable was not installed."

  local installed
  installed="$(openclaw --version)"
  [[ "$installed" == *"${OPENCLAW_VERSION}"* ]] || {
    die "Expected OpenClaw ${OPENCLAW_VERSION}, got: ${installed}"
  }
  log "Installed ${installed}"
}

read_secret_if_missing() {
  local variable_name="$1"
  local prompt="$2"
  local value="${!variable_name:-}"

  if [[ -z "$value" ]]; then
    ((NON_INTERACTIVE == 0)) || {
      die "${variable_name} must be set in non-interactive mode."
    }
    [[ -r /dev/tty ]] || {
      die "No interactive terminal. Export ${variable_name} or use an interactive shell."
    }
    read -r -s -p "$prompt" value </dev/tty
    printf '\n' >/dev/tty
  fi

  [[ -n "$value" ]] || die "${variable_name} cannot be empty."
  [[ "$value" =~ ^[A-Za-z0-9._~:/+=-]+$ ]] || {
    die "${variable_name} contains unsupported whitespace or shell characters."
  }
  printf -v "$variable_name" '%s' "$value"
  export "$variable_name"
}

write_secret_environment() {
  local environment_file="$HOME/.openclaw/modelingagent.env"
  install -d -m 700 "$HOME/.openclaw"
  umask 077
  {
    printf 'DEEPSEEK_API_KEY=%s\n' "$DEEPSEEK_API_KEY"
    printf 'TAVILY_API_KEY=%s\n' "$TAVILY_API_KEY"
  } >"$environment_file"
  chmod 600 "$environment_file"

  local marker="# ModelingAgent OpenClaw environment"
  if [[ ! -f "$HOME/.bashrc" ]] || ! grep -Fq "$marker" "$HOME/.bashrc"; then
    cat >>"$HOME/.bashrc" <<'EOF'

# ModelingAgent OpenClaw environment
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
if [ -f "$HOME/.openclaw/modelingagent.env" ]; then
  set -a
  . "$HOME/.openclaw/modelingagent.env"
  set +a
fi
EOF
  fi
}

write_openclaw_configuration() {
  local workspace_json
  local patch_file
  workspace_json="$(
    node -e 'process.stdout.write(JSON.stringify(process.argv[1]))' \
      "$HOME/.openclaw/workspace"
  )"
  patch_file="$(mktemp "${TMPDIR:-/tmp}/openclaw-local-match.XXXXXX.json5")"

  cleanup_patch() {
    rm -f -- "$patch_file"
  }
  trap cleanup_patch RETURN

  cat >"$patch_file" <<EOF
{
  agents: {
    defaults: {
      workspace: ${workspace_json},
      models: {
        "deepseek/deepseek-v4-flash": { alias: "DeepSeek" },
        "deepseek-v4-pro": {}
      },
      model: { primary: "deepseek-v4-pro" },
      subagents: {
        runTimeoutSeconds: 1800,
        maxConcurrent: 16
      },
      maxConcurrent: 100
    }
  },
  session: {
    dmScope: "per-channel-peer"
  },
  gateway: {
    port: ${GATEWAY_PORT},
    mode: "local",
    bind: "loopback",
    auth: { mode: "token" },
    controlUi: { allowInsecureAuth: true }
  },
  tools: {
    profile: "coding",
    web: {
      search: {
        provider: "tavily",
        enabled: true
      },
      fetch: {
        ssrfPolicy: {
          allowRfc2544BenchmarkRange: true
        }
      }
    }
  },
  plugins: {
    entries: {
      deepseek: { enabled: true },
      tavily: { enabled: true }
    }
  },
  auth: {
    profiles: {
      "deepseek:default": {
        provider: "deepseek",
        mode: "api_key"
      }
    }
  },
  models: {
    providers: {
      deepseek: {
        baseUrl: "https://api.deepseek.com",
        api: "openai-completions",
        models: [
          {
            id: "deepseek-v4-flash",
            name: "DeepSeek V4 Flash",
            reasoning: true,
            input: ["text"],
            contextWindow: 1000000,
            maxTokens: 384000
          },
          {
            id: "deepseek-v4-pro",
            name: "DeepSeek V4 Pro",
            reasoning: true,
            input: ["text"],
            contextWindow: 1000000,
            maxTokens: 384000
          },
          {
            id: "deepseek-chat",
            name: "DeepSeek Chat",
            reasoning: false,
            input: ["text"],
            contextWindow: 131072,
            maxTokens: 8192
          },
          {
            id: "deepseek-reasoner",
            name: "DeepSeek Reasoner",
            reasoning: true,
            input: ["text"],
            contextWindow: 131072,
            maxTokens: 65536
          }
        ]
      }
    }
  }
}
EOF

  log "Validating OpenClaw configuration"
  openclaw config patch --file "$patch_file" --dry-run
  openclaw config patch --file "$patch_file"
  mkdir -p "$HOME/.openclaw/workspace"

  openclaw config set \
    plugins.entries.tavily.config.webSearch.apiKey \
    "$TAVILY_API_KEY"
  openclaw config validate

  trap - RETURN
  cleanup_patch
}

configure_gateway_token() {
  log "Generating or refreshing the Gateway token"
  openclaw doctor --generate-gateway-token --non-interactive --yes
}

wait_for_gateway() {
  local attempt
  for attempt in {1..30}; do
    if openclaw gateway health >/dev/null 2>&1; then
      log "Gateway health check passed"
      return 0
    fi
    sleep 2
  done
  return 1
}

start_gateway() {
  if openclaw gateway health >/dev/null 2>&1; then
    log "Gateway is already healthy"
    return
  fi

  if [[ -z "${XDG_RUNTIME_DIR:-}" && -d "/run/user/$(id -u)" ]]; then
    export XDG_RUNTIME_DIR="/run/user/$(id -u)"
  fi

  if command -v systemctl >/dev/null 2>&1 && systemctl --user show-environment >/dev/null 2>&1; then
    log "Installing the Gateway systemd user service"
    openclaw gateway install --force --port "$GATEWAY_PORT"
    install -d -m 700 "$HOME/.config/systemd/user/openclaw-gateway.service.d"
    cat >"$HOME/.config/systemd/user/openclaw-gateway.service.d/environment.conf" <<'EOF'
[Service]
EnvironmentFile=%h/.openclaw/modelingagent.env
EOF
    systemctl --user daemon-reload
    systemctl --user restart openclaw-gateway.service
  else
    log "systemd user service is unavailable; starting Gateway with nohup"
    local pid_file="$HOME/.openclaw/gateway.pid"
    if [[ -f "$pid_file" ]]; then
      local old_pid
      old_pid="$(cat "$pid_file" 2>/dev/null || true)"
      if [[ "$old_pid" =~ ^[0-9]+$ ]] && kill -0 "$old_pid" 2>/dev/null; then
        kill "$old_pid"
        sleep 1
      fi
    fi
    nohup openclaw gateway run \
      >"$HOME/.openclaw/gateway.log" 2>&1 &
    printf '%s\n' "$!" >"$pid_file"
  fi

  wait_for_gateway || {
    printf '\nGateway did not become healthy. Inspect with:\n' >&2
    printf '  openclaw gateway status\n' >&2
    printf '  journalctl --user -u openclaw-gateway.service -n 200 --no-pager\n' >&2
    printf '  tail -n 200 %q\n' "$HOME/.openclaw/gateway.log" >&2
    exit 1
  }
}

print_summary() {
  log "Installation complete"
  node --version
  npm --version
  openclaw --version
  printf 'OpenClaw executable: %s\n' "$(command -v openclaw)"
  printf 'Configuration: %s\n' "$HOME/.openclaw/openclaw.json"
  printf 'Secret environment: %s\n' "$HOME/.openclaw/modelingagent.env"
  printf 'Agent concurrency: '
  openclaw config get agents.defaults.maxConcurrent
  printf 'Subagent concurrency: '
  openclaw config get agents.defaults.subagents.maxConcurrent
  if ((START_GATEWAY)); then
    openclaw gateway status
  else
    printf 'Gateway startup was skipped. Start it with: openclaw gateway run\n'
  fi

  cat <<EOF

To run the 40-problem training experiment:

  python scripts/run_clean_baseline_train.py \\
    --num-problems 40 \\
    --openclaw-command "$(command -v openclaw)"

To resume, add:

  --experiment openclaw_experiments/interaction_strategy_clean_baseline_train_YYYYMMDD_HHMMSS
EOF
}

install_system_dependencies
install_nvm_and_node
install_openclaw
read_secret_if_missing DEEPSEEK_API_KEY "DeepSeek API Key: "
read_secret_if_missing TAVILY_API_KEY "Tavily API Key: "
write_secret_environment
write_openclaw_configuration
configure_gateway_token
if ((START_GATEWAY)); then
  start_gateway
fi
print_summary
