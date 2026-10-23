# Fixes for the Report (pt1_nityasri.pdf) and the PPT (Niha-ppt.pptx)

Both files were read in full: the report (27 pages) and the PPT (12 slides).
Items are ordered by importance. ☐ = still to do by hand.

---

## A. Problems in BOTH documents

| # | Problem | Fix |
|---|---|---|
| A1 ☐ | **Guide mismatch.** PPT slide 1 lists two guides, *Dr. V. Ulagamuthalvi* and *Dr. M. Selvi*. The report (Bonafide, Declaration, Acknowledgement) names only *Dr. M. Selvi*. | Ask your department which is correct. If Dr. M. Selvi is the only guide, remove Dr. V. Ulagamuthalvi from slide 1. If there are two guides, add the second one to the Bonafide certificate and Acknowledgement. |
| A2 ☐ | **Dataset not identified.** The PPT references Kaggle, IMDb and TMDB, but the report names no dataset at all. TMDB was not used. | Add one dataset reference to both documents. The columns (budget, gross, score, votes, released, writer, star, company, runtime, rating, 1980–2020) match the Kaggle **"Movie Industry"** dataset by Daniel Grijalvo, which was scraped from IMDb. Please confirm this is where your CSV came from. Suggested reference: *D. Grijalvo, "Movie Industry: Four decades of movies," Kaggle, 2021. [Online]. Available: https://www.kaggle.com/datasets/danielgrijalvas/movies*. Remove TMDB from the PPT references. |
| A3 ☐ | **Implementation tool.** Both documents describe Power BI only. The PPT reference 5 says "Pandas and **Matplotlib**", but the project uses Plotly. | State that the system is implemented in **Python (Pandas, Plotly, Streamlit)** and that Power BI was used as the design prototype (see section B4). Change "Matplotlib" to "Plotly and Streamlit". |
| A4 ☐ | **Results have no numbers.** Report §5.1 says it "describes the intended outputs without inventing results"; PPT slide 9 is generic. | Replace Report Chapter 5 with `docs/results_chapter.md`. Replace PPT slide 9 with the slides in `results_slides.pptx` (section C). |

## B. Report (pt1_nityasri.pdf)

### B1. Front matter and page numbers
| # | Problem | Fix |
|---|---|---|
| B1.1 ☐ | **Table of Contents page numbers are wrong for the front matter.** It shows ABSTRACT → 5, ACKNOWLEDGEMENT → 3, LIST OF FIGURES → 7, LIST OF TABLES → 8, but these pages carry Roman numerals. | Use the actual page labels: ABSTRACT → **v**, ACKNOWLEDGEMENT → **iii**, LIST OF FIGURES → **vii**, LIST OF TABLES → **viii**. Also add BONAFIDE CERTIFICATE → i, DECLARATION → ii, TRAINING CERTIFICATE → iv. |
| B1.2 ☐ | ToC order: Abstract is listed **before** Acknowledgement, but in the report Acknowledgement (iii) comes before Abstract (v). | List the entries in the order the pages appear. |
| B1.3 ☐ | After you replace Chapter 5, the page numbers of Chapter 5, Chapter 6 and References will change. | In Word: *References → Update Table → Update entire table*, or retype the numbers. |
| B1.4 ☐ | **Training Certificate page (iv) is blank.** | Scan the certificate and insert it. |
| B1.5 ☐ | **Declaration names only NITYASRI.S** ("I, NITYASRI.S (44110544) … done by me"). | Make it a joint declaration: "We, NITYASRI.S (44110544) and NIHASRIKA VIJAYAN (44110534), hereby declare … done by us …", with two signature lines. (Or check whether each student submits a separate copy.) |
| B1.6 ☐ | The Bonafide certificate says "**Project Phase-1**", but the title page says "Professional Training I". | Use one name consistently, probably "Professional Training I". |
| B1.7 ☐ | The Acknowledgement is written as "I / me / my" although there are two students. | Change to "We / us / our". |
| B1.8 ☐ | **List of Figures** has only 4.1 and 4.2. **List of Tables** has 5.1 "Dashboard Visualizations…". | Add Figures 5.1–5.16 and Tables 5.1–5.5 from the new Chapter 5. Remove the old Table 5.1, or keep it as Table 5.6 if you keep that text. |

### B2. Chapter 3 – Requirements
| # | Problem | Fix |
|---|---|---|
| B2.1 ☐ | §3.1.1 Technical Feasibility mentions Power BI only. | Add: "The final implementation uses Python 3.11 with Pandas for data processing, Plotly for interactive charts and Streamlit for the web dashboard. All of these are free and open source." |
| B2.2 ☐ | Table 3.2 Software Requirements lists Power BI / Power Query only. | Add these rows: *Programming language – Python 3.10+*; *Libraries – Pandas, Plotly, Streamlit, python-pptx, kaleido*; *Testing – pytest*; *Browser – Edge / Chrome*; *IDE – VS Code*. |
| B2.3 ☐ | §3.1.2 Economic Feasibility and Table 4.4 mention possible Power BI licensing costs. | Note that the Python implementation has **no licence cost**. |
| B2.4 ☐ | Table 3.1, risk "Unclear revenue units". | Add the finding: revenue and budget are in nominal US dollars and are **not inflation-adjusted** (see §5.11). |

