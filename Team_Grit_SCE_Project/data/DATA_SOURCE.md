# Data Source & Access

## Dataset

**Survey of Consumer Expectations (SCE) — Household Finance (Housing/Household Spending & Finance) microdata**
Published by the **Federal Reserve Bank of New York (FRBNY)**, Center for Microeconomic Data.

- Landing page: <https://www.newyorkfed.org/microeconomics/sce>
- The SCE is a monthly, nationally representative internet survey of about 1,300 U.S. household heads. The Household Finance module is fielded **once a year in August**.
- The file in this repo covers the **2014–2019 August waves**: 6,809 responses and 397 variables.

## How to download it yourself

1. Go to <https://www.newyorkfed.org/microeconomics/sce> and open the **Data** / **Microdata** section for the SCE.
2. Download the household finance microdata workbook (Excel). It contains the sheets `Disclaimer`, `License`, `Notes`, `Data` and `Codebook`.
3. Save it as `data/raw/SCE_Household_Finance_2014_2019.xlsx` and run `python src/01_clean_data.py`.

A copy of the exact workbook we used is already in `data/raw/`, so no download is needed to reproduce the results.

## Files in this folder

| File | What it is |
|---|---|
| `raw/SCE_Household_Finance_2014_2019.xlsx` | Original FRBNY workbook, unchanged |
| `codebook.csv` | `Codebook` sheet exported to CSV: variable name, label, answer label, answer code |
| `processed/sce_household_finance_clean.csv` | One row per respondent, 46 analysis columns with readable labels. Built by `src/01_clean_data.py` |

## Key variables used

| Concept | Raw variable(s) | Clean column |
|---|---|---|
| Survey wave | `date` (YYYY08) | `survey_year` |
| Survey weight | `quarterly_weights` | `weight` |
| Household income | `b1_1` | `hh_income`, `income_group` |
| Saving vs. withdrawing (last 12m) | `d2` | `saving_behavior`, `net_saver`, `net_dissaver`, `no_savings_account` |
| Liquid savings / 401k(DC) / IRA | `d16new_1`, `c2new_1`, `c2newx1_1` | `liquid_savings`, `dc_retirement_balance`, `ira_balance`, `total_fin_assets`, `savings_tier` |
| Non-housing debt and mix | `g1_1`, `g1a_1`…`g1a_6` | `non_housing_debt`, `pct_*`, `amt_*` |
| Housing debt | `f1`, `f17`, `f18new_1` | `homeowner`, `housing_debt`, `housing_debt_tier` |
| Self-rated credit | `h10a` | `credit_rating` |
| Expected / actual distress | `h8_1`, `h7new`, `f20new`, `k2_1`, `k2b` | `pct_chance_bankruptcy_12m`, `considered_bankruptcy_12m`, `late_3mo_housing_12m`, `pct_chance_can_raise_2k`, `source_of_2k` |
| Income shock | `c3new`, `c3new1` | `large_income_drop` |
| Health shock | `c3new3`, `c3new3a`, `d5_10` | `health_shock`, `withdrew_due_to_health` |
| Retirement plans | `i1_7`, `i17_1`, `d24_1`, `d23_1`, `d25` | `retired`, `planned_retirement_age`, `years_savings_will_last`, `expected_savings_at_retirement`, `savings_adequacy` |

## Cleaning rules

- Income above $5M, balances above $50M and debt above $5M are treated as entry errors and set to missing.
- Planned retirement age is kept only for values 40–90 and only for respondents not yet retired. "Years savings will last" is kept for values 0–60.
- `d2 = 5` appears only in 2018–19 and is not defined in the codebook, so it is set to missing.
- Blank 401(k)/IRA balances count as $0 in `total_fin_assets`, which is defined only when liquid savings is reported.

## License & attribution

The SCE data may be used subject to the license in the workbook's `License` sheet and on the FRBNY site. Any publication must carry this notice:

> Source: Survey of Consumer Expectations, © 2013–2019 Federal Reserve Bank of New York (FRBNY). The SCE data are available without charge at http://www.newyorkfed.org/microeconomics/sce and may be used subject to license terms posted there. FRBNY disclaims any responsibility or legal liability for this analysis and interpretation of Survey of Consumer Expectations data.
