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

Problem ID: `2023_Light_Pollution`
Title: Light Pollution
Source: ICM 2023

<link>2023_ICM_Problem_E.pdf</link> Light Pollution

### Text in the PDF File: 2023_ICM_Problem_E.pdf

**Problem E: Light Pollution**

**Background**
Light pollution refers to the excessive or poor use of artificial light, manifesting as light trespass, over-illumination, and light clutter. It is often visible as a glow in the sky after sunset, especially in large cities, but can also occur in remote areas. Light pollution affects our view of the night sky, has environmental impacts, and influences health and safety. It can disrupt plant growth, wildlife migration, and human circadian rhythms, potentially leading to health issues and contributing to motor vehicle accidents. 

Intervention strategies to mitigate light pollution must consider both positive and negative effects, which vary by location. Factors such as development level, population, biodiversity, geography, and climate influence the impacts of light pollution and the effectiveness of interventions.

**Task**
The task is to support COMAP’s Illumination Control Mission (ICM) by addressing the measurement and mitigation of light pollution effects, considering both human and non-human concerns. Specifically, you should:

- Develop a metric to identify the light pollution risk level of a location.
- Apply and interpret this metric for four types of locations:
  - Protected land
  - Rural community
  - Suburban community
  - Urban community

- Choose two locations and determine the most effective intervention strategy for each using your metric. Discuss the impact of the strategy on the location's risk level.
- Create a 1-page flyer promoting the most effective strategy for one location.

**Submission Requirements**
Your solution should be no more than 25 pages, including:
- One-page Summary Sheet
- Complete solution
- One-page promotion flyer

**Glossary**
- **Artificial Light:** Non-natural light sources.
- **Circadian Rhythms:** The natural 24-hour sleep-wake cycle.
- **Glare:** Excessive brightness reducing visibility.
- **Intervention Strategies:** Actions to mitigate light pollution.
- **Light Clutter:** Excessive grouping of lights.
- **Light Trespass:** Light entering unintended areas.
- **Over-Illumination:** Excessive lighting intensity.
- **Protected Land:** Areas protected for ecological, cultural, or natural importance.
- **Rural Community:** Least densely populated areas, not easily accessible from urban areas.
- **Suburban Community:** Moderately densely populated areas, accessible from urban areas.
- **Urban Community:** Most densely populated areas.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p34_20260917_152137\output\results\draft.md`

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
