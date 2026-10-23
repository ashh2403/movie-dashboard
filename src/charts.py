"""
SHARED CHART STYLING (MODULE 6 - DASHBOARD)
-------------------------------------------
Every chart in the dashboard is built by one of the functions below, so all
charts share the same CinemaScope look: deep-navy cards, warm gold / coral
marks, teal and purple for secondary series, and soft blue-grey labels.

These functions only use Plotly (no Streamlit), so scripts/export_figures.py
can reuse them to save the same charts as PNG images for the report.
"""

import math

import pandas as pd
import plotly.graph_objects as go

# ---- CinemaScope Intelligence palette (also used by src/ui.py) ------------
BG = "#0B1020"           # page background
SIDEBAR = "#0D1530"      # sidebar background
CARD = "#151F3D"         # card / chart panel background
SURFACE = "#1B2850"      # raised surface (tooltips, chips)
BORDER = "#26365F"       # thin blue-grey borders
GOLD = "#FFB547"         # primary accent
CORAL = "#FF7657"        # secondary accent
TEAL = "#72D6AD"         # positive values
PURPLE = "#9C8CFF"       # extra accent for a second series
SKY = "#5AB8F0"          # extra accent for categories
TEXT = "#F5F7FF"         # main text
MUTED = "#A9B8D8"        # axis labels, notes
GRID = "rgba(169,184,216,0.10)"

# Older names kept so every existing import keeps working
NAVY_BG = BG
PANEL = CARD
ORANGE = CORAL
ORANGE_TITLE = GOLD
YELLOW = GOLD

# Colours for categories (certificate donut, stacked bars). Distinct in hue
# AND lightness so they stay readable for colour-blind viewers on navy.
CATEGORY_COLOURS = [GOLD, SKY, CORAL, PURPLE, TEAL]
OTHER_COLOUR = "#5E6B91"

# Plotly animates bars and lines to their new values when a filter changes
TRANSITION = dict(duration=450, easing="cubic-in-out")
FONT = "Inter, Segoe UI, Arial, sans-serif"


def rgba(hex_colour: str, alpha: float) -> str:
    """'#FFB547', 0.3 -> 'rgba(255,181,71,0.3)' (for soft fills)."""
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