### B3. Chapter 4 – Proposed System
| # | Problem | Fix |
|---|---|---|
| B3.1 ☐ | §4.3 has 5 subsections (Data Collection, Preprocessing, **Data Analysis**, **Visualization**, Dashboard & Insights). The PPT and the code use **6 modules** (Revenue & Genre, Rating Trend, Actor & Director are separate). | Rename §4.3.3 to "Revenue & Genre Analysis Module". Split out §4.3.4 "Rating Trend Analysis Module" and §4.3.5 "Actor & Director Analysis Module", then make §4.3.6 "Dashboard & Market Insights Module" (merge the Visualization text into it). Renumber the Testing Plan to §4.3.7. Add one line to each subsection naming its file (see the README module table). |
| B3.2 ☐ | Figure 4.1 is a one-line text arrow ("Movie Dataset → Data Cleaning → …"). | Replace it with the architecture diagram on slide 6 of `results_slides.pptx`: right-click the slide → *Save as Picture* → insert it in the report. |
| B3.3 ☐ | Many sentences are written in the future or conditional tense ("can be used", "should be", "is intended to"). | Now that the system is built, change them to the past or present tense ("was implemented", "is used"). |
| B3.4 ☐ | Table 4.2 Test Plan has no results column. | Copy Table 5.5 (Test results) from `docs/results_chapter.md`; all 39 automated tests pass. |

### B4. Chapter 5 – replace completely
Paste `docs/results_chapter.md`. It contains:
- 5.1 Implementation
- 5.2 Dataset and preprocessing
- 5.3 KPIs
- 5.4 Genres
- 5.5 Ratings
- 5.6 Actors and directors
- 5.7 Budget and ROI
- 5.8 Insights
- 5.9 Testing
- 5.10 Discussion
- 5.11 Limitations

Insert each figure from `reports/figures/` where the text says **Figure 5.x**.

### B5. Chapter 6 and References
| # | Problem | Fix |
|---|---|---|
| B5.1 ☐ | §6.2 Future Enhancement "Add vote counts and rating distributions" is **already done** (Rating Trends page). The same applies to "drill-through pages for movie, actor, and director profiles" (Movie Explorer and the person look-up). | Remove both items, or reword them as achieved. Possible new items: inflation adjustment using CPI data; multi-genre labels; a box-office prediction model; deployment on Streamlit Community Cloud. |
| B5.2 ☐ | §6.1 Conclusion has no findings. | Add 2–3 sentences with the main numbers: Action 42% of revenue; Robert Downey Jr. and Steven Spielberg top earners; score–revenue r = 0.22 vs votes–revenue r = 0.61; revenue +873% from 1980–84 to 2016–20. |
| B5.3 ☐ | References contain no software or dataset entries. | Add: the dataset (A2); *Streamlit Inc., "Streamlit documentation," https://docs.streamlit.io*; *Plotly Technologies Inc., "Plotly Python graphing library," https://plotly.com/python/*; *W. McKinney, "Data Structures for Statistical Computing in Python," Proc. 9th Python in Science Conf., 2010* (Pandas). |

## C. PPT (Niha-ppt.pptx)

| # | Slide | Problem | Fix |
|---|---|---|---|
| C1 ☐ | 1 | Two guides (see A1). The title placeholder is empty; the title sits in the subtitle box. | Fix the guide names. Put the title "MOVIE INDUSTRY PERFORMANCE DASHBOARD" in the title box. |
| C2 ☐ | 3 | **Course Certificate slide is empty**, and its footer and date are missing. | Insert the certificate image, or delete the slide and remove "Certificate" from the Agenda. |
| C3 ☐ | 7 | **System Architecture / Ideation Map is empty.** | Copy slide 6 of `results_slides.pptx`. It shows Data Layer → Preprocessing → Analysis (Modules 3–5) → Visualization → Streamlit Dashboard, with the user's filter loop. |
| C4 ☐ | 8 | Module 4 says "across different genres and years", and Module 6 does not mention filters. | Module 4: "…across genres, years **and certificates**". Module 6: add "with shared filters, a movie explorer and CSV download". You could add the file name for each module in small text. |
| C5 ☐ | 9 | Results slide is a paragraph with no numbers. | Replace it with slides 1–5 of `results_slides.pptx` (dashboard, KPIs, genre, actor/director, insights). |
| C6 ☐ | 10 | Conclusion has no findings. | Add the 3 headline numbers (see B5.2). |
| C7 ☐ | 11 | TMDB, which was not used, and "Matplotlib" are listed; the footer and date are missing. | Use the references from A2 and B5.3 instead. Restore the footer. |
| C8 ☐ | All | The date "18 September 2026" is fixed on every slide. | Update it to the review date (*Insert → Header & Footer → Date*). |
| C9 ☐ | 2 | Agenda includes "Certificate" and "System Architecture". | Keep these only if the slides are filled (C2, C3). Consider adding a "Live Demo" item. |

## D. How to copy the new slides into Niha-ppt.pptx
1. Open both `results_slides.pptx` and `Niha-ppt.pptx`.
2. In `results_slides.pptx`, select the slides in the left panel and press **Ctrl+C**.
3. In `Niha-ppt.pptx`, click below slide 8 and right-click → **Paste Options → Keep Source Formatting** (this keeps the navy design).
4. Delete the old slide 9. Move the architecture slide into position 7.
