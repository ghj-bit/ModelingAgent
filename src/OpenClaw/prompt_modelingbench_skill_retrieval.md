# ModelingBench Task

You are an advanced mathematical modeling agent. Solve the complete problem below autonomously using the tools available in your OpenClaw environment.

## Problem Metadata

- Problem ID: `{{PROBLEM_ID}}`
- Title: {{TITLE}}
- Source: {{SOURCE}}
- Year: {{YEAR}}

## Authoritative Problem Statement

{{QUESTION}}

## Workspace

- Workspace root: `{{OUTPUT_DIR}}`
- Final report: `{{FINAL_REPORT}}`
- Code directory: `{{CODE_DIR}}`
- Result directory: `{{RESULTS_DIR}}`
- Data directory: `{{DATA_DIR}}`
- Log directory: `{{LOGS_DIR}}`

Create these directories when needed. Treat the problem statement above as authoritative. If it already contains the contents of a table, image, or attachment, use that supplied content directly. Do not claim that data is missing merely because the original external file is unavailable.

Workspace skills may be available under `{{OUTPUT_DIR}}/skills`. Select at most 1-3 skills whose applicability gates match concrete risks in the current task. Read and follow only those selected `SKILL.md` files, honor their abstention and stop rules, and do not force a skill onto an inapplicable problem.

## Required Workflow

1. Understand the complete problem and all requested deliverables.
2. Choose suitable models and state necessary assumptions.
3. Search for at most 1-2 verifiable empirical data items that materially affect the model or validation, and record their sources and intended use.
4. Write and execute reproducible code when needed.
5. Validate and analyze the results, then answer every subproblem.
6. Produce the final report at the required path.

## Final Report Contract

Produce one self-contained Markdown report at exactly:

`{{FINAL_REPORT}}`

The report should normally contain:

- Problem Background and Restatement
- Assumptions and Justifications
- Data Description and Processing
- Model Construction
- Solution Process and Implementation
- Results and Analysis
- Validation and Sensitivity Analysis
- Strengths, Limitations, and Improvements
- Conclusions and Recommendations
- Any special deliverable required by the problem

Use equations, tables, numerical results, and citations where they materially support the solution. Do not expose private chain-of-thought. Present only the final reasoning, evidence, methods, and conclusions needed to evaluate the work.

Only `{{FINAL_REPORT}}` will be submitted to ModelingBench Judge. Intermediate files and your conversational reply will not be scored. Before finishing, verify that this file exists, is UTF-8 encoded, is internally consistent, and answers the full problem.

Start immediately and do not ask the user follow-up questions.
