"""
MODULE 2 - DATA PREPROCESSING
-----------------------------
Cleans the raw data step by step:
  1. trim extra spaces in text columns
  2. convert number columns to real numbers
  3. handle missing values
  4. remove exact duplicate rows
  5. remove the same movie listed twice (same title AND same year)
  6. fix inconsistent certificate labels ("Unrated" -> "Not Rated")
  7. drop rows with impossible values (e.g. score above 10)
  8. add helper columns (profit, ROI, release date, decade)

Every step writes one entry into a CLEANING LOG so the Data Quality page
can show exactly what was changed and how many rows were affected.
"""

from functools import lru_cache

import pandas as pd

from src.data_loader import load_data

TEXT_COLUMNS = ["title", "genre", "director", "star", "country",
                "company", "released", "writer", "certificate"]
NUMBER_COLUMNS = ["year", "revenue", "score", "budget", "votes", "runtime"]

# A row without these values cannot be analysed, so it is removed
CRITICAL_COLUMNS = ["title", "genre", "year", "revenue"]

# Different spellings that mean the same certificate
CERTIFICATE_FIXES = {"Unrated": "Not Rated"}


def _log(log, step, description, before, after, affected):
    """Add one row to the cleaning log."""
    log.append({
        "Step": step,
        "What was done": description,
        "Rows before": before,
        "Rows after": after,
        "Values / rows affected": int(affected),
    })


def missing_values_report(df: pd.DataFrame) -> pd.DataFrame:
    """Number of missing (empty) values in every column."""
    blanks = df.isna() | df.astype(str).apply(lambda col: col.str.strip() == "")
    report = blanks.sum().rename("Missing values").to_frame()
    report.index.name = "Column"
    return report.reset_index()


def find_remakes(df: pd.DataFrame) -> pd.DataFrame:
    """Titles that appear more than once but with DIFFERENT years.

    These are remakes / different films that share a name (e.g. 'Aladdin'
    1992 and 2019), so they are NOT duplicates and are kept.
    """
    repeated = df[df.duplicated("title", keep=False)]
    return (repeated.sort_values(["title", "year"])
            [["title", "year", "genre", "director", "revenue"]]
            .reset_index(drop=True))


def clean_data(raw: pd.DataFrame):
    """Run all cleaning steps. Returns (clean_dataframe, cleaning_log_dataframe)."""
    df = raw.copy()
    log = []

    # Step 1 - trim spaces, e.g. " Action " -> "Action"
    before = len(df)
    changed = 0
    for col in TEXT_COLUMNS:
        original = df[col].astype("string")
        df[col] = original.str.strip().str.replace(r"\s+", " ", regex=True)
        changed += (original.fillna("") != df[col].fillna("")).sum()
    _log(log, "1. Trim text", "Removed extra spaces from text columns", before, len(df), changed)

    # Step 2 - make sure number columns really are numbers
    invalid = 0
    for col in NUMBER_COLUMNS:
        converted = pd.to_numeric(df[col], errors="coerce")
        invalid += (converted.isna() & df[col].notna()).sum()
        df[col] = converted
    _log(log, "2. Fix data types", "Converted year, revenue, score, budget, votes, runtime to numbers",
         before, len(df), invalid)

    # Step 3 - missing values
    df[TEXT_COLUMNS] = df[TEXT_COLUMNS].replace("", pd.NA)
    before = len(df)
    df = df.dropna(subset=CRITICAL_COLUMNS)
    _log(log, "3a. Missing critical values", "Dropped rows with no title, genre, year or revenue",
         before, len(df), before - len(df))

    filled = 0
    for col in TEXT_COLUMNS:
        filled += df[col].isna().sum()
        df[col] = df[col].fillna("Unknown")
    for col in ["score", "budget", "votes", "runtime"]:
        filled += df[col].isna().sum()
        df[col] = df[col].fillna(df[col].median())
    _log(log, "3b. Fill other gaps", "Text gaps -> 'Unknown', number gaps -> column median",
         len(df), len(df), filled)

    # Step 4 - exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    _log(log, "4. Exact duplicates", "Removed rows that are identical in every column",
         before, len(df), before - len(df))

    # Step 5 - same movie listed twice (same title in the same year)
    before = len(df)
    df = df.drop_duplicates(subset=["title", "year"], keep="first")
    _log(log, "5. Title + year duplicates", "Removed the same movie listed twice in one year",
         before, len(df), before - len(df))

    # Step 6 - inconsistent labels
    fixed = df["certificate"].isin(CERTIFICATE_FIXES.keys()).sum()
    df["certificate"] = df["certificate"].replace(CERTIFICATE_FIXES)
    _log(log, "6. Standardise certificates", "Merged 'Unrated' into 'Not Rated' (same meaning)",
         len(df), len(df), fixed)

    # Step 7 - impossible values
    before = len(df)
    valid = (df["score"].between(0, 10) & df["year"].between(1900, 2030)
             & (df["revenue"] >= 0) & (df["budget"] >= 0) & (df["runtime"] > 0))
    df = df[valid]
    _log(log, "7. Validate ranges", "Dropped rows with score outside 0-10, bad year or negative money",
         before, len(df), before - len(df))

    # Step 8 - helper columns used by the analysis
    df["year"] = df["year"].astype(int)
    df["profit"] = df["revenue"] - df["budget"]
    # ROI only makes sense when the budget is known (budget > 0)
    df["roi"] = (df["profit"] / df["budget"]).where(df["budget"] > 0)
    df["release_date"] = pd.to_datetime(df["released"].str.replace(r"\s*\(.*\)", "", regex=True),
                                        errors="coerce", format="mixed")
    df["release_country"] = df["released"].str.extract(r"\((.*)\)", expand=False).fillna("Unknown")
    df["decade"] = (df["year"] // 10 * 10).astype(str) + "s"
    _log(log, "8. Add helper columns", "Added profit, ROI, release_date, release_country, decade",
         len(df), len(df), 0)

    return df.reset_index(drop=True), pd.DataFrame(log)


@lru_cache(maxsize=1)
def _clean_cached():
    return clean_data(load_data())


def get_clean_data() -> pd.DataFrame:
    """The cleaned dataset used by every page (cleaned once, then cached)."""
    return _clean_cached()[0].copy()


def get_cleaning_log() -> pd.DataFrame:
    """The cleaning log table shown on the Data Quality page."""
    return _clean_cached()[1].copy()
