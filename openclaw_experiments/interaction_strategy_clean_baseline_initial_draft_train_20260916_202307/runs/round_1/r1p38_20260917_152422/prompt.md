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

Problem ID: `2024_Searching_for_Submersibles`
Title: Searching for Submersibles
Source: MCM 2024

<link>2024_MCM_Problem_B.pdf</link> Searching for Submersibles

### Text in the PDF File: 2024_MCM_Problem_B.pdf

**2024 MCM Problem B: Searching for Submersibles**

**Overview:**
Maritime Cruises Mini-Submarines (MCMS), based in Greece, builds submersibles for deep-sea exploration. They plan to offer tourist adventures in the Ionian Sea to explore shipwrecks. To gain regulatory approval, they need to develop safety procedures for scenarios like loss of communication or mechanical failures, including propulsion loss.

**Tasks:**

1. **Locate:**
   - Develop a model to predict the submersible's location over time.
   - Identify uncertainties in predictions.
   - Determine what information the submersible can send to the host ship to reduce uncertainties and the equipment needed.

2. **Prepare:**
   - Recommend additional search equipment for the host ship, considering costs, maintenance, and readiness.
   - Suggest equipment a rescue vessel might need.

3. **Search:**
   - Create a model to recommend initial deployment points and search patterns to minimize the time to locate a lost submersible.
   - Calculate the probability of finding the submersible over time and with accumulated search results.

4. **Extrapolate:**
   - Expand the model for other tourist destinations like the Caribbean Sea.
   - Adapt the model for multiple submersibles in the same area.

**Report Requirements:**
- Maximum of 25 pages.
- Include a one-page summary, complete solution, and one- to two-page memo to the Greek government.

**Glossary:**
- **Submersible:** An underwater vehicle supported by a larger watercraft, unlike self-supporting submarines.
- **Neutral Buoyancy:** When an object's density equals the fluid's density, causing it to neither sink nor rise.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p38_20260917_152422\output\results\draft.md`

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
