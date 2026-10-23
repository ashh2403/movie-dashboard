# CHAPTER 5 — RESULTS AND DISCUSSION

> **How to use this file:** this chapter replaces the current Chapter 5 of the report (pages 15–16).
> Every number below was calculated by the project code (`src/analysis.py`, `src/insights.py`)
> on the cleaned dataset; the same values appear in the dashboard and in `notebooks/eda.ipynb`.
> Figures are in `reports/figures/` and are named after their figure number
> (e.g. Figure 5.2 = `fig5_2_revenue_by_genre.png`). Money values are in US dollars;
> "bn" = billion, "M" = million.

---

## 5.1 Implementation Overview

The proposed system was implemented in two forms. The first is an interactive Microsoft Power BI report, which served as the visual prototype. The second is a complete Python implementation built with **Pandas** (data handling and analysis), **Plotly** (interactive charts) and **Streamlit** (the web dashboard). The Python version reproduces the Power BI layout. It also adds automated testing, a documented cleaning log and insights generated from the data.

The six modules described in Chapter 4 map directly to source files:

| Module | Implementation |
|---|---|
| 1. Data Collection | `src/data_loader.py` — loads the CSV and renames the 15 columns |
| 2. Data Preprocessing | `src/preprocessing.py` — eight cleaning steps with a cleaning log |
| 3. Revenue & Genre Analysis | `src/analysis.py`, dashboard page *Revenue & Genre* |
| 4. Rating Trend Analysis | `src/analysis.py`, dashboard page *Rating Trends* |
| 5. Actor & Director Analysis | `src/analysis.py`, dashboard page *Actors & Directors* |
| 6. Dashboard & Market Insights | `app.py`, `src/figures.py`, `src/insights.py`, shared sidebar filters |

The dashboard contains a Home page and six analysis pages. Every page shares the same filters for genre, release-year range and certificate, and all charts and insight cards are recalculated whenever a filter changes.

## 5.2 Dataset and Preprocessing Results

The dataset contains **5,421 movies** released between **1980 and 2020**, described by 15 attributes: title, genre, release year, revenue, rating score, director, star, budget, votes, runtime, country, company, release date, writer and certificate. Most of the films are American (79.7%), followed by British (9.1%) and Canadian (2.0%) productions.

Table 5.1 summarises the outcome of the preprocessing module.

**Table 5.1: Results of the data preprocessing steps**

| Step | Check performed | Result |
|---|---|---|
| 1 | Extra spaces in text fields | 0 values changed |
| 2 | Non-numeric values in number fields | 0 invalid values |
| 3 | Missing values (all 15 columns) | 0 missing values; no rows removed |
| 4 | Exact duplicate rows | 0 found |
| 5 | Same title released twice in the same year | 0 found |
| 6 | Inconsistent certificate labels | 17 "Unrated" records merged into "Not Rated" |
| 7 | Out-of-range values (score outside 0–10, negative money, invalid year) | 0 found |
| 8 | Derived fields | profit, ROI, release date, release country and decade added |
| — | **Rows before / after cleaning** | **5,421 / 5,421** |

Eighty-four titles occur more than once (169 rows), for example *Aladdin* (1992 and 2019) and *A Nightmare on Elm Street* (1984 and 2010). Because each occurrence has a different release year and director, these are remakes rather than duplicates and were retained. The source dataset had already been partially cleaned, so no row needed to be removed. The totals of the Python implementation are therefore identical to those of the Power BI dashboard (Table 5.2), which validates both implementations against each other.

## 5.3 Dashboard Outputs and Key Performance Indicators

Figure 5.1 shows the Home page of the dashboard. It contains the four KPI cards, the six overview charts and the four automatically generated insight cards.

**Figure 5.1: Home page of the Movie Industry Performance Dashboard** (`fig5_1_dashboard_home.png`)

**Table 5.2: Key performance indicators (all movies)**

| Indicator | Value | Power BI value |
|---|---|---|
| Total movies | 5,421 | 5K (5,421) |
| Total revenue | 559.61 bn USD | 560bn |
| Total budget | 195.21 bn USD | 195bn |
| Sum of rating score | 34,653.5 | 34.65K |
| Average revenue per movie | 103.2 M USD (median 36.9 M) | — |
| Average rating score | 6.39 / 10 | — |
| Revenue ÷ budget | 2.87 | — |

The large gap between the mean (103.2 M) and the median (36.9 M) revenue shows that the revenue distribution is highly right-skewed: a small number of blockbusters earn far more than a typical film.

## 5.4 Revenue and Genre Analysis (Module 3)

