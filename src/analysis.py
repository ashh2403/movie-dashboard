"""
ANALYSIS FUNCTIONS (MODULES 3, 4 and 5)
---------------------------------------
Pure pandas functions: each takes a DataFrame and returns a small table
or a number. There is NO Streamlit code here, so the same functions are
used by the dashboard, the tests, the notebook and the figure export script.

  Module 3 - Revenue & Genre Analysis
  Module 4 - Rating Trend Analysis
  Module 5 - Actor & Director Analysis
  (+ Budget & ROI, used by the Budget page)
"""

import pandas as pd


# ---------------------------------------------------------------------------
# Overview KPIs (used by the Home page cards)
# ---------------------------------------------------------------------------
def kpis(df: pd.DataFrame) -> dict:
    """The headline numbers shown on the yellow KPI cards."""
    return {
        "movies": len(df),
        "revenue": df["revenue"].sum(),
        "score_sum": df["score"].sum(),
        "budget": df["budget"].sum(),
        "avg_score": df["score"].mean() if len(df) else 0,
        "avg_revenue": df["revenue"].mean() if len(df) else 0,
    }


def movies_by_certificate(df: pd.DataFrame) -> pd.DataFrame:
    """How many movies have each certificate (R, PG-13, ...)."""
    out = df["certificate"].value_counts().rename_axis("certificate").reset_index(name="movies")
    out["share"] = out["movies"] / out["movies"].sum()
    return out


# ---------------------------------------------------------------------------
# MODULE 3 - REVENUE & GENRE ANALYSIS
# ---------------------------------------------------------------------------
def genre_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Total revenue, average revenue and movie count for every genre."""
    out = (df.groupby("genre")
             .agg(total_revenue=("revenue", "sum"),
                  avg_revenue=("revenue", "mean"),
                  median_revenue=("revenue", "median"),
                  movies=("title", "count"),
                  avg_score=("score", "mean"))
             .reset_index()
             .sort_values("total_revenue", ascending=False))
    out["revenue_share"] = out["total_revenue"] / out["total_revenue"].sum()
    return out.reset_index(drop=True)


def avg_revenue_by_genre(df: pd.DataFrame, min_movies: int = 10) -> pd.DataFrame:
    """Average revenue per genre, keeping only genres with at least `min_movies` films.

    Small genres (e.g. Family has only 4 movies) give misleading averages,
    so they are hidden unless the user lowers the minimum.
    """
    out = genre_summary(df)
    out = out[out["movies"] >= min_movies]
    return out.sort_values("avg_revenue", ascending=False).reset_index(drop=True)


def revenue_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Total revenue and movie count for every release year."""
    return (df.groupby("year")
              .agg(revenue=("revenue", "sum"), movies=("title", "count"),
                   avg_revenue=("revenue", "mean"))
              .reset_index()
              .sort_values("year"))


def incomplete_final_year(df: pd.DataFrame, threshold: float = 0.5):
    """Detect a final release year with far fewer movies than usual.

    The dataset has only 8 movies for 2020 (all released January-September)
    against a median of ~144 per year, so 2020's total revenue is NOT
    comparable with other years. Returns None when the last year looks normal,
    otherwise a dict describing it (used for chart annotations and warnings).
    """
    yearly = revenue_by_year(df)
    if len(yearly) < 3:
        return None
    last = yearly.iloc[-1]
    typical = yearly["movies"].iloc[:-1].median()
    if last["movies"] >= threshold * typical:
        return None
    dates = (df.loc[df["year"] == last["year"], "release_date"].dropna()
             if "release_date" in df.columns else pd.Series(dtype="datetime64[ns]"))
    months = (f"released {dates.min():%b}–{dates.max():%b}" if len(dates) else "release dates unknown")
    return {"year": int(last["year"]), "movies": int(last["movies"]), "revenue": float(last["revenue"]),
            "typical": float(typical), "months": months}


def yearly_series(df: pd.DataFrame) -> pd.DataFrame:
    """Per-year movies, revenue, budget and average score (for KPI sparklines)."""
    return (df.groupby("year")
              .agg(movies=("title", "count"), revenue=("revenue", "sum"),
                   budget=("budget", "sum"), avg_score=("score", "mean"))
              .reset_index().sort_values("year"))


def genre_revenue_by_decade(df: pd.DataFrame) -> pd.DataFrame:
    """Total revenue for each genre in each decade (for a stacked chart)."""
    return (df.groupby(["decade", "genre"])["revenue"].sum()
              .reset_index().sort_values(["decade", "revenue"], ascending=[True, False]))


def revenue_growth(df: pd.DataFrame, n_years: int = 5) -> dict:
    """Compare total revenue of the LAST n release years with the FIRST n years."""
    yearly = revenue_by_year(df)
    if len(yearly) < 2 * n_years:
        return {"ok": False}
    first, last = yearly.head(n_years), yearly.tail(n_years)
    first_total, last_total = first["revenue"].sum(), last["revenue"].sum()
    return {
        "ok": True,
        "first_years": (int(first["year"].min()), int(first["year"].max())),
        "last_years": (int(last["year"].min()), int(last["year"].max())),
        "first_total": first_total,
        "last_total": last_total,
        "growth_pct": (last_total / first_total - 1) * 100 if first_total else 0,
        "peak_year": int(yearly.loc[yearly["revenue"].idxmax(), "year"]),
        "peak_revenue": yearly["revenue"].max(),
    }


