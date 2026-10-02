# Reproducing `claude_fp8_scratch_data_r5b`

The from-scratch Claude-Code arm of the interaction-workflow evolution, run on the
MM-Bench "data" pools.  A solver with no prior plan is handed the problem
statement plus a staged retrieval helper (`code/search.py`), asks a human expert
(simulated) up to `max_exchanges` short common-sense questions, and the CPE loop
evolves the interaction policy.  This experiment is the 5-round run of
2026-10-01 23:07 that was resumed the next morning to 10 rounds; the resumed run
kept the stored champion (`seed rounds 0-1 are already measured`).

The machine-readable record of what actually ran is `config.json` in this
directory; the per-round judged results are under `workflows/`, and the per-run
artifacts (run.json / solution.json / solution_report.md / interaction receipt +
evidence) are the tracked files under `cpe_evaluations/`.

## 1. Bill of materials

| Component | What r5b used | Where it is configured |
|---|---|---|
| Solver model | `qwen3.8-27b-fp8`, OpenAI-compatible endpoint `http://gpu6:18764/v1` | `BASE_URL` / `MODEL` in `launch_claude_evolution_from_scratch.sh` |
| Optimizer model | same as solver | `OPT_MODEL` / `OPT_BASE_URL` |
| Judge-feedback model | same as solver | `--judge-feedback-model` |
| MM-Bench judge | `gpt-6.1-sol` at `https://rightapi.ai/v1` | `JUDGE_MODEL` / `JUDGE_BASE_URL` / `JUDGE_KEY_FILE` |
| Human expert | `deepseek-flash` at `https://api.deepseek.com` | `EXPERT_MODEL` / `EXPERT_BASE_URL`, key from `~/.deepseek_api_key` |
| Solver harness | Claude Code CLI **v2.1.280** (`~/.local/bin/claude`) + per-task shim | `src/OpenClaw/claude_backend/run_claude_task.py`, `proxy.py` |
| Python | anaconda env `math_modeling` (python 3.12) | `PY` in the launch script |
| Data | in-repo: `data/MMBench/dataset/<problem>/` + `data/MMBench/problem/<problem>.json` | `--mmbench-root` |
| Fixed rubric | `src/OpenClaw/interaction_initial_substantive_v1.json` | `--fixed-rubric` |

The FP8 server is the cluster deployment of 2026-09-26: vLLM on 4× SM86 (TP=4),
weights kept 8-bit (Marlin weight-only kernel), `GPU_UTIL ≤ 0.80`,
`--max-num-seqs 128`, max_model_len 262144.  Pinned constraints on this cluster:
vLLM **≤ 0.19.1** and NCCL **2.26.5** (newer NCCL segfaults).  Any
OpenAI-compatible endpoint serving the same model works — override `BASE_URL` /
`MODEL` (and the judge/expert variables) in the environment.

**Pools** (fixed in the arm module, not the split file): validation 8 =
`2002_C 2006_C 2012_C 2016_C 2018_C 2020_D 2023_Y 2025_C`, train 10 =
`2003_C 2015_C 2017_C 2017_D 2019_C 2020_C 2021_C 2023_C 2024_C 2024_D`
(disjoint; the pools are every dataset-bearing task minus 2025_D, whose source
release lacks a declared file, and minus 2000_C/2021_D/2022_C, whose data is
defective).

## 2. Launch, exactly as it was done

```bash
cd ModelingAgent
export DEEPSEEK_API_KEY="$(cat "$HOME/.deepseek_api_key")"          # required by the script
bash scripts/launch_claude_evolution_from_scratch.sh claude_fp8_scratch_data_r5b 5    # first pass, 23:07
# after the log prints "CPE best workflow:" (07:52):
bash scripts/launch_claude_evolution_from_scratch.sh claude_fp8_scratch_data_r5b 10   # resume; champion preserved
```

The script self-detaches (`setsid nohup`), appends to
`.env_setup_logs/<name>.log`, and takes the experiment name and `max-rounds` as
its only arguments.  A resume re-reads the seed already written into the
experiment directory and ignores `INTERACTION_INITIAL_WORKFLOW_JSON`.

**Seed**: at r5b's run time the script's default seed was
`openclaw_experiments/exp_prompt/initial_interaction_workflow_info_first.json`
(the "Open-question consultation policy", `max_exchanges: 3`).  The authoritative
copy is this directory's `initial_interaction_workflows.json`.  To replay
faithfully, pin `INTERACTION_INITIAL_WORKFLOW_JSON` to the three-exchange file —
the script's default was changed to a ten-exchange variant on 2026-10-02, after
this run.

Judging and run shape (defaults of the script unless overridden):
`--judge-repeats 3`, `--train-batch-size 3`, `--validation-size 8`,
`--validation-repetitions 1`, `--thinking off`, `MMBENCH_JUDGE_PARALLEL_DIMENSIONS=1`,
`JUDGE_REPEATS=3`.

## 3. Model / endpoint configuration in effect

From this directory's `config.json` (the authoritative record):

- models: `model` = `opt_model` = `judge_feedback_model` = `qwen3.8-27b-fp8`,
  `expert_model` = `deepseek-flash`; `judge_repeats` = 3; `thinking` off.
- CPE: `train_pool`/`validation_pool` as above, `train_batch_size` 3,
  `train_repetitions_per_problem` 2, `validation_size` 8,
  `validation_repetitions` 1, acceptance margins 0.005 (train and validation),
  evolution mode `mutation` only, `max_rounds` 10 (resume).
