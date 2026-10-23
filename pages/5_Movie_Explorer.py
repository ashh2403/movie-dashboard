"""
PAGE 5 - MOVIE EXPLORER (Module 6)
---------------------------------
Search for a movie, sort the table by any column (click a column header)
and download the filtered data as a CSV file.
"""

import streamlit as st

from src import ui
from src.charts import fmt_num
from src.filters import sidebar_filters, stop_if_empty

ui.setup_page("Movie Explorer", "🔎")
df, full_df, _ = sidebar_filters()
ui.page_header("MOVIE", "EXPLORER", "Search, sort and download the movie data")

c1, c2, c3 = st.columns([3, 2, 1])
query = c1.text_input("Search title, star, director or company", placeholder="e.g. Avengers, Tom Hanks, Pixar")
sort_by = c2.selectbox("Sort by", ["revenue", "score", "budget", "profit", "votes", "year", "title"],
                       format_func=str.title)
descending = c3.toggle("Highest first", value=True)

# Search across several text columns (not case-sensitive)
result = df
if query:
    q = query.strip()
    match = False
    for col in ["title", "star", "director", "company", "writer"]:
        match = match | result[col].str.contains(q, case=False, regex=False)
    result = result[match]

stop_if_empty(result)
result = result.sort_values(sort_by, ascending=not descending)

st.markdown(f"**{len(result):,} movies** · total revenue {fmt_num(result['revenue'].sum())} · "
            f"average score {result['score'].mean():.2f}")

columns = ["title", "year", "genre", "certificate", "score", "votes", "revenue", "budget",
           "profit", "director", "star", "company", "country", "runtime"]
st.dataframe(
    result[columns], hide_index=True, width="stretch", height=520,
    column_config={
        "title": st.column_config.TextColumn("Title", width="medium"),
        "genre": "Genre", "certificate": "Certificate", "director": "Director",
        "star": "Star", "company": "Company", "country": "Country",
        "year": st.column_config.NumberColumn("Year", format="%d"),
        "score": st.column_config.NumberColumn("Score", format="%.1f"),
        "votes": st.column_config.NumberColumn("Votes", format="compact"),
        "revenue": st.column_config.NumberColumn("Revenue", format="compact"),
        "budget": st.column_config.NumberColumn("Budget", format="compact"),
        "profit": st.column_config.NumberColumn("Profit", format="compact"),
        "runtime": st.column_config.NumberColumn("Runtime (min)", format="%d"),
    })

# Download exactly what is shown (sidebar filters + search + sort)
csv = result[columns].to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download filtered data (CSV)", csv, file_name="filtered_movies.csv",
                   mime="text/csv", type="primary")

# Detail card for one movie
st.markdown("#### Movie details")
choice = st.selectbox("Pick a movie", result["title"] + " (" + result["year"].astype(str) + ")")
if choice:
    movie = result[(result["title"] + " (" + result["year"].astype(str) + ")") == choice].iloc[0]
    ui.kpi_cards([
        ("Revenue", fmt_num(movie["revenue"]), f"Budget {fmt_num(movie['budget'])}", "revenue"),
        ("Profit", fmt_num(movie["profit"]),
         f"ROI {movie['roi']:.0%}" if movie["budget"] > 0 else "No budget data", "budget"),
        ("Score", f"{movie['score']:.1f} / 10", f"{fmt_num(movie['votes'])} votes", "star"),
        ("Certificate", movie["certificate"], f"{movie['genre']} · {movie['runtime']:.0f} min", "ticket"),
    ])
    st.caption(f"Directed by {movie['director']} · starring {movie['star']} · written by {movie['writer']} · "
               f"{movie['company']} · released {movie['released']}")
