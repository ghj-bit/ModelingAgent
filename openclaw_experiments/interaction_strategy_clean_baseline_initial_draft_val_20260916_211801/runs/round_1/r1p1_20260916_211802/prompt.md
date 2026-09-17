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

Problem ID: `2002_Airline_Overbooking`
Title: Airline Overbooking
Source: MCM 2002

You're all packed and ready to go on a trip to visit your best friend in New York City. After you check in at the ticket counter, the airline clerk announces that your flight has been overbooked. Passengers need to check in immediately to determine if they still have a seat.

Historically, airlines know that only a certain percentage of passengers who have made reservations on a particular flight will actually take that flight. Consequently, most airlines overbook—that is, they take more reservations than the capacity of the aircraft. Occasionally, more passengers will want to take a flight than the capacity of the plane, leading to one or more passengers being bumped and thus unable to take the flight for which they had reservations.

Airlines deal with bumped passengers in various ways. Some are given nothing, some are booked on later flights on other airlines, and some are given some kind of cash or airline ticket incentive.

Consider the overbooking issue in light of the current situation: Less flights by airlines from point A to point B, heightened security at and around airports, passengers' fear, and loss of billions of dollars in revenue by airlines to date.

Build a mathematical model that examines the effects that different overbooking schemes have on the revenue received by an airline company in order to find an optimal overbooking strategy, i.e., the number of people by which an airline should overbook a particular flight so that the company's revenue is maximized. Ensure that your model reflects the issues above, and consider alternatives for handling "bumped" passengers. Additionally, write a short memorandum to the airline's CEO summarizing your findings and analysis.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_val_20260916_211801\runs\round_1\r1p1_20260916_211802\output\results\draft.md`

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
