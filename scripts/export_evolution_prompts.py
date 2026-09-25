"""Collect every prompt the claude co-evolution pipeline sends to an LLM.

The prompts live in three different shapes: a few are files under
``src/OpenClaw/prompts/``, most are string constants inside the launcher, and a
few are assembled at call time from a template plus that round's evidence.  This
script renders all of them into ``openclaw_experiments/exp_prompt/`` as readable
Markdown so the whole set can be read and diffed in one place.

Rendering, not copying, is the point: an assembled prompt has no file to copy,
and the interesting part of a template is where the runtime pieces go.  Those
insertion points are marked with ``«…»`` here, while the placeholders the engine
substitutes by name (``{{PROBLEM_ID}}`` and friends) are left as written.

    python scripts/export_evolution_prompts.py [output-dir]

Re-run after changing any prompt source.  Header comments record the source
location and the source file's md5, so a stale copy is visible.
"""

from __future__ import annotations

import ast
import datetime
import hashlib
import inspect
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

OUT = REPO / "openclaw_experiments" / "exp_prompt"

# Visible markers for the pieces the pipeline fills in per run.  The policy is
# inserted whole, heading included -- its text always opens with the interaction
# heading -- so the marker keeps that heading in place and says where it is from.
POLICY = (
    "# Human Expert Interaction  «← 此标题及其后的步骤/约束均由策略文本自带»\n\n"
    "«ACTIVE INTERACTION POLICY BODY (the evolved text, per round)»"
)
EVIDENCE = "«EVIDENCE BUNDLE (this round's parent rollouts, as JSON)»"
DIALOGUE = "«RECORDED EXPERT DIALOGUE (question, reply, and the run's own record)»"
DRAFT = "«PLANNING DRAFT (draft arm only)»"
CHANGE = "«WHAT THE RUN SAYS THE REPLY CHANGED (self-reported)»"
DATA = "«TASK DATA»"
FENCE = "````"

LAUNCHER = "src/OpenClaw/run_substantive_interaction_workflow_evolution_from_initial_draft_claude.py"


def digest(path: pathlib.Path) -> str:
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except OSError:
        return "n/a"


def source_note(relative: str, line: int = 0, symbol: str = "") -> str:
    """A source pointer that also proves which revision of the file it came from."""
    path = REPO / relative
    where = f"{relative}:{line}" if line else relative
    symbol = f" → `{symbol}`" if symbol else ""
    return f"`{where}`{symbol}（md5 `{digest(path)}`）"


def provenance(origin: str, kind: str, arms: str) -> str:
    return f"**来源**：{origin}\n\n**形态**：{kind}\n\n**在用的臂**：{arms}\n\n"


def block(text: str) -> str:
    return f"{FENCE}text\n{text.rstrip()}\n{FENCE}\n"


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  wrote {path.relative_to(REPO)}  ({len(text)} chars)")


# --------------------------------------------------------------------------- #
# renderers


def solver_prompts() -> tuple[str, str]:
    """The two solver prompts: the draft-free arm's, and the draft arm's."""
    from src.OpenClaw import (
        run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base,
    )
    from src.OpenClaw import (
        run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch,
    )

    base._benchmark = "mmbench"
    sentinel = {"policy_text": POLICY, "workflow_id": "«workflow id»"}
    # The from-scratch launcher sets this, so its prompt is the one with the guard.
    os.environ["INTERACTION_RUNAWAY_GUARD"] = "1"
    from_scratch = scratch.build_from_scratch_solver_prompt(sentinel)
    with_draft = base.build_interactive_solver_prompt(
        sentinel, include_interaction=True, include_draft=True
    )
    return from_scratch, with_draft


def evolver_prompt() -> str:
    from src.OpenClaw import (
        run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base,
    )
    from src.OpenClaw import (
        run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch,
    )

    # This arm's patch sets SOLVER_SOURCE_CONTEXT / SOLVER_START_CONTEXT, which are
    # substituted straight into the template; rendering the draft arm's values
    # would show the wrong sentence for this arm.
    scratch.patch_sibling_launcher()
    head = (
        base.EVOLUTION_PROMPT_HEAD.replace(
            "{similarity_threshold}",
            f"{base.workflow.DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD:.2f}",
        )
        .replace("{solver_source}", base.SOLVER_SOURCE_CONTEXT)
        .replace("{solver_start}", base.SOLVER_START_CONTEXT)
    )
    return "\n".join(
        [
            head,
            base.EVOLUTION_OUTPUT_SCHEMA,
            base.EVOLUTION_EVIDENCE_GUIDE,
            "",
            "```json",
            EVIDENCE,
            "```",
            "",
            base.EVOLUTION_PROMPT_FOOT,
            "",
        ]
    )


