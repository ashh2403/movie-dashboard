"""
SHARED PAGE LOOK (MODULE 6 - DASHBOARD)
---------------------------------------
"CinemaScope Intelligence" design system used by every page:
  * page CSS (colours, typography, cards, sidebar, responsive rules)
  * brand header with the active-filter summary
  * KPI cards with real-data sparklines and optional links to detail pages
  * compact insights panel, fact rows and safe chart rendering

All colours come from src/charts.py so charts and page match exactly.
"""

import html

import streamlit as st

from src.charts import (BG, BORDER, CARD, CORAL, GOLD, MUTED, PURPLE, SIDEBAR, SURFACE, TEAL,
                        TEXT, rgba)

ACCENTS = {"gold": GOLD, "coral": CORAL, "teal": TEAL, "purple": PURPLE}

# ---------------------------------------------------------------------------
# Small line icons (24x24, stroke style) - consistent instead of emojis
# ---------------------------------------------------------------------------
_ICON_PATHS = {
    "film": "<rect x='3' y='3' width='18' height='18' rx='2'/><path d='M7 3v18M17 3v18M3 7.5h4M3 12h18M3 16.5h4M17 7.5h4M17 16.5h4'/>",
    "revenue": "<path d='M3 17l6-6 4 4 8-8'/><path d='M14 7h7v7'/>",
    "budget": "<path d='M19 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2'/><path d='M21 12h-6a2 2 0 0 0 0 4h6v-4z'/>",
    "star": "<path d='M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z'/>",
    "trophy": "<path d='M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4z'/><path d='M17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3'/>",
    "layers": "<path d='M12 3l9 5-9 5-9-5 9-5z'/><path d='M3 13l9 5 9-5'/>",
    "chart": "<path d='M4 20V10M10 20V4M16 20v-7M22 20H2'/>",
    "calendar": "<rect x='3' y='5' width='18' height='16' rx='2'/><path d='M16 3v4M8 3v4M3 11h18'/>",
    "link": "<path d='M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1'/><path d='M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1'/>",
    "users": "<circle cx='9' cy='8' r='4'/><path d='M2 21a7 7 0 0 1 14 0M17 4a4 4 0 0 1 0 8M22 21a7 7 0 0 0-4-6.3'/>",
    "director": "<path d='M4 11h16v9a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-9z'/><path d='M4 11l2.5-6 13 2.5-1.2 3.5'/><path d='M9 5.8l2 3.6M14 6.8l2 3.6'/>",
    "percent": "<path d='M19 5L5 19'/><circle cx='6.5' cy='6.5' r='2.5'/><circle cx='17.5' cy='17.5' r='2.5'/>",
    "down": "<path d='M3 7l6 6 4-4 8 8'/><path d='M14 17h7v-7'/>",
    "ticket": "<path d='M3 8a2 2 0 0 0 2-2h14a2 2 0 0 0 2 2v2a2 2 0 0 0 0 4v2a2 2 0 0 0-2 2H5a2 2 0 0 0-2-2v-2a2 2 0 0 0 0-4V8z'/><path d='M13 6v12' stroke-dasharray='2 2'/>",
    "check": "<circle cx='12' cy='12' r='9'/><path d='M8 12l3 3 5-6'/>",
    "inbox": "<path d='M3 13h5l2 3h4l2-3h5'/><path d='M5 5h14l2 8v6H3v-6l2-8z'/>",
    "copy": "<rect x='8' y='8' width='13' height='13' rx='2'/><path d='M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3'/>",
    "search": "<circle cx='11' cy='11' r='7'/><path d='M21 21l-5-5'/>",
    "clock": "<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/>",
    "spark": "<path d='M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8'/>",
}


def icon(name: str, size: int = 18, colour: str = "currentColor") -> str:
    """Inline SVG icon by name (falls back to the text itself, e.g. an emoji)."""
    path = _ICON_PATHS.get(name)
    if path is None:
        return html.escape(name)
    return (f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{colour}' "
            f"stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>{path}</svg>")


