"""
Take full-page screenshots of every dashboard page (for the README, report and slides).

1. Start the app in another terminal:   streamlit run app.py
2. Run:                                 python scripts/take_screenshots.py
   (app on another port?)               python scripts/take_screenshots.py http://localhost:8502

Uses Microsoft Edge (already installed on Windows) through Playwright,
so no extra browser has to be downloaded.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "screenshots"
URL = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501").rstrip("/")

PAGES = {
    "home": "",
    "revenue_and_genre": "Revenue_and_Genre",
    "rating_trends": "Rating_Trends",
    "actors_and_directors": "Actors_and_Directors",
    "budget_and_roi": "Budget_and_ROI",
    "movie_explorer": "Movie_Explorer",
    "data_quality": "Data_Quality",
}


def wait_until_finished(page, timeout_ms=90000):
    """Wait until Streamlit stops running the script and the page stops changing."""
    page.wait_for_selector("[data-testid='stApp']")
    page.wait_for_timeout(1500)
    page.wait_for_function(
        """() => {
            const running = document.querySelector('[data-testid="stStatusWidget"]');
            const busy = running && running.innerText.includes('Stop');
            const skeleton = document.querySelector('[data-testid="stSkeleton"]');
            return !busy && !skeleton;
        }""", timeout=timeout_ms)
    # wait for the number of drawn elements to stay the same for a moment
    last = -1
    for _ in range(30):
        count = page.evaluate("() => document.querySelectorAll('.main-svg, [data-testid=\"stElementContainer\"]').length")
        if count == last:
            break
        last = count
        page.wait_for_timeout(1000)
    page.wait_for_timeout(1500)          # let the Plotly animations finish


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge")
        except Exception:
            browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5)
        for name, path in PAGES.items():
            page.goto(f"{URL}/{path}")
            # wait until Streamlit has finished running the page script
            wait_until_finished(page)
            if page.locator("[data-testid='stException']").count():
                print(f"!! {name}: the page shows an error")
            file = OUT / f"{name}.png"
            # Streamlit scrolls inside its own container, so measure that for a full-page shot
            height = page.evaluate(
                "() => document.querySelector('[data-testid=\"stMain\"]')?.scrollHeight || 900")
            page.set_viewport_size({"width": 1440, "height": min(int(height) + 40, 8000)})
            page.wait_for_timeout(1500)
            page.screenshot(path=str(file), full_page=True)
            page.set_viewport_size({"width": 1440, "height": 900})
            print("saved", file.relative_to(ROOT))
        browser.close()


if __name__ == "__main__":
    main()