- **`sampling_seed` = 8472815009279553256** — pin this to draw the same training
  batches in the same order.
- Interaction cost model (part of the utility): `max_exchanges` 3,
  token reference 5000, latency cap 540 s, weights 0.5 (exchange) / 0.4 (tokens)
  / 0.0 (latency), `penalty_weight_lambda` 0.05.
- `enable_thinking` is forced off in the shim, not by the `--thinking` flag
  (that flag is parsed but unused).
- Score comparability: same-judge only.  Judge model / judge repeats / pools /
  validation repetitions must match for numbers to be comparable to this record.

## 4. The Claude Code side (solver harness)

Per solving task, `run_claude_task.py` does three things: it starts the shim,
writes a throwaway Claude config directory, and launches one `claude --print`
session pinned to a CPU lane.

**Shim** (`src/OpenClaw/claude_backend/proxy.py`): the Claude session speaks the
Anthropic Messages API to `127.0.0.1:<port>`; the shim translates to OpenAI
`chat/completions` at `CLAUDE_BASE_URL` and hardcodes
`chat_template_kwargs = {"enable_thinking": false}` on every request.

**Environment for the session** (all set by `session_environment()`):

```
ANTHROPIC_BASE_URL=http://127.0.0.1:<shim port>   ANTHROPIC_MODEL=<model>
ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY=<shim key>   ANTHROPIC_SMALL_FAST_MODEL=<model>
ANTHROPIC_DEFAULT_HAIKU_MODEL=<model>   CLAUDE_CONFIG_DIR=<per-task config dir>
CLAUDE_CODE_MAX_OUTPUT_TOKENS=20000     # keeps the prompt ceiling above the compact window
CLAUDE_CODE_AUTO_COMPACT_WINDOW=<unset> # popped: an inherited value would void --autocompact
BASH_DEFAULT_TIMEOUT_MS = BASH_MAX_TIMEOUT_MS = 300000   # this arm dials 1800000 down
DISABLE_AUTOUPDATER=1  DISABLE_TELEMETRY=1  DISABLE_ERROR_REPORTING=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
CLAUDE_MODEL / CLAUDE_BASE_URL / CLAUDE_API_KEY   # claude_backend reads the endpoint from these
OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS = 4   LOKY_MAX_CPU_COUNT=4   CLAUDE_AGENT_CPUS=4
```

**`settings.json` written per task** (verbatim):

```json
{
  "permissions": {
    "allow": ["Bash", "Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "LS",
              "WebFetch", "WebSearch", "NotebookEdit", "TodoWrite"],
    "deny": ["Bash(timeout *)"]
  },
  "enableAllProjectMcpServers": false,
  "outputStyle": "Concise"
}
```

`deny Bash(timeout *)`: the agent used to wrap slow commands in its own
`timeout NNN` chosen from the tool ceiling, and a too-small NNN threw whole runs
away.  `outputStyle: Concise` suppresses narration turns; the built-in style is
used because it keeps the coding instructions.

**CLI invocation** (per task):

```
claude --print --settings <task>/claude_config/settings.json \
  --permission-mode acceptEdits --output-format stream-json --verbose \
  --autocompact 180k \
  --append-system-prompt "<BATCHING_SYSTEM_PROMPT>"
```

with `BATCHING_SYSTEM_PROMPT` (source: `run_claude_task.py`):

> When a script fails, fix every error it revealed in one pass, then run it once
> more — do not fix one error, run, fix the next error, run. Batch the changes
> you already know a file needs before running it again. One run in this
> experiment edited the same file 52 times across 51 script runs, and each of
> those round trips cost more than the edit it carried.

Auto-compact fires at `window − 33000` (180k window → 147k); the shim forwards
streaming `usage` so compaction can fire at all.

**Solver prompt**: generated by the code, not read from a file — the source is
`src/OpenClaw/run_substantive_interaction_workflow_evolution_from_scratch_claude.py`
(step list: clean data → assumptions → models → retrieve with `code/search.py`,
values enter `solution.json` as calibrated inputs → execute → validate → submit;
plus the arm paragraph "the expert is not a mathematical modeler, one short
question per exchange").  A rendered sample of what a run actually received
lives locally in each run's `prompt.md` (not committed).

## 5. Code version — read before claiming an exact replay

The experiment record in this directory is commit `24544fab` of
`ghj-bit/ModelingAgent`; it contains **results only**.  The code that produced
them was commit `a7eb8b2` **plus uncommitted working-tree changes**, of which the
arm-defining ones are:

```
src/OpenClaw/run_substantive_interaction_workflow_evolution_from_scratch_claude.py   (+274)
src/OpenClaw/run_substantive_interaction_workflow_evolution_from_initial_draft_claude.py (+34)
src/OpenClaw/run_substantive_interaction_workflow_evolution.py                        (+37)
scripts/launch_claude_evolution_from_scratch.sh
data/MMBench/problem/*.json   (2026-10-01 alignment edits)
... plus ~30 more files (see `git status`)
```

These changes (the data pools above, the lenient draft resolver, the cleaning
step, the retrieval step) exist only in the working tree; the run cannot be
replayed from commits alone.  Ask the repository owner for the diff against
`a7eb8b2` if you need the exact code state.  Note the working tree has moved on
since (e.g. the launch script's default seed changed on 2026-10-02 evening), so
diff at the file level, not the timestamp level.
