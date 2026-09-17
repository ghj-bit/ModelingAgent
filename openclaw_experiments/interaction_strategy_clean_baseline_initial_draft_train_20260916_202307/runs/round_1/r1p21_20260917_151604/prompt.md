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

Problem ID: `2016_Are_we_heading`
Title: Are we heading towards a thirsty planet?
Source: ICM 2016

<link>2016_ICM_Problem_E.pdf</link> <link>2016_ICM_Problem_E.pdf</link> Are we heading towards a thirsty planet?

### Text in the PDF File: 2016_ICM_Problem_E.pdf

**2016 ICM Problem E: Are we heading towards a thirsty planet?**

**Overview:**
The United Nations reports that 1.6 billion people face water scarcity, with water use growing at twice the rate of population increase. Water scarcity arises from physical scarcity (inadequate water supply) and economic scarcity (poor management and infrastructure). Climate change and population growth may worsen this issue. The challenge is to determine if increasing personal or industrial consumption, or pollution, is contributing to scarcity.

**Key Questions:**
- Can clean water be provided to all?
- How do environmental and social factors affect water availability?
- What historical actions have impacted water scarcity?
- What are the geological and ecological reasons for scarcity?
- What potential exists for new water sources?
- What demographic and health issues are linked to water scarcity?

**Problem Statement:**
The International Clean Water Movement (ICM) seeks solutions to global water problems. Your task is to improve access to clean, fresh water.

**Tasks:**

1. **Model Development:**
   - Create a model to measure a region's ability to provide clean water, considering dynamic supply and demand factors.

2. **Region Analysis:**
   - Select a country or region from the UN water scarcity map where water is heavily or moderately overloaded.
   - Explain the causes of water scarcity, addressing both social and environmental factors.

3. **Future Projection:**
   - Use your model to predict the water situation in the chosen region in 15 years.
   - Assess the impact on citizens' lives, incorporating environmental drivers.

4. **Intervention Plan:**
   - Design a plan addressing all drivers of water scarcity.
   - Discuss the plan's impact on the region and surrounding areas, highlighting strengths and weaknesses.

5. **Future Water Availability:**
   - Project future water availability using your intervention plan and model.
   - Determine if the region can become less susceptible to scarcity and predict when scarcity might become critical.

6. **Report Writing:**
   - Write a 20-page report detailing your model, the region's water scarcity without intervention, your intervention plan, and its effects.
   - Include strengths and weaknesses of your model.

**Resources:**
- An Overview of the State of the World’s Fresh and Marine Waters (2008)
- The World’s Water: Information on the World’s Freshwater Resources
- AQUASTAT by the Food and Agriculture Organization of the United Nations
- The State of the World's Land and Water Resources for food and agriculture (2011)
- GrowingBlue: Water. Economics. Life.
- World Resources Institute

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p21_20260917_151604\output\results\draft.md`

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
