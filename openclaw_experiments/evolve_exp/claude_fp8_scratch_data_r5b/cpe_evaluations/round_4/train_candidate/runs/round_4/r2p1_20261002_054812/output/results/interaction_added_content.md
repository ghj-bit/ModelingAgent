# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Great Lakes 2024_D

## Exchange 1: Data Provenance

**Question (expert_question_1.md):**
"Some Great Lakes river-flow records begin partway through the series rather than starting in 2000. Why do these older years show no flow measurements at all — were the stations not yet recording, or are the early values simply withheld?"

**Reply (expert_reply_1.json):**
The early blanks are a data-availability boundary of the compiled dataset, not of the rivers. The flows are derived quantities computed from lake-level differences, gate settings, hydropower diversions, and rating curves; those computational records were only assembled and published from a certain start year onward. The workbook reproduces the published record's start date. The blanks mean "no value in this source series," not "no water" and not "suppressed." Each sheet's start year should be treated as an empirical property read off the data.

**How the reply affected the work:**
- The missing values in St. Mary's (pre-2009), St. Clair/Detroit (pre-2009), Niagara (2021-22), and St. Lawrence (pre-2012) sheets were interpreted as compilation boundaries, not sensor failures.
- The imputation strategy was chosen accordingly: interior gaps (e.g., the single Ottawa River missing cell) were linearly interpolated along the year axis; truncated leading/trailing blocks were filled by bounded nearest-year fill rather than by assuming a uniform 2000 start.
- The 2017 retrospective uses only sheets with complete 2017 data (Niagara, Ottawa, St. Lawrence all have 2017 values), so no imputed value enters the 2017 balance.

## Exchange 2: Structural Assumption — Monthly Resolution

**Question (expert_question_2.md):**
"The workbook gives only monthly average river flows and monthly average lake levels. Do you consider such monthly averages representative enough to judge how well a water-level control plan worked during 2017?"

**Reply (expert_reply_2.json):**
Yes — monthly averages are representative enough for judging a control plan's performance in 2017, with one caveat. Water levels respond with long time constants (weeks to months); the quantities that matter for stakeholder outcomes — seasonal high/low levels, whether levels stayed within a band, whether flooding or navigation-draft thresholds were breached — are monthly-to-seasonal phenomena that monthly means capture directly. The caveat: monthly averaging hides short-term extremes (storm surges, ice-jam backwater, wind setup) that cause shoreline damage. Monthly resolution is adequate to judge target levels and seasonal regulation, not transient or extreme-event performance.

**How the reply affected the work:**
- The model uses monthly mass balance as its core framework, justified as the appropriate timescale for seasonal regulation assessment.
- The limitation is explicitly stated in the solution: the model cannot judge transient or extreme-event performance, and results are framed as seasonal-regulation outcomes.
- The evaporation/tributary net term EVAP was set to 0 m³/s because the recorded monthly outflow (St. Lawrence at Cornwall) already balances the recorded monthly inflow (Niagara + Ottawa) within averaging noise; adding an independent evaporation term would double-count a flux already embedded in the measured outflow.

## Exchange 3: Decision-Relevant Threshold

**Question (expert_question_3.md):**
"When comparing a proposed lake-level plan against 2017's actually recorded levels, how large a month-to-month difference in Lake Ontario's level would you consider a practically important one for the people living on its shores?"

**Reply (expert_reply_3.json):**
For Lake Ontario shoreline residents, roughly 0.1 m (~4 inches) is where people start to notice; 0.2–0.3 m (8–12 inches) is clearly practically important; 0.3 m (~1 ft) or more is a serious outcome that drives erosion, dock/boathouse damage, and flooding complaints. Context: Lake Ontario's normal seasonal range is ~0.5–0.7 m, and the problem statement notes that a 2–3 ft (0.6–0.9 m) departure from normal dramatically affects stakeholders. A plan shifting monthly levels by ~0.1 m is within the noise of ordinary regulation; 0.2–0.3 m is a real, stakeholder-visible difference. This is an empirical judgment.

**How the reply affected the work:**
- Two decision thresholds were set: ATTENTION = 0.10 m (noticeable) and DECISIVE = 0.20 m (practically important).
- The 2017 retrospective reports, for each control setting, the number of months where the simulated level differs from the actual 2017 level by at least 0.10 m and at least 0.20 m.
- The interpretation of results uses these thresholds: a plan is "satisfactory or better" if it keeps monthly deviations from the actual 2017 level below 0.20 m in most months, or keeps the simulated level within the ±0.30 m target band.
- The target band half-width Z_BAND = 0.30 m was set to match the upper end of the "practically important" range, consistent with the IJC LO-SLRB target band of approximately ±1 ft.
