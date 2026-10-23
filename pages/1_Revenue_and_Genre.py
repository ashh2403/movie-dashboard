"""
PAGE 1 - MODULE 3: REVENUE & GENRE ANALYSIS
-------------------------------------------
Total and average revenue per genre, revenue over the years and how the
genre mix changed by decade.
"""

import streamlit as st

from src import analysis, figures, ui
from src.charts import fmt_num
from src.filters import sidebar_filters, stop_if_empty

ui.setup_page("Revenue & Genre", "💵")
df, full_df, min_movies = sidebar_filters(show_min_movies=True)
ui.page_header("REVENUE &", "GENRE ANALYSIS",
               "Which genres earn the most in total, and which earn the most per movie?", "Module 3")
stop_if_empty(df)

genres = analysis.genre_summary(df)
top = genres.iloc[0]
growth = analysis.revenue_growth(df)

ui.kpi_cards([
    ("Top genre by revenue", str(top["genre"]), f"{fmt_num(top['total_revenue'])} · {top['revenue_share']:.0%} of total", "trophy"),
    ("Genres in selection", str(len(genres)), f"{len(df):,} movies", "layers"),
    ("Average revenue per movie", fmt_num(df["revenue"].mean()), f"Median {fmt_num(df['revenue'].median())}", "chart"),
    ("Peak release year", str(growth["peak_year"]) if growth["ok"] else "-",
     fmt_num(growth["peak_revenue"]) if growth["ok"] else "Need 10+ years", "calendar"),
])
st.write("")

left, right = st.columns(2)
with left:
    ui.show_chart(figures.revenue_by_genre, df)
with right:
    ui.show_chart(figures.avg_revenue_by_genre, df, min_movies)
left, right = st.columns(2)
with left:
    ui.show_chart(figures.revenue_by_year, df)
with right:
    ui.show_chart(figures.revenue_share_by_decade, df)
# ---- Honest note about small samples --------------------------------------
small = genres[genres["movies"] < min_movies]
if len(small):
    st.warning(
        f"**Small samples hidden from the average chart:** "
        + ", ".join(f"{g} ({n} movies)" for g, n in zip(small["genre"], small["movies"]))
        + f". Averages from so few movies are unreliable, e.g. a single hit can make a genre look "
          f"like the best. Lower the *Minimum movies per group* slider to see them.")

# ---- Table with every number used above -----------------------------------
st.markdown("#### Genre summary table")
table = genres.rename(columns={"genre": "Genre", "total_revenue": "Total revenue",
                               "avg_revenue": "Average revenue", "median_revenue": "Median revenue",
                               "movies": "Movies", "avg_score": "Average score",
                               "revenue_share": "Share of revenue"})
st.dataframe(
    table, hide_index=True, width="stretch",
    column_config={
        "Total revenue": st.column_config.NumberColumn(format="compact"),
        "Average revenue": st.column_config.NumberColumn(format="compact"),
        "Median revenue": st.column_config.NumberColumn(format="compact"),
        "Average score": st.column_config.NumberColumn(format="%.2f"),
        "Share of revenue": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
    })
