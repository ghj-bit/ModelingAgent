"""The fixed expert-interaction policies used by the OpenClaw runners.

``MODELING_STRATEGY_ESCALATION`` is the frozen "# Human Expert Interaction"
policy the initial-draft solution-evolution launcher and the workflow-test
runner pin for every task, so the two cannot drift.

``OPERATOR_DRIVEN_CONSULTATION`` is the seed the *Claude Code* solution
evolution arm runs on instead.  It states the consultation as a repertoire of
interaction operators, seeded with four -- resolve uncertainty, challenge
reasoning, inject knowledge, refine/correct -- each carrying its own trigger
condition and execution rule.  The operators and the rule that chooses among
them are the mutable surface the rounds rewrite; the autonomy default, the
exchange budget and the prohibition list -- coding/implementation, parameter
tuning, standard derivations and computation -- sit outside it and are enforced
as fixed by ``assert_fixed_policy_sections_unchanged``.  The list bars parameter
*tuning*, not parameter *plausibility*: asking the expert whether a constant the
agent has itself assumed is of a sensible order of magnitude stays permitted,
and Operator 3 says so.  A round may also add an operator,
which is why the repertoire is stated as steps rather than as a table the engine
would have to be taught to extend -- and why nothing in the policy, fixed
sections included, may state how many operators there are.

The OpenHands arm and the workflow-test runner keep ``MODELING_STRATEGY_
ESCALATION``, so their runs stay comparable with the ones already collected.
"""

MODELING_STRATEGY_ESCALATION = '# Human Expert Interaction\n\n## Interaction Policy 1: Modeling Strategy Escalation\n\nThe agent should solve the modeling task autonomously by default, and every task includes exactly one required consultation: the first expert exchange is part of the workflow, not a contingency. Only a consultation after that first one is triggered by an unresolved strategic uncertainty that could significantly change the modeling framework, core assumptions, or final conclusions.\n\n### Trigger Conditions\n\nComplete the first consultation unconditionally. Choose for it the single open question that most controls the modeling direction of the draft and put that choice to the expert, even when you could defend a default on your own: the value of the expert is to challenge the direction you have already chosen, which a default cannot do. Do not spend this consultation on implementation, derivation, data processing, or validation questions. Any consultation after the first requires **all** of the following conditions:\n\n1. Multiple substantially different yet reasonable modeling directions remain;\n2. The choice may significantly affect the modeling framework, core assumptions, or final conclusions;\n3. The agent cannot resolve the uncertainty independently using the problem statement, `draft.md`, domain knowledge, or its existing analysis;\n4. Expert feedback can be directly converted into a clear and actionable modeling decision.\n\nDo not spend any further consultation on:\n\n- code implementation, debugging, or tool usage;\n- mathematical derivations, data processing, or computation;\n- parameter selection, model training, or tuning;\n- model validation, result checking, or error analysis;\n- routine method selection or minor assumption adjustments;\n- additional confirmation intended merely to improve answer quality;\n- issues that can be resolved through reasonable default assumptions.\n\nIf several uncertainties qualify, address them one at a time in descending order of potential impact on the modeling direction, and only while the interaction budget allows.\n\n### Interaction Workflow\n\nThe steps below are the interaction workflow. They are the only part of this\npolicy open to revision, and each step must stay short enough to be followed\nexactly.\n\n#### Consultation Content\n\nBefore requesting expert feedback, provide only:\n\n1. **Problem Understanding**\n\n   - A brief interpretation of the task objective;\n   - The current modeling stage.\n\n2. **Strategic Decision Point**\n\n   - The core uncertainty that cannot be resolved autonomously;\n   - Its potential impact on the modeling direction.\n\n3. **Candidate Options**\n\n   - No more than three candidate directions;\n   - The main advantages, limitations, and expected impact of each.\n\n#### Feedback Handling\n\nAfter receiving feedback, the agent must:\n\n- translate the feedback into one explicit modeling decision;\n- revise only the modeling strategy directly affected by that decision;\n- treat that decision as settled and carry forward the work it governs autonomously;\n- not reopen a settled decision, and not seek confirmation, review, or validation of one.\n\n### Interaction Limit\n\nMaximum expert interactions: **3**.\n\nOne interaction consists of one question from the agent and one response from the expert. A further interaction is permitted only when it addresses a decision point distinct from every earlier one: a different modeling stage, a different unresolved uncertainty, and a different consequence for the modeling direction. Re-asking about a settled decision, or asking the expert to elaborate on, confirm, or approve an earlier reply, is not a distinct decision point and must not consume the budget. If a reply is incomplete, resolve it autonomously with reasonable default assumptions rather than spending a further interaction on it.\n\n### Stop Conditions\n\nNever terminate this policy before one expert reply has been received. After that, terminate when any of the following conditions is met:\n\n- no strategic uncertainty materially affecting the modeling direction exists;\n- the agent can make the decision independently using available information or reasonable assumptions;\n- every qualifying uncertainty has been converted into an explicit modeling choice;\n- the maximum of three expert interactions has been reached.\n\n### Computational Efficiency\n\nKeep every run bounded. Express grid and sample sweeps as vectorised array\noperations rather than per-element loops, and size the grids and sample counts\nso each script finishes in minutes; a coarse sweep that completes is worth more\nthan a fine one that does not.\n\nAfter this policy terminates, the agent must not request further expert feedback for execution, computation, implementation, checking, or validation.'

