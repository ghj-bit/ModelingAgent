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

## Required Workflow

1. Understand the complete problem and all requested deliverables.
2. Choose suitable models and state necessary assumptions.
3. Search for at most 1-2 verifiable empirical data items that materially affect the model or validation, and record their sources and intended use.
4. Write and execute reproducible code when needed.
5. Validate and analyze the results, then answer every subproblem.
6. Produce the final report at the required path.

## Workflow Summary Contract

Execute the six Required Workflow steps in order. At the end of each step, write
one concise UTF-8 Markdown summary containing that step's decisions, evidence,
outputs, unresolved limitations, and downstream handoff:

1. `{{RESULTS_DIR}}/step_01_problem_understanding.md`
2. `{{RESULTS_DIR}}/step_02_modeling_assumptions.md`
3. `{{DATA_DIR}}/external_data.md`
4. `{{RESULTS_DIR}}/step_04_implementation.md`
5. `{{RESULTS_DIR}}/step_05_validation_analysis.md`
6. `{{FINAL_REPORT}}`

Before starting a later step, read the preceding summaries and the supporting
artifacts they identify. Supporting data, code, and numerical result files may
be created when required, but do not create generic `step_NN.json` receipts or
extra per-step bookkeeping files. Produce the final report only in step 6 after
the first five summaries are complete.

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

The final report must be text-only Markdown; do not embed images, data URLs, base64 payloads, or other binary content.

Only `{{FINAL_REPORT}}` will be submitted to ModelingBench Judge. Intermediate files and your conversational reply will not be scored. Before finishing, verify that this file exists, is UTF-8 encoded, is internally consistent, and answers the full problem.

Start immediately and do not ask the user follow-up questions.
