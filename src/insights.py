"""
MODULE 6 - MARKET INSIGHTS
--------------------------
Builds the "KEY INSIGHTS INTO MARKET TRENDS" cards.
Nothing is hard-coded: every sentence is created from numbers calculated
on the CURRENTLY FILTERED data, so the insights change with the filters.
"""

import math

import pandas as pd

from src import analysis
from src.charts import fmt_num


def describe_correlation(r: float) -> str:
    """Turn a correlation number into words (used in the viva too)."""
    if r is None or math.isnan(r):
        return "not measurable"
    size = abs(r)
    if size < 0.1:
        strength = "negligible"
    elif size < 0.3:
        strength = "weak"
    elif size < 0.5:
        strength = "moderate"
    else:
        strength = "strong"
    direction = "positive" if r > 0 else "negative"
    return f"{strength} {direction}"


def revenue_growth_insight(df: pd.DataFrame) -> dict:
    """Insight 1 - last 5 release years vs first 5 release years."""
    g = analysis.revenue_growth(df, n_years=5)
    if not g["ok"]:
        return {"title": "1. REVENUE GROWTH",
                "text": "Select a range of at least 10 release years to compare early and recent revenue.",
                "takeaway": "Not enough years in the current filter."}
    first = f"{g['first_years'][0]}-{g['first_years'][1]}"
    last = f"{g['last_years'][0]}-{g['last_years'][1]}"
    direction = "higher" if g["growth_pct"] >= 0 else "lower"
    # Warn when the newest year has far fewer movies than usual (e.g. 2020)
    yearly = analysis.revenue_by_year(df)
    newest = yearly.iloc[-1]
    note = ""
    if newest["movies"] < 0.5 * yearly["movies"].median():
        note = f" Note: {int(newest['year'])} has only {int(newest['movies'])} movies."
    return {
        "title": "1. REVENUE GROWTH",
        "text": (f"Movies released in {last} earned {fmt_num(g['last_total'])}, "
                 f"{abs(g['growth_pct']):,.0f}% {direction} than the {fmt_num(g['first_total'])} "
                 f"earned in {first}. The peak year was {g['peak_year']} "
                 f"({fmt_num(g['peak_revenue'])}).{note}"),
        "takeaway": ("Revenue has grown over time" if g["growth_pct"] >= 0 else "Revenue has fallen over time")
                    + " (figures are not inflation-adjusted).",
        "value": g["growth_pct"],
    }


def genre_insight(df: pd.DataFrame) -> dict:
    """Insight 2 - how concentrated revenue is in the leading genre(s)."""
    genres = analysis.genre_summary(df)
    top = genres.iloc[0]
    top3_share = genres.head(3)["revenue_share"].sum()
    if len(genres) == 1:
        text = f"Only {top['genre']} is selected: {fmt_num(top['total_revenue'])} from {top['movies']:,} movies."
    else:
        text = (f"{top['genre']} leads with {fmt_num(top['total_revenue'])}, "
                f"{top['revenue_share']:.0%} of all revenue from {top['movies']:,} movies. "
                f"The top 3 genres together earn {top3_share:.0%}.")
    # "even" share would be 1 / number of genres; compare the leader with that
    even_share = 1 / len(genres)
    if len(genres) == 1:
        takeaway = "Select more genres to compare them."
    elif top["revenue_share"] > 2 * even_share:
        takeaway = f"Revenue is concentrated: {top['genre']} earns over twice an even share."
    else:
        takeaway = "Revenue is fairly evenly spread across the selected genres."
    return {"title": "2. GENRE PERFORMANCE", "text": text,
            "takeaway": takeaway,
            "value": top["revenue_share"], "top_genre": top["genre"]}


def director_insight(df: pd.DataFrame) -> dict:
    """Insight 3 - share of revenue earned by the top 10 directors."""
    top = analysis.top_people_by_revenue(df, "director", 10)
    share = analysis.top_n_share(df, "director", 10)
    movie_share = top["movies"].sum() / len(df)
    n_directors = df["director"].nunique()
    best = top.iloc[0]
    return {
        "title": "3. DIRECTOR IMPACT",
        "text": (f"The top {len(top)} of {n_directors:,} directors earn {share:.0%} of revenue "
                 f"while making only {movie_share:.0%} of the movies. "
                 f"{best['director']} leads with {fmt_num(best['total_revenue'])} "
                 f"from {best['movies']} films."),
        "takeaway": (f"Top directors earn {share / movie_share:.1f}x their share of movies."
                     if movie_share else ""),
        "value": share,
    }


def rating_insight(df: pd.DataFrame, min_movies: int = 10) -> dict:
    """Insight 4 - is a higher score linked to higher revenue?"""
    r_score = analysis.correlation(df, "score", "revenue")
    r_votes = analysis.correlation(df, "votes", "revenue")
    by_genre = analysis.score_by_group(df, "genre", min_movies)
    best = (f" {by_genre.iloc[0]['genre']} has the highest average score "
            f"({by_genre.iloc[0]['avg_score']:.2f})." if len(by_genre) else "")
    if math.isnan(r_score) or math.isnan(r_votes):
        text = "Too few movies in the current filter to measure the rating-revenue link."
        takeaway = "Widen the filters to measure this."
    else:
        text = (f"Score vs revenue correlation is {r_score:.2f} ({describe_correlation(r_score)}); "
                f"votes vs revenue is {r_votes:.2f} ({describe_correlation(r_votes)}).{best}")
        if abs(r_votes) > abs(r_score):
            takeaway = "Popularity (votes) is linked to revenue more than the score is."
        else:
            takeaway = "The score is linked to revenue more than popularity (votes) is."
    return {"title": "4. AUDIENCE RATINGS", "text": text,
            "takeaway": takeaway, "value": r_score}


def key_insights(df: pd.DataFrame, min_movies: int = 10) -> list:
    """The four cards shown at the bottom of the Home page."""
    return [revenue_growth_insight(df), genre_insight(df),
            director_insight(df), rating_insight(df, min_movies)]


def extra_insights(df: pd.DataFrame, min_movies: int = 10) -> list:
    """Short extra facts used on the inner pages and in the results chapter."""
    facts = []
    cert = analysis.movies_by_certificate(df)
    if len(cert):
        facts.append(f"{cert.iloc[0]['certificate']} is the most common certificate "
                     f"({cert.iloc[0]['share']:.0%} of movies).")
    roi = analysis.roi_by_genre(df, min_movies)
    if len(roi):
        facts.append(f"{roi.iloc[0]['genre']} has the best median ROI "
                     f"({roi.iloc[0]['median_roi']:.0%} return on budget).")
    facts.append(f"{analysis.loss_share(df):.0%} of movies earned less than their budget.")
    star = analysis.top_people_by_revenue(df, "star", 1)
    if len(star):
        facts.append(f"{star.iloc[0]['star']} is the top star by revenue "
                     f"({fmt_num(star.iloc[0]['total_revenue'])}).")
    return facts
