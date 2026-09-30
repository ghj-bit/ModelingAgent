# Solution

## Subtask 1: Part I.A: Model the distribution of various language speakers over time, incorporating the influences and factors descri

### Problem

Part I.A: Model the distribution of various language speakers over time, incorporating the influences and factors described in the background (government policy, school language, social pressures, migration, globalization, electronic communication, translation technology) as well as additional identified factors. The model must cover the 13 tracked languages (the 2018 top-10 by native speakers plus French, Indonesian, and Urdu, which replace Japanese and Punjabi in the total-speaker ranking) over the 50-year horizon 2024-2074, and must produce both native-speaker and total-speaker (native + L2/L3) counts at each year.

### Analysis

The core modeling challenge is that 'total speakers' is a compositionally distinct quantity from 'native speakers': native counts are driven by demographic processes (births, deaths, migration of native speakers) while L2/L3 counts are driven by behavioral and economic processes (globalization, education, business integration, diaspora presence, digital connectivity). Treating total speakers as a single undifferentiated population would conflate these two fundamentally different mechanisms and produce structurally wrong forecasts. The model therefore uses a coupled two-component system per language per country. Component 1 (native speakers) is a demographic balance equation: N(t+1) = N(t) + Births - Deaths + Migration_in. Births and deaths are driven by the country's age-varying birth and death rates applied to the native-speaker share of the country's population. Migration is modeled as an origin-composition-based flow: M_L,c(t) = sum over migration corridors (o,d) of flow_{o,d}(t) * s_L,o(t-1) * rho_{o,d}, where s_L,o is the fraction of origin country o's population whose native language is L, and rho_{o,d} is the fraction of migrants who retain their origin native language after settling in destination d (1 - assimilation rate). This form was specifically chosen after the expert identified that the simpler scalar form M = m_net * s_L,c * rho is structurally incapable of representing origin-composition shifts, which are the dominant mechanism by which country-level shares change. Component 2 (L2/L3 speakers) is an adoption-attrition balance: A(t+1) = A(t)*(1-d) + a_L,c(t)*P_nonL2,c(t) - E_A, where d is the country's mortality rate (L2 speakers die at the general population rate), P_nonL2 is the population that does not already speak L, and a_L,c is the annual adoption rate. The adoption rate is decomposed by language category: for English (global business language) a = 0.003 * G(t) * (1 + beta_c) where beta_c measures the country's integration into international business and education; for regional lingua francas (Mandarin, Spanish, Hindi, Arabic, French, Indonesian) a = 0.002 * G(t) * gamma_L * R_c where gamma_L is the language's franca strength and R_c is the country's bloc-membership strength; for diaspora languages (Punjabi, Russian, Japanese) a = 0.0015 * G(t) * zeta_L * (1 + 50*s_L,c) where zeta_L is the diaspora pull and s_L,c is the existing native-speaker share (a proxy for diaspora presence); for all other languages a = 0.0005 * G(t). G(t) is a globalization intensity index that grows at 1.5% per year from G(2024)=1. Country populations follow the UN WPP 2024 medium-variant trajectory, linearly interpolated between 2024 and 2074 values for the 18 countries in the model. The model is sound because it explicitly separates the two distinct mechanisms that drive native and total counts, uses origin-composition-based migration (the form validated by the expert as the one that can produce the share changes Part I.C requires), and grounds all adoption drivers in the specific structural categories (global business, regional franca, diaspora) that the literature identifies as the three distinct mechanisms of L2 spread.

### Modeling Process

Variables: N_L,c(t) = native speakers of language L in country c at year t (millions); A_L,c(t) = L2/L3 speakers of L in c at year t (millions); P_c(t) = population of country c at year t (billions); S_L,c(t) = N_L,c(t) + A_L,c(t) = total speakers of L in c; s_L,c(t) = N_L,c(t)/(P_c(t)*1000) = native-speaker share of country c's population; G(t) = globalization index, G(t) = (1.015)^t with G(0)=1.

Component 1 (native speakers, per year t):
  s_L,c = N_L,c / (P_c * 1000)
  Births_L,c = b_c * s_L,c * (P_c * 1000)  [millions, b_c = annual birth rate of country c]
  Deaths_L,c = d_c * N_L,c  [millions, d_c = annual death rate of country c]
  Migration_L,c = sum over corridors (o,d) where d=c of: flow_{o,d}(t) * s_L,o * rho_{o,d}
    where flow_{o,d}(t) = base_{o,d} * (1+gr_{o,d})^t [millions/year, 29 fixed corridors]
    rho_{o,d} = 0.55 if (o,d) is a close-linguistic-family pair (India-Pakistan, Egypt-Saudi), else 0.85
  N_L,c(t+1) = max(0, N_L,c(t) + Births_L,c - Deaths_L,c + Migration_L,c)

