# Viva Questions – Movie Industry Performance Dashboard

Short answers you can say in 20–30 seconds. Numbers are from the full dataset.

---

### About the project

**1. What does your project do?**
It analyses 5,421 movies released between 1980 and 2020 and presents the results as an interactive web dashboard. Users can see revenue by genre and year, rating trends, the top actors and directors, and budget versus ROI. They can filter by genre, year and certificate. The key insights are generated automatically from the data.

**2. Why did you build it in Python when you already had a Power BI dashboard?**
Power BI was our design prototype. With Python, every calculation is visible code that can be tested automatically with 39 pytest tests. The insight text is calculated instead of typed by hand. The project is also free and open source, and it runs in a browser without any licence. Both versions give the same totals (560bn revenue, 195bn budget, 34,653.5 score), which validates each one against the other.

**3. Explain the six modules and where they are in the code.**
1. Data Collection – `src/data_loader.py`
2. Preprocessing – `src/preprocessing.py`
3. Revenue & Genre – the genre and year functions in `src/analysis.py`
4. Rating Trends – the score functions in `src/analysis.py`
5. Actors & Directors – the people functions in `src/analysis.py`
6. Dashboard & Insights – `app.py`, the pages, `src/figures.py` and `src/insights.py`

Every page has a header comment that names its module.

**4. Which technologies did you use and why?**
- **Pandas** for tables and group-by calculations.
- **Plotly** for interactive charts with hover tooltips.
- **Streamlit** to turn Python scripts into a web app with no HTML or JavaScript.
- **pytest** for testing.
- **kaleido** to export the charts as PNG for the report.
- **python-pptx** to build the result slides.

**5. Explain the architecture.**
It has five layers:
1. CSV data
2. Preprocessing
3. Analysis (pure Pandas functions with no UI code)
4. Visualization (Plotly figure functions)
5. Streamlit dashboard

The user changes a filter, and Streamlit re-runs the page script, filters the data, and recalculates every chart and insight. Keeping the analysis separate from the UI means the same functions serve the dashboard, the tests, the notebook and the report figures.

### Data and preprocessing

**6. Where is the data from?**
A movie dataset with 15 attributes and 5,421 movies from 1980–2020. It matches the Kaggle "Movie Industry" dataset, which was scraped from IMDb. It keeps only movies that have both budget and revenue.

**7. What preprocessing did you do?**
Eight logged steps:
1. Trim spaces.
2. Convert number columns.
3. Handle missing values: drop rows missing title, genre, year or revenue; fill other text with "Unknown" and other numbers with the median.
4. Remove exact duplicates.
5. Remove title-plus-year duplicates.
6. Standardise certificates ("Unrated" → "Not Rated").
7. Validate ranges (score 0–10, no negative money).
8. Add profit, ROI, release date and decade.

The Data Quality page shows the rows before and after each step.

**8. Your dataset had no missing values or duplicates. So what did cleaning actually do?**
It confirmed that the data was clean, which is a result in itself. It also fixed one real inconsistency: 17 "Unrated" records were merged with 61 "Not Rated". It identified 84 repeated titles as remakes, not duplicates. The cleaning code also handles messy data: a test feeds it a dirty table and checks every rule.

**9. Why didn't you delete repeated titles like "Aladdin"?**
They have different years and directors (1992 and 2019), so they are different films (remakes). Deleting them would wrongly remove real revenue. We only treat a row as a duplicate when it has the same title **and** the same year.

**10. Why fill missing numbers with the median and not the mean?**
Movie data is skewed. The mean revenue is 103M but the median is only 37M, because a few blockbusters pull the mean up. The median represents a typical film better.

### Analysis and results

**11. Which genre earns the most?**
Action, with 237.8bn or 42% of all revenue from 1,415 films. The top three genres (Action, Comedy, Animation) earn 72%.

**12. The Power BI chart showed Family as the best genre by average revenue. Is that true?**
No. Family has only four films, so one or two hits create a huge average of 519M. We added a "minimum movies per group" slider (default 10) and show the movie count in every tooltip. With at least 10 films, Animation is the best genre per film, at 281M on average.

**13. Who are the top star and director?**
The top star by revenue is Robert Downey Jr. (11.9bn from 19 films). The top director is Steven Spielberg (9.6bn from 27 films). By average score, with at least 5 films, Christopher Nolan leads at 8.16.

**14. How did revenue change over time?**
Films from 2016–2020 earned 113bn, 873% more than films from 1980–1984. Revenue peaked in 2016 at 27.8bn. Revenue per film also grew, from 44M in 1980 to 245M in 2019. The drop in 2020 happens because only 8 films from 2020 are in the data.

**15. Do higher-rated films earn more?**
Only weakly: the correlation between score and revenue is 0.22. The number of votes, which measures popularity, is much more strongly linked to revenue (r = 0.61). Even so, average revenue rises from 48M for films scoring below 5 to 291M for films scoring 8 and above.

**16. What is correlation? What does r = 0.22 mean?**
Pearson's r measures how strongly two numbers move together on a straight line, from −1 to +1. A value of 0.22 means a weak positive relationship: higher scores tend to go with slightly higher revenue, but there are many exceptions. Correlation does not prove causation.

**17. How do you calculate ROI and why use the median?**
ROI = (revenue − budget) ÷ budget. A few micro-budget hits have huge ROI; *Paranormal Activity* cost $15K and earned $193M. Because of this, the mean ROI is 573% while the median is only 84%. The median shows the typical return. Horror has the best median ROI at 208%.

**18. How concentrated is revenue among directors?**
The top 10 of 2,063 directors earn 10.6% of all revenue while making only 2.4% of the films, which is about 4.5 times their share.

**19. Which certificate is most common, and which scores highest?**
R is the most common, with 2,597 films (48%), followed by PG-13 at 32%. Among certificates with at least 10 films, Not Rated has the highest average score (6.87), and PG has the lowest (6.22).

### Dashboard and implementation

**20. How do the filters work across all pages?**
`src/filters.py` draws the same sidebar on every page and returns the filtered DataFrame, so every chart uses that data. Streamlit forgets widget values when you change page, so we copy each value into `st.session_state`, and the filters stay the same on every page.

**21. How are the insights "calculated, not hard-coded"?**
`src/insights.py` builds each sentence from numbers computed on the filtered data. If you select only Drama, the genre insight talks about Drama. Even the takeaway wording changes: for example, it compares whether votes or score has the stronger correlation.

**22. What happens if a filter returns no movies?**
`stop_if_empty()` shows a friendly message asking the user to widen the filters, and stops the page before any chart is drawn. Charts that become empty because of the minimum-movies slider show a placeholder message. Automated tests check this on every page.

**23. How did you test the project?**
There are 39 pytest tests:
- The totals match Power BI.
- There are no duplicates.
- The top genre, star and director are correct.
- Genre and year totals add up to the overall total.
- Filters work.
- The insights change with filters.
- Every page loads with the full data, a 4-movie selection and an empty selection (using Streamlit AppTest).

**24. Why does performance stay fast?**
The CSV is read and cleaned only once and then cached (`lru_cache` and `st.cache_data`). After that, each filter only runs Pandas operations on 5,421 rows in memory, which takes milliseconds.

### Limitations and future work

**25. What are the limitations, and what would you add next?**
Limitations:
- Revenue is not adjusted for inflation.
- 2020 has only 8 films.
- Small genres have too few films for reliable averages.
- Each film has one genre and one star.
- The dataset favours large US releases.

Future work:
- Inflation adjustment with CPI data.
- Multi-genre labels.
- A box-office prediction model, after proper validation.
- Online deployment on Streamlit Community Cloud.
