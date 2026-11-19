"""
Step 1 - Clean the SCE Household Finance microdata and build a Tableau-ready file.

Input : data/raw/SCE_Household_Finance_2014_2019.xlsx   (sheet "Data", 6,809 rows x 397 cols)
Output: data/processed/sce_household_finance_clean.csv  (one row per respondent, readable labels)

Run from the repository root:  python src/01_clean_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "SCE_Household_Finance_2014_2019.xlsx"
OUT = ROOT / "data" / "processed" / "sce_household_finance_clean.csv"

raw = pd.read_excel(RAW, sheet_name="Data")
df = pd.DataFrame({
    "userid": raw["userid"],
    "survey_year": raw["date"] // 100,          # waves are fielded each August (YYYY08)
    "weight": raw["quarterly_weights"],          # FRBNY survey weight
})

# ---------- Income ----------
inc = raw["b1_1"].where(raw["b1_1"].between(0, 5_000_000))   # drop implausible entries (> $5M)
df["hh_income"] = inc
df["income_group"] = pd.cut(
    inc, [-1, 34_999, 59_999, 99_999, 149_999, np.inf],
    labels=["1. Under $35k", "2. $35k-$60k", "3. $60k-$100k", "4. $100k-$150k", "5. $150k+"],
)

# ---------- Saving behaviour (last 12 months) ----------
# d2: 1 Added more, 2 Withdrew more, 3 Added as much as withdrew, 4 No savings account.
# Code 5 appears only in 2018-19 and is not documented in the codebook -> treated as missing.
d2_map = {1: "Added more than withdrew", 2: "Withdrew more than added",
          3: "Added as much as withdrew", 4: "No savings/investment account"}
df["saving_behavior"] = raw["d2"].map(d2_map)
df["net_saver"] = raw["d2"].map({1: 1, 2: 0, 3: 0, 4: 0})
df["net_dissaver"] = raw["d2"].map({1: 0, 2: 1, 3: 0, 4: 0})
df["no_savings_account"] = raw["d2"].map({1: 0, 2: 0, 3: 0, 4: 1})

# ---------- Balances ----------
cap = lambda s, hi: s.where(s.between(0, hi))
df["liquid_savings"] = cap(raw["d16new_1"], 50_000_000)      # savings/investments excl. retirement
df["dc_retirement_balance"] = cap(raw["c2new_1"], 50_000_000)
df["ira_balance"] = cap(raw["c2newx1_1"], 50_000_000)
# Total financial assets: liquid + DC + IRA. Blank retirement balances are treated as $0
# (most blanks are respondents without those accounts). Only defined where liquid savings is known.
df["total_fin_assets"] = np.where(
    df["liquid_savings"].notna(),
    df[["liquid_savings", "dc_retirement_balance", "ira_balance"]].fillna(0).sum(axis=1),
    np.nan,
)
df["savings_tier"] = pd.cut(
    df["total_fin_assets"], [-1, 9_999, 49_999, 249_999, 999_999, np.inf],
    labels=["1. Under $10k", "2. $10k-$50k", "3. $50k-$250k", "4. $250k-$1M", "5. $1M+"],
)

# ---------- Debt ----------
df["non_housing_debt"] = cap(raw["g1_1"], 5_000_000)
df["has_non_housing_debt"] = (df["non_housing_debt"] > 0).astype(float).where(df["non_housing_debt"].notna())
for col, name in [("g1a_1", "pct_credit_card"), ("g1a_2", "pct_auto"), ("g1a_3", "pct_student"),
                  ("g1a_4", "pct_other_loans"), ("g1a_5", "pct_medical"), ("g1a_6", "pct_legal")]:
    df[name] = raw[col]
    # dollar amount of each debt type = share x total non-housing debt
    df[name.replace("pct_", "amt_")] = raw[col] / 100 * df["non_housing_debt"]

# Housing debt: f1 owns home; f17 has loans against home; f18new_1 amount outstanding.
own = raw["f1"] == 1
df["homeowner"] = raw["f1"].map({1: 1, 2: 0})
hd = pd.Series(np.nan, index=raw.index)
hd[own & (raw["f17"] == 2)] = 0
hd[own & (raw["f17"] == 1)] = cap(raw["f18new_1"], 10_000_000)
df["housing_debt"] = hd
tier = pd.cut(hd, [-1, 0, 99_999, 249_999, np.inf],
              labels=["2. Owner, no mortgage", "3. Mortgage under $100k",
                      "4. Mortgage $100k-$250k", "5. Mortgage $250k+"]).astype(object)
tier[raw["f1"] == 2] = "1. Renter"
df["housing_debt_tier"] = tier

# ---------- Credit & distress ----------
df["credit_rating"] = raw["h10a"].map({1: "1. Below 620", 2: "2. 620-679", 3: "3. 680-719",
                                       4: "4. 720-760", 5: "5. Above 760", 6: "6. Don't know"})
df["pct_chance_bankruptcy_12m"] = raw["h8_1"].where(raw["h8_1"].between(0, 100))
df["considered_bankruptcy_12m"] = raw["h7new"].map({1: 1, 2: 0})
df["late_3mo_housing_12m"] = raw["f20new"].map({1: 1, 2: 0})
df["pct_chance_can_raise_2k"] = raw["k2_1"].where(raw["k2_1"].between(0, 100))
df["source_of_2k"] = raw["k2b"].map({1: "Own savings", 2: "Borrow from bank/credit card",
                                     3: "Borrow from family/friends", 4: "Payday lender/pawn shop",
                                     5: "Borrow from employer"})

# ---------- Shocks ----------
df["large_income_drop"] = np.where(raw["c3new"] == 2, 0,
                          np.where(raw["c3new1"] == 2, 1, np.where(raw["c3new1"] == 1, 0, np.nan)))
df.loc[raw["c3new"].isna(), "large_income_drop"] = np.nan
hlth = raw["c3new3a"]
df["health_shock"] = np.where(raw["c3new3"] == 2, 0,
                     np.where(hlth.isin([3, 4]), 1, np.where(hlth.isin([1, 2, 5]), 0, np.nan)))
df.loc[raw["c3new3"].isna(), "health_shock"] = np.nan
df["shock_group"] = np.select(
    [(df["large_income_drop"] == 1) & (df["health_shock"] == 1),
     df["large_income_drop"] == 1, df["health_shock"] == 1,
     (df["large_income_drop"] == 0) & (df["health_shock"] == 0)],
    ["Both shocks", "Large income drop", "Health deterioration", "No shock"], default=None)
df["withdrew_due_to_health"] = raw["d5_10"].map({1: 1, 2: 1, 3: 0, 4: 0})   # very/somewhat important

# ---------- Retirement ----------
df["retired"] = raw["i1_7"]
pra = raw["i17_1"].where(raw["i17_1"].between(40, 90))
df["planned_retirement_age"] = pra.where(raw["i1_7"] == 0)    # only people not yet retired
df["years_savings_will_last"] = raw["d24_1"].where(raw["d24_1"].between(0, 60)).where(raw["i1_7"] == 0)
df["expected_savings_at_retirement"] = cap(raw["d23_1"], 50_000_000)
df["savings_adequacy"] = raw["d25"].map({1: "Too little", 2: "Too much", 3: "About right"})

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"Wrote {OUT.relative_to(ROOT)}: {df.shape[0]:,} rows x {df.shape[1]} columns")
