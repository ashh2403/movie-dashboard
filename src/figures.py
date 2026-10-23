"""
ALL DASHBOARD CHARTS IN ONE PLACE
---------------------------------
Each function takes the (filtered) movie data and returns a finished Plotly
figure. The dashboard pages show these figures, and scripts/export_figures.py
saves the very same figures as PNG files for the report - so the report
pictures always match the live dashboard.
"""

import pandas as pd
import plotly.graph_objects as go

from src import analysis
from src import charts as ch


# ---------------- MODULE 3 - REVENUE & GENRE ----------------
def revenue_by_genre(df: pd.DataFrame, min_movies: int = 10):
    data = analysis.genre_summary(df)
    return ch.bar_chart(data, "genre", "total_revenue", "Total Revenue by Genre",
                        x_title="Genre", y_title="Total revenue (USD)", horizontal=False,
                        hover_extra={"movies": "Movies"}, colour=ch.CORAL,
                        subtitle="Combined box office per genre, USD")


def avg_revenue_by_genre(df: pd.DataFrame, min_movies: int = 10):
    data = analysis.avg_revenue_by_genre(df, min_movies)
    hidden = df["genre"].nunique() - len(data)
    note = f"USD per movie · genres with ≥ {min_movies} movies" + (f" ({hidden} small genres hidden)" if hidden else "")
    return ch.bar_chart(data, "genre", "avg_revenue", "Average Revenue by Genre",
                        x_title="Average revenue per movie (USD)", y_title="Genre",
                        hover_extra={"movies": "Movies", "median_revenue": "Median revenue"},
                        subtitle=note, colour=ch.TEAL)


def revenue_by_year(df: pd.DataFrame, min_movies: int = 10, height: int = 380):
    """Revenue per release year. An incomplete final year (2020 has only 8
    movies, all released Jan-Sep) is drawn as a dashed segment and labelled,
    so its drop is not mistaken for a real collapse in the box office."""
    data = analysis.revenue_by_year(df)
    partial = analysis.incomplete_final_year(df) if len(data) > 2 else None
    complete = data.iloc[:-1] if partial else data
    fig = ch.line_chart(complete, "year", "revenue", "Total Revenue by Release Year",
                        x_title="Release year", y_title="Total revenue (USD)",
                        hover_extra={"movies": "Movies"}, fill=True, height=height,
                        subtitle="Nominal USD · not adjusted for inflation")
    if partial:
        # dotted muted segment from the last complete year into the partial year;
        # the real value is still plotted and shown in the tooltip
        tail = data.tail(2)
        fig.add_scatter(x=tail["year"], y=tail["revenue"], mode="lines+markers",
                        line=dict(color=ch.MUTED, width=2, dash="dot"),
                        marker=dict(size=[0, 9], color=ch.CARD, line=dict(color=ch.MUTED, width=2)),
                        customdata=list(zip(tail["revenue"].map(ch.fmt_num), tail["movies"])),
                        hovertemplate="<b>%{x}</b><br>Total revenue (USD): %{customdata[0]}"
                                      "<br>Movies: %{customdata[1]}<extra></extra>")
        fig.add_vrect(x0=partial["year"] - 0.5, x1=partial["year"] + 0.5, line_width=0,
                      fillcolor=ch.rgba(ch.MUTED, 0.08), layer="below")
        fig.add_annotation(
            x=partial["year"], y=partial["revenue"], xanchor="right", yanchor="bottom",
            text=(f"<b>{partial['year']}: incomplete data</b><br>"
                  f"only {partial['movies']} movies ({partial['months']})<br>"
                  f"vs a typical {partial['typical']:.0f} per year"),
            showarrow=True, arrowcolor=ch.MUTED, arrowwidth=1.2, ax=-28, ay=-58, align="right",
            font=dict(color=ch.TEXT, size=11), bgcolor=ch.SURFACE, bordercolor=ch.BORDER, borderpad=6)
    return fig


def movies_by_certificate(df: pd.DataFrame, min_movies: int = 10):
    data = analysis.movies_by_certificate(df)
    return ch.donut_chart(data, "certificate", "movies", "Count of Movies by Certificate",
                          centre_label="Movies", subtitle="Content rating (R, PG-13, PG ...)")