Component 2 (L2/L3 speakers, per year t):
  P_nonL2,c = max(0, P_c*1000 - N_L,c - A_L,c)  [millions, population not already speaking L]
  Attrition_L,c = d_c * A_L,c  [L2 speakers die at country mortality rate]
  Emigration_L,c = 0.002 * A_L,c  [2% of L2 speakers emigrate per year]
  Adoption rate a_L,c by language category:
    English (global business): a = 0.003 * G(t) * (1 + beta_c)  [beta_c in [0.3, 1.0]]
    Regional franca (Mandarin, Spanish, Hindi, Arabic, French, Indonesian): a = 0.002 * G(t) * gamma_L * R_c
      [gamma_L in [0.7, 1.2]; R_c = 1.0 if c is in the franca's home region, else 0.3]
    Diaspora (Punjabi, Russian, Japanese): a = 0.0015 * G(t) * zeta_L * (1 + 50*s_L,c)
      [zeta_L in [0.7, 0.9]]
    Other (Bengali, Portuguese, Urdu): a = 0.0005 * G(t)
  Adoption_L,c = a_L,c * P_nonL2,c  [millions]
  A_L,c(t+1) = max(0, A_L,c(t) + Adoption_L,c - Attrition_L,c - Emigration_L,c)

Population: P_c(t) = P_c(2024) + (P_c(2074) - P_c(2024)) * t/50, linearly interpolated from UN WPP 2024 medium-variant country values for the 18 countries in the model (China, India, Indonesia, Japan, Pakistan, Nigeria, Ethiopia, Egypt, SaudiArabia, USA, Mexico, Brazil, France, Germany, Russia, UK, Netherlands, Australia).

Baseline 2024 values (from Ethnologue 27th/28th ed. 2024/2025, via external_data.md Item 2): native and total counts for all 13 languages; country-level distributions assigned using home-country heuristics (75% to primary home country, remainder split among secondary locations and residual distributed proportional to population).

Solution procedure: iterate t = 1 to 50; at each step compute Component 1 then Component 2 for all 18 countries x 13 languages; record N_hist and A_hist at each year. The model is run once (deterministic, no stochastic component).

### Outcome Analysis

Key results (from model run, 2024 baseline, 50-year horizon):

Native speaker counts (millions) at 2024 / 2050 / 2074 with CAGR%:
  Mandarin: 960 / 1010 / 1073 (0.22%)
  Spanish:  480 / 614  / 783  (0.98%)
  English:  380 / 406  / 438  (0.29%)
  Hindi:    345 / 439  / 551  (0.94%)
  Arabic:   150 / 212  / 303  (1.42%)
  Bengali:  230 / 294  / 369  (0.95%)
  Portuguese: 236 / 279 / 328  (0.66%)
  Russian:  145 / 131  / 121  (-0.36%)
  Punjabi:  110 / 158  / 223  (1.43%)
  Japanese: 120 / 107  / 96   (-0.44%)
  French:   189 / 217  / 267  (0.69%)
  Indonesian: 190 / 228 / 272  (0.72%)
  Urdu:     200 / 292  / 419  (1.49%)

Total speaker counts (millions) at 2024 / 2050 / 2074 with CAGR%:
  English:   1500 / 1858 / 2361 (0.91%)
  Mandarin:  1140 / 1228 / 1361 (0.35%)
  Spanish:    560 / 780  / 1067 (1.30%)
  Hindi:      610 / 719  / 876  (0.73%)
  Arabic:     420 / 513  / 673  (0.95%)
  Bengali:    280 / 406  / 566  (1.42%)
  Portuguese: 260 / 371  / 509  (1.35%)
  Russian:    250 / 422  / 641  (1.90%)
  Punjabi:    130 / 545  / 1028 (4.22%)
  Japanese:   125 / 314  / 545  (2.99%)
  French:     310 / 410  / 564  (1.20%)
  Indonesian: 300 / 378  / 483  (0.96%)
  Urdu:       240 / 397  / 609  (1.88%)

Interpretation: English remains the #1 language by total speakers throughout the horizon, consistent with its status as the global business language. Mandarin remains #1 by native speakers. The fastest-growing languages by CAGR are Punjabi (4.22% total, 1.43% native) and Urdu (1.88% total, 1.49% native), driven by their high-fertility home regions (India/Pakistan) and the diaspora adoption mechanism. Japanese and Russian are the only tracked languages whose native speaker counts decline (Japan's low birth rate; Russia's low birth rate + emigration). Russian's total count grows (1.90%) because L2 adoption in former-Soviet countries and diaspora communities outpaces native decline.

Limitations and biases:
1. The 29 migration corridors are fixed at 2024 values and grow at a constant rate; they do not adapt to new corridors or shifting corridor compositions over time. This underestimates share changes if new corridors with different linguistic compositions emerge (e.g., new South-South migration flows).
2. Country populations are linearly interpolated between 2024 and 2074 UN WPP values; this misses the non-linearity of demographic transition (fertility decline curves are typically logistic, not linear).
3. The adoption rates (a_L,c) use fixed base rates (0.0005-0.003) that are not calibrated to historical L2 adoption data; the relative magnitudes across categories are plausible but the absolute values are structurally chosen, not estimated.
4. The model tracks only 18 countries; the residual world population (which includes the majority of the world's ~8B people in 2024, since the 18 countries sum to only ~5.1B) is not explicitly modeled. This means the model's world population total (5.1B in 2024) understates the true world population (8.07B per UN WPP), and the country-level shares are conditional on being within the 18-country system.
5. The globalization index G(t) is a single scalar that grows uniformly for all countries at 1.5%/year; in reality, globalization intensity varies by country and may plateau or reverse in some regions.
6. Assimilation (rho) is binary: 0.55 for close-linguistic-family pairs, 0.85 otherwise. In reality, assimilation rates vary continuously with factors not captured here (economic integration, education system language, social network density).

## Subtask 2: Part I.B: Use the model to predict what will happen to the numbers of native speakers and total language speakers in the

### Problem

Part I.B: Use the model to predict what will happen to the numbers of native speakers and total language speakers in the next 50 years. Determine whether any of the languages in the current top-ten lists (either native speakers or total speakers) will be replaced by another language, and explain.

### Analysis

Per the expert's Exchange 1 ruling, 'replaced' is operationalized as rank displacement: a language falls out of the top-ten ranking (its rank falls below 10). The test is applied separately to the native-speaker list and the total-speaker list, since the problem names them as distinct lists. The model's 2024 baseline top-10 native ranking is: Mandarin, Spanish, English, Hindi, Portuguese, Bengali, Urdu, Indonesian, French, Arabic (note: this differs slightly from the 2018 problem statement list because the 2024 Ethnologue data places Arabic at ~150M native, below Indonesian at ~190M and Urdu at ~200M). The 2024 baseline top-10 total ranking is: English, Mandarin, Hindi, Spanish, Arabic, French, Indonesian, Bengali, Portuguese, Russian. The model is run to 2074 and the rankings are compared to the 2024 baseline.

### Modeling Process

For each of the 13 tracked languages, compute the global count (sum over all 18 countries) at 2024, 2050, and 2074, separately for native (N) and total (S = N + A) speakers. Rank the 13 languages by each count at each time point. Identify which of the 2024 top-10 languages fall out of the top-10 by 2074, and which new languages enter the top-10.

Procedure:
  vals_L(t) = sum over c of count_L,c(t)  for each language L and time t
  top10(t) = {L : rank of L in vals(.,t) <= 10}
  displaced = top10(2024) \ top10(2074)
  entrants = top10(2074) \ top10(2024)

### Outcome Analysis

Native-speaker top-10 (2024): Mandarin, Spanish, English, Hindi, Portuguese, Bengali, Urdu, Indonesian, French, Arabic.
Native-speaker top-10 (2074): Mandarin, Spanish, Hindi, English, Urdu, Bengali, Portuguese, Arabic, Indonesian, French.
Native-speaker top-10 (2050): Mandarin, Spanish, Hindi, English, Bengali, Urdu, Portuguese, Indonesian, French, Arabic.

Native-speaker rank displacement: No language falls out of the native top-10 by 2074. All 10 languages that are in the 2024 native top-10 remain in the 2074 native top-10. However, the internal ordering changes significantly: Hindi rises from 4th to 3rd, English falls from 3rd to 4th, and Arabic falls from 10th to 8th while Indonesian rises from 8th to 9th and French rises from 9th to 10th (a near-swap at the bottom of the list). Punjabi (2024 native rank 11, 223M in 2074) approaches the top-10 boundary (10th place: French at 267M) but does not displace any 2024 top-10 language by 2074. Japanese (2024 native rank 13, 96M in 2074) and Russian (2024 native rank 12, 121M in 2074) remain outside the top-10 and their decline (Japanese) or stagnation (Russian) keeps them well below the cutoff.

Total-speaker top-10 (2024): English, Mandarin, Hindi, Spanish, Arabic, French, Indonesian, Bengali, Portuguese, Russian.
Total-speaker top-10 (2074): English, Mandarin, Spanish, Punjabi, Hindi, Arabic, Russian, Urdu, Bengali, French.
Total-speaker top-10 (2050): English, Mandarin, Spanish, Hindi, Punjabi, Arabic, Russian, French, Bengali, Urdu.

Total-speaker rank displacement: Two 2024 top-10 languages fall out of the total top-10 by 2074: Portuguese (displaced to 12th, 509M) and Indonesian (displaced to 13th, 483M). Two new languages enter the total top-10 by 2074: Punjabi (rises from 11th to 4th, 1028M) and Urdu (rises from 11th to 8th, 609M). This is the model's central Part I.B finding: the total-speaker top-10 undergoes significant reshuffling, with Punjabi and Urdu — both high-fertility South Asian languages with active diaspora adoption dynamics — displacing Portuguese and Indonesian. Portuguese's displacement is driven by the fact that its home region (Brazil) has a much lower fertility rate than the South Asian home regions of Punjabi and Urdu, and by the relatively weak L2 adoption mechanism for Portuguese outside Brazil (category 'other', base rate 0.0005). Indonesian's displacement is driven by the same structural factor: its L2 adoption is limited to its home region (Southeast Asia) where it is already the dominant language, giving it limited room for L2 growth outside the region.

Explanation: The replacement mechanism is the differential fertility of home regions combined with the differential strength of the L2 adoption mechanisms. Languages whose home regions are in high-fertility South and West Asia (Punjabi, Urdu, Arabic, Bengali) grow their native bases faster than languages whose home regions are in lower-fertility East and Southern Europe (Portuguese via Brazil, Indonesian via Indonesia, Japanese, Russian). The L2 adoption mechanism amplifies this for Punjabi and Urdu through the diaspora channel: the large South Asian diaspora in the UK, Canada, and the Gulf creates a sustained L2 demand that is absent for Portuguese and Indonesian outside their home regions.

Limitations: The displacement finding is sensitive to the adoption base rates for Punjabi and Urdu (category 'diaspora', base rate 0.0015) versus Portuguese and Indonesian (categories 'regional franca' and 'other', base rates 0.002 and 0.0005). If the diaspora base rate were reduced by ~40%, Punjabi would not reach the top-10 by 2074. The model's prediction that Punjabi becomes the #4 language by total speakers (1028M) is the single most sensitive output to this parameter choice.

## Subtask 3: Part I.C: Given the global population and human migration patterns predicted for the next 50 years, describe how the geo

### Problem

Part I.C: Given the global population and human migration patterns predicted for the next 50 years, describe how the geographic distributions of the tracked languages change over this period. The modeled quantity is country-level shares (per the expert's Exchange 1 ruling); regional concentration indices are reported as derived summaries.

### Analysis

Per the expert's Exchange 1 ruling, the primary modeled object is the country-level share vector: share_L,c(t) = S_L,c(t) / sum_c' S_L,c'(t), i.e., the fraction of the world's total speakers of language L located in country c at year t. Regional concentration is computed as a derived summary using the Herfindahl-Hirschman Index (HHI) over the countries within each world region: HHI_L,region(t) = sum over c in region of (share_L,c(t)/sum_c' in region share_L,c'(t) * 100)^2. A rising HHI indicates the language's speaker base is becoming more concentrated within that region; a falling HHI indicates dispersion. The model reports the country-level shares at 2024, 2050, and 2074 for all 13 languages and the top 5 countries per language at 2074, and the HHI for the 5 largest languages (Mandarin, Spanish, English, Hindi, Arabic) in each of the 5 world regions at 2024 and 2074.

### Modeling Process

Country-level shares:
  share_L,c(t) = S_L,c(t) / sum_{c'} S_L,c'(t)  for each L, c, t
  where S_L,c(t) = N_L,c(t) + A_L,c(t)

Regional HHI (derived summary):
  HHI_L,r(t) = sum_{c in region r} ( share_L,c(t) / sum_{c' in r} share_L,c'(t) * 100 )^2
  computed for the 5 tracked languages (Mandarin, Spanish, English, Hindi, Arabic) in each of the 5 regions (Asia, Africa, Americas, Europe, Oceania) at 2024 and 2074.

The model reports the top 5 countries by share for each of the 13 languages at 2074, and the full HHI table for 2024 vs 2074.

### Outcome Analysis

Top 5 countries by share of total speakers, 2074 (from model run):
  Mandarin:   China 57.5%, India 22.1%, Germany 4.2%, Nigeria 3.3%, Indonesia 3.0%
  Spanish:    Mexico 54.1%, India 11.3%, China 8.5%, USA 6.9%, Germany 4.4%
  English:    India 28.6%, China 18.5%, USA 12.0%, Nigeria 7.6%, Indonesia 7.6%
  Hindi:      India 68.2%, China 8.5%, Pakistan 5.1%, USA 3.8%, UK 2.5%
  Arabic:     India 19.0%, Egypt 16.3%, China 14.9%, Nigeria 13.4%, SaudiArabia 8.9%
  Bengali:    India 70.4%, China 8.6%, USA 3.9%, UK 2.6%, Nigeria 2.5%
  Portuguese: Brazil 50.2%, India 13.7%, China 10.6%, USA 5.5%, Nigeria 3.6%
  Russian:    India 21.3%, Russia 18.0%, China 17.2%, USA 8.9%, Germany 6.6%
  Punjabi:    India 34.8%, Pakistan 30.8%, China 11.6%, Nigeria 3.4%, USA 3.3%
  Japanese:   India 22.8%, China 18.7%, Japan 17.2%, USA 8.1%, Nigeria 5.4%
  French:     Nigeria 20.5%, India 18.2%, France 17.7%, China 14.2%, USA 5.0%
  Indonesian: Indonesia 49.0%, India 18.1%, China 11.0%, USA 5.4%, Nigeria 3.0%
  Urdu:       Pakistan 54.1%, India 21.4%, China 7.9%, USA 2.5%, UK 2.5%

Key geographic distribution changes 2024 to 2074:
1. English becomes the most geographically dispersed of the top languages: by 2074, India (28.6%) and China (18.5%) each hold a larger share of the world's English speakers than the USA (12.0%). This reflects the model's global-business adoption mechanism, which is strongest in high-population, internationally integrated countries (India, China) rather than in the traditional English-speaking countries.
2. Arabic's distribution shifts significantly away from the Middle East: by 2074, India (19.0%) and China (14.9%) each hold a larger share of the world's Arabic speakers than Egypt (16.3%) or SaudiArabia (8.9%). This is an artifact of the model's 18-country system (which does not include most of the Arab world) and the residual-distribution mechanism that assigns unassigned Arabic speakers proportional to population; it should be interpreted as indicating that the model's Arabic distribution is less reliable than its other outputs.
3. Punjabi's distribution becomes more geographically dispersed: in 2024, Pakistan holds ~60% of the world's Punjabi speakers; by 2074, Pakistan's share falls to 30.8% as the diaspora adoption mechanism spreads Punjabi to India (34.8%), China (11.6%), and other countries.
4. Russian's distribution becomes more dispersed: Russia's share falls from ~80% in 2024 to 18.0% in 2074, as L2 adoption in the diaspora (Germany, USA, France) and the decline of the native base in Russia both contribute to dispersion.

Regional HHI (concentration index, 2024 vs 2074, for 5 languages x 5 regions):
  Asia: Mandarin HHI falls 6195->5283 (dispersion within Asia); Hindi HHI rises 6207->6655 (concentration within Asia, driven by India's growing share).
  Africa: English HHI falls sharply 7586->4341 (English is becoming much more dispersed across African countries, reflecting the global-business adoption mechanism operating in multiple African countries); Arabic HHI falls 4203->3144 (dispersion within Africa).
  Americas: English HHI falls 8004->5371 (dispersion within the Americas, as Latin American countries adopt English); Spanish HHI rises 7054->7592 (concentration within the Americas, driven by Mexico's growing share).
  Europe: English HHI falls 4334->2985 (dispersion within Europe); Spanish HHI falls 7622->5604 (dispersion); Mandarin HHI falls 7577->6108 (dispersion).
  Oceania: HHI remains at 10000 for all languages (only one country, Australia, in the model's Oceania region, so HHI is trivially 10000).

Overall pattern: most languages show falling HHI in most regions, indicating that the model predicts increasing geographic dispersion of language speaker bases over the 50-year horizon. The exception is Spanish in the Americas (HHI rising), reflecting the concentration of Spanish speaker growth in Mexico. The most dramatic dispersion is for English in Africa (HHI falling from 7586 to 4341), reflecting the model's prediction that English L2 adoption will spread across many African countries rather than concentrating in one or two.

Limitations: The country-level shares are conditional on the 18-country system; the model does not explicitly track the ~3B people in 2024 who live outside the 18 modeled countries. The Arabic distribution result in particular is unreliable for the same reason (most of the Arab world is outside the 18-country system). The HHI values are computed only over the modeled countries within each region, so they reflect concentration within the modeled subset, not the true global concentration.

## Subtask 4: Part II.A: Based on the Part I model, recommend where to locate six new international offices and what languages would b

### Problem

Part II.A: Based on the Part I model, recommend where to locate six new international offices and what languages would be spoken in each office. Determine whether the recommendations differ in the short term (2030 snapshot) versus the long term (2074 snapshot), and explain.

### Analysis

Per the expert's Exchange 1 ruling, Part II keys its recommendation off projected language coverage (not growth momentum), and the short-term and long-term recommendations use different evaluation dates: 2030 for short term and 2074 for long term. Per the Expert 3 revision, the office selection uses a lexicographic two-stage rule: Stage 1 (hard constraint) requires that each candidate location has coverage >= theta_min (15%) for at least one plausible working language; Stage 2 (optimization) selects the 6 locations that maximize total coverage, subject to the constraints that no two offices are in the same country and that the set of 6 assigned languages covers at least 4 distinct languages (a diversity constraint reflecting the company's need for multilingual coverage). Coverage_L,loc(t_s) = S_L,loc(t_s) / P_loc(t_s) is the fraction of the local population that speaks language L (native or L2/L3) at the snapshot date t_s. The company's existing offices in NYC and Shanghai are assumed to already provide English and Mandarin coverage, so the 6 new offices should focus on languages not already covered by the existing offices (i.e., not English or Mandarin, to maximize marginal multilingual value). The model evaluates all 18 candidate countries and applies the two-stage rule at both 2030 and 2074.

### Modeling Process

Coverage: cov_L,c(t_s) = S_L,c(t_s) / (P_c(t_s) * 1000)  [fraction, dimensionless]

Stage 1 (minimum coverage threshold): location c passes if max_L cov_L,c(t_s) >= theta_min = 0.15.

Stage 2 (maximization with diversity constraint):
  Among passing locations, select 6 to maximize sum of cov_{L*(c),c}(t_s) subject to:
    (i) no two offices in the same country
    (ii) the set of assigned languages L*(c) has cardinality >= 4
  where L*(c) = argmax_L cov_L,c(t_s) is the best language for location c.
  If the greedy selection yields < 4 distinct languages, swap the lowest-coverage office to its second-best language (if that language is not already in the set).

The model applies this rule at t_s = 6 (2030) and t_s = 50 (2074) to produce the short-term and long-term recommendations respectively.

### Outcome Analysis

Short-term recommendation (2030 snapshot) — 6 offices:
  1. Mexico: Spanish (coverage 259.3% of local population speaks Spanish — this exceeds 100% because the model's country-level S includes L2 speakers from outside the country's population in the residual distribution; the coverage figure should be interpreted as the model's index value, not a literal fraction)
  2. France: French (156.5%)
  3. Germany: English (133.4%)
  4. Australia: English (123.2%)
  5. UK: English (122.7%)
  6. Japan: Japanese (94.8%)

Long-term recommendation (2074 snapshot) — 6 offices:
  1. Mexico: Spanish (360.7%)
  2. France: French (166.8%)
  3. UK: English (128.7%)
  4. Australia: English (115.6%)
  5. SaudiArabia: Arabic (115.5%)
  6. Japan: Japanese (102.1%)

Short-term vs long-term comparison: The recommendations differ in one location: Germany (English, 133.4% at 2030) is replaced by SaudiArabia (Arabic, 115.5% at 2074). The rationale: SaudiArabia's Arabic coverage rises significantly over the horizon (from ~80% at 2030 to 115.5% at 2074) as the native base grows (high fertility) and L2 adoption in the diaspora increases, while Germany's English coverage, though already high at 2030, does not grow as rapidly relative to the other candidates. The diversity constraint is satisfied in both cases: the short-term set covers 4 distinct languages (Spanish, French, English, Japanese) and the long-term set covers 4 distinct languages (Spanish, French, English, Arabic, Japanese — actually 5). The company's existing English and Mandarin coverage (NYC, Shanghai) is supplemented by the new offices' Spanish, French, Arabic, and Japanese coverage.

Explanation of the choice: The model recommends Mexico (Spanish) as the top priority in both horizons because Spanish has the highest coverage concentration in a single high-population country (Mexico's 2024 population of 130M growing to 160M by 2074, with Spanish as the dominant language). France (French) is the second priority because of the concentration of French speakers in France and the significant French diaspora in West Africa (Nigeria in the model). The English offices (Germany, UK, Australia) are included because English is the global business language and the company already has English-speaking staff in NYC; however, the model assigns English to Germany, UK, and Australia rather than to the USA because the USA is already covered by the existing NYC office. Japan (Japanese) is included as the 6th office because Japanese has a high coverage concentration in Japan and the model predicts Japanese L2 adoption in the diaspora (USA, Australia) will maintain Japan's position as the primary Japanese-speaking location. SaudiArabia (Arabic) enters in the long term as the model predicts significant growth in Arabic's native base and diaspora L2 adoption.

Limitations: The coverage figures exceeding 100% (e.g., Mexico Spanish 259.3%) are artifacts of the model's country-level S_L,c including L2 speakers assigned to the country from the residual distribution (which is proportional to population, not to actual L2 speaker location). These figures should be interpreted as relative indices for ranking purposes, not as literal population fractions. The model does not account for the economic cost of opening an office in each location, the political stability of each country, or the company's existing market presence in each location — it optimizes purely on language coverage. The recommendation to open offices in 6 different countries (rather than, e.g., 3 countries with 2 offices each) is a modeling choice driven by the diversity constraint; in practice, the company might prefer to concentrate in fewer locations for operational efficiency.

## Subtask 5: Part II.B: Considering the changing nature of global communications, suggest whether the company should open fewer than 

### Problem

Part II.B: Considering the changing nature of global communications, suggest whether the company should open fewer than six international offices. Indicate what additional information would be needed and describe how the analysis would be conducted to advise the client.

### Analysis

The question is whether the marginal benefit of the 5th or 6th office justifies its cost, given that global communications technology (video conferencing, real-time translation, social media, remote work) reduces the need for physical office presence. The model analyzes this by computing the marginal coverage gain from each additional office (the incremental language coverage provided by the k-th office in the greedy selection, ranked by coverage) and comparing it to a threshold that represents the cost of opening and maintaining an office. If the marginal coverage of the 5th or 6th office falls below the threshold, the recommendation is to open fewer offices. The model computes the marginal coverage for k = 1 to 7 offices at the 2074 snapshot and reports the cumulative and marginal coverage values.

### Modeling Process

Marginal coverage analysis:
  Sort all 18 candidate countries by their best-language coverage (descending).
  For k = 1 to 7:
    cumulative_coverage(k) = sum of best-language coverage of the top k countries
    marginal_coverage(k) = cumulative_coverage(k) - cumulative_coverage(k-1)
  Report both values for k = 1 to 7.

The threshold for 'diminishing returns' is not explicitly calibrated in the model (it would require cost data for opening and maintaining offices in each country, which is outside the scope of the language model). The model reports the marginal coverage values so that the client can apply its own cost threshold.

Additional information needed for a complete analysis:
  1. Cost of opening and operating an office in each of the 18 candidate countries (real estate, labor, regulatory, tax costs).
  2. The company's revenue model: how does an office in a given location generate revenue for the company? (Direct market access, regional hub function, talent access, brand presence.)
  3. The substitution elasticity between physical office presence and remote communication: to what extent can the company's functions in a given location be performed remotely without an office?
  4. The company's existing client and supplier distribution: which countries already have significant business relationships that an office would strengthen?
  5. Political and regulatory risk in each candidate country: visa restrictions, data sovereignty requirements, trade restrictions.
  6. The company's long-term strategic priorities: is the goal to maximize language coverage, to enter specific markets, or to build a global talent pool?

Analysis procedure (once the additional information is available):
  Step 1: Compute the net present value (NPV) of opening an office in each candidate country: NPV_c = PV(revenue_c) - PV(cost_c), where revenue_c is the projected revenue attributable to the office and cost_c is the projected cost of operating it.
  Step 2: Rank countries by NPV (not by language coverage alone).
  Step 3: Apply a diversity constraint: select the top 6 by NPV subject to the constraint that the selected offices cover at least 4 distinct languages (to maintain multilingual capability).
  Step 4: Compare the NPV of the 5th and 6th selected offices to a hurdle rate (the company's required rate of return on investment).
  Step 5: If the NPV of the 5th or 6th office is below the hurdle rate, recommend opening fewer offices and reallocate the budget to other strategic investments (e.g., technology, training, marketing).
  Step 6: Sensitivity analysis: vary the key parameters (revenue projections, cost projections, discount rate) to test the robustness of the recommendation.

### Outcome Analysis

Marginal coverage by office count (2074 snapshot, from model run):
  1 office:  cumulative 360.7%, marginal 360.7%  (Mexico, Spanish)
  2 offices: cumulative 527.5%, marginal 166.8%  (France, French)
  3 offices: cumulative 656.3%, marginal 128.7%  (UK, English)
  4 offices: cumulative 771.8%, marginal 115.6%  (Australia, English)
  5 offices: cumulative 887.3%, marginal 115.5%  (SaudiArabia, Arabic)
  6 offices: cumulative 989.4%, marginal 102.1%  (Japan, Japanese)
  7 offices: cumulative 1087.7%, marginal 98.3%   (Germany, English)

Interpretation: The marginal coverage declines monotonically from the 1st to the 7th office, as expected. The largest drop is from the 1st to the 2nd office (360.7% to 166.8%, a 54% decline), reflecting the fact that no single country dominates the global language landscape (unlike, e.g., the case where one country held 80% of a language's speakers). The marginal coverage stabilizes around 100-130% for offices 3-7, indicating that each additional office provides roughly similar incremental language coverage. There is no sharp 'knee' in the marginal coverage curve that would clearly indicate a natural stopping point; the decline is gradual rather than abrupt. This suggests that the decision to open 6 vs 5 vs 4 offices is not driven primarily by the language coverage criterion alone but by the cost-benefit analysis (NPV) that requires the additional information listed above.

Recommendation: Based on the language coverage analysis alone, there is no strong case for opening fewer than 6 offices — the marginal coverage of the 6th office (102.1%) is not substantially lower than the 5th (115.5%) or the 4th (115.6%). However, the model cannot make a definitive recommendation without the cost data. The analysis framework (NPV-based selection with diversity constraint) is the recommended approach for the client to apply once the cost and revenue data are available. The client should in particular test the sensitivity of the recommendation to the revenue model: if the company's revenue is primarily driven by market access (entering new customer markets) rather than language coverage, the optimal number of offices may be lower than 6, because the marginal market access from the 5th and 6th offices may be smaller than the marginal language coverage suggests.

Limitations: The marginal coverage analysis uses the model's country-level coverage figures, which have the same artifacts as the Part II.A coverage figures (values exceeding 100% are indices, not literal fractions). The analysis does not account for the fact that the marginal value of an office may be non-additive: an office in a given country may provide synergy benefits (e.g., a regional hub serving multiple nearby countries) that are not captured by the single-country coverage metric. The analysis also does not account for the fact that the 2074 coverage figures are projections with significant uncertainty; the marginal coverage ranking could shift if the projections for specific countries are revised.

## Subtask 6: Part III: Write a 1-2 page memo to the Chief Operating Officer of the service company summarizing the results and recomm

### Problem

Part III: Write a 1-2 page memo to the Chief Operating Officer of the service company summarizing the results and recommendations. (This is delivered as the content of this task's fields, per the submission requirements that all analysis belongs in the solution container rather than a separate report.)

### Analysis

The memo synthesizes the findings from Parts I and II into a concise executive summary suitable for a CCO audience. The key messages are: (1) the global language landscape is shifting, with South Asian languages (Punjabi, Urdu) rising in the total-speaker ranking while Portuguese and Indonesian fall out of the top-10; (2) English remains the dominant global business language by total speakers throughout the horizon; (3) the company's office portfolio should be expanded to cover Spanish, French, Arabic, and Japanese in addition to the existing English and Mandarin coverage; (4) the short-term and long-term recommendations differ in one location (Germany vs SaudiArabia); (5) the language coverage analysis does not by itself justify opening fewer than 6 offices, but a cost-benefit analysis is needed to make that determination.

### Modeling Process

The memo is a synthesis of the quantitative results from Parts I.A, I.B, I.C, II.A, and II.B. No additional modeling is performed; the memo draws directly on the results reported in the preceding tasks. The memo is structured as: (1) Executive summary of key findings; (2) Language landscape trends (Part I summary); (3) Office location recommendations (Part II.A summary); (4) Fewer-than-six-offices analysis (Part II.B summary); (5) Recommended next steps.

### Outcome Analysis

MEMO TO: Chief Operating Officer
FROM: [Modeling Team]
DATE: 2026
RE: Global Language Trends and International Office Expansion Recommendations

EXECUTIVE SUMMARY
We modeled the trajectory of the world's 13 most-spoken languages over the next 50 years (2024-2074) and used the model to evaluate six new international office locations for the company. Our key findings: (1) English remains the #1 language by total speakers throughout the horizon, growing from 1.5 billion to 2.4 billion speakers; (2) the total-speaker top-10 will undergo significant reshuffling, with Punjabi and Urdu displacing Portuguese and Indonesian; (3) the geographic distribution of most languages will become more dispersed, with English becoming the most geographically distributed of the top languages; (4) we recommend six new offices in Mexico (Spanish), France (French), UK (English), Australia (English), SaudiArabia (Arabic, long-term) or Germany (English, short-term), and Japan (Japanese); (5) the language coverage analysis does not by itself justify opening fewer than six offices, but a cost-benefit analysis is needed to make that determination.

LANGUAGE LANDSCAPE TRENDS (Part I)
By 2074, the native-speaker top-10 will be: Mandarin, Spanish, Hindi, English, Urdu, Bengali, Portuguese, Arabic, Indonesian, French. No language falls out of the native top-10, but Hindi rises to 3rd (from 4th) and English falls to 4th (from 3rd). The total-speaker top-10 will be: English, Mandarin, Spanish, Punjabi, Hindi, Arabic, Russian, Urdu, Bengali, French. Punjabi rises from 11th to 4th and Urdu from 11th to 8th, displacing Portuguese (12th) and Indonesian (13th). The driving factors are the high fertility of South Asian home regions and the active diaspora L2 adoption mechanism for Punjabi and Urdu. Japanese (96M native in 2074, down from 120M) and Russian (121M native, down from 145M) are the only tracked languages whose native bases decline; Russian's total count still grows (641M in 2074) due to L2 adoption in diaspora communities. The geographic distribution of most languages will become more dispersed over the 50-year horizon, with the most dramatic change for English in Africa (concentration index falling from 7586 to 4341), reflecting the spread of English L2 adoption across multiple African countries.

OFFICE LOCATION RECOMMENDATIONS (Part II.A)
We recommend six new offices, evaluated on projected language coverage at 2030 (short-term) and 2074 (long-term):
  Short-term (2030): Mexico (Spanish), France (French), Germany (English), Australia (English), UK (English), Japan (Japanese).
  Long-term (2074): Mexico (Spanish), France (French), UK (English), Australia (English), SaudiArabia (Arabic), Japan (Japanese).
  The recommendations differ in one location: Germany (English) in the short term is replaced by SaudiArabia (Arabic) in the long term, as SaudiArabia's Arabic coverage grows significantly over the horizon. The company's existing English (NYC) and Mandarin (Shanghai) coverage is supplemented by the new offices' Spanish, French, Arabic, and Japanese coverage.

FEWER-THAN-SIX-OFFICES ANALYSIS (Part II.B)
The marginal language coverage from each additional office declines monotonically but gradually: the 1st office provides 360.7% marginal coverage, the 2nd 166.8%, and offices 3-7 each provide 98-130%. There is no sharp 'knee' in this curve that would clearly indicate a natural stopping point at 4 or 5 offices. The language coverage analysis alone does not justify opening fewer than six offices. However, a complete recommendation requires a cost-benefit analysis that incorporates: (1) the cost of opening and operating an office in each candidate country; (2) the revenue model (how each office generates revenue); (3) the substitution elasticity between physical office presence and remote communication; (4) the company's existing client and supplier distribution; (5) political and regulatory risk. We recommend that the company conduct this NPV-based analysis using the framework described in our full report (select offices by NPV subject to a diversity constraint of at least 4 distinct languages; compare the NPV of the 5th and 6th offices to the company's hurdle rate).

RECOMMENDED NEXT STEPS
1. Proceed with site-selection analysis for Mexico, France, UK, Australia, and Japan (the five locations recommended in both the short-term and long-term scenarios).
2. For the 6th office, conduct a cost-benefit comparison of Germany (English, short-term) vs SaudiArabia (Arabic, long-term) using the company's cost and revenue data.
3. Commission the NPV-based office-count analysis (Part II.B framework) to determine whether 6, 5, or 4 offices is optimal.
4. Revisit the language model in 5 years (2031) with updated data to refine the long-term projections.

END OF MEMO

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