# Clapperboard brand mark (gold, used in the header and the sidebar logo)
BRAND_MARK = (
    "<svg width='34' height='34' viewBox='0 0 40 40' aria-hidden='true'>"
    f"<rect x='1' y='1' width='38' height='38' rx='10' fill='{SURFACE}' stroke='{BORDER}'/>"
    f"<path d='M9 17h22v12a2 2 0 0 1-2 2H11a2 2 0 0 1-2-2V17z' fill='none' stroke='{GOLD}' stroke-width='2'/>"
    f"<path d='M9 17l1.6-6.3 21 4.9-.4 1.4' fill='none' stroke='{GOLD}' stroke-width='2' stroke-linejoin='round'/>"
    f"<path d='M15 12.1l2.4 4.4M21.5 13.6l2.4 4.4' stroke='{CORAL}' stroke-width='2' stroke-linecap='round'/>"
    "</svg>"
)

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

:root {{
  --bg:{BG}; --sidebar:{SIDEBAR}; --card:{CARD}; --surface:{SURFACE}; --border:{BORDER};
  --gold:{GOLD}; --coral:{CORAL}; --teal:{TEAL}; --purple:{PURPLE}; --text:{TEXT}; --muted:{MUTED};
  --radius:14px; --ease:cubic-bezier(.2,.7,.2,1);
}}

/* ---------- Page canvas: deep navy with a faint warm "projector" glow ---------- */
.stApp {{
  background:
    radial-gradient(1100px 420px at 85% -120px, {rgba(GOLD, 0.07)}, transparent 70%),
    radial-gradient(900px 380px at 0% -160px, {rgba(PURPLE, 0.06)}, transparent 70%),
    var(--bg);
}}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container, [data-testid="stMainBlockContainer"] {{
  padding-top: 2.6rem !important; padding-bottom: 2.5rem; max-width: 1480px; }}
h1, h2, h3, h4 {{ font-family: Manrope, Inter, 'Segoe UI', sans-serif; letter-spacing: -.01em; }}
h4 {{ font-size: 1.02rem !important; color: var(--text); margin: .4rem 0 .2rem 0 !important; }}

/* ---------- Brand header ---------- */
.cs-brand {{ display:flex; align-items:center; gap:.65rem; margin-bottom:.55rem; }}
.cs-brand-name {{ font: 700 .78rem/1 Inter, sans-serif; letter-spacing:.16em; text-transform:uppercase;
                  color: var(--text); }}
.cs-brand-name span {{ color: var(--gold); }}
.cs-brand-tag {{ font: 500 .72rem/1 Inter, sans-serif; color: var(--muted); padding:.28rem .55rem;
                 border:1px solid var(--border); border-radius:999px; background:{rgba(SURFACE, 0.5)}; }}
.cs-headline {{ font: 800 2.15rem/1.12 Manrope, Inter, sans-serif; color: var(--text); margin:0;
                letter-spacing:-.02em; }}
.cs-headline em {{ font-style: normal; background: linear-gradient(90deg, {GOLD}, {CORAL});
                   -webkit-background-clip: text; background-clip: text; color: transparent; }}
.cs-sub {{ color: var(--muted); font-size: .95rem; margin:.4rem 0 .8rem 0; max-width: 820px; line-height:1.5; }}
.cs-page-title {{ font: 800 1.65rem/1.15 Manrope, Inter, sans-serif; color: var(--text); margin:0; }}
.cs-page-title em {{ font-style: normal; color: var(--gold); }}

/* Film-strip hairline under the header: a subtle cinematic detail */
.cs-filmstrip {{ height: 6px; margin: .2rem 0 1.1rem 0; opacity:.55; border-radius: 3px;
  background: repeating-linear-gradient(90deg, {rgba(MUTED, 0.22)} 0 10px, transparent 10px 18px); }}

/* Active-filter chips */
.cs-chips {{ display:flex; flex-wrap:wrap; gap:.4rem; margin:.1rem 0 0 0; }}
.cs-chip {{ display:inline-flex; align-items:center; gap:.35rem; font: 500 .78rem/1 Inter, sans-serif;
            color: var(--text); background: var(--surface); border:1px solid var(--border);
            padding:.38rem .65rem; border-radius:999px; white-space:nowrap; }}
