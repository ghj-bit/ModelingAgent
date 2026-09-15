# Linux 安装 OpenClaw：复现本机环境

本文档用于在远程 Linux 服务器上复现当前 Windows 本机的 OpenClaw
运行环境，供 `ModelingAgent` 的 OpenClaw 实验脚本使用。

## 一键安装

仓库中已提供对应安装脚本。在仓库根目录执行：

```bash
bash scripts/install_openclaw_linux_matching_local.sh
```

脚本会在终端中隐藏读取 DeepSeek 和 Tavily API Key，随后安装固定版本、
写入配置并启动 Gateway。自动化环境可以预先设置密钥：

```bash
export DEEPSEEK_API_KEY="替换为真实密钥"
export TAVILY_API_KEY="替换为真实密钥"
bash scripts/install_openclaw_linux_matching_local.sh --non-interactive
```

只安装和配置、不启动 Gateway：

```bash
bash scripts/install_openclaw_linux_matching_local.sh --skip-gateway
```

## 1. 本机环境快照

记录日期：2026-09-15。

| 项目 | 本机值 |
| --- | --- |
| OpenClaw | `2026.6.33`，构建提交 `7af0cfc` |
| 安装方式 | npm 全局安装 |
| Node.js | `v22.22.2` |
| npm | `10.9.7` |
| 默认模型 | `deepseek-v4-pro` |
| 训练脚本模型 | `deepseek/deepseek-v4-flash` |
| Agent 并发 | `100` |
| 子 Agent 并发 | `16` |
| 子 Agent 超时 | `1800` 秒 |
| 工具配置 | `coding` |
| Web 搜索 | Tavily |
| Gateway | `local`、`loopback`、端口 `18789`、token 鉴权 |

这是版本复现文档。不要使用 `openclaw@latest`，否则安装结果不会与本机
一致。当前新版 OpenClaw 已采用不同的 Node.js 版本要求。

## 2. 安装基础工具

Ubuntu/Debian：

```bash
sudo apt-get update
sudo apt-get install -y curl git ca-certificates build-essential
```

如果服务器没有 `sudo` 权限，请让管理员安装上述系统软件；后续 Node.js、
npm 和 OpenClaw 均安装在当前用户目录，不需要 root 权限。

## 3. 安装与本机一致的 Node.js 和 npm

安装用户级 nvm：

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.7/install.sh | bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
```

安装并固定版本：

```bash
nvm install 22.22.2
nvm use 22.22.2
nvm alias default 22.22.2
npm install -g npm@10.9.7
```

检查版本：

```bash
node --version
npm --version
```

预期输出：

```text
v22.22.2
10.9.7
```

新 SSH 会话如果找不到 `nvm`，执行：

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 22.22.2
```

## 4. 安装固定版本 OpenClaw

```bash
npm install -g openclaw@2026.6.33
hash -r
command -v openclaw
openclaw --version
```

预期版本：

```text
OpenClaw 2026.6.33 (7af0cfc)
```

## 5. 配置密钥

本机通过环境变量提供 DeepSeek API Key。不要把真实密钥提交到 Git。

```bash
mkdir -p "$HOME/.openclaw"
chmod 700 "$HOME/.openclaw"

cat > "$HOME/.openclaw/modelingagent.env" <<'EOF'
DEEPSEEK_API_KEY=替换为真实的_DeepSeek_API_Key
EOF

chmod 600 "$HOME/.openclaw/modelingagent.env"
set -a
. "$HOME/.openclaw/modelingagent.env"
set +a
```

确认变量存在，但不要打印密钥：

```bash
test -n "$DEEPSEEK_API_KEY" && echo "DEEPSEEK_API_KEY is configured"
```

## 6. 写入与本机一致的非敏感配置

生成配置补丁：

```bash
cat > "$HOME/openclaw-local-match.json5" <<EOF
{
  agents: {
    defaults: {
      workspace: "${HOME}/.openclaw/workspace",
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
    port: 18789,
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
```

先验证，再写入：

```bash
openclaw config patch --file "$HOME/openclaw-local-match.json5" --dry-run
openclaw config patch --file "$HOME/openclaw-local-match.json5"
mkdir -p "$HOME/.openclaw/workspace"
openclaw config validate
```

## 7. 配置 Tavily

