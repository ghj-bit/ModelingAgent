# 交互相关 rubric 现状

本文件由 `scripts/export_interaction_rubrics.py` 生成，内容逐字取自源文件，
改动源文件后重新运行即可刷新。

## 源文件与指纹

- `src/OpenClaw/interaction_initial_substantive_v1.json` — md5 `a510fe62022e35a899fa75fe2ff21ccb`，2026-09-21 15:52:45
- `src/OpenClaw/interaction_strategy_rubric_v1.md` — md5 `12ec791d9f39ce552539810c5bdaa938`，2026-09-23 17:24:54
- `src/OpenClaw/interaction_strategy_rubric_v2.md` — md5 `b466d6daeefd71e16ef76f7a03eb0491`，2026-09-23 17:58:34
- `src/OpenClaw/interaction_strategy_rubric_v3.md` — md5 `d013f07ffd1e0da0493da7ca7ab8dd25`，2026-09-23 18:57:20
- `src/OpenClaw/interaction_strategy_rubric_v4.md` — md5 `8e8c2e4c66271bdf39b6eea72caf005c`，2026-09-23 21:17:55
- `src/OpenClaw/interaction_strategy_rubric_v5.md` — md5 `cdff05667526f3b533a76abc992a2c70`，2026-09-24 17:58:58
- `src/OpenClaw/interaction_strategy_rubric_v1.json` — md5 `5a9659139ff737abe9a85cc48a0adc51`，2026-09-23 15:17:04

---

## A. 演化实验的固定评分 rubric（当前实验正在用它打分）

`claude_scratch_evolve_r10` 的启动命令里 `--fixed-rubric` 指向的就是这个文件；
`config.json` 的 `fixed_interaction_rubric_source` 同样记录它。该实验
`rubric_evolution = False`，也就是说整个 10 轮里评分标准不变，变的是被评的交互策略。
每轮 `result.json` 里的 `fixed_rubric` / `rubric` 字段即此文件的快照。

**rubric_id**: `interaction_initial_substantive_v1`

**名称**: Traceable substantive consultation

**目的**: Ensure that one independent expert reply causes a verifiable change in the agent's subsequent analysis rather than merely confirming completed work.

### 评分标准

#### 1. Post-reply causal change

**规则**: Consult before implementation about one unresolved qualitative decision without revealing a preferred answer. After the reply, the modeling agent must independently create or revise at least one decision-relevant assumption, criterion, validation scenario, evidence artifact, confidence boundary, or report-scope decision, and state the resulting impact honestly; calculations and validation remain the agent's responsibility.

- ✅ 正面例子：An expert concern about peak-period fairness causes the agent to add and validate a peak-tail scenario after the reply, even if the final recommendation remains unchanged.
- ❌ 负面例子：The agent completes all analysis before consulting, asks the expert to approve its preferred answer, and only copies that approval into the final report.

### 注意力预算

Use one early exchange; add one follow-up only if the same decision remains unresolved.

### 成功判据

Removing the expert reply must remove at least one traceable post-reply analytical change; changing the final conclusion is not mandatory.

---

## B. critic 分支的策略评审 rubric（v1 → v4，版本化迭代）

`interaction_strategy_critic.py` 的 `DEFAULT_RUBRIC` 指向 v4（当前生效版本）；
critic 启动脚本把 v1 称作其固定初始 rubric，之后逐版演化。
这些是**评审策略**用的标准，不是给求解 agent 打分的标准，勿与 A 混用。

### interaction_strategy_rubric_v1.md

`md5 12ec791d9f39ce552539810c5bdaa938`，修改时间 2026-09-23 17:24:54

````markdown
Interaction Strategy: Consultation Value

[40] Decision-relevant consultation before the work: The consultation happens before the modeling work it governs, and the question targets a choice that can change the framework, a core assumption, or a headline conclusion, stated so that the answer could flip the main claim. Deduct when the consultation comes after the affected work is finished, when it asks the expert to endorse an answer the agent has already chosen, or when it is spent on implementation, code, parameters, or validation mechanics.

[40] Traceable change from the reply: The reply produces at least one explicit, recorded modeling change — a decision traced to the reply that names the artifact it changed (assumption, criterion, scenario, scope) — or a recorded reason why no change follows. Deduct when the reply is only restated or praised, when the recorded decision cannot be traced to the reply text, or when a change is claimed that the artifacts do not show.

[20] Answerable question: Brief problem framing, one explicit decision point, and at most three options with tradeoffs, so the expert can answer in one pass. Deduct when there is no explicit decision point, when more than three options are offered, when options carry no tradeoffs, or when the question is open enough that the expert would have to do the modeling to answer it.

---