**Figure 5.2: Total revenue by genre** (`fig5_2_revenue_by_genre.png`)

Revenue is strongly concentrated in a few genres (Figure 5.2). **Action is the leading genre, with 237.75 bn USD (42.5% of all revenue) from 1,415 movies.** Comedy is second with 88.51 bn (15.8%). Comedy has the largest number of films (1,496) but earns only about a third of Action's revenue. Animation is third with 77.87 bn (13.9%) from only 277 films. Together, the top three genres account for **72.2%** of total revenue. Drama (52.10 bn, 9.3%) and Adventure (43.58 bn, 7.8%) complete the top five.

**Figure 5.3: Average revenue per movie by genre (genres with at least 10 movies)** (`fig5_3_avg_revenue_by_genre.png`)

Average revenue per movie gives a different ranking (Figure 5.3). **Animation earns the most per film (281.1 M USD on average; median 192.3 M)**. Action follows with 168.0 M and Adventure with 133.3 M. In the raw data, Family appears to be the best genre with an average of 518.6 M. However, this value is based on only four films, so it is not a reliable estimate. The dashboard therefore applies a *minimum movies per group* threshold (default 10). It also shows the movie count in every tooltip, so that small groups (Family 4, Western 2, Romance 5, Sci-Fi 6, Thriller 7) are not presented as leaders.

**Figure 5.4: Total revenue by release year** (`fig5_4_revenue_by_year.png`)

Total revenue grew steadily across the four decades (Figure 5.4). It rose from 1.77 bn USD in 1980 (40 films) to a **peak of 27.85 bn in 2016**, and then remained almost constant at 27.6–27.7 bn between 2017 and 2019. Films released in the last five years of the dataset (2016–2020) earned **113.05 bn**, which is **873% more** than the 11.62 bn earned by films released in 1980–1984. This growth is not only caused by the larger number of films per year. Average revenue per film also increased, from 44.3 M in 1980 to 245.1 M in 2019. The sharp fall in 2020 (2.27 bn) is an artefact of the data: only eight films from 2020 are included.

**Figure 5.5: Genre share of revenue by decade** (`fig5_5_genre_share_by_decade.png`)

Figure 5.5 shows that Action's dominance has increased over time. Its share of each decade's revenue grew from 34.9% in the 1980s to 36.3% in the 1990s, 38.1% in the 2000s and 48.2% in the 2010s. Over the same period, Comedy's share declined and Animation's share grew, which reflects the rise of franchise and family-animation films.

## 5.5 Rating Trend Analysis (Module 4)

**Figure 5.6: Number of movies by certificate** (`fig5_6_movies_by_certificate.png`)

R-rated films form the largest group, with 2,597 movies (47.9%). They are followed by PG-13 (1,729; 31.9%), PG (907; 16.7%) and G (111; 2.0%), as shown in Figure 5.6. The remaining 77 films are Not Rated, NC-17, TV-MA, X or Approved.

**Figure 5.7: Distribution of rating scores** (`fig5_7_score_distribution.png`)

Rating scores are approximately normally distributed around a **mean of 6.39** (median 6.5, standard deviation 0.96), within a range of 1.9 to 9.3 (Figure 5.7). Two thirds of the films (67.6%) score between 6.0 and 7.9. Only 3.6% score 8.0 or above, and 7.0% score below 5.0. The highest-rated film in the dataset is *The Shawshank Redemption* (9.3).

**Figure 5.8: Average rating score by release year** (`fig5_8_avg_score_by_year.png`)

Average scores are stable over time and range from 6.07 (1983) to 6.61 (2020, only 8 films) (Figure 5.8). The decade average rose slightly, from 6.34 in the 1980s to 6.49 in the 2010s.

**Figure 5.9: Average rating score by genre (genres with at least 10 movies)** (`fig5_9_avg_score_by_genre.png`)

Genres that rate well differ from genres that earn well (Figure 5.9). **Biography has the highest average score (7.09)**, followed by Drama (6.72), Animation (6.69) and Crime (6.69). Horror (5.83), Fantasy (6.05) and Comedy (6.19) score lowest. Action, the highest-earning genre, has a below-average score of 6.25. Among certificates with at least 10 films, Not Rated films (6.87) and NC-17 films (6.66) score highest, while PG-13 (6.29) and PG (6.22) score lowest.

**Figure 5.10: Rating score versus revenue** (`fig5_10_score_vs_revenue.png`)
**Figure 5.11: Number of votes versus rating score** (`fig5_11_votes_vs_score.png`)

**Table 5.3: Correlation between numeric attributes (Pearson r, all 5,421 movies)**

