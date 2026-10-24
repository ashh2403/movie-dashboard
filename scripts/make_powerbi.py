"""
BUILD THE POWER BI VERSION OF THE DASHBOARD
-------------------------------------------
Run from the project folder:   python scripts/make_powerbi.py

Writes a Power BI Project (PBIP) into powerbi/:
    powerbi/MovieDashboard.pbip              <- double-click to open in Power BI Desktop
    powerbi/MovieDashboard.SemanticModel/    <- data model: Movies table + DAX measures (TMDL)
    powerbi/MovieDashboard.Report/           <- 3 report pages (PBIR)

The data is loaded from the public CSV on GitHub (DataUrl parameter), so the
project opens on any computer. In Power BI Desktop use File > Save as to get
a normal .pbix file for the client.

The page layout follows our original Power BI dashboard (reference.jpeg):
KPI cards, top stars, certificate donut, revenue by year / genre / director,
average revenue by genre and the "Key insights into market trends" boxes.
The insight sentences are calculated here from the real data.
"""

import hashlib
import json
import shutil
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.charts import fmt_num                  # noqa: E402
from src.preprocessing import get_clean_data    # noqa: E402

OUT = ROOT / "powerbi"
NAME = "MovieDashboard"
DATA_URL = "https://raw.githubusercontent.com/ashh2403/movie-dashboard/main/data/cleaned_data_final.csv"
BASE_THEME = Path(__file__).resolve().parent / "powerbi_assets" / "CY24SU10.json"

SCHEMA = "https://developer.microsoft.com/json-schemas/fabric"
TABLE = "Movies"