How to score: each criterion scores 0 up to its bracketed maximum (total 100). A non-zero score needs a quote or file pointer from the run's own artifacts; without one it scores 0. Report per criterion: score, evidence, one sentence of justification, one concrete edit to the interaction policy text.

How to evolve: add, split, reword, or retire one criterion per version, each with its own bracketed value, and state predicted_effect — which criteria move, in which direction, on which of last round's runs.
````

### interaction_strategy_rubric_v2.md

`md5 b466d6daeefd71e16ef76f7a03eb0491`，修改时间 2026-09-23 17:58:34

````markdown
Interaction Strategy: Auditable Decision Transfer

[30] Consequential decision, stated as a test: The question names the artifact or headline claim it governs and says what would change if the expert answered differently — a reported number, a conclusion, or a validation outcome. Deduct when the consequence stays implicit, when the question only asserts that the choice "controls the direction", or when no reported value could move either way.

[30] Auditable adoption: For the decision finally taken, the record names the artifact it changed, quotes the phrase in the reply that produced it, and states what was left unchanged. Deduct when the change is only a narrative summary, when nothing from the reply is quoted, or when the record claims a change the artifacts do not show.

[20] Independent judgement: The record shows the agent weighed the reply rather than complying with it — at least one element it declined, constrained, or qualified, with a reason of its own. Deduct when the reply is adopted wholesale, when the disagreement is unrecorded, or when the stated reason merely restates the reply.

[20] Answerable question: At most three options, each with one explicit strength and one explicit limitation, and nothing that asks the expert to compute, fetch data, or write code. Deduct for additional options, missing tradeoffs, or any request for calculation or implementation.

Scores are summed and normalized by this rubric's theoretical maximum (100): normalized = total / 100. A non-zero score needs a quote or a named artifact; without one the criterion scores 0.
````

### interaction_strategy_rubric_v3.md

`md5 d013f07ffd1e0da0493da7ca7ab8dd25`，修改时间 2026-09-23 18:57:20

````markdown
Interaction Strategy: Consultation Quality

[30] Decision-targeted question, asked before the work: The question isolates exactly one open decision, and that decision governs the modeling framework — an assumption, a decision criterion, a scope boundary, or a headline claim — and it is put to the expert before the work it governs is done. Deduct when the question bundles several decisions, when it targets implementation, parameters, data handling, or validation mechanics, or when it arrives after the affected work is already complete.

[30] Genuine alternatives, no steering: The question offers at least two alternatives a competent expert could actually choose between, each with its own tradeoff, and it neither states nor implies which one the agent prefers. Deduct when only one real option is offered and the rest are strawmen, when tradeoffs are missing, or when the wording signals a preferred answer and asks the expert to endorse it.

[25] The reply moves the work: The expert's answer departs from the draft's default — choosing a different alternative, rejecting the framing, or raising a consideration absent from the question — and it is actionable, in that it points at the assumption, criterion, or scope the agent should change. Deduct when the reply only confirms the draft's default, when it surveys possibilities without deciding, or when it must ask for context or computation the question should have supplied.

[15] One exchange, usable in one pass: The consultation stays inside the policy's exchange cap, a second exchange appears only for a decision distinct from the first, and the reply needed no follow-up to be usable. Deduct for a repeated or confirming exchange, for exceeding the cap, or when the reply could not be used without clarification.

Scores are summed and normalized by this rubric's theoretical maximum (100): normalized = total / 100. Score only the dialogue — the policy text, the question, the reply, and the draft it started from. Do not score what the run wrote about the exchange; a record of good practice is not good practice.
````

### interaction_strategy_rubric_v4.md

`md5 8e8c2e4c66271bdf39b6eea72caf005c`，修改时间 2026-09-23 21:17:55

````markdown
Interaction Strategy: Multi-Round Consultation

[20] Decision-targeted opening, asked before the work: The first exchange isolates exactly one open decision that governs the modeling framework — an assumption, a decision criterion, a scope boundary, or a headline claim — and is put to the expert before the work it governs is done. Deduct when it bundles several decisions, when it targets implementation, parameters, data handling, or validation mechanics, or when it arrives after the affected work is already complete.

[20] Options, not steering: Whichever exchange puts candidates to the expert offers at least two alternatives a competent expert could actually choose between, each with its own tradeoff, and neither states nor implies which one the agent prefers. Deduct when only one real option is offered and the rest are strawmen, when tradeoffs are missing, or when the wording signals a preferred answer and asks the expert to endorse it.

[25] Each further exchange asks something new: When a consultation uses more than one exchange, a later exchange asks something the earlier ones did not — a different question about the same decision, or one the previous reply made available — and the difference is in kind, not only in detail. Judge this on the questions themselves, whatever form they take. With a single exchange, score full marks when that exchange was enough to settle the decision, and deduct when the reply plainly opened a question the agent never asked. Deduct when a later exchange is the earlier one asked again in more detail, when it only asks the expert to confirm or elaborate, or when it spends an exchange without settling the decision in play.