def critic_prompts() -> tuple[str, str]:
    from src.OpenClaw import interaction_strategy_critic as critic

    user = critic.build_critic_prompt(
        parent_rank=1,
        policy_text=POLICY,
        problem_id="«problem id»",
        title="«problem title»",
        dialogue=DIALOGUE,
        draft=DRAFT,
        change_summary=CHANGE,
        scores={"«dimension»": "«score»"},
        interaction_cost="«exchanges, tokens, latency»",
    )
    return critic.SYSTEM_PROMPT, user


class StubSolution(dict):
    """A solution stand-in for rendering the judge templates.

    The generators read the background and the requirements through ``get`` but
    walk the tasks through ``items``, so a plain dict cannot satisfy both: its own
    metadata keys would be handed to the per-task loop and break it.  Overriding
    ``items`` keeps the two views separate.
    """

    def items(self):  # noqa: D102 - documented on the class
        task = {
            key: DATA
            for key in (
                "task_description",
                "task_analysis",
                "mathematical_modeling_process",
                "subtask_outcome_analysis",
            )
        }
        return [(f"subtask_{index}", dict(task)) for index in range(1, 4)]


def judge_prompts() -> str:
    """The four MM-Bench scoring prompts, rendered against a stub solution."""
    sys.path.insert(0, str(REPO / "data" / "MMBench" / "evaluation"))
    import prompts as mmbench_prompts  # noqa: PLC0415 - data-dir module, path added above

    stub = StubSolution(background=DATA, problem_requirement=[DATA])
    rendered = []
    for name in (
        "generate_problem_analysis_prompt",
        "generate_modeling_rigorousness_prompt",
        "generate_practicality_and_scientificity_prompt",
        "generate_result_and_bias_analysis_prompt",
    ):
        rendered.append(f"### `{name}()`\n\n{block(getattr(mmbench_prompts, name)(stub))}")
    return "\n".join(rendered)


def seed_policy() -> str:
    """The frozen seed this arm starts from, as the solver receives it.

    Not `src/OpenClaw/prompts/initial_interaction_policy.md`: that file renders the
    *other* constant in `interaction_policy.py` and is exported by
    `scripts/export_initial_interaction_policy.py`.  The claude arm's seed is
    `STRATEGIC_DECISION_CONSULTATION`, and the from-scratch arm runs it through
    `strip_plan_references`, so this renders the workflow the arm actually mints.
    """
    from src.OpenClaw import (
        run_substantive_interaction_workflow_evolution_from_scratch_claude as scratch,
    )
    from src.OpenClaw import interaction_policy

    workflow = scratch.fixed_initial_workflow()
    raw = interaction_policy.STRATEGIC_DECISION_CONSULTATION
    return (
        "# 在用：`fixed_initial_workflow()` 产出的种子（已剔除 draft 相关行）\n\n"
        f"`workflow_id` = `{workflow.get('workflow_id')}`，"
        f"`policy_text` {len(workflow.get('policy_text', ''))} 字符"
        f"（原始常量 `interaction_policy.STRATEGIC_DECISION_CONSULTATION` {len(raw)} 字符）。\n\n"
        + block(workflow.get("policy_text", ""))
        + "\n## 对照：未经 `strip_plan_references` 的原始常量\n\n"
        "draft 臂用的是这一份；from-scratch 臂删掉了所有含 `draft` 的行，因为该臂没有起始计划。\n\n"
        + block(raw)
    )


def system_message_of(function) -> str:
    """Pull a function's inline ``{"role": "system", "content": ...}`` literal.

    Extracted rather than copied so the export cannot drift from the code.  The
    content is written either as a parenthesized run of adjacent literals (long
    multi-line prompts) or as a single quoted literal, so both shapes are tried
    and ``literal_eval`` does the unescaping.
    """
    source = inspect.getsource(function)
    patterns = (
        r'"role":\s*"system",\s*"content":\s*(\((?:[^()]|\([^()]*\))*\))\s*,?\s*\}',
        r'"role":\s*"system",\s*"content":\s*("(?:[^"\\]|\\.)*")\s*,?\s*\}',
    )
    for pattern in patterns:
        match = re.search(pattern, source, re.S)
        if not match:
            continue
        try:
            return ast.literal_eval(match.group(1))
        except (SyntaxError, ValueError):
            continue
    return "«未能自动提取，请见源码中的 system content»"


