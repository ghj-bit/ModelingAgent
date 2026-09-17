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

Problem ID: `2020_Moving_North`
Title: Moving North
Source: MCM 2020

Global ocean temperatures affect the quality of habitats for certain ocean-dwelling species. When temperature changes are too great for their continued thriving, these species move to seek other habitats better suited to their present and future living and reproductive success. One example of this is seen in the lobster population of Maine, USA, that is slowly migrating north to Canada where the lower ocean temperatures provide a more suitable habitat. This geographic population shift can significantly disrupt the livelihood of companies who depend on the stability of ocean-dwelling species.

Your team has been hired as consultants by a Scottish North Atlantic fishery management consortium. The consortium wants to gain a better understanding of issues related to the potential migration of Scottish herring and mackerel from their current habitats near Scotland if and when global ocean temperatures increase. These two fish species represent a significant economic contribution to the Scottish fishing industry. Changes in population locations of herring and mackerel could make it economically impractical for smaller Scotland-based fishing companies, who use fishing vessels without on-board refrigeration, to harvest and deliver fresh fish to markets in Scotland fishing ports.

Requirements

1. Build a mathematical model to identify the most likely locations for these two fish species over the next 50 years, assuming that water temperatures are going to change enough to cause the populations to move.

2. Based upon how rapidly the ocean water temperature change occurs, use your model to predict best case, worst case, and most likely elapsed time(s) until these populations will be too far away for small fishing companies to harvest if the small fishing companies continue to operate out of their current locations.

3. In light of your predictive analysis, should these small fishing companies make changes to their operations?

   a. If yes, use your model to identify and assess practical and economically attractive strategies for small fishing companies. Your strategies should consider, but not be limited to, realistic options that include:
   - Relocating some or all of a fishing company’s assets from a current location in a Scottish port to closer to where both fish populations are moving;
   - Using some proportion of small fishing vessels capable of operating without land-based support for a period of time while still ensuring the freshness and high quality of the catch.
   - Other options that your team may identify and model.

   b. If your team rejects the need for any changes, justify reasons for your rejection based on your modeling results as they relate to the assumptions your team has made.

4. Use your model to address how your proposal is affected if some proportion of the fishery moves into the territorial waters (sea) of another country.

5. In addition to your technical report, prepare a one- to two-page article for Hook Line and Sinker magazine to help fishermen understand the seriousness of the problem and how your proposed solution(s) will improve their future business prospects.

Your submission should consist of:

- One-page Summary Sheet
- One- to Two-page Article
- Your solution of no more than 20 pages, for a maximum of 24 pages with your summary and article.

Glossary

Fishery: The collection of fish of a given species and the area that they inhabit.

Habitat: The type of environment in which an organism or group normally lives or occurs.

Small Fishing Company: A company engaged in commercial fishing with limited or very limited financial resources to invest in new equipment/vessels.

Territorial Waters (sea): "as defined by the 1982 United Nations Convention on the Law of the Sea, is a belt of coastal waters extending at most 12 nautical miles (22.2 km; 13.8 mi) from the baseline (usually the mean low-water mark) of a coastal state. The territorial sea is regarded as the sovereign territory of the state, although foreign ships (military and civilian) are allowed innocent passage through it, or transit passage for straits; this sovereignty also extends to the airspace over and seabed below."

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

`D:\vscode_project\ModelingAgent\openclaw_experiments\interaction_strategy_clean_baseline_initial_draft_train_20260916_202307\runs\round_1\r1p27_20260917_151850\output\results\draft.md`

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
