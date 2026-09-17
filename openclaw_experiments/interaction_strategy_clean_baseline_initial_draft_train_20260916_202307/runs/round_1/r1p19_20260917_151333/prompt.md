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

Problem ID: `2013_Bank_Service_Problem`
Title: Bank Service Problem
Source: HiMCM 2013

The bank manager is trying to improve customer satisfaction by offering better service. Management wants the average customer to wait less than 2 minutes for service and the average length of the queue (length of the waiting line) to be 2 persons or fewer. The bank estimates it serves about 150 customers per day. The existing arrival and service times are given in the tables below.

Time between arrival (min.) Probability  
0 0.10  
1 0.15  
2 0.10  
3 0.35  
4 0.25  
5 0.05  

Table 1: Arrival times

Service Time (min.) Probability  
1 0.25  
2 0.20  
3 0.40  
4 0.15  

Table 2: Service times

(1) Build a mathematical model of the system.

(2) Determine if the current customer service is satisfactory according to the manager guidelines. If not, determine, through modeling, the minimal changes for servers required to accomplish the manager's goal.

(3) In addition to the contest's format, prepare a short 1-2 page non-technical letter to the bank's management with your final recommendations.

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p19_20260917_151333\output\results\draft.md`

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
