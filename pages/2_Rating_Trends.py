"""
PAGE 2 - MODULE 4: RATING TREND ANALYSIS
----------------------------------------
Rating score patterns across genres, release years and certificates,
and how the score relates to revenue and to the number of votes.
"""

import streamlit as st

from src import analysis, figures, insights, ui
from src.filters import sidebar_filters, stop_if_empty

ui.setup_page("Rating Trends", "⭐")
df, full_df, min_movies = sidebar_filters(show_min_movies=True)
ui.page_header("RATING", "TREND ANALYSIS",
               "How are movies rated, and does a better score mean more revenue?", "Module 4")
stop_if_empty(df, needed=3)

r_rev = analysis.correlation(df, "score", "revenue")
r_votes = analysis.correlation(df, "votes", "score")
ui.kpi_cards([
    ("Average score", f"{df['score'].mean():.2f}", f"Median {df['score'].median():.1f} · out of 10", "star"),
    ("Highest score", f"{df['score'].max():.1f}", df.loc[df["score"].idxmax(), "title"], "trophy"),
    ("Score ↔ revenue", f"{r_rev:.2f}", insights.describe_correlation(r_rev) + " correlation", "link"),
    ("Votes ↔ score", f"{r_votes:.2f}", insights.describe_correlation(r_votes) + " correlation", "users"),
])
st.write("")

left, right = st.columns(2)
with left:
    ui.show_chart(figures.score_distribution, df)
with right:
    ui.show_chart(figures.avg_score_by_year, df)
left, right = st.columns(2)
with left:
    ui.show_chart(figures.avg_score_by_genre, df, min_movies)
with right:
    ui.show_chart(figures.avg_score_by_certificate, df, min_movies)
left, right = st.columns(2)
with left:
    ui.show_chart(figures.score_vs_revenue, df)
with right:
    ui.show_chart(figures.votes_vs_score, df)
# ---- Score bands: average revenue for each band of scores -----------------
st.markdown("#### Average revenue by score band")
bands = analysis.score_bands(df)
st.dataframe(bands.rename(columns={"score_band": "Score band", "movies": "Movies",
                                   "avg_revenue": "Average revenue"}),
             hide_index=True, width="stretch",
             column_config={"Average revenue": st.column_config.NumberColumn(format="compact")})
link = "strongly" if abs(r_rev) >= 0.5 else "moderately" if abs(r_rev) >= 0.3 else "only loosely"
ui.facts([
    f"Score vs revenue r = {r_rev:.2f} ({insights.describe_correlation(r_rev)}): "
    f"in this selection, score and revenue are {link} linked.",
    "Correlation shows a relationship, not a cause: marketing, budget and release timing also matter.",
])
