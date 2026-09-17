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

Problem ID: `2023_Dandelions:_Friend?_Foe?`
Title: Dandelions: Friend? Foe? Both? Neither?
Source: HiMCM 2023

<link>2023_HiMCM_Problem_A.pdf</link> <link>2023_HiMCM_Problem_A.pdf</link> Dandelions: Friend? Foe? Both? Neither?

### Text in the PDF File: 2023_HiMCM_Problem_A.pdf

**2023 HiMCM Problem A: Dandelions: Friend? Foe? Both? Neither?**

**Overview:**
- **Dandelion (Taraxacum officinale):** A plant native to Eurasia, now found worldwide. Recognizable by its yellow flowers and puffball seed head, which aids in wind dispersal.

**Tasks:**

1. **Spread Prediction Model:**
   - Develop a mathematical model to predict dandelion spread over 1, 2, 3, 6, and 12 months.
   - Consider climatic conditions: temperate, arid, and tropical climates.

2. **Impact Factor Model for Invasive Species:**
   - Create a model to determine an 'impact factor' for invasive species, considering plant characteristics and environmental harm.
   - Test the model with dandelions.
   - Apply the model to two other invasive plant species, specifying the region where they are invasive.

**Submission Requirements:**
- max 25 pages, including:
  - One-page Summary Sheet
  - Complete solution

**Glossary:**
- **Invasive Species:** Non-native species causing or likely to cause harm to the economy, environment, or human health.

**References:**
1. [Dandelion Information](https://anpc.ab.ca/wp-content/uploads/2015/01/dandelion.pdf)
2. [Dandelion Article](https://hort.extension.wisc.edu/articles/dandelion-taraxacum-officinale/)
3. [Invasive Species Information](https://www.invasivespeciesinfo.gov/what-are-invasive-species)

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p33_20260917_152137\output\results\draft.md`

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
