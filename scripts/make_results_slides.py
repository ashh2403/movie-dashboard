"""
BUILD results_slides.pptx (dark navy + orange, same look as the dashboard)
-------------------------------------------------------------------------
Run from the project folder:   python scripts/make_results_slides.py
(Run scripts/export_figures.py first so the chart images exist.)

The slides use the same 4:3 size as Niha-ppt.pptx, so they can be copied
straight into the presentation. Every number is calculated from the data.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pptx import Presentation                       # noqa: E402
from pptx.dml.color import RGBColor                 # noqa: E402
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN     # noqa: E402
from pptx.util import Inches, Pt                    # noqa: E402

from src import analysis, figures, insights         # noqa: E402
from src.charts import fmt_num                      # noqa: E402
from src.preprocessing import get_clean_data        # noqa: E402

FIG = ROOT / "reports" / "figures"
SLIDE_FIG = ROOT / "reports" / "slide_figures"      # larger-font copies of the charts
OUT = ROOT / "results_slides.pptx"

NAVY = RGBColor(0x0B, 0x14, 0x37)
PANEL = RGBColor(0x17, 0x24, 0x5E)
ORANGE = RGBColor(0xFF, 0x8C, 0x1A)
BAR = RGBColor(0xF0, 0x7A, 0x50)
YELLOW = RGBColor(0xF5, 0xC5, 0x18)
WHITE = RGBColor(0xF2, 0xF4, 0xFF)
MUTED = RGBColor(0xA9, 0xB3, 0xDE)
CREAM = RGBColor(0xFF, 0xF6, 0xD6)
DARK = RGBColor(0x1B, 0x1B, 0x1B)
BLUE = RGBColor(0x1E, 0x7F, 0xB8)

W, H = Inches(10), Inches(7.5)          # 4:3, same as Niha-ppt.pptx


# ---------------------------------------------------------------------------
# Small drawing helpers
# ---------------------------------------------------------------------------
def background(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = NAVY


def text_box(slide, x, y, w, h, text, size=14, colour=WHITE, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = anchor
    lines = text if isinstance(text, list) else [text]
    for i, line in enumerate(lines):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = colour
        run.font.name = "Segoe UI"
    return box


def title(slide, first, accent, subtitle=None):
    """Slide title with one orange word, like the dashboard header."""
    box = slide.shapes.add_textbox(Inches(0.4), Inches(0.25), Inches(9.2), Inches(0.7))
    p = box.text_frame.paragraphs[0]
    for word, colour in ((first + " ", WHITE), (accent, ORANGE)):
        run = p.add_run()
        run.text = word
        run.font.size = Pt(28)
        run.font.bold = True
        run.font.color.rgb = colour
        run.font.name = "Segoe UI"
    if subtitle:
        text_box(slide, Inches(0.4), Inches(0.9), Inches(9.2), Inches(0.4), subtitle, 13, MUTED)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.4), Inches(1.32), Inches(1.2), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ORANGE
    bar.line.fill.background()


def card(slide, x, y, w, h, fill, line_colour=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.adjustments[0] = 0.06
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line_colour:
        shape.line.color.rgb = line_colour
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def kpi(slide, x, y, w, label, value, note):
    card(slide, x, y, w, Inches(1.35), YELLOW)
    text_box(slide, x + Inches(0.15), y + Inches(0.08), w - Inches(0.3), Inches(0.35), label, 12, DARK, True)
    text_box(slide, x + Inches(0.15), y + Inches(0.38), w - Inches(0.3), Inches(0.6), value,
             30 if len(value) <= 6 else 24, DARK, True)
    text_box(slide, x + Inches(0.15), y + Inches(0.95), w - Inches(0.3), Inches(0.35), note, 10, DARK)


def bullets(slide, x, y, w, h, items, size=14):
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.word_wrap = True
    for i, item in enumerate(items):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.space_after = Pt(8)
        dot = p.add_run()
        dot.text = "▶  "
        dot.font.size = Pt(size - 3)
        dot.font.color.rgb = ORANGE
        run = p.add_run()
        run.text = item
        run.font.size = Pt(size)
        run.font.color.rgb = WHITE
        run.font.name = "Segoe UI"


def slide_chart(build, df, name, width_px=720, height_px=470):
    """Render a dashboard chart with larger fonts so it is readable on a slide."""
    import plotly.io as pio
    fig = build(df, 10)
    fig.update_layout(font=dict(size=17), title_font_size=24, height=height_px,
                      margin=dict(l=20, r=25, t=95, b=20))
    fig.update_xaxes(tickfont=dict(size=15), title_font=dict(size=16))
    fig.update_yaxes(tickfont=dict(size=15), title_font=dict(size=16))
    path = SLIDE_FIG / f"{name}.png"
    SLIDE_FIG.mkdir(parents=True, exist_ok=True)
    pio.write_image(fig, path, width=width_px, height=height_px, scale=2)
    return path


def picture(slide, path, x, y, w=None, h=None):
    if path.exists():
        return slide.shapes.add_picture(str(path), x, y, width=w, height=h)
    text_box(slide, x, y, w or Inches(4), Inches(0.5),
             f"[missing {path.name} - run scripts/export_figures.py]", 12, MUTED)


def footer(slide, number):
    text_box(slide, Inches(0.4), Inches(7.05), Inches(6), Inches(0.3),
             "Movie Industry Performance Dashboard · School of Computing - CSE", 9, MUTED)
    text_box(slide, Inches(8.6), Inches(7.05), Inches(1), Inches(0.3), str(number), 9, MUTED, align=PP_ALIGN.RIGHT)


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------
def slide_dashboard(prs, df):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    background(s)
    title(s, "RESULTS:", "DASHBOARD", "Python + Streamlit implementation of the Power BI design")
    pic = picture(s, FIG / "fig5_1_dashboard_home.png", Inches(0.4), Inches(1.55), h=Inches(5.4))
    if pic is not None:
        # centre the screenshot if it is narrower than the slide
        pic.left = int((W - pic.width) / 2) if pic.width < W else Inches(0.4)
        if pic.width > Inches(9.2):
            pic.width, pic.height = Inches(9.2), int(pic.height * Inches(9.2) / pic.width)
    footer(s, 1)


def slide_kpis(prs, df):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    background(s)
    title(s, "KEY", "PERFORMANCE INDICATORS", "Totals match the Power BI dashboard exactly")
    k = analysis.kpis(df)
    w, gap, y = Inches(2.15), Inches(0.18), Inches(1.7)
    cards = [("Total Movies", f"{k['movies']:,}", f"{df['year'].min()}–{df['year'].max()}"),
             ("Total Revenue", fmt_num(k["revenue"]), f"avg {fmt_num(k['avg_revenue'])} / movie"),
             ("Sum of Rating Score", f"{k['score_sum']:,.1f}", f"average {k['avg_score']:.2f} / 10"),
             ("Total Budget", fmt_num(k["budget"]), f"revenue ÷ budget = {k['revenue'] / k['budget']:.2f}x")]
    for i, (label, value, note) in enumerate(cards):
        kpi(s, Inches(0.4) + i * (w + gap), y, w, label, value, note)

    log_rows = len(df)
    budget = analysis.with_budget(df)
    bullets(s, Inches(0.5), Inches(3.4), Inches(9), Inches(3.4), [
        f"Dataset: {log_rows:,} movies, 15 attributes; 0 missing values and 0 duplicates after cleaning "
        f"({analysis.movies_by_certificate(df).shape[0]} certificate labels after merging 'Unrated' → 'Not Rated').",
        f"Median revenue is only {fmt_num(df['revenue'].median())} vs a mean of {fmt_num(df['revenue'].mean())}: "
        "a few blockbusters earn far more than a typical film.",
        f"Total profit {fmt_num(budget['profit'].sum())}, yet {analysis.loss_share(df):.0%} of films earned "
        f"less than their budget (median ROI {budget['roi'].median():.0%}).",
        f"Budget ↔ revenue r = {analysis.correlation(df, 'budget', 'revenue'):.2f}; "
        f"votes ↔ revenue r = {analysis.correlation(df, 'votes', 'revenue'):.2f}; "
        f"score ↔ revenue r = {analysis.correlation(df, 'score', 'revenue'):.2f}.",
    ], size=15)
    footer(s, 2)


def slide_genres(prs, df):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    background(s)
    title(s, "GENRE", "FINDINGS", "Module 3 – Revenue & Genre Analysis")
    picture(s, slide_chart(figures.revenue_by_genre, df, "revenue_by_genre"),
            Inches(0.3), Inches(1.6), w=Inches(4.65))
    picture(s, slide_chart(figures.avg_revenue_by_genre, df, "avg_revenue_by_genre"),
            Inches(5.05), Inches(1.6), w=Inches(4.65))
    g = analysis.genre_summary(df)
    avg = analysis.avg_revenue_by_genre(df, 10)
    roi = analysis.roi_by_genre(df, 10)
    rated = analysis.score_by_group(df, "genre", 10)
    top = g.iloc[0]
    small = g[g["movies"] < 10]
    bullets(s, Inches(0.5), Inches(4.85), Inches(9), Inches(2.1), [
        f"{top['genre']} earns {fmt_num(top['total_revenue'])} = {top['revenue_share']:.0%} of all revenue; "
        f"the top 3 genres earn {g.head(3)['revenue_share'].sum():.0%}.",
        f"Best per film: {avg.iloc[0]['genre']} ({fmt_num(avg.iloc[0]['avg_revenue'])} average) · "
        f"best return: {roi.iloc[0]['genre']} (median ROI {roi.iloc[0]['median_roi']:.0%}).",
        f"Highest rated: {rated.iloc[0]['genre']} ({rated.iloc[0]['avg_score']:.2f}) – "
        "high-rated genres are not the high-earning ones.",
        f"{len(small)} small genres (e.g. Family, {int(small.set_index('genre').loc['Family', 'movies'])} films) "
        "are hidden from averages (minimum 10 films)." if "Family" in set(small["genre"]) else
        "Genres with fewer than 10 films are hidden from averages.",
    ], size=14)
    footer(s, 3)


def slide_people(prs, df):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    background(s)
    title(s, "ACTOR & DIRECTOR", "FINDINGS", "Module 5 – top performers by revenue and rating")
    picture(s, slide_chart(figures.top_stars_by_revenue, df, "top_stars"),
            Inches(0.3), Inches(1.6), w=Inches(4.65))
    picture(s, slide_chart(figures.top_directors_by_revenue, df, "top_directors"),
            Inches(5.05), Inches(1.6), w=Inches(4.65))
    star = analysis.top_people_by_revenue(df, "star", 1).iloc[0]
    director = analysis.top_people_by_revenue(df, "director", 1).iloc[0]
    best = analysis.top_people_by_score(df, "director", 1, 5).iloc[0]
    bullets(s, Inches(0.5), Inches(4.85), Inches(9), Inches(2.1), [
        f"Top star: {star['star']} – {fmt_num(star['total_revenue'])} from {star['movies']} films.",
        f"Top director: {director['director']} – {fmt_num(director['total_revenue'])} from "
        f"{director['movies']} films (avg score {director['avg_score']:.2f}).",
        f"Top 10 directors earn {analysis.top_n_share(df, 'director', 10):.0%} of revenue; "
        f"top 10 stars earn {analysis.top_n_share(df, 'star', 10):.0%}.",
        f"Highest-rated director (≥ 5 films): {best['director']} ({best['avg_score']:.2f}).",
    ], size=14)
    footer(s, 4)


def slide_insights(prs, df):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    background(s)
    title(s, "KEY INSIGHTS INTO", "MARKET TRENDS", "Module 6 – generated automatically from the data")
    cards = insights.key_insights(df)
    w, h, gap = Inches(4.5), Inches(2.6), Inches(0.2)
    for i, c in enumerate(cards):
        x = Inches(0.4) + (i % 2) * (w + gap)
        y = Inches(1.65) + (i // 2) * (h + gap)
        card(s, x, y, w, h, CREAM, ORANGE)
        text_box(s, x + Inches(0.2), y + Inches(0.12), w - Inches(0.4), Inches(0.4), c["title"], 15, BLUE, True)
        text_box(s, x + Inches(0.2), y + Inches(0.55), w - Inches(0.4), Inches(1.4), c["text"], 12, DARK)
        text_box(s, x + Inches(0.2), y + h - Inches(0.7), w - Inches(0.4), Inches(0.6),
                 "Key takeaway: " + c["takeaway"], 11, RGBColor(0xB5, 0x48, 0x1C), True)
    footer(s, 5)


def slide_architecture(prs, df):
    """Optional: a diagram for the empty 'System Architecture' slide."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    background(s)
    title(s, "SYSTEM", "ARCHITECTURE", "Layered design: each layer is one or more Python modules")
    layers = [
        ("Data Layer", "Module 1 · Data Collection", "cleaned_data_final.csv\nsrc/data_loader.py"),
        ("Preprocessing", "Module 2 · Data Preprocessing", "missing values, duplicates,\nlabels · src/preprocessing.py"),
        ("Analysis Layer", "Modules 3, 4, 5", "revenue & genre · ratings ·\nactors & directors · src/analysis.py"),
        ("Visualization", "Module 6 · Charts & Insights", "Plotly charts · KPI cards ·\nsrc/figures.py, src/insights.py"),
        ("Dashboard", "Streamlit web app", "7 pages · shared filters ·\nCSV download · app.py"),
    ]
    box_w, box_h, gap = Inches(1.72), Inches(2.6), Inches(0.15)
    y = Inches(2.0)
    shapes = []
    for i, (name, module, detail) in enumerate(layers):
        x = Inches(0.35) + i * (box_w + gap)
        shape = card(s, x, y, box_w, box_h, PANEL, ORANGE)
        shapes.append(shape)
        head = card(s, x, y, box_w, Inches(0.55), ORANGE)
        text_box(s, x, y, box_w, Inches(0.55), name, 13, NAVY, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
        text_box(s, x + Inches(0.08), y + Inches(0.65), box_w - Inches(0.16), Inches(0.6), module, 11, YELLOW, True,
                 PP_ALIGN.CENTER)
        text_box(s, x + Inches(0.08), y + Inches(1.3), box_w - Inches(0.16), Inches(1.2), detail.split("\n"), 10,
                 WHITE, align=PP_ALIGN.CENTER)
    for left, right in zip(shapes, shapes[1:]):
        line = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, left.left + left.width, y + box_h // 2,
                                      right.left, y + box_h // 2)
        line.line.color.rgb = YELLOW
        line.line.width = Pt(2.5)
        line.line._get_or_add_ln().append(_arrow_head())
    # user + feedback loop
    user = card(s, Inches(3.3), Inches(5.15), Inches(3.4), Inches(0.75), YELLOW)
    text_box(s, Inches(3.3), Inches(5.15), Inches(3.4), Inches(0.75),
             "👤 User: filters by genre, year, certificate", 12, DARK, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    text_box(s, Inches(0.4), Inches(6.1), Inches(9.2), Inches(0.8),
             "Every filter change re-runs the analysis on the filtered data, so all charts, KPIs and insight "
             "cards update together. Tests (pytest) check each layer.", 12, MUTED, align=PP_ALIGN.CENTER)
    footer(s, 6)


def _arrow_head():
    from pptx.oxml.ns import qn
    from lxml import etree
    tail = etree.SubElement(etree.Element(qn("a:dummy")), qn("a:tailEnd"))
    tail.set("type", "triangle")
    tail.set("w", "med")
    tail.set("len", "med")
    return tail


def main():
    df = get_clean_data()
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    for build in (slide_dashboard, slide_kpis, slide_genres, slide_people, slide_insights, slide_architecture):
        build(prs, df)
    prs.save(OUT)
    print(f"saved {OUT.relative_to(ROOT)} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
