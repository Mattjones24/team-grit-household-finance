"""
Step 2 - Weighted analysis and annotated charts for the three research questions.

Input : data/processed/sce_household_finance_clean.csv  (from 01_clean_data.py)
Output: outputs/*.csv  (summary tables)   figures/*.png  (charts)

All shares and means use the FRBNY survey weight (`weight`), so results describe
U.S. household heads rather than just the people who answered. Medians are weighted medians.

Run from the repository root:  python src/02_analysis_and_charts.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
FIG, OUT = ROOT / "figures", ROOT / "outputs"
FIG.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
d = pd.read_csv(ROOT / "data" / "processed" / "sce_household_finance_clean.csv")

# ---------------- helpers ----------------
def wmean(g, c):
    g = g[g[c].notna()]
    return np.average(g[c], weights=g["weight"]) if len(g) else np.nan

def wmedian(g, c):
    g = g[g[c].notna()].sort_values(c)
    if not len(g):
        return np.nan
    cw = g["weight"].cumsum()
    return g[c].iloc[int((cw >= cw.iloc[-1] / 2).argmax())]

def wshare(g, c, value):
    g = g[g[c].notna()]
    return np.average((g[c] == value).astype(float), weights=g["weight"]) if len(g) else np.nan

def save_table(df, name):
    df.round(4).to_csv(OUT / name)

# ---------------- style ----------------
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
NEUTRAL, DARKNEUTRAL = "#b9b8b2", "#52514e"
import os
SLIDES = os.environ.get("SLIDES") == "1"   # SLIDES=1 -> title-free charts for the deck
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
SURFACE = "#ffffff" if SLIDES else "#fcfcfb"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "figure.facecolor": SURFACE, "text.parse_math": False, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})
SOURCE = ("Source: Survey of Consumer Expectations, © 2013-2019 Federal Reserve Bank of New York (FRBNY). "
          "SCE Household Finance survey, 2014-2019 waves; weighted.")
money = FuncFormatter(lambda x, _: f"${x/1000:,.0f}k" if x < 1e6 else f"${x/1e6:,.1f}M")

def finish(fig, title, subtitle, fname):
    if SLIDES:
        (FIG / "slides").mkdir(exist_ok=True)
        fig.savefig(FIG / "slides" / fname, dpi=200, bbox_inches="tight", pad_inches=0.15)
        plt.close(fig)
        return
    fig.suptitle(title, x=0.01, y=0.995, ha="left", fontsize=14, fontweight="bold", color=INK)
    fig.text(0.01, 0.935, subtitle, ha="left", fontsize=10, color=INK2)
    fig.text(0.01, -0.03, SOURCE, ha="left", fontsize=7.5, color=MUTED)
    fig.savefig(FIG / fname, dpi=200, bbox_inches="tight")
    plt.close(fig)

def short(labels):  # "3. $60k-$100k" -> "$60k-$100k"
    return [str(l).split(". ", 1)[-1] for l in labels]

# =====================================================================
# RQ1 - income, saving vs debt, and shocks
# =====================================================================
inc_order = sorted(d["income_group"].dropna().unique())
rq1 = d.groupby("income_group").apply(lambda g: pd.Series({
    "respondents": len(g),
    "pct_added_more": wshare(g, "saving_behavior", "Added more than withdrew"),
    "pct_added_equal": wshare(g, "saving_behavior", "Added as much as withdrew"),
    "pct_withdrew_more": wshare(g, "saving_behavior", "Withdrew more than added"),
    "pct_no_account": wshare(g, "saving_behavior", "No savings/investment account"),
    "pct_with_non_housing_debt": wmean(g, "has_non_housing_debt"),
    "median_non_housing_debt": wmedian(g, "non_housing_debt"),
    "median_liquid_savings": wmedian(g, "liquid_savings"),
    "mean_pct_chance_can_raise_2k": wmean(g, "pct_chance_can_raise_2k"),
    "pct_would_use_own_savings_for_2k": wshare(g, "source_of_2k", "Own savings"),
})).loc[inc_order]
save_table(rq1, "rq1_income_saving_debt.csv")

# Figure 1: saving behaviour by income (100% stacked bars)
fig, ax = plt.subplots(figsize=(10, 5.2))
segs = [("pct_added_more", "Added more than withdrew", BLUE, "white"),
        ("pct_added_equal", "Added as much as withdrew", NEUTRAL, INK),
        ("pct_withdrew_more", "Withdrew more than added", ORANGE, "white"),
        ("pct_no_account", "No savings account", DARKNEUTRAL, "white")]
y = np.arange(len(rq1))[::-1]
left = np.zeros(len(rq1))
for col, lab, colr, txt in segs:
    vals = rq1[col].values
    ax.barh(y, vals, left=left, color=colr, height=0.62, label=lab, edgecolor=SURFACE, linewidth=2)
    for yi, l, v in zip(y, left, vals):
        if v >= 0.06:
            ax.text(l + v / 2, yi, f"{v:.0%}", ha="center", va="center", color=txt, fontsize=9.5, fontweight="bold")
    left += vals
ax.set_yticks(y, short(rq1.index)); ax.set_xlim(0, 1)
ax.xaxis.set_major_formatter(PercentFormatter(1.0)); ax.grid(axis="y", visible=False)
ax.set_xlabel("Share of household heads, last 12 months")
ax.legend(ncol=4, loc="upper left", bbox_to_anchor=(0, 1.1), frameon=False, fontsize=9, handlelength=1.2)
lo, hi = rq1["pct_added_more"].iloc[0], rq1["pct_added_more"].iloc[-1]
lo_na, hi_na = rq1["pct_no_account"].iloc[0], rq1["pct_no_account"].iloc[-1]
fig.subplots_adjust(top=0.80)
finish(fig, "Higher income turns households into net savers",
       f"Net savers rise from {lo:.0%} to {hi:.0%} as income climbs. {lo_na:.0%} of the lowest-income group has no savings account, vs {hi_na:.0%} of the highest.",
       "fig1_saving_behavior_by_income.png")

# Shocks
d["any_shock"] = np.where(d["shock_group"].isin(["Large income drop", "Health deterioration", "Both shocks"]), 1,
                 np.where(d["shock_group"] == "No shock", 0, np.nan))
shock_order = ["No shock", "Large income drop", "Health deterioration", "Both shocks"]
rq1s = d.groupby("shock_group").apply(lambda g: pd.Series({
    "respondents": len(g),
    "pct_added_more": wshare(g, "saving_behavior", "Added more than withdrew"),
    "pct_withdrew_more": wshare(g, "saving_behavior", "Withdrew more than added"),
    "mean_pct_chance_can_raise_2k": wmean(g, "pct_chance_can_raise_2k"),
    "mean_pct_chance_bankruptcy_12m": wmean(g, "pct_chance_bankruptcy_12m"),
})).loc[shock_order]
save_table(rq1s, "rq1_shocks.csv")
rq1si = d[d["any_shock"].notna()].groupby(["income_group", "any_shock"]).apply(lambda g: pd.Series({
    "respondents": len(g), "pct_added_more": wshare(g, "saving_behavior", "Added more than withdrew"),
    "pct_withdrew_more": wshare(g, "saving_behavior", "Withdrew more than added")})).unstack()
save_table(rq1si, "rq1_shocks_by_income.csv")
health_reason = d[d["withdrew_due_to_health"].notna()].groupby("health_shock").apply(
    lambda g: pd.Series({"respondents": len(g), "pct_citing_health": wmean(g, "withdrew_due_to_health")}))
save_table(health_reason, "rq1_withdrawals_citing_health.csv")

# Figure 2: shocks (two panels)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5), gridspec_kw={"width_ratios": [1.35, 1]})
x = np.arange(len(inc_order))
s0 = rq1si[("pct_added_more", 0.0)].values; s1 = rq1si[("pct_added_more", 1.0)].values
a1.plot(x, s0, color=BLUE, lw=2, marker="o", ms=8, mec=SURFACE, mew=2)
a1.plot(x, s1, color=ORANGE, lw=2, marker="o", ms=8, mec=SURFACE, mew=2)
a1.text(x[-1] + 0.12, s0[-1], "No shock", color=INK, va="center", fontsize=9.5, fontweight="bold")
a1.text(x[-1] + 0.12, s1[-1], "Income drop or\nhealth decline", color=INK, va="center", fontsize=9.5, fontweight="bold")
for xi, a, b in zip(x, s0, s1):
    a1.text(xi, a + 0.035, f"{a:.0%}", ha="center", fontsize=8.5, color=INK2)
    a1.text(xi, b - 0.065, f"{b:.0%}", ha="center", fontsize=8.5, color=INK2)
a1.set_xticks(x, [l.replace("-", "-\n") for l in short(inc_order)], fontsize=8.5); a1.set_xlim(-0.3, len(x) - 0.3 + 0.9)
a1.set_ylim(0, 0.8); a1.yaxis.set_major_formatter(PercentFormatter(1.0))
a1.set_ylabel("Share who added more to savings than withdrew"); a1.grid(axis="x", visible=False)
a1.set_title("A shock cuts the saving rate at every income level", loc="left", fontsize=10.5, color=INK, fontweight="bold")
a1.legend(handles=[plt.Line2D([], [], color=BLUE, marker="o", lw=2, label="No shock"),
                   plt.Line2D([], [], color=ORANGE, marker="o", lw=2, label="Income drop or health decline")],
          loc="upper left", frameon=False, fontsize=8.5)
hr = health_reason["pct_citing_health"]
a2.bar([0, 1], [hr.loc[0.0], hr.loc[1.0]], color=[BLUE, ORANGE], width=0.55, edgecolor=SURFACE, linewidth=2)
for i, v in enumerate([hr.loc[0.0], hr.loc[1.0]]):
    a2.text(i, v + 0.02, f"{v:.0%}", ha="center", fontsize=12, fontweight="bold", color=INK)
a2.set_xticks([0, 1], ["No health decline", "Health declined"]); a2.set_ylim(0, 0.95)
a2.yaxis.set_major_formatter(PercentFormatter(1.0)); a2.grid(axis="x", visible=False)
a2.set_ylabel("Share of withdrawers citing health as a reason")
a2.set_title("Health problems drive withdrawals", loc="left", fontsize=10.5, color=INK, fontweight="bold")
n_h = int(health_reason.loc[1.0, "respondents"]); n_nh = int(health_reason.loc[0.0, "respondents"])
a2.text(0.5, 0.97, f"Base: households that withdrew from savings\n(n = {n_nh:,} and {n_h:,})",
        transform=a2.transAxes, ha="center", va="top", fontsize=8, color=MUTED)
fig.subplots_adjust(top=0.80, wspace=0.3)
finish(fig, "Unexpected shocks erase much of the income advantage",
       "Shock = large income drop or a large short-term/permanent deterioration in health in the past 12 months.",
       "fig2_shocks_saving.png")

# =====================================================================
# RQ2 - housing debt vs other debt; credit perception vs distress
# =====================================================================
tier_order = sorted(d["housing_debt_tier"].dropna().unique())
debtors = d[d["non_housing_debt"] > 0]
rq2 = d.groupby("housing_debt_tier").apply(lambda g: pd.Series({
    "respondents": len(g),
    "median_household_income": wmedian(g, "hh_income"),
    "median_housing_debt": wmedian(g, "housing_debt"),
    "pct_with_non_housing_debt": wmean(g, "has_non_housing_debt"),
    "median_non_housing_debt_all": wmedian(g, "non_housing_debt"),
})).loc[tier_order]
types = [("amt_credit_card", "Credit cards", BLUE), ("amt_auto", "Auto loans", ORANGE),
         ("amt_student", "Student loans", AQUA), ("amt_medical", "Medical bills", YELLOW),
         ("amt_other", "Other & legal", MAGENTA)]
debtors = debtors.assign(amt_other=debtors["amt_other_loans"].fillna(0) + debtors["amt_legal"].fillna(0))
comp = debtors[debtors["pct_credit_card"].notna()].groupby("housing_debt_tier").apply(
    lambda g: pd.Series({c: wmean(g, c) for c, _, _ in types} | {"debtors_with_breakdown": len(g),
                        "median_non_housing_debt_debtors": wmedian(g, "non_housing_debt")})).loc[tier_order]
rq2 = rq2.join(comp)
rq2["debt_to_income_non_housing"] = rq2["median_non_housing_debt_debtors"] / rq2["median_household_income"]
save_table(rq2, "rq2_housing_vs_other_debt.csv")
mort = d[d["housing_debt"] > 0]
corr = mort[["housing_debt", "non_housing_debt", "hh_income"]].corr("spearman")
save_table(corr, "rq2_spearman_mortgage_holders.csv")

# Figure 3: average non-housing debt composition by housing-debt tier
fig, ax = plt.subplots(figsize=(10.5, 5.4))
xs = np.arange(len(tier_order)); bottom = np.zeros(len(tier_order))
for c, lab, colr in types:
    vals = rq2[c].values
    ax.bar(xs, vals, bottom=bottom, color=colr, width=0.6, label=lab, edgecolor=SURFACE, linewidth=2)
    bottom += vals
for xi, tot, med in zip(xs, bottom, rq2["median_non_housing_debt_debtors"]):
    ax.text(xi, tot + 1200, f"${tot/1000:,.0f}k avg", ha="center", fontsize=9.5, fontweight="bold", color=INK)
    ax.text(xi, tot + 4800, f"median ${med/1000:,.0f}k", ha="center", fontsize=8, color=INK2)
ax.set_xticks(xs, short(tier_order), fontsize=9); ax.yaxis.set_major_formatter(money)
ax.set_ylabel("Average non-housing debt per indebted household"); ax.grid(axis="x", visible=False)
ax.set_ylim(0, bottom.max() * 1.22)
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], loc="upper left", frameon=False, fontsize=9, title="Debt type", title_fontsize=9)
r = corr.loc["housing_debt", "non_housing_debt"]
ax.text(0.56, 0.97, f"Among mortgage holders, mortgage size and other debt\nare barely related (Spearman ρ = {r:.2f}).\n"
        "Bigger mortgages add auto and card debt in dollars,\nbut not as a share of income.",
        transform=ax.transAxes, ha="center", va="top", fontsize=8.5, color=INK2)
fig.subplots_adjust(top=0.84)
finish(fig, "Large mortgages come with more consumer debt, not less",
       "Average debt by type among households with any non-housing debt, grouped by what they owe on their home.",
       "fig3_housing_vs_other_debt.png")

# Credit perception vs expected distress
cred_order = sorted(d["credit_rating"].dropna().unique())
d["any_bankruptcy_chance"] = (d["pct_chance_bankruptcy_12m"] > 0).astype(float).where(d["pct_chance_bankruptcy_12m"].notna())
rq2c = d.groupby("credit_rating").apply(lambda g: pd.Series({
    "respondents": len(g),
    "mean_pct_chance_bankruptcy_12m": wmean(g, "pct_chance_bankruptcy_12m"),
    "pct_reporting_any_bankruptcy_chance": wmean(g, "any_bankruptcy_chance"),
    "pct_considered_bankruptcy_12m": wmean(g, "considered_bankruptcy_12m"),
    "pct_3mo_late_on_housing_12m": wmean(g, "late_3mo_housing_12m"),
    "n_answering_late_question": g["late_3mo_housing_12m"].notna().sum(),
    "mean_pct_chance_can_raise_2k": wmean(g, "pct_chance_can_raise_2k"),
})).loc[cred_order]
save_table(rq2c, "rq2_credit_rating_vs_distress.csv")

# Figure 4: credit rating vs expected bankruptcy + ability to raise $2k
known = [c for c in cred_order if "Don't" not in c]
sub = rq2c.loc[known]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5))
xk = np.arange(len(known))
a1.bar(xk, sub["mean_pct_chance_bankruptcy_12m"], color=ORANGE, width=0.6, edgecolor=SURFACE, linewidth=2)
for xi, v in zip(xk, sub["mean_pct_chance_bankruptcy_12m"]):
    a1.text(xi, v + 0.3, f"{v:.1f}%", ha="center", fontsize=10, fontweight="bold", color=INK)
a1.set_xticks(xk, short(known)); a1.set_xlabel("Self-reported credit score")
a1.set_ylabel("Average self-rated % chance of bankruptcy, next 12 months")
a1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%")); a1.grid(axis="x", visible=False)
ratio = sub["mean_pct_chance_bankruptcy_12m"].iloc[0] / sub["mean_pct_chance_bankruptcy_12m"].iloc[-1]
a1.set_title(f"Weak credit = {ratio:.0f}x the expected default risk", loc="left", fontsize=10.5, fontweight="bold", color=INK)
a2.bar(xk, sub["mean_pct_chance_can_raise_2k"], color=BLUE, width=0.6, edgecolor=SURFACE, linewidth=2)
for xi, v in zip(xk, sub["mean_pct_chance_can_raise_2k"]):
    a2.text(xi, v + 1.5, f"{v:.0f}%", ha="center", fontsize=10, fontweight="bold", color=INK)
a2.set_xticks(xk, short(known)); a2.set_xlabel("Self-reported credit score"); a2.set_ylim(0, 100)
a2.set_ylabel("Average % chance could come up with $2,000 in a month")
a2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%")); a2.grid(axis="x", visible=False)
a2.set_title("…and far less cushion to absorb a surprise bill", loc="left", fontsize=10.5, fontweight="bold", color=INK)
fig.subplots_adjust(top=0.80, wspace=0.3)
finish(fig, "How people rate their credit predicts how likely they think they are to default",
       "The survey has no direct 'miss a payment' question; expected chance of bankruptcy is the closest forward-looking measure.",
       "fig4_credit_vs_distress.png")

# =====================================================================
# RQ3 - savings, income and retirement plans (people not yet retired)
# =====================================================================
nr = d[d["retired"] == 0]
def rq3_table(key):
    order = sorted(nr[key].dropna().unique())
    return nr.groupby(key).apply(lambda g: pd.Series({
        "n_planned_age": g["planned_retirement_age"].notna().sum(),
        "median_planned_retirement_age": wmedian(g, "planned_retirement_age"),
        "mean_planned_retirement_age": wmean(g, "planned_retirement_age"),
        "n_years_last": g["years_savings_will_last"].notna().sum(),
        "median_years_savings_will_last": wmedian(g, "years_savings_will_last"),
        "mean_years_savings_will_last": wmean(g, "years_savings_will_last"),
        "pct_saying_savings_too_little": wshare(g, "savings_adequacy", "Too little"),
        "median_expected_savings_at_retirement": wmedian(g, "expected_savings_at_retirement"),
    })).loc[order]
rq3s, rq3i = rq3_table("savings_tier"), rq3_table("income_group")
save_table(rq3s, "rq3_retirement_by_savings.csv"); save_table(rq3i, "rq3_retirement_by_income.csv")
save_table(nr[["total_fin_assets", "hh_income", "planned_retirement_age", "years_savings_will_last"]].corr("spearman"),
           "rq3_spearman_not_retired.csv")

# Figure 5: retirement age and years savings last (two panels, both by savings tier and income)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5))
xs = np.arange(5)
a1.plot(xs, rq3s["mean_planned_retirement_age"], color=BLUE, lw=2, marker="o", ms=8, mec=SURFACE, mew=2)
a1.plot(xs, rq3i["mean_planned_retirement_age"], color=ORANGE, lw=2, marker="o", ms=8, mec=SURFACE, mew=2)
for xi, a, b in zip(xs, rq3s["mean_planned_retirement_age"], rq3i["mean_planned_retirement_age"]):
    a1.text(xi, a - 0.32 if a < b else a + 0.18, f"{a:.1f}", ha="center", fontsize=8.5, color=INK2)
    a1.text(xi, b + 0.18 if a < b else b - 0.32, f"{b:.1f}", ha="center", fontsize=8.5, color=INK2)
a1.set_xticks(xs, ["Lowest", "2nd", "Middle", "4th", "Highest"]); a1.set_xlabel("Group (savings tier or income group)")
a1.set_ylim(64.5, 69); a1.set_ylabel("Average planned retirement age"); a1.grid(axis="x", visible=False)
a1.set_title("Higher income → retire ~3 years earlier", loc="left", fontsize=10.5, fontweight="bold", color=INK)
a2.plot(xs, rq3s["mean_years_savings_will_last"], color=BLUE, lw=2, marker="o", ms=8, mec=SURFACE, mew=2)
a2.plot(xs, rq3i["mean_years_savings_will_last"], color=ORANGE, lw=2, marker="o", ms=8, mec=SURFACE, mew=2)
for xi, a, b in zip(xs, rq3s["mean_years_savings_will_last"], rq3i["mean_years_savings_will_last"]):
    a2.text(xi, a + 0.9 if a >= b else a - 1.8, f"{a:.0f}", ha="center", fontsize=8.5, color=INK2)
    a2.text(xi, b - 1.8 if a >= b else b + 0.9, f"{b:.0f}", ha="center", fontsize=8.5, color=INK2)
a2.set_xticks(xs, ["Lowest", "2nd", "Middle", "4th", "Highest"]); a2.set_xlabel("Group (savings tier or income group)")
a2.set_ylim(0, 32); a2.set_ylabel("Average years savings expected to last"); a2.grid(axis="x", visible=False)
a2.set_title("More savings → savings last 2.5x longer", loc="left", fontsize=10.5, fontweight="bold", color=INK)
leg = [plt.Line2D([], [], color=BLUE, marker="o", lw=2, label="By total savings: <$10k · $10-50k · $50-250k · $250k-1M · $1M+"),
       plt.Line2D([], [], color=ORANGE, marker="o", lw=2, label="By income: <$35k · $35-60k · $60-100k · $100-150k · $150k+")]
fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.01, 0.905), ncol=2, frameon=False, fontsize=8.5)
fig.subplots_adjust(top=0.76, wspace=0.28)
finish(fig, "Money buys an earlier and longer-lasting retirement",
       "Household heads not yet retired. Total savings = liquid savings + 401(k)/DC plans + IRAs.",
       "fig5_retirement_by_savings_income.png")

# Figure 6: share who say they are saving "too little" (headline gap)
fig, ax = plt.subplots(figsize=(10, 5.2))
vals = rq3s["pct_saying_savings_too_little"].values
ax.barh(np.arange(5)[::-1], vals, color=BLUE, height=0.6, edgecolor=SURFACE, linewidth=2)
for yi, v in zip(np.arange(5)[::-1], vals):
    ax.text(v + 0.01, yi, f"{v:.0%}", va="center", fontsize=10, fontweight="bold", color=INK)
ax.set_yticks(np.arange(5)[::-1], short(rq3s.index)); ax.set_xlim(0, 0.75)
ax.xaxis.set_major_formatter(PercentFormatter(1.0)); ax.grid(axis="y", visible=False)
ax.set_xlabel("Share expecting to have 'too little' saved for retirement"); ax.set_ylabel("Total savings today")
fig.subplots_adjust(top=0.80)
finish(fig, "Most households with under $50k saved expect a retirement shortfall",
       "Non-retired household heads, by current total savings.", "fig6_retirement_shortfall.png")

# Headline numbers for the README / report
head = {
    "respondents": len(d), "survey_waves": ", ".join(map(str, sorted(d["survey_year"].unique()))),
    "pct_net_savers_overall": wshare(d, "saving_behavior", "Added more than withdrew"),
    "pct_no_savings_account_overall": wshare(d, "saving_behavior", "No savings/investment account"),
    "pct_with_non_housing_debt_overall": wmean(d, "has_non_housing_debt"),
    "median_non_housing_debt_overall": wmedian(d, "non_housing_debt"),
    "median_household_income": wmedian(d, "hh_income"),
}
pd.Series(head).to_csv(OUT / "headline_numbers.csv", header=["value"])
print("Done. Tables in outputs/, charts in figures/.")
