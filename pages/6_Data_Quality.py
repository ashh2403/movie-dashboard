"""
PAGE 6 - MODULE 2: DATA PREPROCESSING / DATA QUALITY
---------------------------------------------------
Shows every cleaning step from src/preprocessing.py with the number of rows
before and after, missing values per column, duplicates, and the repeated
titles that are really remakes (different years) and therefore kept.
"""

import streamlit as st

from src import ui
from src.charts import fmt_num
from src.data_loader import COLUMN_NAMES, load_data, load_raw_data
from src.filters import sidebar_filters
from src.preprocessing import find_remakes, get_cleaning_log, missing_values_report

ui.setup_page("Data Quality", "🧹")
# The sidebar is shown for a consistent look, but this page describes the WHOLE dataset
filtered, clean, _ = sidebar_filters()
ui.page_header("DATA", "QUALITY & CLEANING",
               "What the preprocessing module checked and changed before any analysis", "Module 1 + Module 2")

raw = load_raw_data()
renamed = load_data()
log = get_cleaning_log()
dup_rows = int(renamed.duplicated().sum())
dup_title_year = int(renamed.duplicated(["title", "year"]).sum())
missing_total = int(missing_values_report(renamed)["Missing values"].sum())

ui.kpi_cards([
    ("Rows before cleaning", f"{len(raw):,}", f"{raw.shape[1]} columns in the CSV", "inbox"),
    ("Rows after cleaning", f"{len(clean):,}", f"{len(raw) - len(clean):,} rows removed", "check"),
    ("Duplicates removed", f"{dup_rows + dup_title_year:,}",
     f"{dup_rows} exact · {dup_title_year} same title + year", "copy"),
    ("Missing values found", f"{missing_total:,}", "across all columns", "search"),
])
st.write("")

# ---- Module 1: the columns that were loaded and renamed --------------------
with st.expander("Module 1 – Data collection: columns loaded and renamed", expanded=False):
    st.dataframe([{"Original column": k, "Short name used in code": v,
                   "Type": str(renamed[v].dtype), "Example": str(renamed[v].iloc[0])}
                  for k, v in COLUMN_NAMES.items()], hide_index=True, width="stretch")
    st.caption("'Rating' is the certificate (R, PG-13 ...). 'Sum of Rating Score' is the score out of 10.")

# ---- Module 2: the cleaning log --------------------------------------------
st.markdown("#### Cleaning steps (in the order they run)")
st.dataframe(log, hide_index=True, width="stretch")

totals_ok = (len(clean) == len(raw))
st.success(
    f"Totals after cleaning: {len(clean):,} movies · revenue {fmt_num(clean['revenue'].sum())} · "
    f"budget {fmt_num(clean['budget'].sum())} · sum of rating score {clean['score'].sum():,.1f}"
    + (" — identical to the Power BI dashboard, because cleaning removed no rows." if totals_ok else "."))

left, right = st.columns(2)
with left:
    st.markdown("#### Missing values per column")
    st.dataframe(missing_values_report(renamed), hide_index=True, width="stretch", height=560)
with right:
    st.markdown("#### Certificate labels before → after")
    before = renamed["certificate"].value_counts().rename("Before")
    after = clean["certificate"].value_counts().rename("After")
    labels = before.to_frame().join(after, how="outer").fillna(0).astype(int)
    st.dataframe(labels.sort_values("Before", ascending=False), width="stretch")
    st.caption("'Unrated' and 'Not Rated' mean the same thing, so they were merged.")

# ---- Remakes: same title, different year (kept on purpose) ----------------
remakes = find_remakes(clean)
st.markdown(f"#### Repeated titles with different years ({remakes['title'].nunique()} titles, {len(remakes)} rows)")
st.caption("These are remakes or different films that share a name (e.g. Aladdin 1992 and 2019). "
           "They are NOT duplicates, so they are kept.")
st.dataframe(remakes, hide_index=True, width="stretch", height=360,
             column_config={"title": "Title", "genre": "Genre", "director": "Director",
                            "revenue": st.column_config.NumberColumn("Revenue", format="compact"),
                            "year": st.column_config.NumberColumn("Year", format="%d")})

# ---- Other quality checks --------------------------------------------------
st.markdown("#### Other checks")
per_year = clean.groupby("year").size()
small_years = per_year[per_year < 0.5 * per_year.median()]
ui.facts([
    f"Release years covered: {clean['year'].min()}–{clean['year'].max()} "
    f"(median {per_year.median():.0f} movies per year).",
    *[f"{year} has only {n} movies, so its totals are not comparable with other years." for year, n in small_years.items()],
    f"Movies with budget = 0: {(clean['budget'] == 0).sum():,} (these would be skipped in ROI).",
    f"Release dates that could not be read: {clean['release_date'].isna().sum():,}.",
    f"Year column differs from the release-date year for {(clean['release_date'].dt.year != clean['year']).sum():,} movies "
    "(the 'Released' date is for one country, which can fall in a different year). The year column is used.",
])
