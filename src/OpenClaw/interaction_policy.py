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
exchange budget and the prohibition on asking the expert for parameters,
computation or anything about code sit outside it and are enforced as fixed by
``assert_fixed_policy_sections_unchanged``.  A round may also add an operator,
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

The consultation is assembled from the interaction operators set out below. Each states when it applies and how it is executed. They are a repertoire, not a checklist: an operator is applied only when its trigger condition is met, never merely because the consultation still has budget.

Apply exactly one operator per exchange, and apply an operator again only for a decision distinct from every decision it has already addressed. Address one decision at a time, in descending order of its effect on the modeling direction. The exchange budget is fixed and is to be filled: when no trigger condition is met, put the most consequential open decision to the expert through the operator whose question fits it best.

## Prohibited Requests

No operator, in any wording, may put any of the following to the expert. This list does not change.

- parameter values, ranges, estimates, initial conditions, or calibration targets;
- computation, derivation, data processing, statistical analysis, or simulation;
- code in any form: writing, reading, reviewing, debugging, or tool usage;
- model validation, result checking, error analysis, or numerical comparison;
- routine method selection, minor assumption adjustments, or anything a reasonable default would settle;
- approval, confirmation, or review of a decision the agent has already made.

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

**How.** Name the missing context and how the model changes if it turns out differently, then ask the expert to explain it qualitatively. Derive the values yourself.

**Example.** Agent: "The model turns on how maintenance is scheduled in practice, which nothing here records." Expert: "In planned blocks -- not at random."

### Operator 4: Refine / correct

**When.** After an earlier reply, a weakness that reply exposed is still unresolved, or an aspect stayed shallower than the decision deserves.

**How.** Show the model as it now stands after that reply, then ask the expert to correct what is still wrong or deepen what is still shallow.

**Example.** Agent: "I adopted your reading of the objective. What does the revised model still leave wrong?" Expert: "The constraint that reading implies is missing."

# Interaction Limits

The consultation runs three exchanges, one operator each; an exchange is one question and one reply.

After this policy terminates, the agent must not request further expert feedback for execution, computation, implementation, checking, or validation."""
