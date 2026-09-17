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

Problem ID: `2007_Organ_Transplant:_The`
Title: Organ Transplant: The Kidney Exchange Problem
Source: ICM 2007

<link>2007-ICM.pdf</link> <link>2007-ICM.pdf</link> Organ Transplant: The Kidney Exchange Problem

### Text in the PDF File: 2007-ICM.pdf

# 2007 ICM Problem C: Organ Transplant - The Kidney Exchange Problem

## Overview
The demand for organ transplants, particularly kidneys, far exceeds the supply. The US Organ Procurement and Transplantation Network (OPTN) was established to address this issue, but challenges remain, including long waiting lists and inefficiencies in organ matching.

## Tasks

### Task 1: US Transplant Network Model
- **Objective**: Develop a mathematical model for the US transplant network to identify bottlenecks and improve efficiency.
- **Considerations**: 
  - Potential bottlenecks in organ matching.
  - Allocation of additional resources.
  - Impact of dividing the network into smaller units (e.g., state-level).
  - Policy changes to enhance system effectiveness.

### Task 2: International Policy Comparison
- **Objective**: Compare US policies with those of another country and assess potential improvements.
- **Deliverable**: A one-page report to Congress with findings and recommendations based on the model from Task 1.

### Task 3: Maximizing Kidney Exchanges
- **Objective**: Create a procedure to maximize the number and quality of kidney exchanges.
- **Considerations**: 
  - Medical and psychological factors.
  - Estimation of increased annual transplants and impact on waiting lists.

### Task 4: Patient Decision Strategy
- **Objective**: Develop a strategy for patients to decide on accepting a kidney offer or participating in an exchange.
- **Considerations**: 
  - Risks, alternatives, and probabilities.
  - Differences between cadaver and live donor kidneys.

### Task 5: Policy Recommendations
- **Objective**: Recommend changes to current criteria and policies.
- **Considerations**: 
  - Ethical dimensions of exchange procedures and patient strategies.
  - Criteria for priority and placement.
  - Discussion on organ sales.

### Task 6: Donor Perspective
- **Objective**: Analyze risks and factors influencing donor decisions.
- **Considerations**: 
  - Success probability for recipients.
  - Donor survival and health risks.
  - Influence of personal issues and network size on donor decisions.
  - Strategies to recruit more altruistic donors.

## Key Data
- **Waiting List**: Nearly 94,000 candidates, expected to exceed 100,000.
- **Kidney Transplants**: 68,000 patients waiting; 10,000 from cadavers and 6,000 from living donors annually.
- **Age Distribution of Waiting Patients**:
  - Under 18: 748
  - 18 to 34: 8,033
  - 35 to 49: 20,553
  - 50 to 64: 28,530
  - 65 and over: 10,628

## Ethical and Political Considerations
- **Ethical Issues**: Fairness in waiting list criteria, age priority, and organ allocation.
- **Political Issues**: Regionalization effects, proficiency of local doctors, and potential centralization of transplants.
- **Policy Debates**: Presumed consent, financial compensation for donors, and national policy changes.

## Conclusion
The problem requires a comprehensive approach involving mathematical modeling, policy analysis, and ethical considerations to improve the kidney exchange system and address the organ shortage crisis.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p12_20260917_151034\output\results\draft.md`

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