[20] Every reply moves or sharpens the decision: Each reply changes or sharpens something the work then depends on — rather than leaving the plan it was asked about as it stood — and the run acts on what the reply established. Deduct when a reply only ratifies the plan's existing default or the agent's own stated preference, however well argued, and when what it established is left unused.

[15] Each round depends on the last: An exchange after the first could not have been asked without the reply before it, and either tightens what that reply established or carries it into the next decision it bears on. Deduct when the follow-up could have come in the first exchange, when one decision is split across several exchanges, and when what the reply opened is left unaddressed.

Scores are summed and normalized by this rubric's theoretical maximum (100): normalized = total / 100. Score only the dialogue — the policy text, the questions, the replies, and the draft or plan they started from. Do not score what the run wrote about the exchange; a record of good practice is not good practice.
````

### interaction_strategy_rubric_v5.md ← 当前默认

`md5 cdff05667526f3b533a76abc992a2c70`，修改时间 2026-09-24 17:58:58

````markdown
Interaction Strategy: Single-Exchange Consultation

[20] Decision-targeted opening, asked before the work: The consultation isolates exactly one open decision that governs the modeling framework — an assumption, a decision criterion, a scope boundary, or a headline claim — and is put to the expert before the work it governs is done. Deduct when it bundles several decisions, when it targets implementation, parameters, data handling, or validation mechanics, or when it arrives after the affected work is already complete.

[20] Options, not steering: The question puts candidates to the expert offering at least two alternatives a competent expert could actually choose between, each with its own tradeoff, and neither states nor implies which one the agent prefers. Deduct when only one real option is offered and the rest are strawmen, when tradeoffs are missing, or when the wording signals a preferred answer and asks the expert to endorse it.

[25] One exchange, answerable in one pass: The consultation is a single exchange, and that exchange carries everything a competent expert needs to answer it without asking for context or doing the modeling: the problem framing, the one decision point, and the candidate options with their tradeoffs. Deduct when the question leaves the decision under-specified, when it asks the expert to compute, fetch data, or write code, or when it would need a follow-up to be usable at all.

[20] Every reply moves or sharpens the decision: The reply changes or sharpens something the work then depends on — rather than leaving the work it was asked about as it stood — and the run acts on what the reply established. Deduct when a reply only ratifies the existing default or the agent's own stated preference, however well argued, and when what it established is left unused.

[15] What the reply opens is settled inside the run: The expert's part ends with the reply, so anything the reply introduces — a new constraint, a variant, a failure mode — must be resolved by the agent itself and carried into the modeling work, rather than left unaddressed or sent back as another question. Deduct when a question the reply plainly opened is never taken up, when the agent asks the expert to settle something it could have decided from the reply and the supplied evidence, and when what the reply opened is recorded but not acted on.

Scores are summed and normalized by this rubric's theoretical maximum (100): normalized = total / 100. Score only the dialogue — the policy text, the question, the reply, and the work they produced. Do not score what the run wrote about the exchange; a record of good practice is not good practice.
````

---

## C. 已废弃的旧 schema（仅供追溯）

`interaction_strategy_rubric_v1.json` 采用 `-1 / 0 / +1` 逐条规则计分、共 6 条规则
（R1..R6），与 B 中 v1.md 起的 `0..满分` 求和方法不是同一套，已被取代。原样附上以便对照：