.cs-chip b {{ color: var(--muted); font-weight:500; }}
.cs-chip.on {{ border-color:{rgba(GOLD, 0.55)}; background:{rgba(GOLD, 0.10)}; }}
.cs-chip.on b {{ color: var(--gold); }}

/* ---------- KPI cards ---------- */
.cs-kpi {{ position:relative; background: linear-gradient(180deg, {rgba(SURFACE, 0.55)}, {CARD} 70%);
           border:1px solid var(--border); border-radius: var(--radius); padding: .95rem 1.05rem .8rem;
           min-height: 152px; overflow:hidden;
           transition: transform .25s var(--ease), border-color .25s var(--ease), box-shadow .25s var(--ease); }}
.cs-kpi::before {{ content:""; position:absolute; inset:0 0 auto 0; height:1px;
                   background: linear-gradient(90deg, transparent, var(--accent), transparent); opacity:.7; }}
.cs-kpi-top {{ display:flex; align-items:center; gap:.55rem; }}
.cs-kpi-icon {{ width:30px; height:30px; border-radius:9px; display:grid; place-items:center;
                color: var(--accent); background: color-mix(in srgb, var(--accent) 14%, transparent);
                flex-shrink:0; font-size:.95rem; }}
.cs-kpi-label {{ font: 600 .8rem/1.2 Inter, sans-serif; color: var(--muted); letter-spacing:.01em; }}
.cs-kpi-value {{ font: 800 2rem/1.1 Manrope, Inter, sans-serif; color: var(--text); margin:.55rem 0 .15rem 0;
                 letter-spacing:-.02em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.cs-kpi-value.long {{ font-size: 1.32rem; white-space: normal; line-height:1.2; margin-top:.65rem; }}
.cs-kpi-value small {{ font-size:.9rem; color: var(--muted); font-weight:600; margin-left:.2rem; }}
.cs-kpi-note {{ font-size:.76rem; color: var(--muted); line-height:1.35; }}
.cs-kpi-spark {{ margin-top:.45rem; height:30px; }}
.cs-kpi-spark svg {{ display:block; width:100%; height:30px; }}
.cs-kpi-foot {{ display:flex; justify-content:space-between; font-size:.68rem; color:{rgba(MUTED, 0.8)};
                margin-top:.15rem; }}

/* Clickable KPI cards: the whole card is the page link (keyboard accessible) */
/* every wrapper between the card container and the link stays static, so the
   link's ::after overlay (and the arrow) are positioned against the whole card */
[class*="st-key-kpi-"] {{ position:relative; gap:0 !important; }}
[class*="st-key-kpi-"] [data-testid="stElementContainer"],
[class*="st-key-kpi-"] [data-testid="stPageLink"],
[class*="st-key-kpi-"] [data-testid="stPageLink"] * {{ position: static !important; }}
[class*="st-key-kpi-"] [data-testid="stPageLink"] a {{ padding: 0 !important; margin: 0 !important;
  min-height: 0 !important; height: 0; background: transparent !important; }}
[class*="st-key-kpi-"] [data-testid="stPageLink"] a::after {{ content:""; position:absolute; inset:0;
  border-radius: var(--radius); z-index: 2; cursor: pointer; }}
[class*="st-key-kpi-"] [data-testid="stPageLink"] a p {{ position:absolute !important; right:.95rem; top:.85rem;
  margin:0; font-size:.95rem !important; color: var(--muted) !important; font-weight:600;
  transition: color .2s var(--ease), transform .2s var(--ease); }}
[class*="st-key-kpi-"]:hover [data-testid="stPageLink"] a p {{ color: var(--gold) !important; transform: translate(2px,-2px); }}
[class*="st-key-kpi-"] .cs-kpi-top {{ padding-right: 1.4rem; }}
[class*="st-key-kpi-"]:hover .cs-kpi {{ transform: translateY(-2px); border-color:{rgba(GOLD, 0.45)};
  box-shadow: 0 10px 28px -14px rgba(0,0,0,.7); }}
[class*="st-key-kpi-"]:focus-within .cs-kpi {{ border-color: var(--gold); box-shadow: 0 0 0 2px {rgba(GOLD, 0.35)}; }}

/* ---------- Chart cards ---------- */
[data-testid="stPlotlyChart"] {{ border:1px solid var(--border); border-radius: var(--radius); overflow:hidden;
  background: var(--card); animation: cs-fade .45s var(--ease) both;
  transition: border-color .25s var(--ease); }}
[data-testid="stPlotlyChart"]:hover {{ border-color: {rgba(MUTED, 0.38)}; }}
@keyframes cs-fade {{ from {{ opacity:0; transform: translateY(4px); }} to {{ opacity:1; transform:none; }} }}
.js-plotly-plot .modebar {{ background: transparent !important; }}
.js-plotly-plot .modebar-btn path {{ fill: {MUTED} !important; }}

/* Bordered containers (st.container(border=True)) share the card look */
[data-testid="stVerticalBlockBorderWrapper"] {{ background: var(--card); border-color: var(--border) !important;
  border-radius: var(--radius) !important; }}

/* ---------- Section headings ---------- */
.cs-section {{ display:flex; flex-wrap:wrap; align-items:baseline; column-gap:.75rem; row-gap:.15rem;
                margin: 1.5rem 0 .65rem 0; }}
.cs-section-title {{ font: 700 1.22rem/1.2 Manrope, Inter, sans-serif; color: var(--text); letter-spacing:-.01em; }}
.cs-section span {{ color: var(--muted); font-size:.82rem; }}

/* ---------- Insights panel ---------- */
.cs-insights {{ background: var(--card); border:1px solid var(--border); border-radius: var(--radius);
                padding: 1rem 1.05rem .5rem; height:100%; animation: cs-fade .45s var(--ease) both; }}
.cs-insights-head {{ display:flex; align-items:center; gap:.5rem; margin-bottom:.55rem; }}
.cs-insights-head b {{ font: 700 .98rem/1.2 Manrope, Inter, sans-serif; color: var(--text); }}
.cs-insights-head span {{ margin-left:auto; font-size:.7rem; color: var(--muted); border:1px solid var(--border);
                          padding:.2rem .5rem; border-radius:999px; }}
.cs-insight {{ padding:.7rem 0 .75rem; border-top:1px solid {rgba(MUTED, 0.12)}; }}
.cs-insight:first-of-type {{ border-top:none; padding-top:.2rem; }}
.cs-insight-title {{ display:flex; align-items:center; gap:.45rem; font: 700 .72rem/1 Inter, sans-serif;
                     letter-spacing:.09em; text-transform:uppercase; color: var(--accent); }}
.cs-insight-title i {{ width:7px; height:7px; border-radius:50%; background: var(--accent); display:inline-block; }}
.cs-insight-take {{ color: var(--text); font-weight:600; font-size:.88rem; line-height:1.38; margin:.4rem 0 .2rem; }}
.cs-insight-body {{ color: var(--muted); font-size:.8rem; line-height:1.45; }}

/* Fact rows */
.cs-fact {{ display:flex; gap:.6rem; align-items:flex-start; background: var(--card); border:1px solid var(--border);
            padding:.6rem .85rem; border-radius: 10px; color: var(--text); font-size:.88rem; margin-bottom:.45rem; }}
.cs-fact i {{ flex-shrink:0; width:6px; height:6px; margin-top:.5rem; border-radius:50%; background: var(--gold); }}

/* Data notes (honest caveats such as the incomplete final year) */
.cs-note {{ display:flex; gap:.6rem; align-items:flex-start; font-size:.82rem; color: var(--muted);
            background:{rgba(SURFACE, 0.55)}; border:1px dashed {rgba(MUTED, 0.3)}; border-radius:10px;
            padding:.55rem .8rem; margin:.5rem 0 .2rem 0; line-height:1.45; }}
.cs-note b {{ color: var(--text); }}

/* Alerts (empty states etc.) */
[data-testid="stAlert"] {{ border-radius: 12px; border:1px solid var(--border); }}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{ background: var(--sidebar); border-right: 1px solid var(--border); }}
[data-testid="stSidebarHeader"] {{ padding-bottom: .4rem; }}
[data-testid="stSidebarNav"] {{ padding-top: .2rem; }}
[data-testid="stNavSectionHeader"] {{ font: 700 .66rem/1 Inter, sans-serif !important; letter-spacing:.14em;
  text-transform: uppercase; color: {rgba(MUTED, 0.75)} !important; margin-top:.7rem !important; }}
[data-testid="stSidebarNavLink"] {{ border-radius: 10px; margin: 1px .2rem; padding: .38rem .7rem !important;
  transition: background .2s var(--ease), color .2s var(--ease), transform .2s var(--ease); position:relative; }}
[data-testid="stSidebarNavLink"]:hover {{ background: {rgba(SURFACE, 0.9)} !important; transform: translateX(2px); }}
[data-testid="stSidebarNavLink"] span {{ color: var(--muted); font-weight:500; font-size:.9rem; }}
[data-testid="stSidebarNavLink"][aria-current="page"] {{ background: {rgba(GOLD, 0.12)} !important; }}
[data-testid="stSidebarNavLink"][aria-current="page"] span {{ color: var(--text); font-weight:600; }}
[data-testid="stSidebarNavLink"][aria-current="page"]::before {{ content:""; position:absolute; left:-.2rem; top:22%;
  bottom:22%; width:3px; border-radius:3px; background: var(--gold); }}
[data-testid="stSidebarNavSeparator"] {{ border-color: var(--border) !important; }}

.cs-side-head {{ display:flex; align-items:center; justify-content:space-between; margin:.2rem 0 .35rem; }}
.cs-side-head b {{ font: 700 .98rem/1 Manrope, Inter, sans-serif; color: var(--text); }}
.cs-badge {{ font: 700 .7rem/1 Inter, sans-serif; color: {BG}; background: var(--gold); border-radius:999px;
             padding:.25rem .5rem; }}
.cs-badge.off {{ color: var(--muted); background: var(--surface); border:1px solid var(--border); }}
.cs-group {{ font: 700 .66rem/1 Inter, sans-serif; letter-spacing:.14em; text-transform:uppercase;
             color: {rgba(MUTED, 0.75)}; margin: 1rem 0 .1rem; padding-top:.85rem; border-top:1px solid var(--border); }}
.cs-group.first {{ border-top:none; padding-top:.2rem; margin-top:.3rem; }}
.cs-range {{ display:flex; justify-content:space-between; font: 600 .78rem/1 Inter, sans-serif; color: var(--text);
             margin: -.35rem 0 .1rem; }}
.cs-range span {{ color: var(--muted); font-weight:500; }}
.cs-count {{ font-size:.8rem; color: var(--muted); text-align:center; margin-top:.6rem; }}
.cs-count b {{ color: var(--text); }}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{ font-size:.84rem; font-weight:600; color: var(--text); }}
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [role="group"] {{ background: {CARD};
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease); }}
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [role="group"]:hover {{ border-color: {rgba(GOLD, 0.5)}; }}
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [role="group"]:focus-within {{
  border-color: var(--gold); box-shadow: 0 0 0 2px {rgba(GOLD, 0.18)}; }}
