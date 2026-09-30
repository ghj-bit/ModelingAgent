"""The fixed expert-interaction policies used by the OpenClaw runners.

``MODELING_STRATEGY_ESCALATION`` is the frozen "# Human Expert Interaction"
policy the initial-draft solution-evolution launcher and the workflow-test
runner pin for every task, so the two cannot drift.

``OPERATOR_DRIVEN_CONSULTATION`` is the seed the *Claude Code* solution
evolution arm runs on instead.  It states the consultation as one prose rule
under ``## Interaction Strategy`` -- what the agent must find out before each
exchange, what it puts on the table, and how it treats the reply -- and carries
no operator repertoire at all: the rounds evolve the rule, and the engine
rejects any patch naming an operator section, so there is no second thing for
them to move.  That rule is the seed's only mutable section; the prohibition
list and the exchange budget sit outside it and are enforced as fixed by
``assert_fixed_policy_sections_unchanged``.

The prohibition list is three items -- coding/implementation, standard
mathematical derivations, and computation or data processing.  Parameter
*plausibility* is deliberately not among them: asking the expert whether a
constant the agent has itself assumed is of a sensible order of magnitude,
whether it sits inside a plausible range, and over what interval it should be
checked stays permitted, and the rule's own wording is what has to carry that
ask.

The OpenHands arm and the workflow-test runner keep ``MODELING_STRATEGY_
ESCALATION``, so their runs stay comparable with the ones already collected.

The operator roster this seed used to state was removed on 2026-09-30.  The
Claude arm's consultations had measured it as pure overhead: across the 118
rollouts of ``claude_fp8_infogap_r15`` every judgment exchange returned the
single word the expert role prompt asked for, so the operator a question was
headed with decided nothing about its content, and no scorer ever read it.  The
seed now states the consultation as a prose rule and nothing else.
"""

MODELING_STRATEGY_ESCALATION = '# Human Expert Interaction\n\n## Interaction Policy 1: Modeling Strategy Escalation\n\nThe agent should solve the modeling task autonomously by default, and every task includes exactly one required consultation: the first expert exchange is part of the workflow, not a contingency. Only a consultation after that first one is triggered by an unresolved strategic uncertainty that could significantly change the modeling framework, core assumptions, or final conclusions.\n\n### Trigger Conditions\n\nComplete the first consultation unconditionally. Choose for it the single open question that most controls the modeling direction of the draft and put that choice to the expert, even when you could defend a default on your own: the value of the expert is to challenge the direction you have already chosen, which a default cannot do. Do not spend this consultation on implementation, derivation, data processing, or validation questions. Any consultation after the first requires **all** of the following conditions:\n\n1. Multiple substantially different yet reasonable modeling directions remain;\n2. The choice may significantly affect the modeling framework, core assumptions, or final conclusions;\n3. The agent cannot resolve the uncertainty independently using the problem statement, `draft.md`, domain knowledge, or its existing analysis;\n4. Expert feedback can be directly converted into a clear and actionable modeling decision.\n\nDo not spend any further consultation on:\n\n- code implementation, debugging, or tool usage;\n- mathematical derivations, data processing, or computation;\n- parameter selection, model training, or tuning;\n- model validation, result checking, or error analysis;\n- routine method selection or minor assumption adjustments;\n- additional confirmation intended merely to improve answer quality;\n- issues that can be resolved through reasonable default assumptions.\n\nIf several uncertainties qualify, address them one at a time in descending order of potential impact on the modeling direction, and only while the interaction budget allows.\n\n### Interaction Workflow\n\nThe steps below are the interaction workflow. They are the only part of this\npolicy open to revision, and each step must stay short enough to be followed\nexactly.\n\n#### Consultation Content\n\nBefore requesting expert feedback, provide only:\n\n1. **Problem Understanding**\n\n   - A brief interpretation of the task objective;\n   - The current modeling stage.\n\n2. **Strategic Decision Point**\n\n   - The core uncertainty that cannot be resolved autonomously;\n   - Its potential impact on the modeling direction.\n\n3. **Candidate Options**\n\n   - No more than three candidate directions;\n   - The main advantages, limitations, and expected impact of each.\n\n#### Feedback Handling\n\nAfter receiving feedback, the agent must:\n\n- translate the feedback into one explicit modeling decision;\n- revise only the modeling strategy directly affected by that decision;\n- treat that decision as settled and carry forward the work it governs autonomously;\n- not reopen a settled decision, and not seek confirmation, review, or validation of one.\n\n### Interaction Limit\n\nMaximum expert interactions: **3**.\n\nOne interaction consists of one question from the agent and one response from the expert. A further interaction is permitted only when it addresses a decision point distinct from every earlier one: a different modeling stage, a different unresolved uncertainty, and a different consequence for the modeling direction. Re-asking about a settled decision, or asking the expert to elaborate on, confirm, or approve an earlier reply, is not a distinct decision point and must not consume the budget. If a reply is incomplete, resolve it autonomously with reasonable default assumptions rather than spending a further interaction on it.\n\n### Stop Conditions\n\nNever terminate this policy before one expert reply has been received. After that, terminate when any of the following conditions is met:\n\n- no strategic uncertainty materially affecting the modeling direction exists;\n- the agent can make the decision independently using available information or reasonable assumptions;\n- every qualifying uncertainty has been converted into an explicit modeling choice;\n- the maximum of three expert interactions has been reached.\n\n### Computational Efficiency\n\nKeep every run bounded. Express grid and sample sweeps as vectorised array\noperations rather than per-element loops, and size the grids and sample counts\nso each script finishes in minutes; a coarse sweep that completes is worth more\nthan a fine one that does not.\n\nAfter this policy terminates, the agent must not request further expert feedback for execution, computation, implementation, checking, or validation.'

OPERATOR_DRIVEN_CONSULTATION = """# Human Expert Interaction

## Interaction Strategy

Given the problem statement and the attachments, you may ask any question you want to ask.

## Prohibited Requests

The agent must not request feedback for:

- coding, debugging, or implementation issues;
- standard mathematical derivations;
- computation or data processing.

# Interaction Limits

The consultation runs three exchanges; an exchange is one question and one reply.

After this policy terminates, the agent must not request further expert feedback for execution, computation, implementation, checking, or validation."""
