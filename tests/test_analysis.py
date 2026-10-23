"""
TESTS (Testing Plan T-01 to T-06 in the report)
-----------------------------------------------
Run with:   pytest
Checks that the Python results match the Power BI dashboard.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import analysis, insights                     # noqa: E402
from src.charts import fmt_num                          # noqa: E402
from src.data_loader import COLUMN_NAMES, load_data, load_raw_data  # noqa: E402
from src.filters import apply_filters                   # noqa: E402
from src.preprocessing import clean_data, find_remakes, get_clean_data  # noqa: E402


@pytest.fixture(scope="module")
def df():
    return get_clean_data()


# ---- T-01 Module 1: data loads without unintended changes ------------------
def test_raw_file_has_5421_rows_and_15_columns():
    raw = load_raw_data()
    assert raw.shape == (5421, 15)


def test_columns_are_renamed():
    assert list(load_data().columns) == list(COLUMN_NAMES.values())


# ---- T-02 Module 2: missing values and duplicates --------------------------
def test_no_duplicates_after_cleaning(df):
    assert not df.duplicated().any()
    assert not df.duplicated(["title", "year"]).any()


def test_no_missing_values_in_key_columns(df):
    assert df[["title", "genre", "year", "revenue", "score", "budget"]].notna().all().all()


def test_cleaning_removes_duplicates_and_fills_gaps():
    """Feed the cleaner a small messy table and check every rule."""
    messy = pd.DataFrame({
        "title": ["A", "A", " B ", "C", "D", None],
        "genre": ["Action", "Action", "Drama", "Drama", "Comedy", "Comedy"],
        "year": [2000, 2000, 2001, 2002, 2003, 2004],
        "revenue": [10, 10, 20, None, 40, 50],
        "score": [7.0, 7.0, None, 6.0, 11.0, 5.0],   # 11 is impossible
        "director": ["X", "X", "Y", "Z", "W", "V"],
        "star": ["P", "P", "Q", "R", "S", "T"],
        "budget": [5, 5, 10, 10, 10, 10],
        "votes": [1, 1, 2, 3, 4, 5],
        "runtime": [90, 90, 100, 100, 100, 100],
        "country": ["US"] * 6, "company": ["Co"] * 6,
        "released": ["June 1, 2000 (United States)"] * 6,
        "writer": ["Wr"] * 6,
        "certificate": ["R", "R", "Unrated", "PG", "PG", "PG"],
    })
    clean, log = clean_data(messy)
    assert clean["title"].tolist() == ["A", "B"]        # dup, missing title/revenue, score 11 removed
    assert clean.loc[1, "certificate"] == "Not Rated"   # inconsistent label fixed
    assert clean.loc[1, "score"] == pytest.approx(7.0)  # missing score -> median of 7, 7, 11
    assert len(log) == 9


def test_remakes_are_kept_not_removed(df):
    remakes = find_remakes(df)
    assert "Aladdin" in set(remakes["title"])
    assert remakes["title"].nunique() == 84


# ---- Totals must match the Power BI dashboard -----------------------------
def test_totals_match_power_bi(df):
    k = analysis.kpis(df)
    assert k["movies"] == 5421
    assert fmt_num(k["revenue"]) == "560bn"
    assert fmt_num(k["budget"]) == "195bn"
    assert k["score_sum"] == pytest.approx(34653.5)


# ---- T-03 / T-04 Module 3: genre and year analysis ------------------------
def test_top_genre_by_total_revenue_is_action(df):
    assert analysis.genre_summary(df).iloc[0]["genre"] == "Action"


def test_genre_totals_add_up_to_overall_total(df):
    assert analysis.genre_summary(df)["total_revenue"].sum() == df["revenue"].sum()


def test_min_movies_hides_small_genres(df):
    shown = set(analysis.avg_revenue_by_genre(df, min_movies=10)["genre"])
    assert "Family" not in shown                       # only 4 movies
    assert "Family" in set(analysis.avg_revenue_by_genre(df, min_movies=1)["genre"])


def test_yearly_revenue_adds_up(df):
    assert analysis.revenue_by_year(df)["revenue"].sum() == df["revenue"].sum()


# ---- T-06 Module 5: actor and director rankings ---------------------------
def test_top_star_is_robert_downey_jr(df):
    assert analysis.top_people_by_revenue(df, "star", 1).iloc[0]["star"] == "Robert Downey Jr."


def test_top_director_is_steven_spielberg(df):
    assert analysis.top_people_by_revenue(df, "director", 1).iloc[0]["director"] == "Steven Spielberg"


# ---- T-05 filters ---------------------------------------------------------
def test_filters_and_empty_result(df):
    action = apply_filters(df, ["Action"], (2000, 2010), [])
    assert set(action["genre"]) == {"Action"}
    assert action["year"].between(2000, 2010).all()
    empty = apply_filters(df, ["Western"], (2015, 2020), ["G"])
    assert len(empty) == 0


# ---- Module 6: insights come from the data --------------------------------
def test_insights_use_real_numbers(df):
    cards = insights.key_insights(df)
    assert len(cards) == 4
    assert "Action" in cards[1]["text"]
    assert "Steven Spielberg" in cards[2]["text"]


def test_insights_change_with_filter(df):
    drama = apply_filters(df, ["Drama"], (1980, 2020), [])
    assert "Drama" in insights.genre_insight(drama)["text"]


def test_budget_roi_skips_zero_budget():
    data = pd.DataFrame({"title": ["a", "b"], "genre": ["X", "X"], "budget": [0, 10],
                         "revenue": [5, 30], "profit": [5, 20], "roi": [None, 2.0]})
    assert len(analysis.with_budget(data)) == 1


def test_number_format():
    assert fmt_num(559_607_950_720) == "560bn"
    assert fmt_num(12_000_000) == "12M"
    assert fmt_num(5_421) == "5.4K"
    assert fmt_num(34_653.5) == "34.7K"
