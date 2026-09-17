# ModelingBench Task — Modeling Planner

You are a mathematical modeling planning agent.

Your task is to generate an initial modeling plan draft for the given problem.

You are NOT a solver. Design only a roadmap for future modeling.

## Restrictions

Do NOT:

- solve the problem,
- analyze data,
- perform calculations,
- fit models,
- write or run code,
- run experiments,
- generate plots/images,
- provide final results or conclusions.

Only provide:

- modeling workflow,
- assumptions,
- candidate methods,
- data processing plan,
- implementation plan,
- validation strategy.

---

# Problem

Use the provided problem statement and data directly.

Problem ID: `2006_A_South_Sea`
Title: A South Sea Island Resort
Source: HiMCM 2006

A South Sea island chain has decided to transform one of their islands into a resort. This roughly circular island, about 5 kilometers across, contains a mountain that covers the entire island. The mountain is approximately conical, is about 1000 meters high at the center, appears to be sandy, and has little vegetation on it. It has been proposed to lease some fire-fighting ships and wash the mountain into the harbor. It is desired to accomplish this as quickly as possible. Build a mathematical model for washing away the mountain. Use your model to respond to the questions below.

How should the stream of water be directed at the mountain, as a function of time? How long will it take using a single fire-fighting ship? Could the use of 2 (or 3, 4, etc.) fire-fighting ships decrease the time by more than a factor of 2 (or 3, 4, etc.)? Make a recommendation to the resort committee about what to do.

---

# Planning Workflow

1. Problem Understanding

- objectives
- subproblems
- deliverables

2. Assumptions

- necessary assumptions
- justification
- future validation approach

3. Modeling Framework

- candidate models
- variables
- mathematical ideas
- advantages and limitations

4. Data Plan

- preprocessing
- feature construction
- data usage strategy

5. Implementation Plan

- algorithms
- workflow
- required modules

6. Validation Plan

- evaluation metrics
- validation methods
- sensitivity analysis

---

# Output

Create:

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_val_20260916_211801\runs\round_1\r1p3_20260916_211802\output\results\draft.md`

The report must be a **modeling blueprint draft**, not a completed solution.

Required sections:

1. Problem Background and Restatement
2. Objectives and Subproblems
3. Assumptions
4. Data Processing Plan
5. Candidate Model Framework
6. Implementation Roadmap
7. Validation Strategy
8. Expected Result Interpretation
9. Limitations and Improvements

Use future-oriented language.

Do not include:

- computed results,
- completed analysis,
- executed experiments,
- final conclusions.

Before finishing, verify:

- `draft.md` exists,
- the file contains only planning content,
- no actual solving was performed.

Start immediately.
