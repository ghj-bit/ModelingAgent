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
- Solution file: `{{RESULTS_DIR}}/solution.json`

Create these directories when needed. Use the problem statement above as the task definition. If it already contains the contents of a table, image, or attachment, use that supplied content directly. Do not claim that data is missing merely because the original external file is unavailable.

## Required Workflow

1. Understand the complete problem and all requested deliverables.
2. State the necessary modeling assumptions.
3. Choose and formulate suitable models.
4. Search only for external evidence necessary to support or validate high-impact factual assumptions, empirical parameters, or real-world mechanisms. Do not impose a fixed limit on the number of variables or sources, and do not perform searches that cannot affect the model, validation, or conclusion. Record each source and its intended use.
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

## MM-Bench Solution File

When the task is an MM-Bench problem, the Markdown report is not the complete
submission. Also write the machine-readable solution container that MM-Bench
Judge reads:

`{{RESULTS_DIR}}/solution.json`

It must be valid UTF-8 JSON with exactly this shape:

```json
{
  "tasks": [
    {
      "task_description": "...",
      "task_analysis": "...",
      "preliminary_formulas": "...",
      "mathematical_modeling_process": "...",
      "task_code": "...",
      "is_pass": true,
      "execution_result": "...",
      "solution_interpretation": "...",
      "subtask_outcome_analysis": "..."
    }
  ]
}
```

### Subtask Granularity

Write one element in `tasks` for each subproblem the problem statement asks
about, in the original order. Do not merge several subproblems into one element,
and do not split one subproblem across elements. A special deliverable the
problem requires (memo, position paper, schedule, recommendation) belongs to the
subtask that asks for it, not to an element of its own.

### Field Content

| Field | Content |
| --- | --- |
| `task_description` | What this subtask must deliver and how it fits the overall problem decomposition. |
| `task_analysis` | Modeling analysis of this subtask: objective, assumptions and their justification, chosen method, alternatives considered, technical risks. |
| `preliminary_formulas` | Notation, variables and parameters with units, and the core mathematical relations, written in LaTeX. |
| `mathematical_modeling_process` | The complete modeling and solution process for this subtask: model construction, parameter estimation, algorithm and implementation steps. |
| `task_code` | The code actually executed for this subtask, or an empty string when the subtask needs no computation. |
| `is_pass` | `true` only when that computation ran successfully and its outputs passed basic checks; otherwise `false`. |
| `execution_result` | The key numerical outputs produced by the executed computation. |
| `solution_interpretation` | How the results are read and the direct answer to this subtask. |
| `subtask_outcome_analysis` | Conclusions, interpretation limits, and the data, model, and computational bias analysis for this subtask. |

Every field is a plain string, and LaTeX is allowed inside strings. Escape
newlines, quotes, and backslashes so the file parses as strict JSON. Do not wrap
the file in a Markdown code fence, and do not embed images, charts, base64
payloads, or data URLs. The solution file must state the same models, numbers,
and conclusions as the report.

Start immediately and do not ask the user follow-up questions.
