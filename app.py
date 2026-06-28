"""
app.py
Freeze-Dried Home-Cooked Meal Service - Hyderabad Market Validation Dashboard

Pages: Home & Data Overview | Descriptive Analysis | Diagnostic Analysis |
       Correlation Analysis | Business Insights | Raw Data
"""

import streamlit as st
import pandas as pd
import plotly.express as px

import data_cleaning as dc
import analytics as an

st.set_page_config(page_title="Freeze-Dry Hyderabad Market Validation", layout="wide", page_icon="🥘")

# --------------------------------------------------------------------------
# DATA LOADING
# --------------------------------------------------------------------------
st.sidebar.title("🥘 Freeze-Dry Hyderabad")
st.sidebar.caption("Customer demand validation dashboard")
uploaded = st.sidebar.file_uploader("Upload questionnaire export (.xlsx/.csv)", type=["xlsx", "csv"])


@st.cache_data
def get_raw_data(file):
    return dc.load_raw(file)


@st.cache_data
def get_clean_data(_raw_df):
    df, report = dc.clean_and_transform(_raw_df)
    return df, report


DATA_SOURCE = uploaded if uploaded is not None else "data/Freeze_Dry_Survey_Data.xlsx"
raw = get_raw_data(DATA_SOURCE)
df, report = get_clean_data(raw)

if uploaded is not None:
    st.sidebar.success(f"Loaded {len(df)} responses from uploaded file")
else:
    st.sidebar.info(f"Using bundled sample data ({len(df)} respondents)")

PAGE = st.sidebar.radio("Navigate", [
    "🏠 Home & Data Overview", "📊 Descriptive Analysis", "🔍 Diagnostic Analysis",
    "🔗 Correlation Analysis", "💡 Business Insights", "📄 Raw Data",
])
st.sidebar.markdown("---")
st.sidebar.caption("Is there a market for freeze-dried home-cooked meals in Hyderabad? "
                    "NRI/Family-sending & Traveler/Student segments.")

COLOR_SEQ = px.colors.qualitative.Set2

