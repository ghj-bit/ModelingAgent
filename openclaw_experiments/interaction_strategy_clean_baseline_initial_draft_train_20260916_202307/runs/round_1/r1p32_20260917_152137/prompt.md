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

Problem ID: `2022_Water_and_Hydroelectric`
Title: Water and Hydroelectric Power Sharing
Source: MCM 2022

<link>2022_MCM_Problem_B.pdf</link> <link>2022_MCM_Problem_B.pdf</link> Water and Hydroelectric Power Sharing

### Text in the PDF File: 2022_MCM_Problem_B.pdf

**2022 MCM Problem B: Water and Hydroelectric Power Sharing**

**Background**

Dams have been used for centuries to manage water supplies, create reservoirs, and generate hydroelectric power. However, climate change is reducing water volumes, impacting both water supply and electricity generation. In the U.S., states like Arizona, California, Wyoming, New Mexico, and Colorado are negotiating water and electricity management at the Glen Canyon and Hoover dams. Current agreements allocate more water than is available, and continued drought could lead to shortages.

**Task**

Develop a water allocation plan for the five states, considering:

- Coordination between Glen Canyon (Lake Powell) and Hoover (Lake Mead) dams.
- Allocation of water and electricity to agriculture, industry, and residences.
- Mexico's rights to residual water.
- Potential water flow into the Gulf of California.

**Model Requirements**

1. Create a mathematical model to manage fixed water supply and demand conditions.
2. Determine water draw from Lake Mead and Lake Powell to meet demands.
3. Assess how long demands can be met without additional water supply.
4. Recommend solutions for competing interests between water usage and electricity production.
5. Address scenarios where water is insufficient to meet all demands.

**Considerations**

- Changes in water and electricity demands due to population and industrial growth or decline.
- Increased use of renewable energy technologies.
- Implementation of water and electricity conservation measures.

**Submission Requirements**

- A mathematical solution for water allocation, independent of historical agreements or political influences.
- A one- to two-page article for "Drought and Thirst" magazine.
- A complete solution within 25 pages, including a summary and main solution content.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p32_20260917_152137\output\results\draft.md`

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