def expert_roles() -> str:
    from src.OpenClaw import baseline
    from src.OpenClaw import run_substantive_interaction_experiment as substantive

    in_force = substantive.SUBSTANTIVE_EXPERT_ROLE_PROMPT
    ask = baseline.ASK_EXPERT_ROLE_PROMPT
    overridden = baseline.HUMAN_MODELING_EXPERT_ROLE_PROMPT
    note = (
        "引擎启动时把 `baseline.HUMAN_MODELING_EXPERT_ROLE_PROMPT` 覆盖为 "
        "`substantive.SUBSTANTIVE_EXPERT_ROLE_PROMPT`（`run_substantive_interaction_experiment.py:1383`），"
        "所以**在用的是第一份**；第二份是 baseline 模块里的原版，仅在未覆盖的路径上生效。\n"
    )
    if overridden.strip() == in_force.strip():
        note += "\n（当前两者文本相同。）\n"
    return (
        "## 在用：`SUBSTANTIVE_EXPERT_ROLE_PROMPT`\n\n"
        + block(in_force)
        + "\n## 另一份角色设定：`ASK_EXPERT_ROLE_PROMPT`\n\n"
        + block(ask)
        + "\n"
        + note
    )


# --------------------------------------------------------------------------- #


def build() -> dict[str, str]:
    from_scratch, with_draft = solver_prompts()
    critic_system, critic_user = critic_prompts()

    solver = (
        "# 求解 agent（solver）prompt\n\n"
        "建模求解 agent 收到的完整 prompt：基座模板内联在启动器里，"
        "其中插入当轮生效的交互策略，并按臂插入不同段落。\n\n"
        + provenance(
            source_note(LAUNCHER, 1128, "build_interactive_solver_prompt()"),
            "运行时拼装（本文件为渲染结果；`«…»` 标出插入点）",
            "from-scratch 臂与协同演化臂用变体 A；draft 臂用变体 B",
        )
        + "补充：`{{PROBLEM_ID}}` / `{{RESULTS_DIR}}` / `{{DRAFT_PATH}}` 等双花括号占位符由引擎按名替换；"
        "`# Search Scope and Long Commands` 段仅在 `INTERACTION_RUNAWAY_GUARD=1` 时出现"
        "（from-scratch 与协同演化启动脚本默认开启，draft 臂不设）。\n\n"
        "## 变体 A：from-scratch 臂（当前在跑 `claude_scratch_evolve_r10`）\n\n"
        "变体 A 的交互段末尾多一段 `### Keep the consultation proportionate`，"
        "来自 `run_substantive_interaction_workflow_evolution_from_scratch_claude.py` 的 "
        "`INTERACTION_PROPORTIONALITY_NOTE`：它刻意写在策略文本之外，演化器改不掉。\n\n"
        + block(from_scratch)
        + "\n## 变体 B：draft 臂（`launch_claude_evolution.sh`）\n\n"
        + block(with_draft)
    )

    from src.OpenClaw import run_substantive_interaction_workflow_evolution as engine

    evolver = (
        "# 演化器（optimizer / evolver）prompt\n\n"
        "发给策略演化器的 prompt：把当轮母代 rollout 作为证据，要求它输出一版新的交互策略 JSON。"
        "§1/§2/§3/§5 是固定模板，§4 之后是逐轮变化的证据 JSON。\n\n"
        + provenance(
            source_note(
                LAUNCHER,
                742,
                "EVOLUTION_PROMPT_HEAD / EVOLUTION_OUTPUT_SCHEMA / EVOLUTION_EVIDENCE_GUIDE / EVOLUTION_PROMPT_FOOT",
            ),
            "静态常量拼接 + 运行时证据（本文件为渲染结果）",
            "三个 claude 臂共用；臂差异只体现在 `{solver_source}` / `{solver_start}` 两个句子上",
        )
        + "注意：上文的 §1–§5 是**用户消息**；调用时另有一条独立的 system 消息（见下），"
        "以及一条把单次 run 压成 50 字变更摘要的辅助调用（它产出的摘要进入 §4 证据）。\n\n"
        + block(evolver_prompt())
        + "\n## 同一次调用里的 system 消息\n\n"
        + provenance(
            source_note(
                "src/OpenClaw/run_substantive_interaction_workflow_evolution.py",
                1649,
                "engine.propose_cpe_workflow()",
            ),
            "静态常量",
            "全部臂共用",
        )
        + block(system_message_of(engine.propose_cpe_workflow))
        + "\n## 证据摘要的辅助调用（system 消息）\n\n"
        + provenance(
            source_note(
                "src/OpenClaw/run_substantive_interaction_workflow_evolution.py",
                926,
                "engine.summarize_interaction_report_changes()",
            ),
            "静态常量；`temperature=0.1`、`max_tokens=200`、`response_format=json_object`，user 段为 run 的 JSON",
            "全部臂共用（模型取 `--judge-feedback-model`）",
        )
        + block(system_message_of(engine.summarize_interaction_report_changes))
    )

    critic = (
        "# critic prompt（协同演化臂）\n\n"
        "协同演化臂在演化器 prompt 之后追加的评审块：critic 先按 rubric 给每个母代的交互打分，"
        "评审结果再作为一个额外证据节点拼进演化器 prompt。\n\n"
        + provenance(
            source_note(
                "src/OpenClaw/interaction_strategy_critic.py",
                35,
                "SYSTEM_PROMPT / OUTPUT_SCHEMA_HINT / build_critic_prompt()",
            ),
            "system 为静态常量；user 为运行时拼装（本文件为渲染结果）",
            "仅协同演化臂（`launch_claude_coevolution.sh`）",
        )
        + "注意：`# The plan the consultation started from` 一节在 from-scratch 臂恒为空——"
        "该臂没有起始计划，而证据过滤器 `optimizer_interaction_artifacts` 也只放行 "
        "`expert_interaction` 一种工件，draft 永远不会出现在 critic 的输入里。\n\n"
        "## system\n\n"
        + block(critic_system)
        + "\n## user（渲染结果）\n\n"
        + block(critic_user)
    )

    judge = (
        "# MM-Bench judge prompt\n\n"
        "打分用的四个维度 prompt，由基准自带的评测脚本发出。评分标准（固定 rubric）另行注入，"
        "见 `src/OpenClaw/prompts/interaction_rubrics_current.md`。\n\n"
        + provenance(
            source_note("data/MMBench/evaluation/prompts.py"),
            "运行时拼装（本文件为用桩数据渲染的结果）",
            "全部臂共用（`--mmbench-judge-model`）",
        )
        + judge_prompts()
    )

    expert = (
        "# 人类专家（human expert）角色设定\n\n"
        "让 LLM 扮演建模专家、回答 agent 战略提问的角色 prompt。"
        "运行时写入 `<run_dir>/output/logs/operator_roles/human_modeling_expert.md`，"
        "再作为 system 消息发给专家模型。\n\n"
        + provenance(
            source_note(
                "src/OpenClaw/run_substantive_interaction_experiment.py",
                55,
                "SUBSTANTIVE_EXPERT_ROLE_PROMPT",
            ),
            "静态常量；调用时另有运行时追加",
            "全部臂共用",
        )
        + "两点运行时追加（本文件只导出静态常量）：\n\n"
        "1. 写角色文件时 `baseline.human_expert_role_prompt()` 会追加 "
        "`## Authoritative Problem Statement` 及该题的题面字段；\n"
        "2. 实际调用时 system 消息外面还有一句包装：\n\n"
        + block(
            "You are being called directly through an API, not as an OpenClaw "
            "subagent. Follow the role and problem statement below exactly.\n\n"
            "<角色文件全文>"
        )
        + "   （`src/OpenClaw/run_interaction_rubric_evolution.py:1440` 的 `call_direct_human_expert()`；"
        "user 段为历史对话 + `Answer only this current qualitative question:` + 本次提问。）\n\n"
        + expert_roles()
    )

    prompts = {
        "solver_agent.md": solver,
        "optimizer_evolver.md": evolver,
        "critic.md": critic,
        "judge_mmbench.md": judge,
        "human_expert_role.md": expert,
        "interaction_policy_seed.md": (
            "# 交互策略种子（frozen seed）\n\n"
            "填进 solver prompt 交互段的初始策略，全部臂都从它出发，演化器只能改写它、不能换掉它。\n\n"
            + provenance(
                source_note("src/OpenClaw/interaction_policy.py", 18, "STRATEGIC_DECISION_CONSULTATION")
                + " → "
                + source_note("src/OpenClaw/run_substantive_interaction_workflow_evolution_from_scratch_claude.py", 99, "fixed_initial_workflow()"),
                "静态常量 + 该臂的 `strip_plan_references()` 处理",
                "from-scratch 臂与协同演化臂用上面的第一份；draft 臂用未剔除 draft 行的原始常量",
            )
            + seed_policy()
        ),
    }
    planner = REPO / "src" / "OpenClaw" / "prompts" / "mmbench_planner_prompt.md"
    prompts["planner_draft.md"] = (
        "# planner prompt\n\n"
        "证据预取阶段的规划 prompt。**本臂不读它产出的计划**——from-scratch 臂只复制同目录下的 "
        "`data/external_data.md`，规划本身从不进入求解器，列在这里只为说明证据从哪来。\n\n"
        + provenance(
            source_note("src/OpenClaw/prompts/mmbench_planner_prompt.md"),
            "静态文件",
            "上游证据预取（不在三个演化臂的运行路径上）",
        )
        + block(planner.read_text(encoding="utf-8"))
    )
    return prompts