def revenue_share_by_decade(df: pd.DataFrame, min_movies: int = 10):
    """Share of each decade's revenue earned by the top genres."""
    data = analysis.genre_revenue_by_decade(df)
    top_genres = analysis.genre_summary(df).head(5)["genre"].tolist()
    data["genre"] = data["genre"].where(data["genre"].isin(top_genres), "Other")
    data = data.groupby(["decade", "genre"], as_index=False)["revenue"].sum()
    data["share"] = data["revenue"] / data.groupby("decade")["revenue"].transform("sum")
    # show the movie count under each decade, e.g. "2020s (8 movies)", so tiny decades are obvious
    counts = df.groupby("decade").size()
    data["decade"] = data["decade"].map(lambda d: f"{d}<br>({counts[d]:,} movies)")
    fig = go.Figure()
    order = top_genres + (["Other"] if "Other" in set(data["genre"]) else [])
    for i, genre in enumerate(order):
        part = data[data["genre"] == genre]
        colour = ch.OTHER_COLOUR if genre == "Other" else ch.CATEGORY_COLOURS[i]
        fig.add_bar(x=part["decade"], y=part["share"], name=genre,
                    marker=dict(color=colour, line=dict(color=ch.PANEL, width=2)),
                    customdata=part["revenue"].map(ch.fmt_num),
                    hovertemplate=f"<b>{genre}</b> %{{x}}<br>Share: %{{y:.0%}}<br>Revenue: %{{customdata}}<extra></extra>")
    ch.style(fig, "Genre Share of Revenue by Decade", "Decade", "Share of decade revenue",
             subtitle="Top 5 genres; the rest grouped as Other")
    fig.update_layout(barmode="stack", showlegend=True, legend=dict(font=dict(color=ch.TEXT)))
    fig.update_yaxes(tickformat=".0%")
    return fig


# ---------------- MODULE 4 - RATING TRENDS ----------------
def score_distribution(df: pd.DataFrame, min_movies: int = 10):
    fig = ch.histogram(df, "score", "Distribution of Rating Scores", x_title="Rating score (out of 10)",
                       subtitle="How many movies received each score")
    return ch.add_average_line(fig, df["score"].mean(), f"Mean {df['score'].mean():.2f}", axis="x")


def avg_score_by_year(df: pd.DataFrame, min_movies: int = 10):
    data = analysis.score_by_year(df)
    fig = ch.line_chart(data, "year", "avg_score", "Average Rating Score by Release Year",
                        x_title="Release year", y_title="Average score", money=False,
                        hover_extra={"movies": "Movies"})
    return fig


def avg_score_by_genre(df: pd.DataFrame, min_movies: int = 10):
    data = analysis.score_by_group(df, "genre", min_movies)
    fig = ch.bar_chart(data, "genre", "avg_score", "Average Rating Score by Genre",
                       x_title="Average score (out of 10)", y_title="Genre", money=False,
                       hover_extra={"movies": "Movies"},
                       subtitle=f"Genres with at least {min_movies} movies")
    if len(data):
        lo = max(0, data["avg_score"].min() - 0.5)
        fig.update_xaxes(range=[lo, min(10, data["avg_score"].max() + 0.3)])
    return fig


def avg_score_by_certificate(df: pd.DataFrame, min_movies: int = 10):
    data = analysis.score_by_group(df, "certificate", min_movies)
    fig = ch.bar_chart(data, "certificate", "avg_score", "Average Rating Score by Certificate",
                       x_title="Average score (out of 10)", y_title="Certificate", money=False,
                       hover_extra={"movies": "Movies"},
                       subtitle=f"Certificates with at least {min_movies} movies")
    if len(data):
        fig.update_xaxes(range=[max(0, data["avg_score"].min() - 0.5), min(10, data["avg_score"].max() + 0.3)])
    return fig


def score_vs_revenue(df: pd.DataFrame, min_movies: int = 10):
    r = analysis.correlation(df, "score", "revenue")
    return ch.scatter_chart(df, "score", "revenue", "Rating Score vs Revenue",
                            x_title="Rating score", y_title="Revenue (USD)", money_y=True, log_y=True,
                            subtitle=f"Each dot is a movie · correlation r = {r:.2f} · log scale")


def votes_vs_score(df: pd.DataFrame, min_movies: int = 10):
    r = analysis.correlation(df, "votes", "score")
    trend = "Popular movies tend to score higher" if r >= 0.1 else (
        "Popular movies tend to score lower" if r <= -0.1 else "Little link between votes and score")
    return ch.scatter_chart(df, "votes", "score", "Number of Votes vs Rating Score",
                            x_title="Votes", y_title="Rating score", money_x=True, log_x=True,
                            subtitle=f"{trend} · r = {r:.2f} · log scale")


# ---------------- MODULE 5 - ACTORS & DIRECTORS ----------------
def top_stars_by_revenue(df: pd.DataFrame, min_movies: int = 10, n: int = 10):
    data = analysis.top_people_by_revenue(df, "star", n)
    return ch.bar_chart(data, "star", "total_revenue", f"Top {n} Stars by Total Revenue",
                        x_title="Total revenue (USD)", y_title="",
                        hover_extra={"movies": "Movies", "avg_score": "Average score"},
                        subtitle="Lead actor's combined box office, USD")


def top_directors_by_revenue(df: pd.DataFrame, min_movies: int = 10, n: int = 10):
    data = analysis.top_people_by_revenue(df, "director", n)
    return ch.bar_chart(data, "director", "total_revenue", f"Top {n} Directors by Total Revenue",
                        x_title="Total revenue (USD)", y_title="",
                        hover_extra={"movies": "Movies", "avg_score": "Average score"},
                        subtitle="Combined box office of each director's movies, USD", colour=ch.PURPLE)