本机启用了 Tavily 插件，并将其用作 Web 搜索提供方。通过隐藏输入读取密钥：

```bash
read -rsp "Tavily API Key: " TAVILY_API_KEY
echo
openclaw config set plugins.entries.tavily.config.webSearch.apiKey "$TAVILY_API_KEY"
unset TAVILY_API_KEY
```

如果实验不需要联网检索，可以关闭 Tavily：

```bash
openclaw config set tools.web.search.enabled false --strict-json
```

这会与本机配置产生差异，但不影响本地数据和代码工具。

## 8. 生成 Gateway token

```bash
openclaw doctor --generate-gateway-token
openclaw config validate
```

不要打印、复制到日志或提交生成的 Gateway token。

## 9. 启动 Gateway

### 9.1 使用 systemd 用户服务

```bash
openclaw gateway install --port 18789
```

让 Gateway 服务读取 DeepSeek 密钥：

```bash
mkdir -p "$HOME/.config/systemd/user/openclaw-gateway.service.d"

cat > "$HOME/.config/systemd/user/openclaw-gateway.service.d/environment.conf" <<'EOF'
[Service]
EnvironmentFile=%h/.openclaw/modelingagent.env
EOF

systemctl --user daemon-reload
systemctl --user restart openclaw-gateway.service
```

服务器退出 SSH 后仍需运行 Gateway 时，可由管理员执行一次：

```bash
sudo loginctl enable-linger "$(whoami)"
```

### 9.2 没有 systemd 用户服务

```bash
set -a
. "$HOME/.openclaw/modelingagent.env"
set +a

nohup openclaw gateway run \
  > "$HOME/.openclaw/gateway.log" 2>&1 &
```

## 10. 验证安装

```bash
node --version
npm --version
openclaw --version
openclaw config validate
openclaw gateway health
openclaw gateway status
```

关键结果应为：

```text
Node.js: v22.22.2
npm: 10.9.7
OpenClaw: 2026.6.33 (7af0cfc)
Gateway: 127.0.0.1:18789
Agent maxConcurrent: 100
Subagent maxConcurrent: 16
```

检查并发配置：

```bash
openclaw config get agents.defaults.maxConcurrent
openclaw config get agents.defaults.subagents.maxConcurrent
openclaw config get agents.defaults.subagents.runTimeoutSeconds
```

预期依次得到 `100`、`16`、`1800`。

## 11. 执行 ModelingAgent 训练实验

进入仓库并加载密钥：

```bash
cd /inspire/hdd/project/ai4education/qianhong-p-qianhong/ghj_workspace/ModelingAgent

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 22.22.2

set -a
. "$HOME/.openclaw/modelingagent.env"
set +a
```

新建一个 40 题实验：

```bash
python scripts/run_clean_baseline_train.py \
  --num-problems 40 \
  --openclaw-command "$(command -v openclaw)"
```

只有显式传入实验目录才会断点续跑：

```bash
python scripts/run_clean_baseline_train.py \
  --num-problems 40 \
  --openclaw-command "$(command -v openclaw)" \
  --experiment openclaw_experiments/interaction_strategy_clean_baseline_train_YYYYMMDD_HHMMSS
```

续跑时，`runs/round_1/evaluation_checkpoint.json` 中已经完成的题目会被跳过。

## 12. 常见问题

### `openclaw: command not found`

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 22.22.2
hash -r
command -v openclaw
```

### Gateway 无法连接

```bash
openclaw gateway status
journalctl --user -u openclaw-gateway.service -n 200 --no-pager
```

没有 systemd 时：

```bash
tail -n 200 "$HOME/.openclaw/gateway.log"
```

### 配置与本机不一致

```bash
openclaw config get agents.defaults.model.primary
openclaw config get agents.defaults.maxConcurrent
openclaw config get agents.defaults.subagents.maxConcurrent
openclaw config get gateway.mode
openclaw config get gateway.bind
openclaw config get gateway.port
```

预期分别为：`deepseek-v4-pro`、`100`、`16`、`local`、`loopback`、
`18789`。

## 参考资料

- OpenClaw 安装：https://docs.openclaw.ai/install
- OpenClaw Gateway：https://docs.openclaw.ai/cli/gateway
- OpenClaw 配置：https://docs.openclaw.ai/cli/config
- nvm 安装：https://github.com/nvm-sh/nvm#installing-and-updating
