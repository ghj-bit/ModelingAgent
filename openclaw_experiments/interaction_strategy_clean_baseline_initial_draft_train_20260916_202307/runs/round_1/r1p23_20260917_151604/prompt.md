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

Problem ID: `2017_Jet_Lag`
Title: Jet Lag
Source: IM2C 2017

Organizing international meetings is not easy in many ways, including the problem that some of the participants may experience the effects of jet lag after recent travel from their home country to the meeting location which may be in a different time-zone, or in a different climate and time of year, and so on. All these things may dramatically affect the productivity of the meeting.

The International Meeting Management Corporation (IMMC) has asked your expert group (your team) to help solve the problem by creating an algorithm that suggests the best place(s) to hold a meeting given the number of participants, their home cities, approximate dates of the meeting and other information that the meeting management company may request from its clients.

The participants are usually from all corners of the Earth, and the business or scientific meeting implies doing hard intellectual team work for three intensive days, with the participants contributing approximately equally to the end result. Assume that there are no visa problems or political limitations, and so any country or city can be a potential meeting location.

The output of the algorithm should be a list of recommended places (regions, zones, or specific cities) that maximize the overall productivity of the meeting. The questions of costs are not of primary importance, but the IMMC, just as any other company, has a limited budget. So the costs may be considered as a secondary criterion. And the IMMC definitely cannot afford bringing the participants in a week before the meeting to acclimatize or give them the time to rest after a long exhausting journey.

Test your algorithm at least on the two following datasets:

Scenario 1) “Small Meeting”:

Time: mid-June Participants: 6 individuals from: Monterey CA, USA Zutphen, Netherlands Melbourne, Australia Shanghai, China Hong Kong (SAR), China Moscow, Russia

Scenario 2) “Big meeting”:

Time: January Participants: 11 individuals from: Boston MA, USA (2 people) Singapore Beijing, China Hong Kong (SAR), China (2 people) Moscow, Russia Utrecht, Netherlands Warsaw, Poland Copenhagen, Denmark Melbourne, Australia

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p23_20260917_151604\output\results\draft.md`

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
