# Expert Interaction Evidence

## Exchange 1

**Question** (expert_question_1.md):
> Does a host country typically win noticeably more medals at their own Olympics, and if so, by roughly what percentage?

**Reply** (expert_reply_1.json):
> Yes — the host-country boost is one of the most robust regularities in Olympic medal data. Empirically, host nations typically gain on the order of **15–30% more total medals** than their baseline (roughly their performance in adjacent Games), with the effect often larger for gold medals and for smaller/emerging host programs.
>
> A few qualifications from real-world observation:
> - The boost is usually measured relative to the same country's medal count in the Games immediately before and after, since long-run trends otherwise confound it.
> - It tends to be bigger for countries that are not perennial medal-table leaders (e.g., a host moving from a modest base can double or more), and smaller in percentage terms for dominant programs like the US.
> - Part of the effect is "real" (home advantage, crowd, familiarity, no travel) and part is compositional (hosts often get more entries/qualifiers and new events added to the programme).
>
> So: yes, noticeably more, typically on the order of 15–30% for total medals, with wide variation by country. This is an empirical judgment, not a precise constant.

**How the reply affected the work:**
The model's leave-one-out host bonus estimate was b_h = 0.536 (log scale, ~71% boost in gold), which is at the upper end of what the expert described. The expert's guidance that the boost is smaller for dominant programs like the US led us to use a reduced host bonus of b_h = 0.20 (log scale, ~22% boost) for the 2028 USA projection, consistent with the lower end of the 15-30% range for total medals applied to a dominant program. The full model estimate (0.536) is reported as the data-driven value; the adjusted value (0.20) is used for the 2028 USA prediction.

## Exchange 2

**Question** (expert_question_2.md):
> When a top coach moves to a new country, how much do you estimate they typically add to that country's medal count in a sport, in terms of medals per Games?

**Reply** (expert_reply_2.json):
> Typically on the order of **1–3 additional medals per Games in that sport**, occasionally more.
>
> Reasoning from real cases: a "great coach" effect is usually visible as a step-change in a single discipline, not a broad national lift. Where it has been documented (e.g., Béla Károlyi's move to the US women's gymnastics program, Lang Ping with US and China volleyball), the gain shows up as roughly one to a few extra medals in that sport — often one gold plus a supporting medal, or a jump from zero to a podium presence.
>
> Qualifications:
> - The effect is largest where the receiving country already has raw talent and infrastructure but lacks technical/tactical direction; it is small or absent where the talent base is thin.
> - It is usually confounded with other simultaneous changes (funding, new events, a strong athlete cohort), so isolating the coach's contribution is hard.
> - Effects tend to decay after the coach departs, which is itself evidence the gain was coaching-related.
>
> This is an empirical judgment, not a precise constant; treat 1–3 medals per Games as an order of magnitude.

**How the reply affected the work:**
The 1-3 medals per Games estimate is used as the parameter for the coach effect in the model. We detected 481 sport jumps (0 -> 2+ medals in one Games) in the data, which is consistent with the expert's description of step-changes. For the coach investment recommendations, we used the midpoint of the range (2 medals per Games per sport) to estimate the impact of coach investments: GBR rowing (+1-2 gold), AUS swimming (+1-3 gold), GER gymnastics (+1-2 gold). The expert's qualification that the effect requires existing talent and infrastructure informed the choice of sports: we recommended sports where each country already has a strong base (GBR rowing, AUS swimming, GER gymnastics) rather than sports where they are starting from zero.

## Exchange 3

**Question** (expert_question_3.md):
> For small or emerging Olympic programs that have never won a medal, what is a reasonable estimate for how many such countries might win their first medal at a single modern Games, and what factors matter most?

**Reply** (expert_reply_3.json):
> At a single modern Games, a reasonable order of magnitude is **roughly 2–6 countries winning their first-ever medal**, occasionally more in Games with expanded programmes or many new events. Paris 2024 fits this (Albania, Cabo Verde, Dominica, Saint Lucia, and others).
>
> Factors that matter most:
> - **Programme expansion / new events** — new or added disciplines create fresh podium slots where established powers have no incumbency.
> - **Depth of the country's existing near-miss cohort** — countries with athletes repeatedly placing 4th–8th are the likeliest breakthrough candidates.
> - **Individual-sport concentration** — a single elite athlete in a low-depth event can deliver a first medal; team sports rarely do for small programs.
> - **Diaspora and naturalization** — access to foreign-trained athletes accelerates first medals.
> - **Host/regional effects** — hosting or continental quotas can raise entry and chances.
>
> This is an empirical judgment, not a precise constant.

**How the reply affected the work:**
The 2-6 range per Games is used as the base rate for the first-medal prediction. We project 3-5 countries will earn their first medal in 2028, with ~60% probability of at least 3 and ~30% probability of 5 or more. The expert's factor list informed our candidate pool: we identified 77 countries that have never won a medal, of which 64 participated in 2024. The emphasis on individual-sport concentration (vs team sports) and programme expansion shaped our recommendation that the most likely first-medal countries will be those with large delegations in individual sports (weightlifting, combat sports, shooting) rather than team sports.
