"""Export the interaction rubrics in force to one readable Markdown file.

Two families live side by side and are easy to confuse:

* ``src/OpenClaw/interaction_initial_substantive_v1.json`` -- the *fixed scoring
  rubric* the workflow-evolution arm hands the judge.  It is what a round is
  scored against and it never changes during a run.
* ``src/OpenClaw/interaction_strategy_rubric_v*.md`` -- the *strategy review
  rubric* the critic arm reads, one version per iteration.  The critic's
  ``DEFAULT_RUBRIC`` points at the newest one; the launcher calls v1 its fixed
  initial rubric.  The older ``interaction_strategy_rubric_v1.json`` is the
  superseded ``-1/0/+1`` schema and is listed only for provenance.

Rendering them together, verbatim and with hashes, is what makes a review
possible: a rubric quoted out of context is impossible to check against the file
it came from.  Re-run this whenever any of them changes.

    python scripts/export_interaction_rubrics.py [output.md]
"""

from __future__ import annotations

import datetime
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

RUBRIC_DIR = REPO / "src" / "OpenClaw"
FIXED_RUBRIC = RUBRIC_DIR / "interaction_initial_substantive_v1.json"
CRITIC_RUBRICS = sorted(RUBRIC_DIR.glob("interaction_strategy_rubric_v*.md"))
LEGACY_RUBRIC = RUBRIC_DIR / "interaction_strategy_rubric_v1.json"
CRITIC_DEFAULT = RUBRIC_DIR / "interaction_strategy_rubric_v6.md"
OUT = RUBRIC_DIR / "prompts" / "interaction_rubrics_current.md"


def digest(path: pathlib.Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def stamp(path: pathlib.Path) -> str:
    """Path, hash and mtime, so a quote in a review can be tied to a file."""
    rel = path.relative_to(REPO)
    if not path.is_file():
        return f"- `{rel}` — 不存在"
    mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
    return f"- `{rel}` — md5 `{digest(path)}`，{mtime:%Y-%m-%d %H:%M:%S}"


def render_fixed_rubric(payload: dict) -> list[str]:
    lines = [
        f"**rubric_id**: `{payload.get('rubric_id', '')}`",
        "",
        f"**名称**: {payload.get('name', '')}",
        "",
        f"**目的**: {payload.get('purpose', '')}",
        "",
        "### 评分标准",
        "",
    ]
    for index, criterion in enumerate(payload.get("criteria", []), start=1):
        lines += [
            f"#### {index}. {criterion.get('name', '')}",
            "",
            f"**规则**: {criterion.get('rule', '')}",
            "",
            f"- ✅ 正面例子：{criterion.get('positive_example', '')}",
            f"- ❌ 负面例子：{criterion.get('negative_example', '')}",
            "",
        ]
    for key, label in (("attention_budget", "注意力预算"), ("success_test", "成功判据")):
        if payload.get(key):
            lines += [f"### {label}", "", str(payload[key]), ""]
    for key, value in payload.items():
        if key in {"rubric_id", "name", "purpose", "criteria", "attention_budget", "success_test"}:
            continue
        lines += [f"### {key}", "", f"```\n{value}\n```", ""]
    return lines


def build() -> str:
    lines = [
        "# 交互相关 rubric 现状",
        "",
        "本文件由 `scripts/export_interaction_rubrics.py` 生成，内容逐字取自源文件，",
        "改动源文件后重新运行即可刷新。",
        "",
        "## 源文件与指纹",
        "",
        stamp(FIXED_RUBRIC),
        *[stamp(path) for path in CRITIC_RUBRICS],
        stamp(LEGACY_RUBRIC),
        "",
        "---",
        "",
        "## A. 演化实验的固定评分 rubric（当前实验正在用它打分）",
        "",
        "`claude_scratch_evolve_r10` 的启动命令里 `--fixed-rubric` 指向的就是这个文件；",
        "`config.json` 的 `fixed_interaction_rubric_source` 同样记录它。该实验",
        "`rubric_evolution = False`，也就是说整个 10 轮里评分标准不变，变的是被评的交互策略。",
        "每轮 `result.json` 里的 `fixed_rubric` / `rubric` 字段即此文件的快照。",
        "",
    ]
    lines += render_fixed_rubric(json.loads(FIXED_RUBRIC.read_text(encoding="utf-8")))

    lines += [
        "---",
        "",
        "## B. critic 分支的策略评审 rubric（v1 → v4，版本化迭代）",
        "",
        "`interaction_strategy_critic.py` 的 `DEFAULT_RUBRIC` 指向 v4（当前生效版本）；",
        "critic 启动脚本把 v1 称作其固定初始 rubric，之后逐版演化。",
        "这些是**评审策略**用的标准，不是给求解 agent 打分的标准，勿与 A 混用。",
        "",
    ]
    for path in CRITIC_RUBRICS:
        marker = " ← 当前默认" if path == CRITIC_DEFAULT else ""
        lines += [
            f"### {path.name}{marker}",
            "",
            f"`md5 {digest(path)}`，修改时间 "
            f"{datetime.datetime.fromtimestamp(path.stat().st_mtime):%Y-%m-%d %H:%M:%S}",
            "",
            "````markdown",
            path.read_text(encoding="utf-8").rstrip(),
            "````",
            "",
        ]

    if LEGACY_RUBRIC.is_file():
        lines += [
            "---",
            "",
            "## C. 已废弃的旧 schema（仅供追溯）",
            "",
            "`interaction_strategy_rubric_v1.json` 采用 `-1 / 0 / +1` 逐条规则计分、共 6 条规则",
            "（R1..R6），与 B 中 v1.md 起的 `0..满分` 求和方法不是同一套，已被取代。原样附上以便对照：",
            "",
            "```json",
            json.dumps(
                json.loads(LEGACY_RUBRIC.read_text(encoding="utf-8")),
                ensure_ascii=False,
                indent=2,
            ),
            "```",
            "",
        ]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    output = pathlib.Path(argv[1]).expanduser() if len(argv) > 1 else OUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build(), encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
