"""
MODULE 1 - DATA COLLECTION
--------------------------
Loads the movie dataset from the CSV file and renames the long
Power BI style column names to short, easy-to-use names.
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd

# Location of the dataset (data/cleaned_data_final.csv), found relative to this file
# so the app works no matter which folder you start it from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "cleaned_data_final.csv"

# Original column name  ->  short name used everywhere in the code
COLUMN_NAMES = {
    "Movie Title": "title",
    "Genre": "genre",
    "Sum of Release year": "year",
    "Sum of Revenue": "revenue",
    "Sum of Rating Score": "score",        # IMDb-style score out of 10
    "Director": "director",
    "Star": "star",
    "Sum of Budget": "budget",
    "Sum of Votes": "votes",
    "Sum of Runtime": "runtime",
    "Country": "country",
    "Company": "company",
    "Released": "released",
    "Writer": "writer",
    "Rating": "certificate",               # R, PG-13, PG, G ...
}


@lru_cache(maxsize=4)
def _read_csv_cached(path: str) -> pd.DataFrame:
    # 'utf-8-sig' removes the invisible BOM character Excel adds to the first column name
    return pd.read_csv(path, encoding="utf-8-sig")


def load_raw_data(path=DATA_PATH) -> pd.DataFrame:
    """Read the CSV file exactly as it is (no changes).

    The file is read from disk only once (cached); every call after that
    returns a fresh copy, so one page can never change another page's data.
    """
    return _read_csv_cached(str(path)).copy()


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Give every column a short lowercase name (see COLUMN_NAMES above)."""
    return df.rename(columns=COLUMN_NAMES)


def load_data(path=DATA_PATH) -> pd.DataFrame:
    """Module 1 entry point: read the file and rename the columns."""
    return rename_columns(load_raw_data(path))
