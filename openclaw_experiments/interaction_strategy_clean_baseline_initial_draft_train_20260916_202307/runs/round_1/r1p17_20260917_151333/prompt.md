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

Problem ID: `2011_Space_Shuttle_Problem:`
Title: Space Shuttle Problem: No More Space Shuttles
Source: HiMCM 2011

On July 21, 2011, the 135th and final US Space Shuttle landed in Florida after its 13-day mission into orbit, complete with a docking at the International Space Station (ISS). NASA will now have to rely on other nations or commercial endeavors to travel into space until a replacement vehicle is developed and constructed. Develop a comprehensive ten-year plan complete with costs, payloads, and flight schedules to maintain the ISS.

Some interesting facts possibly worthy of your consideration:

The ISS is at full capacity with 6 astronauts, but can surge during shuttle docks to as high as 13. The ISS is scheduled to remain in service until at least the year 2020. Historically, transport to the ISS using US Shuttles has cost between $5000-10,000 per pound. Shuttle missions have lasted approximately 10-14 days in orbit. Missions on board the ISS typically last around six months. Recently, progress has been made within private industry to launch unmanned rockets into space. Russia is willing to launch US astronauts into space at a cost of about $60 million each.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p17_20260917_151333\output\results\draft.md`

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
