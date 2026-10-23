"""
PAGE TESTS (Testing Plan T-05, T-07, T-08)
-----------------------------------------
Runs every dashboard page without a browser (Streamlit AppTest) and checks:
  * the page loads with no errors
  * filters that match zero movies show a friendly message instead of crashing
"""

import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PAGES = ["app.py"] + sorted(str(p.relative_to(ROOT)) for p in (ROOT / "pages").glob("*.py"))


def run_page(page, **saved_filters):
    at = AppTest.from_file(str(ROOT / page), default_timeout=60)
    for key, value in saved_filters.items():
        at.session_state[f"saved_{key}"] = value
    return at.run()


@pytest.mark.parametrize("page", PAGES)
def test_page_loads_without_errors(page):
    at = run_page(page)
    assert not at.exception, at.exception


@pytest.mark.parametrize("page", PAGES)
def test_page_handles_empty_filter(page):
    # Western + certificate G + 2015-2020 matches no movie at all
    at = run_page(page, genres=["Western"], certificates=["G"], years=(2015, 2020))
    assert not at.exception, at.exception
    if "Data_Quality" not in page:     # Data Quality describes the full dataset
        assert any("No movies match" in info.value for info in at.info)


@pytest.mark.parametrize("page", PAGES)
def test_page_handles_tiny_selection(page):
    # Family has only 4 movies: every group is below the default minimum of 10
    at = run_page(page, genres=["Family"])
    assert not at.exception, at.exception
