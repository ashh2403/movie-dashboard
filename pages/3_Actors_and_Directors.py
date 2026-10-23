"""
PAGE 3 - MODULE 5: ACTOR & DIRECTOR ANALYSIS
--------------------------------------------
Top performers by total revenue and by average rating score,
plus the most successful star + director partnerships.
"""

import streamlit as st

from src import analysis, figures, ui
from src.charts import fmt_num
from src.filters import sidebar_filters, stop_if_empty

ui.setup_page("Actors & Directors", "🎭")
df, full_df, _ = sidebar_filters()
ui.page_header("ACTOR &", "DIRECTOR ANALYSIS",
               "Who are the top performers by box-office revenue and by rating score?", "Module 5")
stop_if_empty(df)

# Controls that only this page needs
c1, c2 = st.columns(2)
top_n = c1.slider("How many people to show", 5, 20, 10)
min_films = c2.slider("Minimum movies for the score ranking", 1, 15, 5,
                      help="A person with only 1 good film should not top the score ranking.")

star = analysis.top_people_by_revenue(df, "star", 1).iloc[0]
director = analysis.top_people_by_revenue(df, "director", 1).iloc[0]
ui.kpi_cards([
    ("Top star by revenue", star["star"], f"{fmt_num(star['total_revenue'])} · {star['movies']} movies", "star"),
    ("Top director by revenue", director["director"],
     f"{fmt_num(director['total_revenue'])} · {director['movies']} movies", "director"),
    ("Top 10 directors' share", f"{analysis.top_n_share(df, 'director', 10):.0%}",
     f"of revenue · {df['director'].nunique():,} directors in total", "chart"),
    ("Top 10 stars' share", f"{analysis.top_n_share(df, 'star', 10):.0%}",
     f"of revenue · {df['star'].nunique():,} stars in total", "ticket"),
])
st.write("")

tab_rev, tab_score, tab_pairs = st.tabs([":material/payments: By total revenue", ":material/star_rate: By average score", ":material/handshake: Star + director pairs"])

with tab_rev:
    left, right = st.columns(2)
    with left:
        ui.show_chart(figures.top_stars_by_revenue, df, n=top_n)
    with right:
        ui.show_chart(figures.top_directors_by_revenue, df, n=top_n)
    ui.show_chart(figures.top_directors_area, df, n=max(top_n, 12))
with tab_score:
    left, right = st.columns(2)
    with left:
        ui.show_chart(figures.top_people_by_score, df, "star", min_films, top_n)
    with right:
        ui.show_chart(figures.top_people_by_score, df, "director", min_films, top_n)
    st.caption(f"Only people with at least {min_films} movies are ranked by score, "
               "so one lucky film cannot put someone at the top.")

with tab_pairs:
    pairs = analysis.star_director_pairs(df, top_n)
    if pairs.empty:
        st.info("No star + director pair made 2 or more films together in this selection.")
    else:
        st.dataframe(pairs.rename(columns={"director": "Director", "star": "Star", "movies": "Movies together",
                                           "total_revenue": "Total revenue", "avg_score": "Average score"}),
                     hide_index=True, width="stretch",
                     column_config={"Total revenue": st.column_config.NumberColumn(format="compact"),
                                    "Average score": st.column_config.NumberColumn(format="%.2f")})

# ---- Look up one person --------------------------------------------------
st.markdown("#### Look up a star or director")
kind = st.radio("Person type", ["director", "star"], horizontal=True, format_func=str.title)
people = analysis.people_summary(df, kind).sort_values("total_revenue", ascending=False)
name = st.selectbox(f"Choose a {kind}", people[kind])
if name:
    person = people[people[kind] == name].iloc[0]
    st.markdown(f"**{name}** — {person['movies']} movies · total revenue {fmt_num(person['total_revenue'])} · "
                f"average score {person['avg_score']:.2f}")
    films = df[df[kind] == name].sort_values("year")[["title", "year", "genre", "revenue", "score"]]
    st.dataframe(films, hide_index=True, width="stretch",
                 column_config={"title": "Title", "genre": "Genre",
                                "revenue": st.column_config.NumberColumn("Revenue", format="compact"),
                                "score": st.column_config.NumberColumn("Score", format="%.1f"),
                                "year": st.column_config.NumberColumn("Year", format="%d")})