```json
{
  "rubric_id": "interaction_strategy_v1",
  "name": "Consultation value and budget discipline",
  "purpose": "Score one round's interaction strategy together with the consultation it actually produced, so the evolver learns which policy rules earn their cost. Every rule is decidable from artifacts the run already writes; nothing here judges the modeling result itself (that is the task score).",
  "inputs": {
    "policy": "the '# Human Expert Interaction' block of the run's prompt.md",
    "receipt": "output/results/interaction_receipt.json (questions_asked, expert_answers, exchange_count, workflow_max_exchanges)",
    "evidence": "output/results/interaction_evidence.md",
    "raw": "output/logs/operator_feedback/expert_question_N.md and expert_reply_N.json",
    "cost": "interaction_cost recorded by the launcher (exchanges, tokens, latency) — reported, not scored here"
  },
  "scoring_protocol": {
    "per_rule": "-1 = the rule is violated, 0 = not exercised or undecidable, +1 = the rule is clearly satisfied",
    "aggregate": "0.5 + 0.5 * mean(rule scores) so the scale stays 0..1 and 0.5 is neutral",
    "repeat": "score three times, keep the median per rule; report the spread",
    "must_cite": "every non-zero score needs a quote or file pointer, otherwise it becomes 0",
    "output_schema": {
      "rule_scores": [
        {
          "id": "R1",
          "score": -1,
          "evidence": "interaction_evidence.md: 'the consultation was held after the pipeline had already run'",
          "why": "one sentence tying the evidence to the plus/minus clause",
          "fix": "one concrete edit to the interaction policy text, addressed to the rule that failed"
        }
      ],
      "aggregate": 0.5,
      "top_fix": "the single policy edit with the largest expected score gain",
      "unjudgeable": [
        "rule ids whose evidence is missing from this run"
      ],
      "notes": "at most 60 words, no restating of the scores"
    }
  },
  "criteria": [
    {
      "id": "R1",
      "name": "Timing and independence",
      "rule": "The consultation happens before the work it governs, and the question is a genuine open decision rather than a request for approval.",
      "plus": "The affected modeling work starts only after the reply; the question states the decision point without revealing which option the agent prefers.",
      "minus": "The consultation comes after the affected work is finished; the question discloses a preferred answer and asks the expert to endorse it; a settled decision is re-opened.",
      "evidence": "timestamps of the question file versus the artifacts it governs; the wording of the question"
    },
    {
      "id": "R2",
      "name": "Decision weight",
      "rule": "The question targets a choice that can change the framework, a core assumption, or a headline conclusion.",
      "plus": "The question names what differs between the options in modeling terms (assumptions, criteria, deliverable, quantitative outcome), and the answer could flip the main claim.",
      "minus": "The consultation is spent on implementation, code, parameters, data handling, or validation mechanics; or on a choice whose outcome cannot change any reported number.",
      "evidence": "the 'Strategic Decision Point' section of the question and its stated impact"
    },
    {
      "id": "R3",
      "name": "Consultation package",
      "rule": "The question is answerable in one pass: brief problem framing, one explicit decision point, at most three options with tradeoffs.",
      "plus": "All three blocks present; at most three options, each with advantage, limitation, and expected impact in a few lines.",
      "minus": "No explicit decision point; more than three options; options without tradeoffs; an open-ended 'what do you think' that the expert cannot answer without doing the modeling.",
      "evidence": "structure and length of expert_question_1.md"
    },
    {
      "id": "R4",
      "name": "Traceable adoption",
      "rule": "The reply produces at least one explicit, recorded modeling change, or a recorded reason why no change follows.",
      "plus": "At least one decision traced to the reply, naming the artifact it changed (assumption, criterion, scenario, scope); 'no change' is recorded with the reason.",
      "minus": "The reply is only restated or praised; the recorded decision cannot be traced to the reply text; a change is claimed that the artifacts do not show.",
      "evidence": "interaction_evidence.md decision section versus the raw reply and the affected artifact"
    },
    {
      "id": "R5",
      "name": "Budget discipline",
      "rule": "One exchange is the default; a further exchange is spent only on a decision distinct from every earlier one, and never exceeded the cap.",
      "plus": "Exactly one exchange when one suffices; a second only for a different stage or uncertainty, with the distinction stated; stops once the decision is settled.",
      "minus": "The cap is exceeded; a second exchange repeats the first uncertainty or asks for elaboration, confirmation, or review of an earlier reply.",
      "evidence": "exchange_count versus workflow_max_exchanges; the topics of the questions in order"
    },
    {
      "id": "R6",
      "name": "Fidelity of the record",
      "rule": "What the run records about the exchange matches the raw question and reply files.",
      "plus": "The reply is quoted or faithfully summarized, its caveats and limits are kept, and the raw files are left untouched.",
      "minus": "The reply is paraphrased into something stronger or weaker than it was; a caveat is dropped; a decision is attributed to the expert that the reply does not support.",
      "evidence": "interaction_evidence.md and interaction_added_content.md versus expert_reply_N.json"
    }
  ],
  "attention_budget": "One mandatory early exchange; a second only for a distinct unresolved decision; the cap is the policy's own max_exchanges. The launcher scores exchange count, tokens, and latency outside this rubric, so do not double-count cost here.",
  "success_test": "Removing the reply from a run that scores +1 on R1, R2 and R4 must remove at least one traceable modeling decision; a rubric version that cannot separate such a run from an approval-seeking run is not doing any work.",
  "evolution_hooks": {
    "stable_ids": "R1..R6 keep their ids across versions so per-rule scores stay comparable over rounds",
    "allowed_edits": "reword a rule's plus/minus, split a rule into two, retire a rule that is never decisive, or add one new rule with its own id, plus and minus",
    "forbidden": "rewriting the whole rubric in one step, editing rule ids, or adding a rule whose evidence no run writes",
    "each_edit_must_state": "predicted_effect = which rule scores move, in which direction, on which of last round's runs"
  }
}
```

