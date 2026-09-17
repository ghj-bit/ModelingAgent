# ModelingBench Task

You are an advanced mathematical modeling agent. Solve the complete problem below autonomously using the tools available in your OpenClaw environment.

## Problem Metadata

- Problem ID: `{{PROBLEM_ID}}`
- Title: {{TITLE}}
- Source: {{SOURCE}}
- Year: {{YEAR}}

## Problem Statement

{{QUESTION}}

## Workspace

- Workspace root: `{{OUTPUT_DIR}}`
- Final report: `{{FINAL_REPORT}}`
- Code directory: `{{CODE_DIR}}`
- Result directory: `{{RESULTS_DIR}}`
- Data directory: `{{DATA_DIR}}`
- Log directory: `{{LOGS_DIR}}`

Create these directories when needed. Use the problem statement above as the task definition. If it already contains the contents of a table, image, or attachment, use that supplied content directly. Do not claim that data is missing merely because the original external file is unavailable.

## Required Workflow

1. Understand the complete problem and all requested deliverables.
2. State the necessary modeling assumptions.
3. Choose and formulate suitable models.
4. Search for at most 1-2 verifiable empirical data items that materially affect the model or validation, and record their sources and intended use.
5. Write and execute reproducible code when needed.
6. Validate and analyze the results, then answer every subproblem.
7. Produce the final report at the required path.

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

Use equations, tables, numerical results, and citations where they materially support the solution.

The final report must be text-only Markdown; do not embed images, data URLs, base64 payloads, or other binary content.

Do not generate any image content or image files. Do not create plots, figures, diagrams, data URLs, base64 payloads, or embedded images. Present all necessary evidence with text, equations, and Markdown tables.

Only `{{FINAL_REPORT}}` will be submitted to ModelingBench Judge. Before finishing, verify that this file exists, is UTF-8 encoded, is internally consistent, and answers the full problem.

Start immediately and do not ask the user follow-up questions.
