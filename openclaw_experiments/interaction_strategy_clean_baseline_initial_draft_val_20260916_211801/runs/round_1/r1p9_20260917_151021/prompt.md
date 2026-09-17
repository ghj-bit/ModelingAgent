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

Problem ID: `2023_Preparing_for_Olympic`
Title: Preparing for Olympic Medal Ceremonies
Source: MidMCM 2023

<link>2023_MidMCM_Problem_C.pdf</link> Preparing for Olympic Medal Ceremonies

### Text in the PDF File: 2023_MidMCM_Problem_C.pdf

**2023 MidMCM Problem C: Preparing for Olympic Medal Ceremonies**

**Overview:**
The International Olympic Committee (IOC) is preparing for the Paris 2024 Olympic Games, scheduled from July 26 to August 11, 2024. They need to order an appropriate number of medals and flags for the medal ceremonies to avoid shortages or excesses. Your task is to develop models to determine the necessary quantities.

**Key Information:**
- **Participating Countries:** Invitations have been sent to 203 National Olympic Committees (NOCs).
- **Olympic Sports:** The 2024 Summer Olympics will feature 40 sports with 329 medal events.
- **Medal Ceremonies:** Each event awards Gold, Silver, and Bronze medals. Flags of the winning countries are displayed.
- **Venues:** The events will be held across 37 venues, primarily in and around Paris, with some overseas locations like Tahiti.

**Task Requirements:**
1. **Venue Selection and Analysis:**
   - Choose one venue: La Défense Arena, Bercy Arena, or Stade de France.
   - Develop a schedule for medal ceremonies at the chosen venue.
   - Create a model to determine the number of medals (Gold, Silver, Bronze) needed.
   - Create a model to determine the number and types of flags needed.

2. **Model Application:**
   - Apply your models to the other two venues.
   - Develop comprehensive models for medals and flags needed across all three venues.

3. **Communication:**
   - Write a one- to two-page letter to the IOC explaining your model and its effectiveness in ensuring adequate medal and flag supplies.

4. **Reflection:**
   - Consider the applicability of your model to all 37 venues and future Olympic Games, including Winter Olympics.

**Submission Guidelines:**
- Include a one-page summary, complete solution, and letter to the IOC
- The solution document should not exceed 25 pages.

**References:**
- [1] Olympic Games Paris 2024 Information: https://olympics.com/ioc/news/one-year-to-go-ioc-invites-nocs-and-their-best-athletes-to-the-olympic-games-paris-2024
- [2] Olympic Sports Overview: https://olympics.com/en/sports/summer-olympics#paris-2024
- [3] Paris 2024 Schedule: https://olympics.com/en/news/olympic-games-paris-2024-full-schedule-and-day-by-day-competitions
- [4] Paris Olympics Venues: https://www.parisdigest.com/sports/paris-olympics-2024.htm
- [5] Venue Concept: https://www.paris2024.org/en/competition-venue-concept/

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_val_20260916_211801\runs\round_1\r1p9_20260917_151021\output\results\draft.md`

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
