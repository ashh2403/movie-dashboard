"""
PAGE 4 - BUDGET & ROI (supports Modules 3 and 6)
-----------------------------------------------
Budget vs revenue, profit = revenue - budget, and median ROI by genre.
Movies with budget = 0 are skipped because ROI cannot be calculated.
"""

import streamlit as st

from src import analysis, figures, ui
from src.charts import fmt_num
from src.filters import sidebar_filters, stop_if_empty

ui.setup_page("Budget & ROI", "💰")
df, full_df, min_movies = sidebar_filters(show_min_movies=True)
ui.page_header("BUDGET &", "ROI ANALYSIS",
               "Does spending more lead to earning more? Which genres give the best return?")
stop_if_empty(df)

with_budget = analysis.with_budget(df)
skipped = len(df) - len(with_budget)
stop_if_empty(with_budget)

total_profit = with_budget["profit"].sum()
ui.kpi_cards([
    ("Total profit", fmt_num(total_profit), "Revenue − budget, all selected movies", "revenue"),
    ("Median ROI", f"{with_budget['roi'].median():.0%}", "Typical return on each $1 of budget", "percent"),
    ("Movies that lost money", f"{analysis.loss_share(df):.0%}",
     f"{(with_budget['profit'] < 0).sum():,} of {len(with_budget):,} movies", "down"),
    ("Budget ↔ revenue", f"{analysis.correlation(with_budget, 'budget', 'revenue'):.2f}", "Correlation (−1 to +1)", "link"),
])
if skipped:
    st.caption(f"{skipped:,} movies with budget = 0 were skipped on this page.")
st.write("")

ui.show_chart(figures.budget_vs_revenue, df)
left, right = st.columns(2)
with left:
    ui.show_chart(figures.median_roi_by_genre, df, min_movies)
with right:
    ui.show_chart(figures.median_profit_by_genre, df, min_movies)
ui.show_chart(figures.top_profit_movies, df)
st.markdown("#### Why the median ROI?")
st.markdown(
    "ROI = (revenue − budget) ÷ budget. A few low-budget hits have ROI of several thousand percent, "
    "which would make the **average** ROI misleading. The **median** is the middle movie, so it shows "
    "the typical return for a genre.")
best_roi = with_budget.nlargest(5, "roi")[["title", "year", "genre", "budget", "revenue", "roi"]]
st.dataframe(best_roi, hide_index=True, width="stretch",
             column_config={"title": "Title", "genre": "Genre",
                            "budget": st.column_config.NumberColumn("Budget", format="compact"),
                            "revenue": st.column_config.NumberColumn("Revenue", format="compact"),
                            "roi": st.column_config.NumberColumn("ROI (x budget)", format="%.1f"),
                            "year": st.column_config.NumberColumn("Year", format="%d")})