ROWS = (
    ("solver_agent.md", "求解 agent", "建模求解 agent 收到的完整 prompt（两个臂变体）"),
    ("optimizer_evolver.md", "演化器", "产出下一版交互策略的 prompt（§1–§5 + 证据）"),
    ("critic.md", "critic", "协同演化臂的评审 prompt（system + user）"),
    ("judge_mmbench.md", "MM-Bench judge", "四个评分维度的打分 prompt"),
    ("human_expert_role.md", "人类专家", "扮演建模专家的角色设定"),
    ("interaction_policy_seed.md", "交互策略种子", "注入 solver prompt 的初始策略文本（本臂实际用的那份）"),
    ("planner_draft.md", "planner", "上游证据预取用的规划 prompt（本臂只复用其产物）"),
)


def readme(prompts: dict[str, str]) -> str:
    listing = "\n".join(
        f"| `{name}` | {role} | {what} |" for name, role, what in ROWS if name in prompts
    )
    missing = [name for name, _, _ in ROWS if name not in prompts]
    if missing:
        listing += "\n" + "\n".join(f"| `{name}` | — | 本次未生成 |" for name in missing)
    return f"""# 交互策略演化实验的 prompt 全集

本目录由 `scripts/export_evolution_prompts.py` 生成，内容为**渲染后的 prompt 模板**：
静态部分逐字照抄，运行时填入的部分用 `«…»` 标出，引擎按名替换的占位符（`{{{{PROBLEM_ID}}}}` 等）原样保留。

覆盖当前 claude 三个臂（draft / from-scratch / 协同演化）实际发出的 prompt。
生成时间：{datetime.datetime.now():%Y-%m-%d %H:%M:%S}；源文件 md5 见各文件头部。

## 文件

| 文件 | 角色 | 内容 |
|---|---|---|
{listing}

## 不放在本目录的两类内容

- **评分标准（rubric）**：固定 rubric `src/OpenClaw/interaction_initial_substantive_v1.json` 与
  critic 用的 `interaction_strategy_rubric_v6.md` 已由 `scripts/export_interaction_rubrics.py`
  导出到 `src/OpenClaw/prompts/interaction_rubrics_current.md`。它们是注入 prompt 的**内容**而非模板，
  不在这里再存一份，免得两处漂移。
- **单次运行的真实渲染件**（想看实际拼装效果时从这里取）：
  `<实验>/cpe_evaluations/round_N/<phase>/runs/.../prompt.md`（solver 实际收到的）、
  `<实验>/workflows/round_N/evolution_prompt.md`（演化器实际收到的）、
  `<实验>/workflows/round_N/critic_review.md`（critic 产出）。

## 重新生成

```
python scripts/export_evolution_prompts.py
```
"""


def main(argv: list[str]) -> int:
    output = pathlib.Path(argv[1]).expanduser() if len(argv) > 1 else OUT
    print(f"Rendering prompts into {output}")
    prompts = build()
    for name, text in prompts.items():
        write(output / name, text)
    write(output / "README.md", readme(prompts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