def top_directors_area(df: pd.DataFrame, min_movies: int = 10, n: int = 12):
    """Area chart of the top directors (same style as the Power BI dashboard)."""
    data = analysis.top_people_by_revenue(df, "director", n)
    fig = ch.line_chart(data, "director", "total_revenue", "Total Revenue by Director",
                        x_title="Director", y_title="Total revenue (USD)", area=True,
                        hover_extra={"movies": "Movies"}, colour=ch.PURPLE,
                        subtitle=f"Top {len(data)} directors · USD, all their movies combined")
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=10))
    return fig


def top_people_by_score(df: pd.DataFrame, person: str, min_people_movies: int = 5, n: int = 10):
    data = analysis.top_people_by_score(df, person, n, min_people_movies)
    label = "Stars" if person == "star" else "Directors"
    fig = ch.bar_chart(data, person, "avg_score", f"Top {n} {label} by Average Score",
                       x_title="Average score (out of 10)", y_title=label[:-1], money=False,
                       hover_extra={"movies": "Movies", "total_revenue": "Total revenue"},
                       subtitle=f"Only {label.lower()} with at least {min_people_movies} movies")
    if len(data):
        fig.update_xaxes(range=[max(0, data["avg_score"].min() - 0.5), min(10, data["avg_score"].max() + 0.2)])
    return fig


def top_directors_by_score(df: pd.DataFrame, min_movies: int = 10):
    return top_people_by_score(df, "director", 5)


def top_stars_by_score(df: pd.DataFrame, min_movies: int = 10):
    return top_people_by_score(df, "star", 5)


# ---------------- BUDGET & ROI ----------------
def budget_vs_revenue(df: pd.DataFrame, min_movies: int = 10):
    data = analysis.with_budget(df)
    r = analysis.correlation(data, "budget", "revenue")
    fig = ch.scatter_chart(data, "budget", "revenue", "Budget vs Revenue",
                           x_title="Budget (USD)", y_title="Revenue (USD)",
                           money_x=True, money_y=True, log_x=True, log_y=True, trendline=False,
                           subtitle=f"Dots above the dashed teal line made a profit · r = {r:.2f} · log scale")
    if len(data):
        low = max(1, min(data["budget"].min(), data["revenue"].min()))
        high = max(data["budget"].max(), data["revenue"].max())
        fig.add_scatter(x=[low, high], y=[low, high], mode="lines", hoverinfo="skip",
                        line=dict(color=ch.TEAL, dash="dash", width=2), name="Break-even")
    return fig


def median_roi_by_genre(df: pd.DataFrame, min_movies: int = 10):
    data = analysis.roi_by_genre(df, min_movies)
    data = data.assign(roi_pct=data["median_roi"] * 100)
    fig = ch.bar_chart(data, "genre", "roi_pct", "Median ROI by Genre",
                       x_title="Median ROI (%)", y_title="Genre", money=False,
                       hover_extra={"movies": "Movies", "median_profit": "Median profit"},
                       subtitle=f"ROI = (revenue − budget) ÷ budget · genres with ≥ {min_movies} movies",
                       colour=ch.TEAL)
    fig.update_xaxes(ticksuffix="%")
    return fig


def median_profit_by_genre(df: pd.DataFrame, min_movies: int = 10):
    data = analysis.roi_by_genre(df, min_movies).sort_values("median_profit", ascending=False)
    return ch.bar_chart(data, "genre", "median_profit", "Median Profit by Genre",
                        x_title="Median profit per movie (USD)", y_title="Genre",
                        hover_extra={"movies": "Movies"},
                        subtitle=f"Profit = revenue − budget · genres with ≥ {min_movies} movies")


def top_profit_movies(df: pd.DataFrame, min_movies: int = 10):
    data = analysis.top_profit_movies(df, 10)
    data = data.assign(label=data["title"] + " (" + data["year"].astype(str) + ")")
    return ch.bar_chart(data, "label", "profit", "Top 10 Most Profitable Movies",
                        x_title="Profit (USD)", y_title="",
                        hover_extra={"budget": "Budget", "revenue": "Revenue"},
                        subtitle="Profit = revenue − budget, USD", colour=ch.TEAL)


# Figures exported for the report, in Chapter 5 order: (file name, function)
REPORT_FIGURES = [
    ("fig5_2_revenue_by_genre", revenue_by_genre),
    ("fig5_3_avg_revenue_by_genre", avg_revenue_by_genre),
    ("fig5_4_revenue_by_year", revenue_by_year),
    ("fig5_5_genre_share_by_decade", revenue_share_by_decade),
    ("fig5_6_movies_by_certificate", movies_by_certificate),
    ("fig5_7_score_distribution", score_distribution),
    ("fig5_8_avg_score_by_year", avg_score_by_year),
    ("fig5_9_avg_score_by_genre", avg_score_by_genre),
    ("fig5_10_score_vs_revenue", score_vs_revenue),
    ("fig5_11_votes_vs_score", votes_vs_score),
    ("fig5_12_top_stars_by_revenue", top_stars_by_revenue),
    ("fig5_13_top_directors_by_revenue", top_directors_by_revenue),
    ("fig5_14_top_directors_by_score", top_directors_by_score),
    ("fig5_15_budget_vs_revenue", budget_vs_revenue),
    ("fig5_16_median_roi_by_genre", median_roi_by_genre),
]
