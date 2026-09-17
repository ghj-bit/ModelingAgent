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

Problem ID: `2014_The_Next_Plague?`
Title: The Next Plague?
Source: HiMCM 2014

In 2014, the world saw the infectious Ebola virus spreading in western Africa. Throughout human history, epidemics have come and gone with some infecting and/or killing thousands and lasting for years and others taking less of a human toll. Some believe these events are just nature’s way of controlling the growth of a species while others think they could be a conspiracy or deliberate act to cause harm. This problem will most likely come down to how to expend (or not expend) scarce resources (doctors, containment facilities, money, research, serums, etc...) to deal with a crisis.

Situation: A routine humanitarian mission on an island in Indonesia reported a small village where almost half of its 300 inhabitants are showing similar symptoms. In the past week, 15 of the "infected" have died. This village is known to trade with nearby villages and other islands. Your modeling team works for a major center of disease control in the capital of your country (or if you prefer, for the International World Health Organization).

Requirement 1: Develop a mathematical model(s) that performs the following functions as well as how/when to best allocate these scarce resources and... Determines and classifies the type and severity of the spread of the disease Determines if an epidemic is contained or not Triggers appropriate measures (when to treat, when to transport victims, when to restrict movement, when to let a disease run its course, etc...) to contain a disease Note: While you may want to start with the well-known "SIR" family of models for parts of this problem, consider others, modifications to the SIR, multiple models, or creating your own.

Requirement 2: Based on the information given, your model, and the assumptions your team has made, what initial recommendations does your team have for your country’s center for disease control? (Give 3-5 recommendations with justifications) Additional Situational Information: A multi-national research team just returned to your country’s capital after spending 7 days gathering information in the infected village. Requirement 3: You can ask them up to 3 questions to improve your model. What would you ask and why? Additional Situational Information: The multi-national research team concluded that the disease: Appears to spread through contact with bodily fluids of an infected person The elderly and children are more likely to die if infected A nearby island is starting to show similar signs of infection One of the researchers that returned to your capital appears infected Requirement 4: How does the additional information above change/modify your model? Requirement 5: Write a one-page synopsis of your findings for your local non-technical news outlet.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_val_20260916_211801\runs\round_1\r1p6_20260917_150759\output\results\draft.md`

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