.st-key-reset_filters button {{ border:1px solid var(--border); background: transparent; color: var(--text);
  transition: all .2s var(--ease); }}
.st-key-reset_filters button:hover:not(:disabled) {{ border-color: var(--gold); color: var(--gold);
  background:{rgba(GOLD, 0.08)}; }}

/* Buttons (download etc.) */
[data-testid="stDownloadButton"] button, [data-testid="stBaseButton-secondary"] {{
  transition: all .2s var(--ease); }}

/* Tabs */
[data-baseweb="tab-list"] {{ gap:.25rem; }}
[data-baseweb="tab"] {{ border-radius: 10px 10px 0 0; }}

/* Keyboard focus is always visible */
a:focus-visible, button:focus-visible, [role="tab"]:focus-visible {{
  outline: 2px solid var(--gold) !important; outline-offset: 2px; }}

/* ---------- Responsive ---------- */
@media (max-width: 1200px) {{
  .cs-kpi-value {{ font-size: 1.7rem; }}
  .cs-headline {{ font-size: 1.85rem; }}
}}
@media (max-width: 900px) {{
  .block-container, [data-testid="stMainBlockContainer"] {{ padding-left: 1rem !important;
     padding-right: 1rem !important; padding-top: 3.2rem !important; }}
  .cs-headline {{ font-size: 1.55rem; }}
  .cs-page-title {{ font-size: 1.35rem; }}
  .cs-kpi {{ min-height: 0; }}
}}
@media (max-width: 640px) {{
  .cs-headline {{ font-size: 1.35rem; }}
  .cs-sub {{ font-size: .86rem; }}
  .cs-brand-tag {{ display:none; }}
  .cs-kpi {{ margin-bottom: .6rem; }}
}}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation: none !important; transition: none !important; }}
}}
</style>
"""

# Sidebar logo (clapperboard + wordmark), written as an SVG data file at import
_LOGO_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='236' height='40' viewBox='0 0 236 40'>"
    f"<rect x='1' y='3' width='34' height='34' rx='9' fill='{SURFACE}' stroke='{BORDER}'/>"
    f"<path d='M8 17h20v11a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2V17z' fill='none' stroke='{GOLD}' stroke-width='2'/>"
    f"<path d='M8 17l1.5-5.6 19 4.4-.4 1.2' fill='none' stroke='{GOLD}' stroke-width='2' stroke-linejoin='round'/>"
    f"<path d='M13.5 12.6l2.2 4M19.5 14l2.2 4' stroke='{CORAL}' stroke-width='2' stroke-linecap='round'/>"
    f"<text x='46' y='19' font-family='Manrope, Inter, Segoe UI, sans-serif' font-size='15' font-weight='800' "
    f"fill='{TEXT}'>CinemaScope</text>"
    f"<text x='46' y='33' font-family='Inter, Segoe UI, sans-serif' font-size='9.5' font-weight='600' "
    f"letter-spacing='2.4' fill='{GOLD}'>INTELLIGENCE</text>"
    "</svg>"
)
_ICON_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 36 40'>"
    f"<rect x='1' y='3' width='34' height='34' rx='9' fill='{SURFACE}' stroke='{BORDER}'/>"
    f"<path d='M8 17h20v11a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2V17z' fill='none' stroke='{GOLD}' stroke-width='2'/>"
    f"<path d='M8 17l1.5-5.6 19 4.4-.4 1.2' fill='none' stroke='{GOLD}' stroke-width='2' stroke-linejoin='round'/>"
    "</svg>"
)


def setup_page(page_title: str, icon_: str = "🎬"):
    """First call on every page: browser tab title, wide layout, CSS, logo."""
    st.set_page_config(page_title=f"{page_title} · CinemaScope Intelligence", page_icon=icon_,
                       layout="wide", initial_sidebar_state="auto")
    st.markdown(CSS, unsafe_allow_html=True)
    try:
        st.logo(_LOGO_SVG, size="large", icon_image=_ICON_SVG)
    except Exception:       # older Streamlit without SVG logos: the header still shows the brand
        pass


def _brand_row(tag: str = "") -> str:
    tag_html = f"<span class='cs-brand-tag'>{html.escape(tag)}</span>" if tag else ""
    return (f"<div class='cs-brand'>{BRAND_MARK}"
            f"<div class='cs-brand-name'>CinemaScope <span>Intelligence</span></div>{tag_html}</div>")


def chips_html(chips) -> str:
    """chips = [(label, value, is_active), ...] -> row of filter chips."""
    parts = [f"<span class='cs-chip{' on' if on else ''}'><b>{html.escape(label)}</b>{html.escape(value)}</span>"
             for label, value, on in chips]
    return f"<div class='cs-chips' aria-label='Active filters'>{''.join(parts)}</div>"


def dashboard_header(subtitle: str, chips=None, tag: str = ""):
    """Home page header: brand, headline, subtitle and the active-filter summary."""
    st.markdown(
        _brand_row(tag)
        + "<h1 class='cs-headline'>The business behind the <em>big screen</em>.</h1>"
        + f"<p class='cs-sub'>{html.escape(subtitle)}</p>"
        + (chips_html(chips) if chips else "")
        + "<div class='cs-filmstrip' aria-hidden='true'></div>",
        unsafe_allow_html=True)


_ACRONYMS = {"ROI", "KPI", "USD", "CSV"}


def _title_case(text: str) -> str:
    """'BUDGET & ROI ANALYSIS' -> 'Budget & ROI Analysis' (acronyms stay upper case)."""
    return " ".join(w if w.upper() in _ACRONYMS else w.capitalize() for w in text.split())


def page_header(first: str, accent: str, subtitle: str, module: str = "", chips=None):
    """Inner page header, e.g. 'Revenue & Genre Analysis' with the accent word in gold."""
    if chips is None:
        from src.filters import filter_chips   # local import: filters is page-level
        chips = filter_chips()
    st.markdown(
        _brand_row(module)
        + f"<h1 class='cs-page-title'>{html.escape(_title_case(first))} <em>{html.escape(_title_case(accent))}</em></h1>"
        + f"<p class='cs-sub'>{html.escape(subtitle)}</p>"
        + (chips_html(chips) if chips else "")
        + "<div class='cs-filmstrip' aria-hidden='true'></div>",
        unsafe_allow_html=True)


def section(title: str, note: str = ""):
    """Small section heading with an optional muted note."""
    note_html = f"<span>{html.escape(note)}</span>" if note else ""
    st.markdown(f"<div class='cs-section'><div class='cs-section-title' role='heading' aria-level='2'>"
                f"{html.escape(title)}</div>{note_html}</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
def sparkline(values, colour: str, partial_last: bool = False) -> str:
    """Tiny inline-SVG trend line built from REAL values (e.g. revenue per year).

    partial_last=True draws the final segment dotted, for an incomplete year.
    """
    vals = [float(v) for v in values]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    w, h, pad = 100.0, 30.0, 3.0
    pts = [(i * w / (len(vals) - 1), h - pad - (v - lo) / span * (h - 2 * pad)) for i, v in enumerate(vals)]
    main = pts[:-1] if partial_last else pts
    line = " ".join(f"{x:.2f},{y:.2f}" for x, y in main)
    area = f"0,{h} " + line + f" {main[-1][0]:.2f},{h}"
    gid = f"g{abs(hash((tuple(vals), colour))) % 10**8}"
    tail = ""
    if partial_last:
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        tail = (f"<polyline points='{x1:.2f},{y1:.2f} {x2:.2f},{y2:.2f}' fill='none' stroke='{MUTED}' "
                f"stroke-width='1.4' stroke-dasharray='2 2' vector-effect='non-scaling-stroke'/>")
    return (f"<svg viewBox='0 0 {w:.0f} {h:.0f}' preserveAspectRatio='none' role='img' aria-label='trend per release year'>"
            f"<defs><linearGradient id='{gid}' x1='0' y1='0' x2='0' y2='1'>"
            f"<stop offset='0' stop-color='{colour}' stop-opacity='.28'/>"
            f"<stop offset='1' stop-color='{colour}' stop-opacity='0'/></linearGradient></defs>"
            f"<polygon points='{area}' fill='url(#{gid})'/>"
            f"<polyline points='{line}' fill='none' stroke='{colour}' stroke-width='1.8' "
            f"stroke-linejoin='round' vector-effect='non-scaling-stroke'/>{tail}</svg>")


def _kpi_html(card: dict) -> str:
    accent = ACCENTS.get(card.get("accent", "gold"), card.get("accent", GOLD))
    value = html.escape(str(card["value"]))
    unit = f"<small>{html.escape(card['unit'])}</small>" if card.get("unit") else ""
    spark = ""
    if card.get("spark") is not None and len(card["spark"]) > 1:
        spark = (f"<div class='cs-kpi-spark'>{sparkline(card['spark'], accent, card.get('partial_last', False))}</div>"
                 f"<div class='cs-kpi-foot'><span>{html.escape(card.get('spark_from', ''))}</span>"
                 f"<span>{html.escape(card.get('spark_label', ''))}</span>"
                 f"<span>{html.escape(card.get('spark_to', ''))}</span></div>")
    return (f"<div class='cs-kpi' style='--accent:{accent}'>"
            f"<div class='cs-kpi-top'><div class='cs-kpi-icon'>{icon(card.get('icon', 'chart'))}</div>"
            f"<div class='cs-kpi-label'>{html.escape(card['label'])}</div></div>"
            f"<div class='cs-kpi-value{' long' if len(str(card['value'])) > 9 else ''}' title='{value}'>"
            f"{value}{unit}</div>"
            f"<div class='cs-kpi-note'>{html.escape(card.get('note', ''))}</div>{spark}</div>")


def kpi_cards(cards):
    """Row of KPI cards.

    Each card is either a tuple (label, value, note, icon) or a dict with keys:
      label, value, note, icon, accent ('gold' | 'coral' | 'teal' | 'purple'),
      unit, spark (list of real values), spark_from / spark_to / spark_label,
      partial_last, link (page file to open), link_label.
    """
    accents = ["gold", "coral", "teal", "purple"]
    columns = st.columns(len(cards))
    for i, (col, card) in enumerate(zip(columns, cards)):
        if not isinstance(card, dict):
            label, value, note, icon_name = card
            card = {"label": label, "value": value, "note": note, "icon": icon_name}
        card.setdefault("accent", accents[i % len(accents)])
        with col:
            if card.get("link"):
                with st.container(key=f"kpi-{i}-{card['label'].lower().replace(' ', '-')}"):
                    st.markdown(_kpi_html(card), unsafe_allow_html=True)
                    st.page_link(card["link"], label="↗", help=card.get("link_label", "Open details"))
            else:
                st.markdown(_kpi_html(card), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------
def insights_panel(cards, heading: str = "Key insights into market trends", badge: str = "Live"):
    """Compact panel: each insight shows its takeaway first, then the numbers."""
    accents = [GOLD, CORAL, PURPLE, TEAL]
    rows = []
    for card, accent in zip(cards, accents):
        title = card["title"].split(". ", 1)[-1]
        rows.append(f"<div class='cs-insight' style='--accent:{accent}'>"
                    f"<div class='cs-insight-title'><i></i>{html.escape(title)}</div>"
                    f"<div class='cs-insight-take'>{html.escape(card['takeaway'])}</div>"
                    f"<div class='cs-insight-body'>{html.escape(card['text'])}</div></div>")
    st.markdown(f"<div class='cs-insights' role='region' aria-label='{html.escape(heading)}'>"
                f"<div class='cs-insights-head'>{icon('spark', 16, GOLD)}<b>{html.escape(heading)}</b>"
                f"<span>{html.escape(badge)}</span></div>{''.join(rows)}</div>", unsafe_allow_html=True)


def insight_cards(cards, heading: str = "Key insights into market trends"):
    """Backward-compatible name: renders the insights panel."""
    insights_panel(cards, heading)


def facts(lines):
    """Short highlighted facts under a chart."""
    for line in lines:
        st.markdown(f"<div class='cs-fact'><i></i><div>{html.escape(line)}</div></div>", unsafe_allow_html=True)


def note(text_html: str):
    """Muted, dashed-border data note (text may contain <b> tags; caller escapes data)."""
    st.markdown(f"<div class='cs-note'>{icon('clock', 16, MUTED)}<div>{text_html}</div></div>",
                unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
_CHART_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "cinemascope_chart"},
}


def show_chart(fig_or_builder, *args, key=None, **kwargs):
    """Draw a Plotly chart full width.

    Accepts a finished figure, or a builder function plus its arguments, e.g.
    show_chart(figures.revenue_by_genre, df). With a builder, any error while
    building is shown as a friendly message instead of breaking the page.
    """
    if callable(fig_or_builder):
        try:
            fig = fig_or_builder(*args, **kwargs)
        except Exception as exc:        # error state: keep the rest of the page working
            st.error(f"This chart could not be drawn for the current selection ({type(exc).__name__}). "
                     "Try widening the filters or press Reset filters.", icon=":material/error:")
            return None
    else:
        fig = fig_or_builder
    return st.plotly_chart(fig, width="stretch", config=_CHART_CONFIG, key=key)
