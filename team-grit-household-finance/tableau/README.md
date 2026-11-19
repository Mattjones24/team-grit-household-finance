# Tableau

`Team_Grit_SCE_Household_Finance.twb` contains 8 worksheets and 3 dashboards (one per research question), all built on the cleaned CSV with survey-weighted calculated fields.

**To open it:** double-click the .twb. If Tableau can't find the data, click *Edit Connection* and point it to `data/processed/sce_household_finance_clean.csv` in this repo. Then use **File → Export Packaged Workbook** to save a `.twbx` (which bundles the data) here, and **Dashboard → Export Image** to add PNG screenshots of each dashboard.

Data source for every sheet: `../data/processed/sce_household_finance_clean.csv`

Suggested dashboards (each mirrors a chart in `../figures/`):

| Dashboard | Rows / Columns | Color / Filter |
|---|---|---|
| RQ1 Saving by income | `income_group` × weighted share of `saving_behavior` | Filter: `shock_group`, `survey_year` |
| RQ1 Shocks | `income_group` × weighted avg `net_saver` | Color: `shock_group` |
| RQ2 Debt mix | `housing_debt_tier` × weighted avg `amt_credit_card`, `amt_auto`, `amt_student`, `amt_medical` | Filter: `non_housing_debt > 0` |
| RQ2 Credit & distress | `credit_rating` × weighted avg `pct_chance_bankruptcy_12m` | Tooltip: `pct_chance_can_raise_2k` |
| RQ3 Retirement | `savings_tier` / `income_group` × weighted avg `planned_retirement_age`, `years_savings_will_last` | Filter: `retired = 0` |

Weighted average calculated field, e.g.:
`SUM([net_saver] * [weight]) / SUM(IIF(ISNULL([net_saver]), 0, [weight]))`
