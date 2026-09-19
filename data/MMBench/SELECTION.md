# MM-Bench subset used by the interaction-workflow evolution experiment

Copied from `LLM-MM-Agent/MMBench`. The full benchmark is 804 MB; this
subset is 41.0 MB because the experiment only ever runs the
train and validation splits. The 32 test-split tasks (2021-2025) account for
794 MB of the original and are excluded here.

- `problem/` — all 111 problem statements (JSON)
- `evaluation/` — the native MM-Bench evaluator
- `dataset/` — datasets for the 8 train/validation tasks that ship one;
  the remaining train/validation tasks declare no dataset.

## Train split (30)

2014_C, 2015_A, 2015_B, 2015_C, 2015_D, 2016_A, 2016_B, 2016_C, 2016_D, 2016_E, 2016_F, 2017_A, 2017_B, 2017_C, 2017_D, 2017_E, 2017_F, 2018_A, 2018_B, 2018_C, 2018_D, 2018_E, 2018_F, 2019_A, 2019_B, 2019_C, 2019_D, 2019_E, 2019_F, 2020_A

## Validation split (5)

2020_B, 2020_C, 2020_D, 2020_E, 2020_F

## Test split (excluded — 32 tasks, 794 MB)

2021_A, 2021_B, 2021_C, 2021_D, 2021_E, 2021_F, 2022_A, 2022_B, 2022_C, 2022_D, 2022_E, 2022_F, 2023_A, 2023_B, 2023_C, 2023_D, 2023_E, 2023_F, 2023_Y, 2023_Z, 2024_A, 2024_B, 2024_C, 2024_D, 2024_E, 2024_F, 2025_A, 2025_B, 2025_C, 2025_D, 2025_E, 2025_F
