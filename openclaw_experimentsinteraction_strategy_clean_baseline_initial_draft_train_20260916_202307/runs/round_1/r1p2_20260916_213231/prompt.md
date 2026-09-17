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

Problem ID: `2001_Forest_Service`
Title: Forest Service
Source: HiMCM 2001

Your team has been approached by the Forest Service to help allocate resources to fight wildfires. In particular, the Forest Service is concerned about wildfires in a wilderness area consisting of small trees and brush in a park shaped like a square with dimensions 80 km on a side. Several years ago, the Forest Service constructed a network of north-south and east-west firebreaks that form a rectangular grid across the interior of the entire wilderness area. The firebreaks were built at 5 km intervals. Wildfires are most likely to occur during the dry season, which extends from July through September in this particular region. During this season, there is a prevailing westerly wind throughout the day. There are frequent lightning bursts that cause wildfires. The Forest Service wants to deploy four fire-fighting units to control fires during the next dry season. Each unit consists of 10 firefighters, one pickup truck, one dump truck, one water truck (50,000 liters), and one bulldozer (w/ truck and trailer). The unit has chainsaws, hand tools, and other fire-fighting equipment. The people can be quickly moved by helicopter within the wilderness area, but all the equipment must be driven via the existing firebreaks. One helicopter is on standby at all times throughout the dry season. Your task is to determine the best distribution of fire-fighting units within the wilderness area. The Forest Service is able to set up base camps for those units at sites anywhere within the area. In addition, you are asked to prepare a damage assessment forecast. This forecast will be used to estimate the amount of wilderness likely to be burned by fire as well as acting as a mechanism for helping the Service determine when additional fire-fighting units need to be brought in from elsewhere.

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

`D:\vscode_project\ModelingAgent\openclaw_experimentsinteraction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p2_20260916_213231\output\results\draft.md`

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
