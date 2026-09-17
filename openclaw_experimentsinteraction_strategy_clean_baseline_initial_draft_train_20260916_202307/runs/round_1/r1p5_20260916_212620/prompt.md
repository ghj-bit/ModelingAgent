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

Problem ID: `2002_School_Busing`
Title: School Busing
Source: HiMCM 2002

Consider a school where most of the students are from rural areas, so they must be bused. The buses might pick up all the students and go to the elementary school and then continue from that school to pick up more students for the high school. A clear alternative would be to have separate buses for each school, even though they would need to trace over the same routes. There are, of course, restrictions on time (no student should be in the bus more than an hour), drivers, equipment, money, and so forth. How can you set up school bus routes to optimize budget dollars while balancing the time on the bus for various school groups? Build a mathematical model that could be used by various rural and perhaps urban school districts. How would you test the model prior to implementation? Prepare a short article to the school board explaining your model, its assumptions, and its results.

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

`D:\vscode_project\ModelingAgent\openclaw_experimentsinteraction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p5_20260916_212620\output\results\draft.md`

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
