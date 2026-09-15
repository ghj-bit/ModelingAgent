# Empirical data items used to calibrate / validate the model

Only a small number of verifiable public figures were used; each materially affects the
fleet economics or the validation.

1. **Vehicle capacity and purchase price**
   - Type C (conventional) school buses: 54–90 passengers; Type D (transit-style): 72–90.
     A standard 72-passenger bus is the industry workhorse. New 72-passenger bus:
     ≈ US$130,000–$160,000.
   - Sources: Gregory Poole Equipment Co., "How Much Does a School Bus Cost?"
     (https://www.gregorypoole.com/school-bus-costs);
     Rohrer Bus, "Frequently Asked Questions About School Buses"
     (https://www.rohrerbus.com/school-bus-faqs).
   - Use: seat capacity Q = 72 (design value, sensitivity 36–84) and capital-cost magnitude
     for the fixed cost per bus-day.

2. **Operating economics (fuel, annual mileage) and per-mile reimbursement benchmark**
   - Typical school bus ≈ 7 mpg; ≈ 12,000 miles/yr per bus (NYSBCA "School Bus Facts",
     https://www.nysbca.com/fastfacts).
   - State cost-based reimbursement benchmark: Nebraska reimburses regular transportation at
     ≈ US$1.91 per bus-mile (Georgia Public Policy Foundation, "A Review of K-12
     Transportation in Georgia",
     https://www.georgiapolicy.org/publications/a-review-of-k-12-transportation-in-georgia).
   - Use: 7 mpg + a diesel price gives the fuel component of the variable cost per km; the
     $1.91/mile figure is used as an external sanity benchmark for total per-mile cost.

3. **Sector structure (who is bused, rural premium)**
   - ≈ 51.9% of Georgia district students are bused; ≈ 54% nationally ride yellow buses.
   - Rural school-district transportation costs run about **40% more per student** than
     city/suburban districts (Ellegood, W.A., et al., 2024, "The many costs of operating
     school buses in America," *Research in Transportation Economics*,
     https://www.sciencedirect.com/science/article/abs/pii/S0739885923001415).
   - Use: justifies the rural-first framing and the higher per-student cost in the model.

All monetary values are order-of-magnitude design inputs; the model's qualitative
conclusions are shown (Section 7) to be robust to wide variation in every cost parameter.
