<!--
Generated from `src/OpenClaw/interaction_policy.py::MODELING_STRATEGY_ESCALATION`.

That module is the source of truth: the initial-draft evolution launcher and the
workflow-test runner both import it, so their copies cannot drift.  Do not edit
this file by hand — change the module and re-run:

    python scripts/export_initial_interaction_policy.py
-->

*Frozen initial interaction policy — 4,072 characters.*

# Human Expert Interaction

## Interaction Policy 1: Modeling Strategy Escalation

The agent should solve the modeling task autonomously by default. This policy may be triggered only when an unresolved strategic uncertainty could significantly change the modeling framework, core assumptions, or final conclusions.

### Trigger Conditions

Request expert feedback only when **all** of the following conditions are met:

1. Multiple substantially different yet reasonable modeling directions remain;
2. The choice may significantly affect the modeling framework, core assumptions, or final conclusions;
3. The agent cannot resolve the uncertainty independently using the problem statement, `draft.md`, domain knowledge, or its existing analysis;
4. Expert feedback can be directly converted into a clear and actionable modeling decision.

Do not request expert feedback for:

- code implementation, debugging, or tool usage;
- mathematical derivations, data processing, or computation;
- parameter selection, model training, or tuning;
- model validation, result checking, or error analysis;
- routine method selection or minor assumption adjustments;
- additional confirmation intended merely to improve answer quality;
- issues that can be resolved through reasonable default assumptions.

If several uncertainties qualify, address them one at a time in descending order of potential impact on the modeling direction, and only while the interaction budget allows.

### Interaction Workflow

The steps below are the interaction workflow. They are the only part of this
policy open to revision, and each step must stay short enough to be followed
exactly.

#### Consultation Content

Before requesting expert feedback, provide only:

1. **Problem Understanding**

   - A brief interpretation of the task objective;
   - The current modeling stage.

2. **Strategic Decision Point**

   - The core uncertainty that cannot be resolved autonomously;
   - Its potential impact on the modeling direction.

3. **Candidate Options**

   - No more than three candidate directions;
   - The main advantages, limitations, and expected impact of each.

#### Feedback Handling

After receiving feedback, the agent must:

- translate the feedback into one explicit modeling decision;
- revise only the modeling strategy directly affected by that decision;
- treat that decision as settled and carry forward the work it governs autonomously;
- not reopen a settled decision, and not seek confirmation, review, or validation of one.

### Interaction Limit

Maximum expert interactions: **3**.

One interaction consists of one question from the agent and one response from the expert. A further interaction is permitted only when it addresses a decision point distinct from every earlier one: a different modeling stage, a different unresolved uncertainty, and a different consequence for the modeling direction. Re-asking about a settled decision, or asking the expert to elaborate on, confirm, or approve an earlier reply, is not a distinct decision point and must not consume the budget. If a reply is incomplete, resolve it autonomously with reasonable default assumptions rather than spending a further interaction on it.

### Stop Conditions

Terminate this policy when any of the following conditions is met:

- no strategic uncertainty materially affecting the modeling direction exists;
- the agent can make the decision independently using available information or reasonable assumptions;
- every qualifying uncertainty has been converted into an explicit modeling choice;
- the maximum of three expert interactions has been reached.

### Computational Efficiency

Keep every run bounded. Express grid and sample sweeps as vectorised array
operations rather than per-element loops, and size the grids and sample counts
so each script finishes in minutes; a coarse sweep that completes is worth more
than a fine one that does not.

After this policy terminates, the agent must not request further expert feedback for execution, computation, implementation, checking, or validation.