| Pair of attributes | r | Strength |
|---|---|---|
| Budget – Revenue | 0.740 | strong positive |
| Votes – Revenue | 0.615 | strong positive |
| Votes – Score | 0.474 | moderate positive |
| Runtime – Score | 0.414 | moderate positive |
| Runtime – Revenue | 0.276 | weak positive |
| Score – Revenue | 0.223 | weak positive |

The correlation between score and revenue is weak (r = 0.22; Figure 5.10), whereas the number of votes is strongly correlated with revenue (r = 0.62). Popularity, measured as audience reach, is therefore more closely linked to box-office success than perceived quality is. Votes and score are moderately correlated (r = 0.47; Figure 5.11), so widely seen films tend to be rated slightly higher.

Even so, the average revenue of a film rises consistently with its score band (Table 5.4). The weak overall correlation is mainly caused by the very large spread of revenue within each band.

**Table 5.4: Average revenue by rating-score band**

| Score band | Movies | Average revenue |
|---|---|---|
| Below 5 | 377 | 48.1 M |
| 5 – 6 | 1,185 | 64.9 M |
| 6 – 7 | 2,291 | 95.8 M |
| 7 – 8 | 1,371 | 137.0 M |
| 8 and above | 197 | 291.2 M |

## 5.6 Actor and Director Analysis (Module 5)

**Figure 5.12: Top 10 stars by total revenue** (`fig5_12_top_stars_by_revenue.png`)

**Robert Downey Jr. is the highest-earning star, with 11.86 bn USD from 19 films** (an average of 624.0 M per film). He is followed by Tom Hanks (9.90 bn, 38 films), Tom Cruise (9.44 bn, 33 films), Will Smith (7.95 bn, 23 films) and Johnny Depp (7.41 bn, 31 films), as shown in Figure 5.12. The ranking reflects both talent and volume. Robert Downey Jr. leads because of a very high revenue per film, whereas Tom Hanks's total is built on twice as many films. The top 10 stars, out of 1,845, account for 13.9% of all revenue but only 4.5% of the films.

**Figure 5.13: Top 10 directors by total revenue** (`fig5_13_top_directors_by_revenue.png`)

**Steven Spielberg is the highest-earning director, with 9.63 bn USD from 27 films** and a high average score of 7.44. He is followed by Anthony Russo (6.84 bn from only 5 films, an average of 1.37 bn per film), Peter Jackson (6.62 bn, 11 films), Michael Bay (6.45 bn, 13 films) and James Cameron (6.25 bn, 7 films). Revenue is highly concentrated among directors: **the top 10 of 2,063 directors earn 10.6% of total revenue while directing only 2.4% of the films**, which is about 4.5 times their share of films.

**Figure 5.14: Top 10 directors by average rating score (minimum 5 films)** (`fig5_14_top_directors_by_score.png`)

Ranked by average score, with a minimum of five films to avoid one-film outliers, the leading directors are Christopher Nolan (8.16, 11 films), Quentin Tarantino (8.10), Hayao Miyazaki (8.10), Denis Villeneuve (7.98) and James Cameron (7.87) (Figure 5.14). Christopher Nolan, James Cameron and Peter Jackson appear in both the revenue and the score rankings, so they combine commercial and critical success. Among stars with at least five films, the highest average scores belong to Kang-ho Song (7.74), Leonardo DiCaprio (7.50, 20 films), Kevin Spacey (7.48) and Viggo Mortensen (7.48).

The most successful star–director partnerships were Anthony Russo with Robert Downey Jr. (4.85 bn from 2 films), David Yates with Daniel Radcliffe (3.22 bn, 3 films) and Gore Verbinski with Johnny Depp (3.19 bn, 5 films). All of these partnerships belong to large film franchises.

## 5.7 Budget and Return on Investment

**Figure 5.15: Budget versus revenue (log scale)** (`fig5_15_budget_vs_revenue.png`)
**Figure 5.16: Median ROI by genre (genres with at least 10 movies)** (`fig5_16_median_roi_by_genre.png`)

Budget is the attribute most strongly associated with revenue (r = 0.74; Figure 5.15). Across all films, revenue exceeded budget by a total of **364.40 bn USD**. However, success is not guaranteed: **32.2% of films (1,744) earned less than their budget**. Return on investment, defined as ROI = (revenue − budget) ÷ budget, is extremely skewed. The median ROI is 83.6%, while the mean is 572.7% because of a few low-budget hits; *Paranormal Activity* earned 193.4 M on a 15,000 USD budget. The median is therefore used to compare genres.