# ---------------------------------------------------------------------------
# Number formatting like Power BI: 560bn, 12.3M, 5.4K
# ---------------------------------------------------------------------------
def fmt_num(value, prefix: str = "") -> str:
    """Short number format used in KPI cards, axes and tooltips."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    sign = "-" if value < 0 else ""
    value = abs(value)
    for size, suffix in ((1e9, "bn"), (1e6, "M"), (1e3, "K")):
        if value >= size:
            scaled = value / size
            text = f"{scaled:.0f}" if scaled >= 100 else f"{scaled:.1f}".rstrip("0").rstrip(".")
            return f"{sign}{prefix}{text}{suffix}"
    if value == int(value):
        return f"{sign}{prefix}{int(value)}"
    return f"{sign}{prefix}{value:.1f}"


def _nice_ticks(max_value: float, count: int = 5):
    """Round tick positions (0, 50bn, 100bn ...) for a money axis."""
    if not max_value or math.isnan(max_value) or max_value <= 0:
        return [0]
    raw_step = max_value / count
    power = 10 ** math.floor(math.log10(raw_step))
    step = min((m * power for m in (1, 2, 2.5, 5, 10) if m * power >= raw_step))
    return [i * step for i in range(int(max_value // step) + 2)]


def money_axis(fig: go.Figure, axis: str, max_value: float) -> go.Figure:
    """Label a revenue/budget axis as 0, 50bn, 100bn instead of 5e10."""
    ticks = _nice_ticks(max_value)
    settings = dict(tickvals=ticks, ticktext=[fmt_num(t) for t in ticks])
    if axis == "x":
        fig.update_xaxes(**settings)
    else:
        fig.update_yaxes(**settings)
    return fig


# ---------------------------------------------------------------------------
# Base layout - applied to every chart
# ---------------------------------------------------------------------------
def style(fig: go.Figure, title: str, x_title: str = "", y_title: str = "",
          height: int = 380, subtitle: str = "") -> go.Figure:
    """Apply the CinemaScope theme, a clear title, subtitle and axis labels."""
    full_title = f"<b>{title}</b>"
    if subtitle:
        full_title += f"<br><span style='font-size:12px;color:{MUTED}'>{subtitle}</span>"
    fig.update_layout(
        title=dict(text=full_title, x=0.025, xanchor="left", y=0.965, yanchor="top",
                   font=dict(size=15, color=TEXT, family=FONT)),
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(family=FONT, color=TEXT, size=12),
        height=height,
        margin=dict(l=14, r=22, t=82 if subtitle else 58, b=14),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=GOLD, align="left",
                        font=dict(color=TEXT, size=12, family=FONT)),
        showlegend=False,
        barcornerradius=5,
        bargap=0.28,
        transition=TRANSITION,
    )
    axis_style = dict(gridcolor=GRID, zeroline=False, linecolor=BORDER, showline=False,
                      tickfont=dict(color=MUTED, size=11), title_font=dict(color=MUTED, size=12),
                      title_standoff=10, automargin=True)
    fig.update_xaxes(title_text=x_title, **axis_style)
    fig.update_yaxes(title_text=y_title, **axis_style)
    return fig


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------
def empty_chart(title: str, message: str = "No data for the current filters",
                height: int = 380) -> go.Figure:
    """Placeholder panel shown instead of a chart when there is nothing to plot."""
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(color=MUTED, size=14))
    style(fig, title, height=height)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def bar_chart(data: pd.DataFrame, category: str, value: str, title: str,
              x_title: str = "", y_title: str = "", horizontal: bool = True,
              money: bool = True, hover_extra: dict = None, height: int = 380,
              subtitle: str = "", colour: str = GOLD) -> go.Figure:
    """Single-colour bar chart.

    hover_extra = {"movies": "Movies"} adds extra lines to the tooltip,
    e.g. the movie count, so small groups are easy to spot.
    """
    if data.empty:
        return empty_chart(title, "No group has enough movies - lower the 'Minimum movies' slider", height)
    hover_extra = hover_extra or {}
    custom = [data[value].map(lambda v: fmt_num(v) if money else f"{v:,.2f}")]
    value_label = (x_title if horizontal else y_title) or "Value"
    lines = [f"{value_label}: %{{customdata[0]}}"]
    for i, (col, label) in enumerate(hover_extra.items(), start=1):
        custom.append(data[col].map(lambda v: f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}"))
        lines.append(f"{label}: %{{customdata[{i}]}}")
    customdata = list(zip(*custom))

    # The leading bar is drawn in full colour, the rest slightly softer,
    # so the eye goes to the top performer first.
    colours = [colour] + [rgba(colour, 0.72)] * (len(data) - 1)
    marker = dict(color=colours, line=dict(width=0))
    if horizontal:
        trace = go.Bar(x=data[value], y=data[category], orientation="h",
                       marker=marker, customdata=customdata,
                       hovertemplate="<b>%{y}</b><br>" + "<br>".join(lines) + "<extra></extra>")
    else:
        trace = go.Bar(x=data[category], y=data[value], marker=marker,
                       customdata=customdata,
                       hovertemplate="<b>%{x}</b><br>" + "<br>".join(lines) + "<extra></extra>")
    fig = go.Figure(trace)
    style(fig, title, x_title, y_title, height, subtitle)
    if horizontal:
        fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")  # biggest bar on top
        if money:
            money_axis(fig, "x", data[value].max())
    else:
        fig.update_xaxes(gridcolor="rgba(0,0,0,0)", tickangle=-45 if len(data) > 6 else 0,
                         tickfont=dict(size=10 if len(data) > 10 else 11))
        if money:
            money_axis(fig, "y", data[value].max())
    return fig


def line_chart(data: pd.DataFrame, x: str, y: str, title: str, x_title: str = "",
               y_title: str = "", money: bool = True, area: bool = False,
               hover_extra: dict = None, height: int = 380, subtitle: str = "",
               colour: str = GOLD, fill: bool = False) -> go.Figure:
    """Line (or filled area) chart, e.g. revenue by release year.

    area=True  -> category x-axis area chart (e.g. directors)
    fill=True  -> soft tinted fill under a time-series line
    """
    if data.empty:
        return empty_chart(title, height=height)
    hover_extra = hover_extra or {}
    custom = [data[y].map(lambda v: fmt_num(v) if money else f"{v:,.2f}")]
    lines = [f"{y_title or y}: %{{customdata[0]}}"]
    for i, (col, label) in enumerate(hover_extra.items(), start=1):
        custom.append(data[col].map(lambda v: f"{v:,.0f}"))
        lines.append(f"{label}: %{{customdata[{i}]}}")
    filled = area or fill
    fig = go.Figure(go.Scatter(
        x=data[x], y=data[y], mode="lines+markers" if len(data) < 60 else "lines",
        line=dict(color=colour, width=2.6, shape="spline", smoothing=0.5),
        marker=dict(size=6, color=colour, line=dict(color=CARD, width=1.5)),
        fill="tozeroy" if filled else None,
        fillgradient=dict(type="vertical", colorscale=[[0, rgba(colour, 0.0)], [1, rgba(colour, 0.32)]])
        if filled else None,
        customdata=list(zip(*custom)),
        hovertemplate="<b>%{x}</b><br>" + "<br>".join(lines) + "<extra></extra>",
    ))
    style(fig, title, x_title, y_title, height, subtitle)
    fig.update_layout(hovermode="closest")
    if money:
        money_axis(fig, "y", data[y].max())
    return fig


def donut_chart(data: pd.DataFrame, names: str, values: str, title: str,
                centre_label: str = "Movies", max_slices: int = 5,
                height: int = 380, subtitle: str = "") -> go.Figure:
    """Donut chart. Slices after the top `max_slices` are merged into 'Other'."""
    data = data.sort_values(values, ascending=False)
    top = data.head(max_slices)
    rest = data.iloc[max_slices:]
    if len(rest):
        other_names = ", ".join(rest[names].astype(str))
        top = pd.concat([top, pd.DataFrame({names: ["Other"], values: [rest[values].sum()]})])
    colours = CATEGORY_COLOURS[:min(len(top), max_slices)] + ([OTHER_COLOUR] if len(rest) else [])
    hover_note = [f"<br><i>includes {other_names}</i>" if n == "Other" else "" for n in top[names]]
    fig = go.Figure(go.Pie(
        labels=top[names], values=top[values], hole=0.66, sort=False,
        marker=dict(colors=colours, line=dict(color=CARD, width=3)),
        textinfo="percent", textposition="inside", textfont=dict(color=BG, size=11),
        insidetextorientation="horizontal",
        customdata=hover_note,
        hovertemplate="<b>%{label}</b><br>Movies: %{value:,}<br>Share: %{percent}%{customdata}<extra></extra>",
        domain=dict(x=[0.0, 0.62]),
    ))
    total = int(top[values].sum())
    fig.add_annotation(text=f"<b style='font-size:22px'>{fmt_num(total)}</b><br>"
                            f"<span style='color:{MUTED}'>{centre_label}</span>",
                       x=0.31, y=0.5, xref="paper", yref="paper",
                       showarrow=False, font=dict(color=TEXT, size=12))
    style(fig, title, height=height, subtitle=subtitle)
    # hide % labels that do not fit inside tiny slices (they stay in the tooltip)
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode="hide")
    # legend sits in its own column to the right, so it never covers the ring
    fig.update_layout(showlegend=True,
                      legend=dict(font=dict(color=TEXT, size=12), orientation="v",
                                  x=0.68, xanchor="left", y=0.5, yanchor="middle",
                                  bgcolor="rgba(0,0,0,0)", itemclick="toggleothers"))
    return fig


def scatter_chart(data: pd.DataFrame, x: str, y: str, title: str, x_title: str = "",
                  y_title: str = "", money_x: bool = False, money_y: bool = False,
                  log_x: bool = False, log_y: bool = False, trendline: bool = True,
                  height: int = 420, subtitle: str = "") -> go.Figure:
    """Scatter plot of movies (one dot per movie) with an optional trend line."""
    if data.empty:
        return empty_chart(title, height=height)
    hover = (data["title"] + " (" + data["year"].astype(str) + ")<br>"
             + data["genre"] + "<br>" + (x_title or x) + ": " + data[x].map(lambda v: fmt_num(v))
             + "<br>" + (y_title or y) + ": " + data[y].map(lambda v: fmt_num(v)))
    fig = go.Figure(go.Scattergl(
        x=data[x], y=data[y], mode="markers",
        marker=dict(size=7, color=GOLD, opacity=0.5, line=dict(color=CARD, width=0.5)),
        text=hover, hovertemplate="%{text}<extra></extra>",
    ))
    if trendline and len(data) >= 3:
        # straight best-fit line (least squares), drawn on the axis scale actually shown
        xs = data[x].apply(math.log10) if log_x else data[x]
        ys = data[y].apply(math.log10) if log_y else data[y]
        mean_x, mean_y = xs.mean(), ys.mean()
        var_x = ((xs - mean_x) ** 2).sum()
        if var_x > 0:
            slope = ((xs - mean_x) * (ys - mean_y)).sum() / var_x
            x_line = pd.Series([xs.min(), xs.max()])
            y_line = mean_y + slope * (x_line - mean_x)
            fig.add_trace(go.Scatter(
                x=10 ** x_line if log_x else x_line, y=10 ** y_line if log_y else y_line,
                mode="lines", line=dict(color=TEAL, width=2, dash="dash"),
                hoverinfo="skip", name="Trend"))
    style(fig, title, x_title, y_title, height, subtitle)
    if log_x:
        fig.update_xaxes(type="log")
    if log_y:
        fig.update_yaxes(type="log")
    if money_x and not log_x:
        money_axis(fig, "x", data[x].max())
    if money_y and not log_y:
        money_axis(fig, "y", data[y].max())
    if log_x and money_x:
        _log_money_ticks(fig, "x", data[x])
    if log_y and money_y:
        _log_money_ticks(fig, "y", data[y])
    return fig


def _log_money_ticks(fig, axis, values):
    """Ticks like 1M, 10M, 100M, 1bn on a log axis."""
    low = math.floor(math.log10(max(values.min(), 1)))
    high = math.ceil(math.log10(values.max()))
    ticks = [10 ** p for p in range(low, high + 1)]
    settings = dict(tickvals=ticks, ticktext=[fmt_num(t) for t in ticks])
    (fig.update_xaxes if axis == "x" else fig.update_yaxes)(**settings)


def histogram(data: pd.DataFrame, column: str, title: str, x_title: str = "",
              y_title: str = "Number of movies", bin_size: float = 0.2,
              height: int = 380, subtitle: str = "") -> go.Figure:
    """Distribution chart, e.g. how many movies got each score."""
    fig = go.Figure(go.Histogram(
        x=data[column], xbins=dict(size=bin_size), marker_color=GOLD,
        marker_line=dict(color=CARD, width=1),
        hovertemplate=f"{x_title or column}: %{{x}}<br>Movies: %{{y:,}}<extra></extra>",
    ))
    style(fig, title, x_title, y_title, height, subtitle)
    fig.update_layout(bargap=0.05)
    return fig


def add_average_line(fig: go.Figure, value: float, label: str, axis: str = "y") -> go.Figure:
    """Dashed teal reference line (e.g. the overall average)."""
    if axis == "y":
        fig.add_hline(y=value, line=dict(color=TEAL, dash="dash", width=1.5),
                      annotation_text=label, annotation_font_color=TEAL,
                      annotation_position="top left")
    else:
        fig.add_vline(x=value, line=dict(color=TEAL, dash="dash", width=1.5),
                      annotation_text=label, annotation_font_color=TEAL,
                      annotation_position="top right")
    return fig
