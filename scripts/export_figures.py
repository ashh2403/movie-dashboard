"""
EXPORT EVERY CHART AS A PNG FOR THE REPORT
------------------------------------------
Run from the project folder:   python scripts/export_figures.py

Saves the same Plotly figures the dashboard shows (src/figures.py) into
reports/figures/, named after their figure number in Chapter 5,
e.g. fig5_2_revenue_by_genre.png. Uses kaleido for the PNG export.

Figure 5.1 is the dashboard screenshot: run scripts/take_screenshots.py
(with the app running) and it is copied here automatically.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import plotly.io as pio                       # noqa: E402

from src.figures import REPORT_FIGURES       # noqa: E402
from src.preprocessing import get_clean_data # noqa: E402

OUT = ROOT / "reports" / "figures"
WIDTH, HEIGHT, SCALE = 1100, 620, 2          # 2200 x 1240 pixels, sharp in Word / PowerPoint


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = get_clean_data()
    print(f"Exporting {len(REPORT_FIGURES)} figures from {len(df):,} movies ...")

    for name, build in REPORT_FIGURES:
        fig = build(df, 10)
        fig.update_layout(height=HEIGHT, margin=dict(l=30, r=30, t=90, b=30))
        path = OUT / f"{name}.png"
        pio.write_image(fig, path, width=WIDTH, height=HEIGHT, scale=SCALE)
        print("  saved", path.relative_to(ROOT))

    # Figure 5.1 - the dashboard home page screenshot
    shot = ROOT / "reports" / "screenshots" / "home.png"
    if shot.exists():
        shutil.copy(shot, OUT / "fig5_1_dashboard_home.png")
        print("  saved reports/figures/fig5_1_dashboard_home.png (screenshot)")
    else:
        print("  (no screenshot yet - run scripts/take_screenshots.py while the app is running)")
    print("Done.")


if __name__ == "__main__":
    main()