As Figure 5.16 shows, **Horror gives the best typical return (median ROI 208.4%)**, followed by Animation (192.0%) and Fantasy (113.7%). Crime (30.4%), Biography (47.4%) and Drama (52.6%) give the lowest. Animation combines a high ROI with the highest median profit per film (121.7 M). The most profitable individual films were *Avatar* (2.61 bn profit), *Avengers: Endgame* (2.44 bn) and *Titanic* (2.00 bn).

## 5.8 Key Market Insights (Module 6)

The Home page generates the following four insights automatically from the filtered data. The values shown here are for the full dataset.

1. **Revenue growth:** Films released in 2016–2020 earned 113 bn, 873% more than those released in 1980–1984. Revenue peaked in 2016 (27.8 bn). 2020 contains only 8 films.
2. **Genre performance:** Action earns 42% of all revenue, and the top three genres earn 72%. Revenue is therefore concentrated rather than evenly spread across genres.
3. **Director impact:** The top 10 directors earn 11% of revenue from 2% of the films, led by Steven Spielberg (9.6 bn from 27 films).
4. **Audience ratings:** Score is only weakly linked to revenue (r = 0.22), while votes, a measure of popularity, are strongly linked (r = 0.61). Biography is the highest-rated genre (7.09).

Because these sentences are generated from the data rather than written by hand, they remain correct under any filter. For example, selecting only Drama films updates the genre insight to describe Drama.

## 5.9 Testing and Validation Results

The test plan in Table 4.2 was automated with **pytest** (`tests/test_analysis.py` and `tests/test_pages.py`). All **39 tests passed**.

**Table 5.5: Test results**

| Test ID | Activity | Result |
|---|---|---|
| T-01 | Import dataset | 5,421 rows × 15 columns loaded; columns renamed — **Pass** |
| T-02 | Missing and duplicate records | 0 missing values, 0 duplicates; the cleaning rules were also verified on a deliberately messy sample table — **Pass** |
| T-03 | Average revenue by genre | Genre totals sum exactly to overall revenue; small genres hidden below the threshold — **Pass** |
| T-04 | Yearly revenue view | Yearly totals sum exactly to overall revenue — **Pass** |
| T-05 | Genre and year filters | Filtered data contains only the selected genre and years; empty selections show a message instead of an error — **Pass** |
| T-06 | Actor and director summaries | Top star = Robert Downey Jr., top director = Steven Spielberg, top genre = Action (match Power BI) — **Pass** |
| T-07 | Labels and units | All charts have titles, axis labels and Power BI-style number formats (560bn, 12M, 5.4K) — **Pass** |
| T-08 | Usability | All 7 pages load without errors for the full data, a 4-movie selection and an empty selection — **Pass** |

## 5.10 Discussion

The results show that commercial success in this dataset is concentrated along three dimensions: **genre** (Action), **people** (a small group of franchise directors and stars) and **time** (recent decades). The analysis also shows that the best measure depends on the question being asked:

* **Total** revenue rewards volume (Comedy has the most films), **average** revenue rewards consistent high earners (Animation), and **median ROI** rewards cheap productions with a dedicated audience (Horror). A studio that maximises total revenue, revenue per film or return on investment would therefore choose different genres.
* Critical quality and box-office revenue are related but distinct. Biography and Drama score highest but earn little per film, whereas Action earns the most with below-average scores. Popularity (number of votes) explains revenue better than the score does.
* Rankings of people depend on the number of films each person has. The dashboard therefore shows the movie count next to every total and requires a minimum number of films before ranking anyone by average score.

These findings are associations, not causes. Budget, marketing, franchise status, release timing and distribution all influence revenue, and the dataset does not contain most of these factors.

## 5.11 Limitations

* **No inflation adjustment.** Revenue and budget are nominal US-dollar values, so part of the growth since 1980 reflects inflation and higher ticket prices rather than real growth.
* **Incomplete final year.** 2020 contains only 8 films, and 1980–1982 contain fewer than 75 films each. Totals for these years are not comparable with other years.
* **Small genres.** Family (4 films), Western (2), Romance (5), Sci-Fi (6) and Thriller (7) are too small for reliable averages. Each film has only one genre label, so genres such as Family are under-represented.
* **Selection bias.** The dataset includes only films for which both budget and revenue were available. These are mostly larger, mainly American releases (79.7%), so small and independent films are under-represented.
* **Data-entry outliers.** A few budgets are extremely small (16 films below 100,000 USD). Some are genuine micro-budget films, but they inflate ROI values, which is why medians are used.
* **One star per film.** Only the lead star is recorded, so supporting actors receive no credit in the actor analysis.
* **Release dates.** For 708 films the release-date year differs from the year column, because the release date is the release in one particular country. The year column was used for all analysis.