# CinemaScope palette (same colours as src/charts.py)
BG, CARD, SURFACE, BORDER = "#0B1020", "#151F3D", "#1B2850", "#26365F"
GOLD, CORAL, TEAL, PURPLE, SKY = "#FFB547", "#FF7657", "#72D6AD", "#9C8CFF", "#5AB8F0"
TEXT, MUTED = "#F5F7FF", "#A9B8D8"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def guid(key: str) -> str:
    """Stable GUID, so re-running the script gives the same files."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"movie-dashboard/{key}"))


def short_id(key: str) -> str:
    """20-character hex name used by Power BI for pages and visuals."""
    return hashlib.md5(key.encode()).hexdigest()[:20]


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def lit(value: str):
    return {"expr": {"Literal": {"Value": value}}}


def text_lit(text: str):
    return lit("'" + text.replace("'", "''") + "'")


def colour(hex_colour: str):
    return {"solid": {"color": text_lit(hex_colour)}}


def column(prop: str):
    return {"Column": {"Expression": {"SourceRef": {"Entity": TABLE}}, "Property": prop}}


def measure(prop: str):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": TABLE}}, "Property": prop}}


def projection(field: dict, active: bool = False):
    prop = next(iter(field.values()))["Property"]
    proj = {"field": field, "queryRef": f"{TABLE}.{prop}", "nativeQueryRef": prop}
    if active:
        proj["active"] = True
    return proj


def sort_by(field: dict, direction: str = "Descending"):
    return {"sort": [{"field": field, "direction": direction}]}


def top_n_filter(column_prop: str, measure_prop: str, n: int):
    """Visual-level Top N filter: keep the n values of a column with the highest measure."""
    src = {"SourceRef": {"Source": "m"}}
    return {
        "name": short_id(f"topn/{column_prop}/{measure_prop}/{n}"),
        "field": column(column_prop),
        "type": "TopN",
        "filter": {
            "Version": 2,
            "From": [
                {"Name": "subquery", "Type": 2, "Expression": {"Subquery": {"Query": {
                    "Version": 2,
                    "From": [{"Name": "m", "Entity": TABLE, "Type": 0}],
                    "Select": [{"Column": {"Expression": src, "Property": column_prop}, "Name": "field"}],
                    "OrderBy": [{"Direction": 2, "Expression": {"Measure": {"Expression": src,
                                                                            "Property": measure_prop}}}],
                    "Top": n,
                }}}},
                {"Name": "m", "Entity": TABLE, "Type": 0},
            ],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {"Expression": src, "Property": column_prop}}],
                "Table": {"SourceRef": {"Source": "subquery"}},
            }}}],
        },
    }


def container(title: str = "", subtitle: str = "", background: str = CARD, border: bool = True):
    """Card look for a visual: navy panel, thin border, white title, muted subtitle."""
    objs = {
        "background": [{"properties": {"show": lit("true"), "color": colour(background),
                                       "transparency": lit("0D")}}],
        "border": [{"properties": {"show": lit("true" if border else "false"), "color": colour(BORDER),
                                   "radius": lit("10D")}}],
        "title": [{"properties": {"show": lit("true" if title else "false")}}],
    }
    if title:
        objs["title"][0]["properties"].update({"text": text_lit(title), "fontColor": colour(TEXT),
                                               "fontSize": lit("12D"), "bold": lit("true")})
    if subtitle:
        objs["subTitle"] = [{"properties": {"show": lit("true"), "text": text_lit(subtitle),
                                            "fontColor": colour(MUTED), "fontSize": lit("9D")}}]
    return objs


def axes():
    """Readable axis labels on the dark background."""
    return {
        "categoryAxis": [{"properties": {"labelColor": colour(MUTED), "titleColor": colour(MUTED),
                                         "showAxisTitle": lit("true")}}],
        "valueAxis": [{"properties": {"labelColor": colour(MUTED), "titleColor": colour(MUTED),
                                      "showAxisTitle": lit("true"), "gridlineColor": colour(BORDER)}}],
    }


def bar_colour(hex_colour: str):
    return {"dataPoint": [{"properties": {"fill": colour(hex_colour)}}]}


# ---------------------------------------------------------------------------
# Visuals
# ---------------------------------------------------------------------------
class Page:
    def __init__(self, key: str, display_name: str, height: int):
        self.name = short_id(f"page/{key}")
        self.display_name = display_name
        self.height = height
        self.visuals = []

    def add(self, key, pos, visual, filters=None):
        x, y, w, h = pos
        z = len(self.visuals) * 1000
        container_json = {
            "$schema": f"{SCHEMA}/item/report/definition/visualContainer/2.0.0/schema.json",
            "name": short_id(f"{self.name}/{key}"),
            "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z},
            "visual": {**visual, "drillFilterOtherVisuals": True},
        }
        if filters:
            container_json["filterConfig"] = {"filters": filters}
        self.visuals.append(container_json)


def chart(vtype, category, value, title, subtitle, colour_hex=None, sort=None, extra_objects=None):
    objects = axes()
    if colour_hex:
        objects.update(bar_colour(colour_hex))
    if extra_objects:
        objects.update(extra_objects)
    query = {"queryState": {"Category": {"projections": [projection(column(category), active=True)]},
                            "Y": {"projections": [projection(measure(value))]}}}
    query["sortDefinition"] = sort or sort_by(measure(value))
    return {"visualType": vtype, "query": query, "objects": objects,
            "visualContainerObjects": container(title, subtitle)}


def kpi_card(measure_name, label, whole_number=False):
    """Gold KPI card like the original dashboard: dark value on gold."""
    labels = {"color": colour(BG), "fontSize": lit("24D")}
    if whole_number:
        labels["labelDisplayUnits"] = lit("1D")      # 5,421 instead of 5K
    return {
        "visualType": "card",
        "query": {"queryState": {"Values": {"projections": [projection(measure(measure_name))]}}},
        "objects": {"labels": [{"properties": labels}],
                    "categoryLabels": [{"properties": {"show": lit("true"), "color": colour(BG),
                                                       "fontSize": lit("10D")}}]},
        "visualContainerObjects": container(label, background=GOLD, border=False)
        | {"title": [{"properties": {"show": lit("true"), "text": text_lit(label), "fontColor": colour(BG),
                                     "fontSize": lit("11D"), "bold": lit("true")}}]},
    }


def slicer(column_prop, label, mode="Dropdown"):
    return {
        "visualType": "slicer",
        "query": {"queryState": {"Values": {"projections": [projection(column(column_prop), active=True)]}},
                  "sortDefinition": sort_by(column(column_prop), "Ascending")},
        "objects": {"data": [{"properties": {"mode": text_lit(mode)}}],
                    "header": [{"properties": {"show": lit("true"), "text": text_lit(label),
                                               "fontColor": colour(GOLD)}}],
                    "items": [{"properties": {"fontColor": colour(TEXT), "background": colour(SURFACE)}}]},
        "visualContainerObjects": container(),
    }


def textbox(paragraphs, background=None):
    """paragraphs = [[(text, size_pt, colour, bold), ...], ...]"""
    paras = []
    for runs in paragraphs:
        text_runs = []
        for text, size, hex_colour, bold in runs:
            style = {"fontFamily": "Segoe UI", "fontSize": f"{size}pt", "color": hex_colour}
            if bold:
                style["fontWeight"] = "bold"
            text_runs.append({"value": text, "textStyle": style})
        paras.append({"textRuns": text_runs})
    vco = container(background=background or CARD, border=background is not None)
    if background is None:
        vco["background"] = [{"properties": {"show": lit("false")}}]
    return {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": paras}}]},
            "visualContainerObjects": vco}


def table(columns):
    return {
        "visualType": "tableEx",
        "query": {"queryState": {"Values": {"projections": [projection(column(c)) for c in columns]}},
                  "sortDefinition": sort_by(column("Revenue"))},
        "objects": {"columnHeaders": [{"properties": {"fontColor": colour(GOLD), "backColor": colour(SURFACE)}}],
                    "values": [{"properties": {"fontColorPrimary": colour(TEXT), "backColorPrimary": colour(CARD),
                                               "fontColorSecondary": colour(TEXT),
                                               "backColorSecondary": colour(SURFACE)}}]},
        "visualContainerObjects": container("All movies", "Sorted by revenue · click a header to sort"),
    }


# ---------------------------------------------------------------------------
# Real numbers for the insight boxes
# ---------------------------------------------------------------------------
def insight_numbers():
    df = get_clean_data()
    n = {"movies": len(df), "first": int(df["year"].min()), "last": int(df["year"].max())}

    genre = df.groupby("genre")["revenue"].sum().sort_values(ascending=False)
    n["top_genre"], n["top_genre_rev"] = genre.index[0], genre.iloc[0]
    n["top_genre_share"] = genre.iloc[0] / genre.sum()
    n["top3_share"] = genre.head(3).sum() / genre.sum()

    early = df[df["year"].between(n["first"], n["first"] + 4)]["revenue"].sum()
    late = df[df["year"].between(n["last"] - 4, n["last"])]["revenue"].sum()
    n["early"], n["late"], n["growth"] = early, late, late / early - 1
    by_year = df.groupby("year")["revenue"].sum()
    n["peak_year"], n["peak_rev"] = int(by_year.idxmax()), by_year.max()
    n["last_year_movies"] = int((df["year"] == n["last"]).sum())

    directors = df.groupby("director").agg(revenue=("revenue", "sum"), movies=("title", "size"))
    top10 = directors.sort_values("revenue", ascending=False).head(10)
    n["dir_rev_share"] = top10["revenue"].sum() / df["revenue"].sum()
    n["dir_movie_share"] = top10["movies"].sum() / len(df)
    n["top_dir"], n["top_dir_rev"], n["top_dir_movies"] = top10.index[0], top10["revenue"].iloc[0], \
        int(top10["movies"].iloc[0])

    n["r_score"] = df["score"].corr(df["revenue"])
    n["r_votes"] = df["votes"].corr(df["revenue"])
    scores = df.groupby("genre").agg(score=("score", "mean"), movies=("title", "size"))
    best = scores[scores["movies"] >= 10].sort_values("score", ascending=False)
    n["best_score_genre"], n["best_score"] = best.index[0], best["score"].iloc[0]
    n["avg_score"] = df["score"].mean()

    avg_rev = df.groupby("genre").agg(avg=("revenue", "mean"), movies=("title", "size"))
    avg_rev = avg_rev[avg_rev["movies"] >= 10].sort_values("avg", ascending=False)
    n["best_avg_genre"], n["best_avg"] = avg_rev.index[0], avg_rev["avg"].iloc[0]
    return n


# ---------------------------------------------------------------------------
# Report pages
# ---------------------------------------------------------------------------
W = 1280
GAP = 20
QUARTER = (W - 2 * GAP - 3 * GAP) / 4        # 4 cards per row
THIRD = (W - 2 * GAP - 2 * GAP) / 3          # 3 charts per row
HALF = (W - 2 * GAP - GAP) / 2               # 2 charts per row


def col_x(i, width):
    return GAP + i * (width + GAP)


def header(page, title_words, subtitle):
    """Page title (textbox) on the left and the three shared slicers on the right."""
    runs = [(word, 24, colour_hex, True) for word, colour_hex in title_words]
    page.add("title", (GAP, 10, 760, 80), textbox([runs, [(subtitle, 10, MUTED, False)]]))
    page.add("slicer_genre", (800, 14, 150, 72), slicer("Genre", "Genre"))
    page.add("slicer_cert", (960, 14, 140, 72), slicer("Certificate", "Certificate"))
    page.add("slicer_year", (1110, 14, 150, 72), slicer("Release Year", "Release year", mode="Between"))


def overview_page(n):
    page = Page("overview", "Overview", 1230)
    header(page, [("MOVIE INDUSTRY ", TEXT), ("PERFORMANCE ", CORAL), ("DASHBOARD", TEXT)],
           f"Revenue, budget and audience insights across {n['movies']:,} movies released "
           f"{n['first']}–{n['last']} · nominal US dollars")

    cards = [("Total Movies", "Total Movies", True), ("Total Revenue", "Total Revenue (USD)", False),
             ("Sum of Rating Score", "Sum of Rating Score", False), ("Total Budget", "Total Budget (USD)", False)]
    for i, (m, label, whole) in enumerate(cards):
        page.add(f"kpi_{i}", (col_x(i, QUARTER), 100, QUARTER, 95), kpi_card(m, label, whole))

    y1, y2, h = 215, 565, 330
    page.add("top_stars", (col_x(0, THIRD), y1, THIRD, h),
             chart("clusteredBarChart", "Star", "Total Revenue", "Top 10 Stars by Total Revenue",
                   "Lead actor's combined box office, USD", CORAL),
             filters=[top_n_filter("Star", "Total Revenue", 10)])
    page.add("certificate", (col_x(1, THIRD), y1, THIRD, h), {
        "visualType": "donutChart",
        "query": {"queryState": {"Category": {"projections": [projection(column("Certificate"), active=True)]},
                                 "Y": {"projections": [projection(measure("Total Movies"))]}},
                  "sortDefinition": sort_by(measure("Total Movies"))},
        "objects": {"legend": [{"properties": {"show": lit("true"), "labelColor": colour(TEXT),
                                               "position": text_lit("Right")}}],
                    "labels": [{"properties": {"color": colour(TEXT)}}]},
        "visualContainerObjects": container("Count of Movies by Certificate", "Content rating (R, PG-13, PG ...)"),
    })
    page.add("revenue_year", (col_x(2, THIRD), y1, THIRD, h),
             chart("lineChart", "Release Year", "Total Revenue", "Total Revenue by Release Year",
                   f"{n['last']} has only {n['last_year_movies']} movies in the data", GOLD,
                   sort=sort_by(column("Release Year"), "Ascending")))
    page.add("revenue_genre", (col_x(0, THIRD), y2, THIRD, h),
             chart("clusteredColumnChart", "Genre", "Total Revenue", "Total Revenue by Genre",
                   "Combined box office per genre, USD", CORAL))
    page.add("revenue_director", (col_x(1, THIRD), y2, THIRD, h),
             chart("areaChart", "Director", "Total Revenue", "Total Revenue by Director",
                   "Top 12 directors, all their movies combined", PURPLE),
             filters=[top_n_filter("Director", "Total Revenue", 12)])
    page.add("avg_revenue_genre", (col_x(2, THIRD), y2, THIRD, h),
             chart("clusteredBarChart", "Genre", "Average Revenue (10+ movies)", "Average Revenue by Genre",
                   "USD per movie · genres with at least 10 movies", TEAL))

    page.add("insights_title", (GAP, 915, W - 2 * GAP, 40),
             textbox([[("KEY INSIGHTS INTO MARKET TRENDS", 16, GOLD, True)]]))
    boxes = [
        ("1. REVENUE GROWTH", CORAL,
         f"Movies released in {n['last'] - 4}–{n['last']} earned {fmt_num(n['late'])}, "
         f"{n['growth']:.0%} more than the {fmt_num(n['early'])} of {n['first']}–{n['first'] + 4}. "
         f"The peak year was {n['peak_year']} ({fmt_num(n['peak_rev'])}).",
         f"Revenue has grown strongly over time (not adjusted for inflation). "
         f"{n['last']} has only {n['last_year_movies']} movies, so its drop is not real."),
        ("2. GENRE PERFORMANCE", GOLD,
         f"{n['top_genre']} leads with {fmt_num(n['top_genre_rev'])}, {n['top_genre_share']:.0%} of all "
         f"revenue. The top 3 genres earn {n['top3_share']:.0%}.",
         f"Revenue is concentrated in a few genres. Per movie, {n['best_avg_genre']} earns the most "
         f"({fmt_num(n['best_avg'])} on average)."),
        ("3. DIRECTOR IMPACT", PURPLE,
         f"The top 10 directors earn {n['dir_rev_share']:.0%} of revenue from only "
         f"{n['dir_movie_share']:.0%} of the movies.",
         f"{n['top_dir']} leads with {fmt_num(n['top_dir_rev'])} from {n['top_dir_movies']} films."),
        ("4. AUDIENCE RATINGS", TEAL,
         f"Average score is {n['avg_score']:.2f}/10. Score vs revenue r = {n['r_score']:.2f} (weak); "
         f"votes vs revenue r = {n['r_votes']:.2f} (strong).",
         f"Popularity matters more than the score. {n['best_score_genre']} has the highest average "
         f"score ({n['best_score']:.2f})."),
    ]
    for i, (heading, accent, fact, takeaway) in enumerate(boxes):
        page.add(f"insight_{i}", (col_x(i, QUARTER), 960, QUARTER, 200), textbox([
            [(heading, 11, accent, True)],
            [(fact, 9, TEXT, False)],
            [("Key takeaway: ", 9, accent, True), (takeaway, 9, MUTED, False)],
        ], background=CARD))
    page.add("footer", (GAP, 1170, W - 2 * GAP, 40), textbox([[(
        "Insight texts describe all movies. Charts and cards follow the Genre, Certificate and "
        "Release year filters. Source: IMDb-derived movie industry dataset.", 8, MUTED, False)]]))
    return page


def ratings_budget_page():
    page = Page("ratings_budget", "Ratings & Budget", 1235)
    header(page, [("RATINGS ", TEXT), ("& ", CORAL), ("BUDGET", TEXT)],
           "How audiences rate movies, and which genres return the most on their budget")
    cards = [("Average Rating", "Average Rating (out of 10)", False), ("Median ROI", "Median ROI", False),
             ("Total Profit", "Total Profit (USD)", False), ("Revenue per Budget", "Revenue ÷ Budget", False)]
    for i, (m, label, whole) in enumerate(cards):
        page.add(f"kpi_{i}", (col_x(i, QUARTER), 100, QUARTER, 95), kpi_card(m, label, whole))

    rows = [(215, 330), (565, 330), (915, 300)]
    page.add("score_genre", (col_x(0, HALF), rows[0][0], HALF, rows[0][1]),
             chart("clusteredBarChart", "Genre", "Average Rating (10+ movies)", "Average Rating by Genre",
                   "Genres with at least 10 movies", TEAL))
    page.add("score_year", (col_x(1, HALF), rows[0][0], HALF, rows[0][1]),
             chart("lineChart", "Release Year", "Average Rating", "Average Rating by Release Year",
                   "Average score out of 10", GOLD, sort=sort_by(column("Release Year"), "Ascending")))
    page.add("roi_genre", (col_x(0, HALF), rows[1][0], HALF, rows[1][1]),
             chart("clusteredBarChart", "Genre", "Median ROI (10+ movies)", "Median ROI by Genre",
                   "ROI = (revenue − budget) ÷ budget · genres with at least 10 movies", TEAL))
    page.add("director_score", (col_x(1, HALF), rows[1][0], HALF, rows[1][1]),
             chart("clusteredBarChart", "Director", "Average Rating (5+ movies)",
                   "Top 10 Directors by Average Rating", "Directors with at least 5 movies", PURPLE),
             filters=[top_n_filter("Director", "Average Rating (5+ movies)", 10)])
    page.add("movies_decade", (col_x(0, HALF), rows[2][0], HALF, rows[2][1]),
             chart("clusteredColumnChart", "Decade", "Total Movies", "Movies Released per Decade",
                   "Number of movies in the dataset", SKY, sort=sort_by(column("Decade"), "Ascending")))
    page.add("profit_genre", (col_x(1, HALF), rows[2][0], HALF, rows[2][1]),
             chart("clusteredColumnChart", "Genre", "Total Profit", "Total Profit by Genre",
                   "Profit = revenue − budget, USD", CORAL))
    return page


def explorer_page():
    page = Page("explorer", "Movie Explorer", 835)
    header(page, [("MOVIE ", TEXT), ("EXPLORER", CORAL)],
           "Every movie in the dataset · use the filters, or click a column header to sort")
    cards = [("Total Movies", "Movies shown", True), ("Total Revenue", "Total Revenue (USD)", False),
             ("Average Revenue", "Average Revenue (USD)", False), ("Average Rating", "Average Rating", False)]
    for i, (m, label, whole) in enumerate(cards):
        page.add(f"kpi_{i}", (col_x(i, QUARTER), 100, QUARTER, 95), kpi_card(m, label, whole))
    page.add("table", (GAP, 215, W - 2 * GAP, 600), table(
        ["Movie Title", "Release Year", "Genre", "Certificate", "Director", "Star",
         "Revenue", "Budget", "Rating Score", "Votes"]))
    return page


# ---------------------------------------------------------------------------
# Semantic model (TMDL)
# ---------------------------------------------------------------------------
COLUMNS = [  # (name, TMDL dataType, M type, formatString, summarizeBy)
    ("Movie Title", "string", "type text", None, "none"),
    ("Genre", "string", "type text", None, "none"),
    ("Release Year", "int64", "Int64.Type", "0", "none"),
    ("Revenue", "int64", "Int64.Type", "#,0", "sum"),
    ("Rating Score", "double", "type number", "0.0", "average"),
    ("Director", "string", "type text", None, "none"),
    ("Star", "string", "type text", None, "none"),
    ("Budget", "int64", "Int64.Type", "#,0", "sum"),
    ("Votes", "int64", "Int64.Type", "#,0", "sum"),
    ("Runtime", "int64", "Int64.Type", "0", "average"),
    ("Country", "string", "type text", None, "none"),
    ("Company", "string", "type text", None, "none"),
    ("Released", "string", "type text", None, "none"),
    ("Writer", "string", "type text", None, "none"),
    ("Certificate", "string", "type text", None, "none"),
]
EXTRA_COLUMNS = [
    ("Profit", "int64", "#,0", "sum"),
    ("Decade", "string", None, "none"),
]
MEASURES = [  # (name, DAX, formatString)
    ("Total Movies", "COUNTROWS(Movies)", "#,0"),
    ("Total Revenue", "SUM(Movies[Revenue])", "#,0"),
    ("Total Budget", "SUM(Movies[Budget])", "#,0"),
    ("Total Profit", "[Total Revenue] - [Total Budget]", "#,0"),
    ("Sum of Rating Score", "SUM(Movies[Rating Score])", "#,0.0"),
    ("Average Rating", "AVERAGE(Movies[Rating Score])", "0.00"),
    ("Average Revenue", "AVERAGE(Movies[Revenue])", "#,0"),
    ("Revenue per Budget", "DIVIDE([Total Revenue], [Total Budget])", '0.00"x"'),
    ("Median ROI",
     "MEDIANX(FILTER(Movies, Movies[Budget] > 0), DIVIDE(Movies[Revenue] - Movies[Budget], Movies[Budget]))",
     "0%"),
    # Averages of tiny groups are unreliable, so they are blank (hidden) below a minimum
    ("Average Revenue (10+ movies)", "IF([Total Movies] >= 10, [Average Revenue])", "#,0"),
    ("Average Rating (10+ movies)", "IF([Total Movies] >= 10, [Average Rating])", "0.00"),
    ("Average Rating (5+ movies)", "IF([Total Movies] >= 5, [Average Rating])", "0.00"),
    ("Median ROI (10+ movies)", "IF([Total Movies] >= 10, [Median ROI])", "0%"),
]


def tmdl_name(name: str) -> str:
    return f"'{name}'" if any(c in name for c in " ()+-./&") else name


def movies_table_tmdl() -> str:
    names = ", ".join(f'"{c[0]}"' for c in COLUMNS)
    text_cols = ", ".join(f'{{"{c[0]}", Text.Trim, type text}}' for c in COLUMNS if c[1] == "string")
    num_types = ", ".join(f'{{"{c[0]}", {c[2]}}}' for c in COLUMNS if c[1] != "string")
    m = [
        "let",
        f'    Source = Csv.Document(Web.Contents(DataUrl), [Delimiter = ",", Columns = {{{names}}}, '
        'Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),',
        '    #"Removed Header Row" = Table.Skip(Source, 1),',
        f'    #"Trimmed Text" = Table.TransformColumns(#"Removed Header Row", {{{text_cols}}}),',
        f'    #"Changed Type" = Table.TransformColumnTypes(#"Trimmed Text", {{{num_types}}}, "en-US"),',
        '    #"Merged Unrated" = Table.ReplaceValue(#"Changed Type", "Unrated", "Not Rated", '
        'Replacer.ReplaceValue, {"Certificate"}),',
        '    #"Added Profit" = Table.AddColumn(#"Merged Unrated", "Profit", each [Revenue] - [Budget], Int64.Type),',
        '    #"Added Decade" = Table.AddColumn(#"Added Profit", "Decade", '
        'each Text.From(Number.IntegerDivide([Release Year], 10) * 10) & "s", type text)',
        "in",
        '    #"Added Decade"',
    ]
    lines = [f"table {TABLE}", f"\tlineageTag: {guid('table/Movies')}", ""]
    for name, dax, fmt in MEASURES:
        lines += [f"\tmeasure {tmdl_name(name)} = {dax}",
                  f"\t\tformatString: {fmt}",
                  f"\t\tlineageTag: {guid('measure/' + name)}", ""]
    for name, dtype, _, fmt, summarize in COLUMNS:
        lines += column_tmdl(name, dtype, fmt, summarize)
    for name, dtype, fmt, summarize in EXTRA_COLUMNS:
        lines += column_tmdl(name, dtype, fmt, summarize)
    lines += [f"\tpartition {TABLE} = m", "\t\tmode: import", "\t\tsource ="]
    lines += [f"\t\t\t\t{line}" for line in m]
    lines += ["", "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(lines)


def column_tmdl(name, dtype, fmt, summarize):
    lines = [f"\tcolumn {tmdl_name(name)}", f"\t\tdataType: {dtype}"]
    if fmt:
        lines.append(f"\t\tformatString: {fmt}")
    lines += [f"\t\tlineageTag: {guid('column/' + name)}", f"\t\tsummarizeBy: {summarize}",
              f"\t\tsourceColumn: {name}", "", "\t\tannotation SummarizationSetBy = Automatic", ""]
    return lines


def write_semantic_model():
    folder = OUT / f"{NAME}.SemanticModel"
    write_json(folder / ".platform", {
        "$schema": f"{SCHEMA}/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": guid("semanticModel")},
    })
    write_json(folder / "definition.pbism", {
        "$schema": f"{SCHEMA}/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.1", "settings": {}})
    d = folder / "definition"
    write_text(d / "database.tmdl", "database\n\tcompatibilityLevel: 1601\n")
    write_text(d / "model.tmdl", "\n".join([
        "model Model",
        "\tculture: en-US",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tsourceQueryCulture: en-US",
        "\tdataAccessOptions",
        "\t\tlegacyRedirects",
        "\t\treturnErrorValuesAsNull",
        "",
        'annotation PBI_QueryOrder = ["DataUrl","Movies"]',
        "",
        "annotation __PBI_TimeIntelligenceEnabled = 0",
        "",
        f"ref table {TABLE}",
        "",
    ]))
    write_text(d / "expressions.tmdl", "\n".join([
        "/// Web address of the movie CSV. Change it here (Transform data > Edit parameters) to use another copy.",
        f'expression DataUrl = "{DATA_URL}" meta [IsParameterQuery = true, Type = "Text", '
        "IsParameterQueryRequired = true]",
        f"\tlineageTag: {guid('expression/DataUrl')}",
        "",
        "\tannotation PBI_ResultType = Text",
        "",
    ]))
    write_text(d / "tables" / f"{TABLE}.tmdl", movies_table_tmdl())


# ---------------------------------------------------------------------------
# Report (PBIR)
# ---------------------------------------------------------------------------
def theme():
    return {
        "name": "CinemaScope",
        "dataColors": [CORAL, GOLD, SKY, PURPLE, TEAL, "#5E6B91", "#F28FB1", "#C9D66B", "#4FC1C9", "#E0A96D"],
        "background": CARD,
        "foreground": TEXT,
        "tableAccent": GOLD,
        "good": TEAL, "neutral": GOLD, "bad": CORAL,
        "textClasses": {
            "title": {"fontFace": "Segoe UI Semibold", "fontSize": 12, "color": TEXT},
            "header": {"fontFace": "Segoe UI Semibold", "fontSize": 12, "color": TEXT},
            "label": {"fontFace": "Segoe UI", "fontSize": 9, "color": MUTED},
            "callout": {"fontFace": "Segoe UI Semibold", "fontSize": 24, "color": TEXT},
        },
        "visualStyles": {
            "page": {"*": {
                "background": [{"color": {"solid": {"color": BG}}, "transparency": 0}],
                "outspace": [{"color": {"solid": {"color": BG}}, "transparency": 0}],
            }},
            "*": {"*": {
                "background": [{"show": True, "color": {"solid": {"color": CARD}}, "transparency": 0}],
                "title": [{"fontColor": {"solid": {"color": TEXT}}}],
                "categoryAxis": [{"labelColor": {"solid": {"color": MUTED}},
                                  "titleColor": {"solid": {"color": MUTED}}}],
                "valueAxis": [{"labelColor": {"solid": {"color": MUTED}},
                               "titleColor": {"solid": {"color": MUTED}},
                               "gridlineColor": {"solid": {"color": BORDER}}}],
                "legend": [{"labelColor": {"solid": {"color": TEXT}}}],
            }},
        },
    }


def write_report(pages):
    folder = OUT / f"{NAME}.Report"
    write_json(folder / ".platform", {
        "$schema": f"{SCHEMA}/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": guid("report")},
    })
    write_json(folder / "definition.pbir", {
        "$schema": f"{SCHEMA}/item/report/definitionProperties/1.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}},
    })
    resources = folder / "StaticResources"
    (resources / "SharedResources" / "BaseThemes").mkdir(parents=True, exist_ok=True)
    shutil.copy(BASE_THEME, resources / "SharedResources" / "BaseThemes" / "CY24SU10.json")
    write_json(resources / "RegisteredResources" / "CinemaScope.json", theme())

    d = folder / "definition"
    write_json(d / "version.json", {
        "$schema": f"{SCHEMA}/item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    write_json(d / "report.json", {
        "$schema": f"{SCHEMA}/item/report/definition/report/1.3.0/schema.json",
        "themeCollection": {
            "baseTheme": {"name": "CY24SU10", "reportVersionAtImport": "5.61", "type": "SharedResources"},
            "customTheme": {"name": "CinemaScope.json", "reportVersionAtImport": "5.61",
                            "type": "RegisteredResources"},
        },
        "layoutOptimization": "None",
        "resourcePackages": [
            {"name": "SharedResources", "type": "SharedResources",
             "items": [{"name": "CY24SU10", "path": "BaseThemes/CY24SU10.json", "type": "BaseTheme"}]},
            {"name": "RegisteredResources", "type": "RegisteredResources",
             "items": [{"name": "CinemaScope.json", "path": "CinemaScope.json", "type": "CustomTheme"}]},
        ],
        "settings": {
            "useStylableVisualContainerHeader": True,
            "exportDataMode": "AllowSummarizedAndUnderlying",
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True,
        },
    })
    write_json(d / "pages" / "pages.json", {
        "$schema": f"{SCHEMA}/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [p.name for p in pages],
        "activePageName": pages[0].name,
    })
    for p in pages:
        pd_ = d / "pages" / p.name
        write_json(pd_ / "page.json", {
            "$schema": f"{SCHEMA}/item/report/definition/page/1.4.0/schema.json",
            "name": p.name,
            "displayName": p.display_name,
            "displayOption": "FitToWidth",
            "height": p.height,
            "width": W,
            "objects": {
                "background": [{"properties": {"color": colour(BG), "transparency": lit("0D")}}],
                "outspace": [{"properties": {"color": colour(BG), "transparency": lit("0D")}}],
            },
        })
        for v in p.visuals:
            write_json(pd_ / "visuals" / v["name"] / "visual.json", v)


def main():
    # Clear the old output file by file: OneDrive can lock folders, so a plain
    # rmtree may fail half-way. Empty folders that are still locked are harmless.
    if OUT.exists():
        for f in OUT.rglob("*"):
            if f.is_file():
                f.unlink()
        for d in sorted((p for p in OUT.rglob("*") if p.is_dir()), reverse=True):
            try:
                d.rmdir()
            except OSError:
                pass
    write_json(OUT / f"{NAME}.pbip", {
        "$schema": f"{SCHEMA}/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [{"report": {"path": f"{NAME}.Report"}}],
        "settings": {"enableAutoRecovery": True},
    })
    write_text(OUT / ".gitignore", "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")
    write_text(OUT / "HOW TO OPEN.txt", "\n".join([
        "MOVIE INDUSTRY PERFORMANCE DASHBOARD - POWER BI",
        "",
        "1. Unzip this folder first (right-click the ZIP > Extract All). Do not open it from inside the ZIP.",
        "   Keep it in a short location, e.g. Desktop or Documents.",
        "2. Install Power BI Desktop (free) from the Microsoft Store if you do not have it.",
        "3. Double-click MovieDashboard.pbip. Keep the two folders next to it - they belong together.",
        "4. If Power BI asks how to connect to the web data, choose 'Anonymous' and click 'Connect'.",
        "   The movie data is downloaded from the internet, so stay online.",
        "5. Optional: File > Save as > choose .pbix to keep everything in one file.",
        "",
        "Pages: Overview, Ratings & Budget, Movie Explorer. Use the Genre, Certificate and",
        "Release year filters at the top of each page.",
        "",
    ]))
    write_semantic_model()
    pages = [overview_page(insight_numbers()), ratings_budget_page(), explorer_page()]
    write_report(pages)
    count = sum(len(p.visuals) for p in pages)
    print(f"Power BI project written to {OUT.relative_to(ROOT)}  ({len(pages)} pages, {count} visuals)")
    print(f"Open {OUT.relative_to(ROOT) / (NAME + '.pbip')} in Power BI Desktop, then File > Save as > .pbix")


if __name__ == "__main__":
    main()
