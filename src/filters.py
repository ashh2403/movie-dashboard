"""
SHARED SIDEBAR FILTERS (MODULE 6 - DASHBOARD)
---------------------------------------------
Every page calls `sidebar_filters()` once. It draws the same three filters
(genre, release-year range, certificate) and returns the filtered data,
so every chart on every page updates when a filter changes.

The chosen values are remembered when you move to another page.
"""

import pandas as pd
import streamlit as st

from src.preprocessing import get_clean_data

# Streamlit forgets widget values when you switch pages, so each value is
# also copied into a "saved_..." key that survives page changes.
_FILTER_KEYS = ["genres", "years", "certificates", "min_movies"]


@st.cache_data(show_spinner="Loading movie data...")
def load_movies() -> pd.DataFrame:
    """Modules 1 + 2: load and clean the dataset (cached by Streamlit)."""
    return get_clean_data()


def _restore(key, default):
    """Put the saved value back into the widget before it is drawn."""
    saved = f"saved_{key}"
    if saved not in st.session_state:
        st.session_state[saved] = default
    st.session_state[key] = st.session_state[saved]


def _save(key):
    st.session_state[f"saved_{key}"] = st.session_state[key]


def _reset(defaults: dict):
    for key, value in defaults.items():
        st.session_state[f"saved_{key}"] = value
        st.session_state[key] = value


def apply_filters(df: pd.DataFrame, genres, years, certificates) -> pd.DataFrame:
    """Plain pandas filtering (an empty selection means 'all')."""
    mask = df["year"].between(years[0], years[1])
    if genres:
        mask &= df["genre"].isin(genres)
    if certificates:
        mask &= df["certificate"].isin(certificates)
    return df[mask]


def _defaults(df: pd.DataFrame) -> dict:
    return {"genres": [], "years": (int(df["year"].min()), int(df["year"].max())),
            "certificates": [], "min_movies": 10}


def active_filter_count(df: pd.DataFrame = None) -> int:
    """How many of genre / year / certificate differ from 'everything'."""
    df = load_movies() if df is None else df
    defaults = _defaults(df)
    state = st.session_state
    return sum([bool(state.get("saved_genres")),
                tuple(state.get("saved_years", defaults["years"])) != tuple(defaults["years"]),
                bool(state.get("saved_certificates"))])


def _short_list(items, everything: str, noun: str) -> str:
    if not items:
        return everything
    if len(items) <= 2:
        return ", ".join(items)
    return f"{len(items)} {noun}"


def filter_chips():
    """[(label, value, is_active), ...] describing the current filters (for page headers)."""
    df = load_movies()
    defaults = _defaults(df)
    state = st.session_state
    years = tuple(state.get("saved_years", defaults["years"]))
    genres = state.get("saved_genres", [])
    certs = state.get("saved_certificates", [])
    filtered = apply_filters(df, genres, years, certs)
    return [("Years ", f"{years[0]}–{years[1]}", years != tuple(defaults["years"])),
            ("Genre ", _short_list(genres, "All", "genres"), bool(genres)),
            ("Certificate ", _short_list(certs, "All", "selected"), bool(certs)),
            ("Movies ", f"{len(filtered):,} of {len(df):,}", len(filtered) != len(df))]


def sidebar_filters(show_min_movies: bool = False):
    """Draw the sidebar filters and return (filtered_df, full_df, min_movies)."""
    df = load_movies()
    all_genres = sorted(df["genre"].unique())
    all_certs = df["certificate"].value_counts().index.tolist()   # most common first
    year_min, year_max = int(df["year"].min()), int(df["year"].max())
    defaults = _defaults(df)

    for key in _FILTER_KEYS:
        _restore(key, defaults[key])

    n_active = active_filter_count(df)
    with st.sidebar:
        badge = (f"<span class='cs-badge'>{n_active} active</span>" if n_active
                 else "<span class='cs-badge off'>None active</span>")
        st.markdown(f"<div class='cs-side-head'><b>Filters</b>{badge}</div>", unsafe_allow_html=True)

        # ---- Group 1: what kind of movie ----
        st.markdown("<div class='cs-group first'>Content</div>", unsafe_allow_html=True)
        st.multiselect("Genre", all_genres, key="genres", placeholder="All genres",
                       on_change=_save, args=("genres",))
        st.multiselect("Certificate", all_certs, key="certificates", placeholder="All certificates",
                       on_change=_save, args=("certificates",),
                       help="Content rating, e.g. R, PG-13, PG. Listed from most to least common.")

        # ---- Group 2: when ----
        st.markdown("<div class='cs-group'>Release window</div>", unsafe_allow_html=True)
        st.slider("Release year", year_min, year_max, key="years",
                  on_change=_save, args=("years",))
        start, end = st.session_state["years"]
        st.markdown(f"<div class='cs-range'><div><span>From</span> {start}</div>"
                    f"<div>{end - start + 1} years</div><div><span>To</span> {end}</div></div>",
                    unsafe_allow_html=True)

        # ---- Group 3: how averages are calculated ----
        if show_min_movies:
            st.markdown("<div class='cs-group'>Analysis settings</div>", unsafe_allow_html=True)
            st.slider("Minimum movies per group", 1, 50, key="min_movies",
                      on_change=_save, args=("min_movies",),
                      help="Average charts hide genres or certificates with fewer movies than this. "
                           "A tiny group gives a misleading average: Family has only 4 movies, "
                           "so one hit makes it look like the best genre. Default: 10.")

        st.markdown("<div class='cs-group'></div>", unsafe_allow_html=True)
        st.button("Reset filters", on_click=_reset, args=(defaults,), width="stretch",
                  icon=":material/restart_alt:", key="reset_filters",
                  disabled=(n_active == 0 and st.session_state["min_movies"] == defaults["min_movies"]))

    filtered = apply_filters(df, st.session_state["genres"], st.session_state["years"],
                             st.session_state["certificates"])

    with st.sidebar:
        st.markdown(f"<div class='cs-count'>Showing <b>{len(filtered):,}</b> of {len(df):,} movies</div>",
                    unsafe_allow_html=True)

    return filtered, df, st.session_state["min_movies"]


def stop_if_empty(df: pd.DataFrame, needed: int = 1):
    """Show a friendly message instead of crashing when the filters match nothing."""
    if len(df) < needed:
        st.info("🎬 No movies match the current filters. "
                "Try selecting more genres or certificates, widening the year range, "
                "or press **Reset filters** in the sidebar.")
        st.stop()
