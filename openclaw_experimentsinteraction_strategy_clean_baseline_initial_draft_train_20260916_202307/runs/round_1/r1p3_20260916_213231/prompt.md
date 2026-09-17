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

Problem ID: `2001_Skyscrapers`
Title: Skyscrapers
Source: HiMCM 2001

Skyscrapers vary in height, size (square footage), occupancy rates, and usage. They adorn the skyline of our major cities. But as we have seen several times in history, the height of the building might preclude escape during a catastrophe either human or natural (earthquake, tornado, hurricane, etc). Let's consider the following scenario. A building (a skyscraper) needs to be evacuated. Power has been lost so the elevator banks are inoperative except for use by firefighters and rescue personnel with special keys. Build a mathematical model to clear the building within X minutes. Use this mathematical model to state the height of the building, maximum occupation, and type of evacuation methods used. Solve your model for X = 15 minutes, 30 minutes, and 60 minutes.

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

`D:\vscode_project\ModelingAgent\openclaw_experimentsinteraction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p3_20260916_213231\output\results\draft.md`

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