# ---------------------------------------------------------------------------
# MODULE 4 - RATING TREND ANALYSIS
# ---------------------------------------------------------------------------
def score_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Average score and movie count for every release year."""
    return (df.groupby("year")
              .agg(avg_score=("score", "mean"), movies=("title", "count"))
              .reset_index())


def score_by_group(df: pd.DataFrame, column: str, min_movies: int = 10) -> pd.DataFrame:
    """Average score per genre / certificate / country (groups with >= min_movies films)."""
    out = (df.groupby(column)
             .agg(avg_score=("score", "mean"), median_score=("score", "median"),
                  movies=("title", "count"), avg_revenue=("revenue", "mean"))
             .reset_index())
    out = out[out["movies"] >= min_movies]
    return out.sort_values("avg_score", ascending=False).reset_index(drop=True)


def score_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Group movies into score bands and show average revenue for each band."""
    bins = [0, 5, 6, 7, 8, 10]
    labels = ["Below 5", "5 - 6", "6 - 7", "7 - 8", "8 and above"]
    bands = pd.cut(df["score"], bins=bins, labels=labels, right=False, include_lowest=True)
    return (df.groupby(bands, observed=False)
              .agg(movies=("title", "count"), avg_revenue=("revenue", "mean"))
              .rename_axis("score_band").reset_index())


def correlation(df: pd.DataFrame, col_a: str, col_b: str) -> float:
    """Pearson correlation between two number columns (-1 to +1)."""
    if len(df) < 3:
        return float("nan")
    return float(df[col_a].corr(df[col_b]))


# ---------------------------------------------------------------------------
# MODULE 5 - ACTOR & DIRECTOR ANALYSIS
# ---------------------------------------------------------------------------
def people_summary(df: pd.DataFrame, person: str) -> pd.DataFrame:
    """Revenue, movie count and average score for every star or director.

    `person` must be "star" or "director".
    """
    return (df.groupby(person)
              .agg(total_revenue=("revenue", "sum"),
                   avg_revenue=("revenue", "mean"),
                   movies=("title", "count"),
                   avg_score=("score", "mean"))
              .reset_index())


def top_people_by_revenue(df: pd.DataFrame, person: str, n: int = 10) -> pd.DataFrame:
    """Top n stars / directors by TOTAL revenue."""
    return (people_summary(df, person)
            .sort_values("total_revenue", ascending=False).head(n).reset_index(drop=True))


def top_people_by_score(df: pd.DataFrame, person: str, n: int = 10, min_movies: int = 5) -> pd.DataFrame:
    """Top n stars / directors by AVERAGE score (only people with >= min_movies films)."""
    out = people_summary(df, person)
    out = out[out["movies"] >= min_movies]
    return (out.sort_values(["avg_score", "movies"], ascending=False)
               .head(n).reset_index(drop=True))


def top_n_share(df: pd.DataFrame, person: str, n: int = 10) -> float:
    """Share (0-1) of all revenue earned by the top n stars / directors."""
    total = df["revenue"].sum()
    if total == 0:
        return 0.0
    return top_people_by_revenue(df, person, n)["total_revenue"].sum() / total


def star_director_pairs(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Most successful star + director combinations (2 or more films together)."""
    out = (df.groupby(["director", "star"])
             .agg(movies=("title", "count"), total_revenue=("revenue", "sum"),
                  avg_score=("score", "mean"))
             .reset_index())
    out = out[out["movies"] >= 2]
    return out.sort_values("total_revenue", ascending=False).head(n).reset_index(drop=True)


# ---------------------------------------------------------------------------
# BUDGET & ROI (supporting analysis for the Budget page)
# ---------------------------------------------------------------------------
def with_budget(df: pd.DataFrame) -> pd.DataFrame:
    """Only movies with a known budget (budget > 0); ROI is undefined otherwise."""
    return df[df["budget"] > 0]


def roi_by_genre(df: pd.DataFrame, min_movies: int = 10) -> pd.DataFrame:
    """Median ROI and median profit per genre.

    The MEDIAN is used because a few huge hits (ROI of 100x or more) would
    make the average misleading.
    """
    out = (with_budget(df).groupby("genre")
             .agg(median_roi=("roi", "median"), median_profit=("profit", "median"),
                  total_profit=("profit", "sum"), movies=("title", "count"))
             .reset_index())
    out = out[out["movies"] >= min_movies]
    return out.sort_values("median_roi", ascending=False).reset_index(drop=True)


def top_profit_movies(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Movies with the highest profit (revenue - budget)."""
    cols = ["title", "year", "genre", "budget", "revenue", "profit", "roi"]
    return with_budget(df).nlargest(n, "profit")[cols].reset_index(drop=True)


def loss_share(df: pd.DataFrame) -> float:
    """Share (0-1) of movies whose revenue was lower than their budget."""
    b = with_budget(df)
    return float((b["profit"] < 0).mean()) if len(b) else 0.0
