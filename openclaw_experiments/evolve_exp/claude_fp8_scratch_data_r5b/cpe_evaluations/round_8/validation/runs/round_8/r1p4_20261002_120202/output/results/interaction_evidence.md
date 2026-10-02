# Interaction Evidence

## Exchange 1 — Operational Mechanism (how the money works)
**Question (Q1):** When a foundation gives a college a large grant, is it one lump sum or spread over years?

**Expert reply:** A large grant is almost always disbursed as smaller payments spread over several years (commonly 3–5 yr), as a multi-year "grant commitment" the recipient draws down against milestones/budget periods. For a five-year, $100M/yr program, each school's award is a multi-year commitment paid in installments; the foundation's $100M is the **annual** outflow, not a one-time transfer.

**How the reply affected the work:**
- The $100M figure is treated as an **annual** budget (5 × $100M = $500M total program), not a single 5-yr lump sum. This fixes the total fund pool F = 500,000,000.
- Each school's allocation is modeled as a **multi-year commitment paid in installments** over the 5-yr horizon (a per-year drawdown), rather than a one-time transfer. This shapes the ROI/return timing: returns (improved student outcomes) are measured over the 5-yr commitment window, and the per-school allocation is the committed commitment, not a single disbursement.
- Consequence for the optimization: the decision variable is a per-school **committed** award (sum of installments) over the 5-yr horizon, with the constraint that total committed awards ≤ F = 500M.

## Exchange 2 — Causal Hierarchy (what drives student success)
**Question (Q2):** Which matters more for a college's student success: the quality of students it admits, or what it does with them?

**Expert reply:** "What a college does" (value added) matters more for the value it adds; intake quality matters more for the raw outcomes it reports. Raw metrics (graduation, repayment, earnings) are heavily driven by incoming selectivity and socioeconomic mix — a school admitting well-prepared affluent students posts strong outcomes regardless of its effort. To find schools with demonstrated potential to effectively use private funding, Goodgrant must look at value-added / adjusted performance (outcomes relative to student profile), not raw outcomes. Institutional effects on completion and earnings exist but are typically smaller than the student-intake effect. Intake quality is the dominant confounder; "what the school does" is what's worth funding, but only visible after controlling for intake.

**How the reply affected the work:**
- The model ranks schools on **value-added**, not raw outcome rates. Raw earnings/graduation would reward selective, affluent-feeding schools (common-cause artifact: intake quality drives both the outcome and the apparent "quality"). The model instead regresses each outcome on intake proxies and uses the residual — the school-specific deviation above what intake predicts — as the "effective use of funding" signal.
- Intake proxies available in the data: `SAT_AVG` (47% coverage, fallback to ACT composites), `PCTPELL` (99.8% coverage, Pell share = socioeconomic mix), and `PCIP10` (share in business). The residual approach controls for the dominant confounder (intake quality / SES).
- Consequence: schools that "out-perform their intake profile" — i.e., add value to the students they admit — score high, which is the defensible criterion for "potential for effective use of private funding." Raw high-performers with high-intake are not automatically favored.

## Exchange 3 — Decision-Relevant Uncertainty Threshold (what makes a school worth funding)
**Question (Q3):** If a school's predicted earnings boost is small, how large a miss makes it not worth a $500,000 grant?

**Expert reply:** No clean absolute dollar threshold. A $500k grant is philanthropic spend whose return is measured in student outcomes, not dollars repaid. Two readings: (a) financial — worth it if earnings-boost × students affected > $500k; with 500 students that needs ~$1,000/student added lifetime earnings, so almost any positive boost clears it; the size of the miss is not the real question. (b) philanthropic — the relevant comparison is boost per dollar vs. what the same $500k would buy at another school; a school is not worth funding if its predicted boost per dollar is at or below the median of the candidate pool, regardless of absolute boost. The disqualifying "miss" is relative — being below the marginal school in the ranked list. Any absolute cutoff (e.g. <$2,000/student) is arbitrary, not supported by data.

**How the reply affected the work:**
- ROI is defined as **relative value added per dollar committed**, not an absolute earnings gain. A school earns a slot only if its value-added-per-dollar exceeds the marginal (last-funded) school in the ranked list. This makes the selection **rank-driven** under the budget constraint: sort schools by value-added-per-dollar and fund top-to-bottom until the $500M total commitment is exhausted.
- No arbitrary absolute earnings threshold is imposed. The cutoff is the marginal value-added-per-dollar of the last funded school (the shadow price of the budget).
- The "boost per dollar" is computed as the school's value-added score (earnings residual, z-scored) scaled by its enrollments affected (the number of students whose outcomes the grant can move) divided by the committed award — i.e., marginal students-affected per dollar. This is the actionable decision rule.
- Consequence for the optimization: the allocation is a knapsack / marginal-value selection. Schools are ordered by value-added-per-dollar; the budget F = 500M is spent down the list. The recommended candidate list is the prefix of that ordering, with the per-school committed award and its ROI (value-added per dollar) reported.
