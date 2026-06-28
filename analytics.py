"""
analytics.py
============
Descriptive, diagnostic, and correlation analytics for the cleaned
Freeze-Dry Meal Service survey dataset.
"""

import numpy as np
import pandas as pd
from scipy import stats

NUMERIC_COLS = [
    "age_numeric", "income_numeric", "household_numeric", "price_numeric",
    "qty_numeric", "spend_numeric", "E1_Likelihood_To_Use_Score",
    "D1_Taste_Retention_Importance", "D2_Price_Affordability_Importance",
    "D3_Shelf_Life_Importance", "D4_Hygiene_Certification_Importance",
    "D5_Convenience_Importance", "D6_Brand_Trust_Importance",
    "D7_Variety_Importance", "D8_Speed_Turnaround_Importance",
]

CATEGORICAL_COLS = [
    "A2_Segment", "A4_Gender", "A6_Occupation", "C4_Packaging_Preference",
    "B4_Frequency_Sending_Food", "A3_Age_Group", "A7_Income_Bracket",
]


# --------------------------------------------------------------------------
# DESCRIPTIVE
# --------------------------------------------------------------------------

def descriptive_stats(df, cols=None):
    cols = [c for c in (cols or NUMERIC_COLS) if c in df.columns]
    desc = df[cols].describe().T
    desc["skew"] = df[cols].skew()
    return desc.round(2)


def correlation_matrix(df, cols=None):
    cols = [c for c in (cols or NUMERIC_COLS) if c in df.columns]
    return df[cols].corr()


def top_correlations(corr_df, top_n=8, min_abs=0.05):
    pairs = []
    cols = corr_df.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr_df.iloc[i, j]
            if pd.notna(r) and abs(r) >= min_abs:
                pairs.append((cols[i], cols[j], r))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    return pairs[:top_n]


def _strength_label(r):
    a = abs(r)
    if a >= 0.5:
        return "strong"
    if a >= 0.3:
        return "moderate"
    if a >= 0.1:
        return "weak"
    return "negligible"


def correlation_insight_sentences(pairs):
    sentences = []
    for v1, v2, r in pairs:
        direction = "positive" if r > 0 else "negative"
        strength = _strength_label(r)
        sentences.append(f"**{v1}** and **{v2}** show a {strength} {direction} correlation (r = {r:.2f}).")
    return sentences


def preference_frequency(df, prefix):
    """Count frequency of each option for a parsed multi-select group
    (columns named '{prefix}__{label}')."""
    cols = [c for c in df.columns if c.startswith(f"{prefix}__")]
    counts = df[cols].sum().sort_values(ascending=False)
    counts.index = [c.split("__", 1)[1] for c in counts.index]
    out = counts.reset_index()
    out.columns = ["Option", "Count"]
    out["% of respondents"] = (out["Count"] / len(df) * 100).round(1)
    return out


# --------------------------------------------------------------------------
# DIAGNOSTIC
# --------------------------------------------------------------------------

def chi_square_test(df, cat_col, target_col="likely_to_use_label2"):
    ct = pd.crosstab(df[cat_col], df[target_col])
    chi2, p, dof, expected = stats.chi2_contingency(ct)
    n = ct.values.sum()
    r, k = ct.shape
    denom = min(r - 1, k - 1) if min(r - 1, k - 1) > 0 else 1
    cramers_v = np.sqrt((chi2 / n) / denom)
    resid = ((ct - expected) / np.sqrt(expected)).round(2)
    return {"crosstab": ct, "chi2": chi2, "p_value": p, "dof": dof,
            "cramers_v": cramers_v, "std_residuals": resid}


def rate_table(df, group_col, target_col="likely_to_use_binary", min_count=5):
    overall_rate = df[target_col].mean()
    g = df.groupby(group_col).agg(n=(target_col, "count"), positive=(target_col, "sum"))
    g["rate_%"] = (g["positive"] / g["n"] * 100).round(1)
    g["overall_rate_%"] = round(overall_rate * 100, 1)
    g["deviation_pts"] = (g["rate_%"] - g["overall_rate_%"]).round(1)
    g = g[g["n"] >= min_count].sort_values("deviation_pts", ascending=False)
    return g.reset_index()


def continuous_group_diff(df, numeric_col, target_col="likely_to_use_label2"):
    a = df.loc[df[target_col] == "Yes", numeric_col].dropna()
    b = df.loc[df[target_col] == "No", numeric_col].dropna()
    stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    return {"yes_mean": a.mean(), "yes_median": a.median(),
            "no_mean": b.mean(), "no_median": b.median(),
            "u_stat": stat, "p_value": p}