OPERATOR_DRIVEN_CONSULTATION = """# Human Expert Interaction

## Principle

The agent solves the modeling task autonomously by default: the model, the code, the calculation, the validation, and the report are its own work. It consults the expert for strategic, qualitative judgment it cannot reach from the problem statement, the pre-gathered evidence, or its own analysis.

The expert never does computation. Every technical translation of a reply -- assumptions, equations, parameter values, code, and validation -- stays with the agent, which must be able to justify each one on its own evidence.

## Interaction Operators

Before each exchange:

Identify the most important unresolved decision that could materially affect the modeling direction or conclusions.

Determine what kind of expert input is needed:

- resolve ambiguity;
- challenge a key assumption;
- provide missing real-world knowledge;
- refine a previously introduced modeling mechanism.

Select the operator that best matches that need.

Name the operator you selected -- its number and its name -- at the head of the
question, so the exchange records which operator it applied. Every exchange
carries one.

Ask exactly one focused question.

After each expert reply:

Determine what decision, assumption, constraint, or mechanism changed.

Incorporate the required implications into the model.

Identify any new high-impact uncertainty introduced by the reply.

Re-rank the remaining unresolved decisions before choosing the next operator.

Later exchanges must depend on earlier replies. Do not predefine an operator sequence and do not choose an operator merely for diversity.

## Prohibited Requests

The agent must not request feedback for:

- coding, debugging, or implementation issues;
- parameter tuning or optimization details;
- standard mathematical derivations;
- computation, data processing, or routine validation.

# 可选交互算子

### Operator 1: Resolve uncertainty

**When.** An open decision could change the modeling direction, framework, or conclusions, and the problem statement, the evidence, and the agent's own analysis cannot separate two or more defensible readings.

**How.** Lay out the competing readings and what each implies for the model, then ask which one the real-world setting favors. State no preference.

**Example.** Agent: "Should the objective minimize peak demand or total consumption? They imply different models." Expert: "Peak -- that is what the system is constrained by."

### Operator 2: Challenge reasoning

**When.** A load-bearing assumption or chain of reasoning has gone uncriticized, and being wrong about it would move the conclusions.

**How.** State it plainly and without defending it, then ask the expert to attack it or name a factor the model left out. Validate the changes yourself.

**Example.** Agent: "The model treats the two effects as independent." Expert: "They are not -- the second saturates at high load, and you leave that out."

### Operator 3: Inject knowledge

**When.** The model depends on how the real-world system actually behaves, and that knowledge is missing from the problem statement and the evidence and cannot be reached by calculation.

**How.** Name the missing context and how the model changes if it turns out differently, then ask the expert to explain it qualitatively, including whether the order of magnitude you have assumed is plausible for the real setting. Derive the values yourself.

**Example.** Agent: "The model turns on how maintenance is scheduled in practice, which nothing here records." Expert: "In planned blocks -- not at random."

### Operator 4: Refine / correct

**When.** After an earlier reply, a weakness that reply exposed is still unresolved, or an aspect stayed shallower than the decision deserves.

**How.** Show the model as it now stands after that reply, then ask the expert to correct what is still wrong or deepen what is still shallow.

**Example.** Agent: "I adopted your reading of the objective. What does the revised model still leave wrong?" Expert: "The constraint that reading implies is missing."

# Interaction Limits

The consultation runs three exchanges, one operator each; an exchange is one question and one reply.

After this policy terminates, the agent must not request further expert feedback for execution, computation, implementation, checking, or validation."""


_ROUTED_SECTION_HEADING = "# 可选交互算子"

# The Router makes the operator choice an explicit, stated decision instead of
# one the solver reaches by reading four `When` clauses and picking.  It exists
# because that implicit routing collapsed in practice: across the first 22
# consultations of claude_fp8_opseed_r10, 45% ran the identical 1-2-4 arc, the
# last exchange was Operator 4 in 78% of them, and Operator 3 was reached for in
# only 8% -- a fixed script, not a reading of the state.
#
# It targets the three failures that audit found, and nothing else:
#   * the state is read into one line before anything is chosen, so the choice
#     has a stated basis rather than a habitual one;
#   * the arc is declared an output of that reading, which makes "it is this
#     operator's turn" an explicit failure rather than a default;
#   * no operator may be reached for without the reply its `When` requires, which
#     is what let Operator 4 become the automatic last move.
_ROUTER_STEP = """### Router

**When.** Before each exchange, and again after every reply. The choice is made here, from the state as it now stands, and is never carried forward from the previous exchange.

**How.** Read the state into one line: the modeling stage, the decisions the earlier replies already settled, and the single largest decision still open. Choose the operator whose `When` that decision meets, name that decision in one line before the question, and put that one decision to the expert. The arc is an output of this reading and not a plan: repeating a familiar sequence is a routing failure unless the state genuinely repeated, and no operator may be reached for because it is the turn it usually takes.

**Example.** State: the direction is settled and the model validated; the load assumption the conclusion rests on has never been criticized; no reply has exposed anything unresolved. Choice: Operator 2, because the uncriticized assumption is the largest open decision. Not Operator 4: no reply exposed a weakness for it to act on."""

# Derived rather than retyped.  The two arms of the routing experiment have to
# differ by this block and by nothing else, and deriving the routed seed makes
# that a property of the code instead of a claim about a careful copy -- a
# retyped second policy could drift from the first and quietly turn the
# comparison into two changes.
OPERATOR_DRIVEN_CONSULTATION_ROUTED = OPERATOR_DRIVEN_CONSULTATION.replace(
    f"{_ROUTED_SECTION_HEADING}\n\n",
    f"{_ROUTED_SECTION_HEADING}\n\n{_ROUTER_STEP}\n\n",
    1,
)
if OPERATOR_DRIVEN_CONSULTATION_ROUTED == OPERATOR_DRIVEN_CONSULTATION:
    # Loud, because the silent version of this is an experiment whose two arms
    # are the same policy with different labels.
    raise RuntimeError(
        "routed seed: the operator section heading moved, so the Router step was "
        f"not inserted (looked for {_ROUTED_SECTION_HEADING!r})"
    )
