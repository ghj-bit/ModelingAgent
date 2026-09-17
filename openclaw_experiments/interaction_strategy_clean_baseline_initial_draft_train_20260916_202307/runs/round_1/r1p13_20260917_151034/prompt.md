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

Problem ID: `2007_The_Airplane_Seating`
Title: The Airplane Seating Problem
Source: MCM 2007

Airlines are free to seat passengers waiting to board an aircraft in any order whatsoever. It has become customary to seat passengers with special needs first, followed by first-class passengers (who sit at the front of the plane). Then coach and business-class passengers are seated by groups of rows, beginning with the row at the back of the plane and proceeding forward. Apart from consideration of the passengers' wait time, from the airline's point of view, time is money, and boarding time is best minimized. The plane makes money for the airline only when it is in motion, and long boarding times limit the number of trips that a plane can make in a day. The development of larger planes, such as the Airbus A380 (800 passengers), accentuate the problem of minimizing boarding (and deboarding) time. Devise and compare procedures for boarding and deboarding planes with varying numbers of passengers: small (85-210), midsize (210-330), and large (450-800). Prepare an executive summary, not to exceed two single-spaced pages, in which you set out your conclusions to an audience of airline executives, gate agents, and flight crews. Note: The 2 page executive summary is to be included IN ADDITION to the reports required by the contest guidelines. An article appeared in the NY Times Nov 14, 2006 addressing procedures currently being followed and the importance to the airline of finding better solutions.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p13_20260917_151034\output\results\draft.md`

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
