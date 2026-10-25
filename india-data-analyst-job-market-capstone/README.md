# India Data Analyst Job Market Capstone

**Dashboard:** [Open the current dashboard](reports/dashboard.html) · **Status:** pipeline ready; real postings require Adzuna API credentials and weekly collection.

**Question:** What skills do data-analyst postings in India request, how do advertised salaries vary by location and experience, and how do postings change across weekly snapshots?

This is a reproducible research pipeline, not a findings report yet. It contains no invented job records. Findings and charts appear after you add Adzuna API credentials and collect real snapshots.

## Data and use

Data comes from Adzuna's official job-search API (`jobs/in/search/{page}`), queried for `data analyst` across India and Chennai. The project stores API-returned postings in a local SQLite database, derives skill flags from title/description text, and records each collection run for time comparisons. Collection dates are UTC. Search results are a sample surfaced by Adzuna's API and are not a census of the Indian job market.

Adzuna documents API access, required `app_id`/`app_key`, and the search endpoint in its [overview](https://developer.adzuna.com/overview) and [search documentation](https://developer.adzuna.com/docs/search). Its [terms of service](https://developer.adzuna.com/docs/terms_of_service) permit personal and academic research; other uses may require written agreement. This project is for personal portfolio research. Review current terms and your account limits before collecting or publishing data. Do not publish raw ad text or credentials. The database stays local by default.

## Setup

1. Install Python 3.10+.
2. In this folder run `python -m venv .venv`, then activate it and run `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and fill in credentials from your Adzuna developer account. Never commit `.env`.
4. Collect a snapshot: `python src/collect.py --pages 2 --results-per-page 50`.
5. Build metrics and dashboard exports: `python src/analyze.py`.
6. Repeat collection weekly. Each run gets a `pull_id`; SQL retains first/last seen dates and weekly snapshots. Schedule `python src/collect.py` with Windows Task Scheduler or cron, then run analysis after each pull.

The API page count and result limits are configurable to respect account quotas. Start with a small pull. The collector runs one query for India and one for Chennai (25 km radius); Chennai jobs may also occur in the national query. The `pull_jobs` table preserves which query returned each posting.

## Outputs

`data/jobs.db` is created locally. Analysis writes summarized CSVs, chart PNGs, and `reports/dashboard.html` for use in Power BI/Tableau or as a local preview. CSVs are safe aggregate tables; inspect them before sharing. The dashboard includes counts, not ad descriptions or employer-level extracts.

## Definitions and caveats

- **Skill demand:** share of unique observed postings whose title/description contains a skill's maintained keyword patterns. One posting can mention multiple skills; percentages need not sum to 100%.
- **Salary:** API `salary_min` / `salary_max` values are stored as returned. Salary comparisons include only postings with disclosed salary. Do not infer an undisclosed salary from title or location.
- **Experience:** heuristic classification from explicit wording (internship, entry-level/fresher, senior/lead/principal, or years-of-experience phrases). Ambiguous ads remain `unspecified`; it is not an inferred candidate seniority label.
- **Change over time:** compare the first and latest collection `pull_id` for each query scope. Search result ranking, API coverage, duplicates, and ads expiring between pulls can change the observed sample.
- **Duplicates:** Adzuna ad IDs identify the record. A posting returned by both scopes is one job for deduplicated skill/salary summaries, but it remains linked to both scopes in `pull_jobs`.
- **Salary currency/period:** preserve the API values as returned; confirm the country API's unit and period in the current response/account documentation before interpreting or comparing values. The dashboard labels values as API-reported and avoids converting to annual pay.

## Project layout

- `src/collect.py` — official API ingestion and SQLite persistence
- `src/analyze.py` — SQL-backed metrics and aggregate exports
- `sql/analysis.sql` — reusable example queries
- `data/` — local database (ignored by Git)
- `reports/` — generated aggregates, charts, and dashboard (ignored by Git)

## Case study template

After at least four weekly pulls, write a short case study with the sample dates, query parameters, number of unique ads, top skills, salary coverage, city/experience sample sizes, and first-to-last changes. Include caveats and one chart per claim. Do not publish a conclusion until real pulls have populated the database.

### Weekly collection on Windows

After `.env` is configured and a manual run succeeds, open PowerShell in this folder and run `./register_weekly_task.ps1` to register a Monday 8:00 AM local-time task. Review/edit it in Windows Task Scheduler. The task runs `run_weekly.ps1`, which collects two pages per scope and refreshes reports. To remove it, run `Unregister-ScheduledTask -TaskName 'India Data Analyst Job Market Weekly Collection' -Confirm:$false`.

The official API schema lists `in` as a supported country code and documents `where` for place-based search: [live API schema](https://developer.adzuna.com/swagger/spec/test2.json). Confirm the endpoint returns useful coverage for the selected query when you first run it.



