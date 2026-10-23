"""
HOME PAGE - MOVIE INDUSTRY PERFORMANCE DASHBOARD  (CinemaScope Intelligence)
===========================================================================
Run with:   streamlit run app.py

This file does two jobs:
  1. builds the sidebar menu (st.navigation), grouped into sections, and
  2. draws the Home page:
       * brand header with the active-filter summary
       * 4 KPI cards (real values + per-year sparklines, each opens a detail page)
       * the hero "revenue by release year" chart next to the key-insights panel
       * the 5 other overview charts from the Power BI dashboard

How the 6 project modules fit together:
  Module 1  Data Collection     -> src/data_loader.py
  Module 2  Data Preprocessing  -> src/preprocessing.py   (Data Quality page shows the log)
  Module 3  Revenue & Genre     -> src/analysis.py        (Revenue & Genre page)
  Module 4  Rating Trends       -> src/analysis.py        (Rating Trends page)
  Module 5  Actors & Directors  -> src/analysis.py        (Actors & Directors page)
  Module 6  Dashboard/Insights  -> this file, src/ui.py, src/figures.py, src/insights.py
"""

import streamlit as st

from src import analysis, figures, insights, ui
from src.charts import fmt_num
from src.filters import filter_chips, sidebar_filters, stop_if_empty

PAGE_REVENUE = "pages/1_Revenue_and_Genre.py"
PAGE_RATINGS = "pages/2_Rating_Trends.py"
PAGE_BUDGET = "pages/4_Budget_and_ROI.py"
PAGE_EXPLORER = "pages/5_Movie_Explorer.py"


def home():
    # ---- Page setup + shared sidebar filters (Module 6) --------------------
    ui.setup_page("Overview")
    df, full_df, min_movies = sidebar_filters(show_min_movies=True)

    head, action = st.columns([5, 1], vertical_alignment="bottom")
    with head:
        ui.dashboard_header(
            "Box-office performance, production budgets, star and director power, and audience ratings "
            f"for {len(full_df):,} movies released {full_df['year'].min()}–{full_df['year'].max()}. "
            "All money values are nominal US dollars.",
            chips=filter_chips(), tag="Movie Industry Performance Dashboard")
    with action:
        # Export: exactly the movies behind every number on this page
        st.download_button("Export CSV", df.drop(columns=["release_date"]).to_csv(index=False).encode("utf-8"),
                           file_name="cinemascope_filtered_movies.csv", mime="text/csv",
                           icon=":material/download:", width="stretch", disabled=df.empty,
                           help="Download the movies that match the current filters")
    stop_if_empty(df)

    # ---- KPI cards (Module 6): real totals + per-year sparklines -----------
    k = analysis.kpis(df)
    yearly = analysis.yearly_series(df)
    partial = analysis.incomplete_final_year(df) is not None
    span = dict(spark_from=str(yearly["year"].min()), spark_to=str(yearly["year"].max()),
                partial_last=partial)
    ui.kpi_cards([
        dict(label="Total Movies", value=f"{k['movies']:,}", icon="film", accent="gold",
             note=f"{df['genre'].nunique()} genres · {df['director'].nunique():,} directors",
             spark=yearly["movies"].tolist(), spark_label="movies / year", **span,
             link=PAGE_EXPLORER, link_label="Open Movie Explorer"),
        dict(label="Total Revenue (USD)", value=fmt_num(k["revenue"]), icon="revenue", accent="coral",
             note=f"Avg {fmt_num(k['avg_revenue'])} per movie · median {fmt_num(df['revenue'].median())}",
             spark=yearly["revenue"].tolist(), spark_label="revenue / year", **span,
             link=PAGE_REVENUE, link_label="Open Revenue & Genre"),
        dict(label="Total Budget (USD)", value=fmt_num(k["budget"]), icon="budget", accent="purple",
             note=(f"Revenue ÷ budget = {k['revenue'] / k['budget']:.2f}x" if k["budget"] else "No budget data"),
             spark=yearly["budget"].tolist(), spark_label="budget / year", **span,
             link=PAGE_BUDGET, link_label="Open Budget & ROI"),
        dict(label="Average Rating", value=f"{k['avg_score']:.2f}", unit="/ 10", icon="star", accent="teal",
             note=f"Sum of rating score {k['score_sum']:,.1f}",
             spark=yearly["avg_score"].tolist(), spark_label="avg score / year", **span,
             link=PAGE_RATINGS, link_label="Open Rating Trends"),
    ])
    if partial:
        p = analysis.incomplete_final_year(df)
        ui.note(f"<b>{p['year']} is incomplete in the source data:</b> only {p['movies']} movies "
                f"({p['months']}) against a typical {p['typical']:.0f} per year. Its totals are shown "
                "as they are, drawn dotted in the sparklines and the revenue chart. They are not a real "
                "collapse of the box office.")

    # ---- Hero chart + insights panel (Modules 3 and 6) ---------------------
    ui.section("Box-office trajectory", "Revenue earned by movies released each year")
    hero, panel = st.columns([2, 1], gap="medium")
    with hero:
        ui.show_chart(figures.revenue_by_year, df, height=640)          # Module 3
    with panel:
        ui.insights_panel(insights.key_insights(df, min_movies))        # Module 6

    # ---- The other overview charts (Modules 3, 4, 5) -----------------------
    ui.section("Talent, audience and genre mix", "Hover any bar or slice for exact values")
    row = st.columns(3, gap="medium")
    with row[0]:
        ui.show_chart(figures.top_stars_by_revenue, df)                  # Module 5
    with row[1]:
        ui.show_chart(figures.movies_by_certificate, df)                 # Module 4
    with row[2]:
        ui.show_chart(figures.revenue_by_genre, df)                      # Module 3

    row = st.columns(2, gap="medium")
    with row[0]:
        ui.show_chart(figures.top_directors_area, df)                    # Module 5
    with row[1]:
        ui.show_chart(figures.avg_revenue_by_genre, df, min_movies)      # Module 3
        if min_movies <= 4 and "Family" in set(df["genre"]):
            st.caption("⚠️ Family has only 4 movies, so its average is not reliable.")

    st.caption("Source: movie industry dataset (IMDb-derived), 1980–2020. Revenue and budget are nominal "
               "US dollars, not adjusted for inflation. Use the sidebar pages for detailed analysis.")


# ---- Sidebar menu: every page of the dashboard, grouped --------------------
pages = {
    "Overview": [
        st.Page(home, title="Home", icon=":material/space_dashboard:", default=True),
    ],
    "Analysis": [
        st.Page(PAGE_REVENUE, title="Revenue & Genre", icon=":material/payments:"),
        st.Page(PAGE_RATINGS, title="Rating Trends", icon=":material/star_rate:"),
        st.Page("pages/3_Actors_and_Directors.py", title="Actors & Directors", icon=":material/theater_comedy:"),
        st.Page(PAGE_BUDGET, title="Budget & ROI", icon=":material/account_balance_wallet:"),
    ],
    "Data": [
        st.Page(PAGE_EXPLORER, title="Movie Explorer", icon=":material/manage_search:"),
        st.Page("pages/6_Data_Quality.py", title="Data Quality", icon=":material/fact_check:"),
    ],
}
st.navigation(pages).run()