# ==========================================================================
# PAGE 1: HOME & DATA OVERVIEW
# ==========================================================================
if PAGE == "🏠 Home & Data Overview":
    st.title("🏠 Home & Data Overview")
    st.caption("Primary research survey - Freeze-Dried Home-Cooked Meal Service, Hyderabad")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Respondents", len(df))
    c2.metric("Likely to use", f"{df['likely_to_use_binary'].mean()*100:.1f}%")
    c3.metric("Median max price/kg", f"Rs {df['price_numeric'].median():.0f}")
    c4.metric("Median monthly spend", f"Rs {df['spend_numeric'].median():.0f}")

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.pie(df, names="A2_Segment", title="Segment mix", hole=0.4,
                      color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(height=350)
        st.plotly_chart(fig, width="stretch")
    with col2:
        fig = px.pie(df, names="A4_Gender", title="Gender mix", hole=0.4,
                      color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(height=350)
        st.plotly_chart(fig, width="stretch")
    with col3:
        fig = px.pie(df, names="likely_to_use_label2", title="Likely to use?", hole=0.4,
                      color_discrete_sequence=["#0F6E56", "#D85A30"])
        fig.update_layout(height=350)
        st.plotly_chart(fig, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(df, x="age_numeric", color="A2_Segment", nbins=20,
                            title="Age distribution by segment", color_discrete_sequence=COLOR_SEQ)
        st.plotly_chart(fig, width="stretch")
    with col2:
        fig = px.histogram(df, x="price_numeric", color="A2_Segment", nbins=20,
                            title="Max price willing to pay (Rs/kg)", marginal="box",
                            color_discrete_sequence=COLOR_SEQ)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Respondents by segment and purchase intent")
    seg_intent = df.groupby(["A2_Segment", "likely_to_use_label2"]).size().reset_index(name="count")
    fig = px.bar(seg_intent, x="A2_Segment", y="count", color="likely_to_use_label2", barmode="group",
                  title="Segment vs likely-to-use", color_discrete_sequence=["#D85A30", "#0F6E56"])
    st.plotly_chart(fig, width="stretch")

# ==========================================================================
# PAGE 2: DESCRIPTIVE ANALYSIS
# ==========================================================================
elif PAGE == "📊 Descriptive Analysis":
    st.title("📊 Descriptive Analysis")
    st.caption("Distributions, summary statistics, and preference patterns")

    st.subheader("Summary statistics")
    desc = an.descriptive_stats(df)
    st.dataframe(desc, width="stretch")
    st.caption("'skew' beyond +/-1 flags a noticeably right- or left-skewed variable "
               "(income and spend are right-skewed here - a few high-value respondents pull the mean above the median).")

    st.subheader("Key variable distributions")
    dist_vars = ["age_numeric", "income_numeric", "price_numeric", "qty_numeric", "spend_numeric"]
    cols = st.columns(3)
    for i, var in enumerate(dist_vars):
        with cols[i % 3]:
            fig = px.histogram(df, x=var, nbins=20, title=var, color_discrete_sequence=["#0F6E56"])
            fig.update_layout(height=300, margin=dict(t=40, b=20))
            st.plotly_chart(fig, width="stretch")

    st.subheader("Price and spend by segment (boxplots)")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.box(df, x="A2_Segment", y="price_numeric", color="A2_Segment",
                      title="Max price/kg by segment", color_discrete_sequence=COLOR_SEQ)
        st.plotly_chart(fig, width="stretch")
    with col2:
        fig = px.box(df, x="A2_Segment", y="spend_numeric", color="A2_Segment",
                      title="Monthly spend by segment", color_discrete_sequence=COLOR_SEQ)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Average importance score per priority (Likert 1-5)")
    likert_cols = [c for c in an.NUMERIC_COLS if c.startswith("D")]
    likert_means = df[likert_cols].mean().sort_values(ascending=True)
    fig = px.bar(x=likert_means.values, y=likert_means.index, orientation="h",
                  title="What matters most to respondents", color_discrete_sequence=["#0F6E56"])
    fig.update_layout(xaxis_title="Mean importance (1-5)", yaxis_title="")
    st.plotly_chart(fig, width="stretch")

    st.subheader("Dish, occasion & channel preferences")
    pref_options = {
        "C1 - Dishes preferred": "C1", "C2 - Occasions": "C2",
        "C3 - Trusted channels": "C3", "B5 - Methods currently used": "B5",
    }
    pref_choice = st.selectbox("Choose a preference question", list(pref_options.keys()))
    freq = an.preference_frequency(df, pref_options[pref_choice])
    fig = px.bar(freq, x="% of respondents", y="Option", orientation="h",
                  title=pref_choice, color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, width="stretch")

# ==========================================================================
# PAGE 3: DIAGNOSTIC ANALYSIS
# ==========================================================================
elif PAGE == "🔍 Diagnostic Analysis":
    st.title("🔍 Diagnostic Analysis")
    st.caption("Which attributes are statistically associated with purchase intent, and why")

    chosen = st.selectbox("Choose an attribute to diagnose", an.CATEGORICAL_COLS)
    result = an.chi_square_test(df, chosen)
    ct_pct = result["crosstab"].div(result["crosstab"].sum(axis=1), axis=0) * 100

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(ct_pct, barmode="stack", title=f"{chosen} vs likely-to-use (row %)",
                      color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(yaxis_title="% of respondents")
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.metric("Chi-square p-value", f"{result['p_value']:.4f}")
        st.metric("Cramer's V (effect size)", f"{result['cramers_v']:.3f}")
        sig = "Statistically significant (p < 0.05)" if result["p_value"] < 0.05 else "Not statistically significant"
        st.write(sig)

    st.subheader("Standardized residuals heatmap")
    fig = px.imshow(result["std_residuals"], text_auto=".2f", color_continuous_scale="RdBu", zmin=-3, zmax=3,
                     title="Which categories drive the association (|residual| > 2 = significant)", aspect="auto")
    st.plotly_chart(fig, width="stretch")

    st.subheader("Likely-to-use rate by group")
    rt = an.rate_table(df, chosen)
    fig = px.bar(rt, x=chosen, y="deviation_pts", color="deviation_pts", color_continuous_scale="RdBu_r",
                  title="Deviation from overall likely-to-use rate (percentage points)")
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(rt, width="stretch")

    st.subheader("Continuous variable comparison (Mann-Whitney U)")
    num_choice = st.selectbox("Compare this numeric variable between likely vs unlikely buyers",
                               ["price_numeric", "income_numeric", "spend_numeric", "age_numeric"])
    diff = an.continuous_group_diff(df, num_choice)
    col1, col2 = st.columns([1, 2])
    with col1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Median (likely)", f"{diff['yes_median']:.0f}")
        c2.metric("Median (unlikely)", f"{diff['no_median']:.0f}")
        c3.metric("p-value", f"{diff['p_value']:.4f}")
    with col2:
        fig = px.violin(df, x="likely_to_use_label2", y=num_choice, color="likely_to_use_label2",
                          box=True, points="all", title=f"{num_choice} by purchase intent",
                          color_discrete_sequence=["#D85A30", "#0F6E56"])
        st.plotly_chart(fig, width="stretch")

# ==========================================================================
# PAGE 4: CORRELATION ANALYSIS
# ==========================================================================
elif PAGE == "🔗 Correlation Analysis":
    st.title("🔗 Correlation Analysis")
    st.caption("How numeric variables move together, and what that means for the business")

    corr = an.correlation_matrix(df)

    st.subheader("Correlation heatmap")
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu", zmin=-1, zmax=1,
                     title="Correlation matrix - numeric survey variables", aspect="auto")
    fig.update_layout(height=650)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Strongest correlated pairs")
    pairs = an.top_correlations(corr, top_n=10)
    pair_df = pd.DataFrame(pairs, columns=["Variable 1", "Variable 2", "r"])
    pair_df["pair_label"] = pair_df.apply(lambda row: f"{row['Variable 1']} vs {row['Variable 2']}", axis=1)
    pair_df["abs_r"] = pair_df["r"].abs()
    fig = px.bar(pair_df.sort_values("abs_r"), x="r", y="pair_label",
                  orientation="h", color="r", color_continuous_scale="RdBu", range_color=[-1, 1],
                  title="Top 10 correlated variable pairs")
    fig.update_layout(yaxis_title="")
    st.plotly_chart(fig, width="stretch")

    st.subheader("Auto-generated insights")
    for sentence in an.correlation_insight_sentences(pairs):
        st.markdown(f"- {sentence}")

    st.subheader("Explore a relationship")
    col1, col2 = st.columns(2)
    numeric_cols = [c for c in an.NUMERIC_COLS if c in df.columns]
    with col1:
        x_var = st.selectbox("X variable", numeric_cols, index=numeric_cols.index("income_numeric"))
    with col2:
        y_var = st.selectbox("Y variable", numeric_cols, index=numeric_cols.index("price_numeric"))
    if x_var == y_var:
        st.warning("Pick two different variables to see a scatter plot.")
    else:
        fig = px.scatter(df, x=x_var, y=y_var, color="A2_Segment", trendline="ols",
                          title=f"{x_var} vs {y_var}, by segment", color_discrete_sequence=COLOR_SEQ)
        st.plotly_chart(fig, width="stretch")
        r_val = df[[x_var, y_var]].corr().iloc[0, 1]
        st.markdown(f"Correlation: r = **{r_val:.2f}** ({an._strength_label(r_val)} "
                    f"{'positive' if r_val > 0 else 'negative'} relationship).")

# ==========================================================================
# PAGE 5: BUSINESS INSIGHTS
# ==========================================================================
elif PAGE == "💡 Business Insights":
    st.title("💡 Business Insights: Is there a market in Hyderabad?")

    seg_rates = an.rate_table(df, "A2_Segment")
    top_seg = seg_rates.iloc[0]
    price_diff = an.continuous_group_diff(df, "price_numeric")

    pct_nri = (df["A2_Segment"] == "NRI / Family-sending").mean() * 100
    pct_trav = (df["A2_Segment"] == "Traveler / Student").mean() * 100
    pct_neither = (df["A2_Segment"] == "Neither").mean() * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("Overall likely-to-use", f"{df['likely_to_use_binary'].mean()*100:.1f}%")
    c2.metric(f"Top segment: {top_seg['A2_Segment']}", f"{top_seg['rate_%']}%", f"{top_seg['deviation_pts']:+.1f} pts vs avg")
    c3.metric("Price gap (likely vs unlikely)", f"Rs {price_diff['yes_median']-price_diff['no_median']:.0f}/kg")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(seg_rates, x="A2_Segment", y="rate_%", color="A2_Segment",
                      title="Likely-to-use rate by segment", color_discrete_sequence=COLOR_SEQ)
        fig.add_hline(y=seg_rates["overall_rate_%"].iloc[0], line_dash="dash",
                      annotation_text="Overall average")
        st.plotly_chart(fig, width="stretch")
    with col2:
        price_compare = pd.DataFrame({
            "Group": ["Likely to use", "Unlikely to use"],
            "Median max price/kg": [price_diff["yes_median"], price_diff["no_median"]],
        })
        fig = px.bar(price_compare, x="Group", y="Median max price/kg", color="Group",
                      title="Willingness to pay: likely vs unlikely buyers",
                      color_discrete_sequence=["#0F6E56", "#D85A30"])
        st.plotly_chart(fig, width="stretch")

    st.markdown(f"""
**Overall demand signal:** {df['likely_to_use_binary'].mean()*100:.1f}% of respondents say they are
likely or very likely to use a freeze-dried home-cooked meal service in the next 6 months.

**Strongest segment:** `{top_seg['A2_Segment']}` shows the highest purchase intent at
**{top_seg['rate_%']}%**, which is {top_seg['deviation_pts']:+.1f} points above the overall average
of {top_seg['overall_rate_%']}%.

**Segment mix in the sample:** {pct_nri:.0f}% NRI/Family-sending, {pct_trav:.0f}% Traveler/Student,
{pct_neither:.0f}% with no clear use case.

**Willingness to pay:** respondents likely to use the service have a median max-price of
Rs {price_diff['yes_median']:.0f}/kg vs Rs {price_diff['no_median']:.0f}/kg for those unlikely
(Mann-Whitney p = {price_diff['p_value']:.4f}), suggesting price sensitivity is not the main barrier
for the core segments - poor awareness or trust likely matters more.

**Recommendation:** Hyderabad shows a real, segmentable market — prioritize the
{top_seg['A2_Segment']} segment for early go-to-market, and use the Descriptive/Diagnostic/Correlation
pages to pick the dish types and channels that resonate most with that group.
""")

# ==========================================================================
# PAGE 6: RAW DATA
# ==========================================================================
elif PAGE == "📄 Raw Data":
    st.title("📄 Raw Data")
    st.caption("Unprocessed questionnaire export, exactly as collected")

    c1, c2 = st.columns(2)
    c1.metric("Rows", raw.shape[0])
    c2.metric("Columns", raw.shape[1])

    st.dataframe(raw, width="stretch")
    st.download_button("Download raw data as CSV", raw.to_csv(index=False).encode("utf-8"),
                        file_name="freeze_dry_raw_responses.csv", mime="text/csv")
