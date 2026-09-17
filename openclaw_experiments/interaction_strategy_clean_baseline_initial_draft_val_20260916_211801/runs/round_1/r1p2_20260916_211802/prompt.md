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

Problem ID: `2003_Gamma_Knife_Treatment`
Title: Gamma Knife Treatment Planning
Source: MCM 2003

Stereotactic radiosurgery delivers a single high dose of ionizing radiation to a radiographically well-defined, small intracranial 3D brain tumor without delivering any significant fraction of the prescribed dose to the surrounding brain tissue. Three modalities are commonly used in this area; they are the gamma knife unit, heavy charged particle beams, and external high-energy photon beams from linear accelerators. The gamma knife unit delivers a single high dose of ionizing radiation emanating from 201 cobalt-60 unit sources through a heavy helmet. All 201 beams simultaneously intersect at the isocenter, resulting in a spherical (approximately) dose distribution at the effective dose levels. Irradiating the isocenter to deliver dose is termed a “shot.” Shots can be represented as different spheres. Four interchangeable outer collimator helmets with beam channel diameters of 4, 8, 14, and 18 mm are available for irradiating different size volumes. For a target volume larger than one shot, multiple shots can be used to cover the entire target. In practice, most target volumes are treated with 1 to 15 shots. The target volume is a bounded, three-dimensional digital image that usually consists of millions of points. The goal of radiosurgery is to deplete tumor cells while preserving normal structures. Since there are physical limitations and biological uncertainties involved in this therapy process, a treatment plan needs to account for all those limitations and uncertainties. In general, an optimal treatment plan is designed to meet the following requirements.

Minimize the dose gradient across the target volume. Match specified isodose contours to the target volumes. Match specified dose-volume constraints of the target and critical organ. Minimize the integral dose to the entire volume of normal tissues or organs. Constrain dose to specified normal tissue points below tolerance doses. Minimize the maximum dose to critical volumes.

Prohibit shots from protruding outside the target. Prohibit shots from overlapping (to avoid hot spots). Cover the target volume with effective dosage as much as possible. But at least 90% of the target volume must be covered by shots. Use as few shots as possible.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_val_20260916_211801\runs\round_1\r1p2_20260916_211802\output\results\draft.md`

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
