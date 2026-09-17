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

Problem ID: `2022_Power_Profile_of`
Title: Power Profile of a Cyclist
Source: MCM 2022

<link>2022_MCM_Problem_A.pdf</link> <link>2022_MCM_Problem_A.pdf</link> Power Profile of a Cyclist

### Text in the PDF File: 2022_MCM_Problem_A.pdf

**2022 MCM Problem A: Power Profile of a Cyclist**

**Background**
In bicycle road races, such as individual time trials, cyclists aim to complete a course in the shortest time. A rider's power curve shows the maximum power they can sustain over different durations. More power typically means less time before needing recovery. Riders must manage their power to minimize race time, considering fatigue and energy limits.

**Objective**
Develop a model to determine the relationship between a cyclist's position on a course and the power they apply, considering energy limits and past exertion.

**Model Requirements**
1. Define power profiles for two rider types: a time trial specialist and another type (consider gender differences).
2. Apply the model to:
   - 2021 Olympic Time Trial course in Tokyo, Japan
   - A custom-designed course with at least four sharp turns and a nontrivial road grade, ending near its start.
3. Assess the impact of weather conditions, such as wind direction and strength.
4. Evaluate sensitivity to deviations from target power distribution.
5. Extend the model for a team time trial with six riders, focusing on the fourth rider's finish time.

**Deliverables**
- A two-page race guidance for a Directeur Sportif, focusing on one rider and one course, with an overview and model summary.
- A complete solution of no more than 25 pages, including:
  - One-page Summary Sheet
  - Complete solution
  - Two-page rider’s race guidance

**Glossary**
- **Criterium**: A race on a closed course, defined by laps or time.
- **Directeur Sportif**: Team director managing riders and race strategy.
- **Individual Time Trial**: Riders race alone on a set course; fastest time wins.
- **Power Curve**: Graph of maximum power a rider can sustain over time.

**Rider Types**
- **Climber**: Excels in long climbs.
- **Puncheur**: Specializes in short, steep climbs and accelerations.
- **Rouleur**: Versatile across various terrains.
- **Sprinter**: High power for short bursts, focuses on race finishes.
- **Time Trial Specialist**: Excels in individual time trials.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p31_20260917_152137\output\results\draft.md`

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
