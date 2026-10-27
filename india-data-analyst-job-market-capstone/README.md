# India Remote Data Analyst Job Market Capstone

**Dashboards:** [Current aggregate dashboard](reports/dashboard.html) · [Two-page mobile preview — Skill demand and Role comparison](reports/powerbi_preview.html) · [Role-skill aggregate CSV](reports/role_skill_latest.csv) · **Scope:** remote roles open to India-based applicants. This source has no reliable Chennai worksite filter, so the project does not claim to represent Chennai or on-site vacancies.

## Question

What skills do India-eligible remote data analyst job listings ask for, what salary ranges do they disclose by experience level, and how do the number and mix of listings change across weekly snapshots?

## Data source and access

This project uses the [Himalayas public Jobs API](https://himalayas.app/api), which supports country-filtered searches without an API key. The API documentation lists country filtering and exposes title, description, seniority, salary, currency, and pay period when supplied. It refreshes daily; this project collects weekly snapshots. A search API result is a platform sample, not a census of India's job market.

The query searches `data analyst` and filters `country=IN`. The API search matches job content broadly, so the collector keeps only titles matching data analyst, analytics analyst, or business-intelligence analyst patterns; unrelated jobs that mention the phrase only in a description are excluded. Himalayas listings are remote roles; the filter means they are open to applicants in India, not that the employer or worksite is in India. There is no Chennai city filter in this API. The project analyzes aggregates only, links back to Himalayas as the source, and does not publish copied job descriptions or individual listings. Follow the API's [terms and API-use rules](https://himalayas.app/terms) and [API documentation](https://himalayas.app/api), including its apply-link and attribution requirements if displaying listings.

## Initial snapshot — 25 October 2026

The first API pull reported 467 broad keyword-search candidates. A title filter retained 44 data analyst, analytics analyst, and business-intelligence analyst listings eligible to remote applicants in India. In this filtered snapshot, SQL appeared in 34/44 (77.3%), data visualization in 32/44 (72.7%), and Python in 30/44 (68.2%). Only 2/44 (4.5%) disclosed salary: one INR annual range (₹700,000–₹1,000,000) and one USD annual range ($98,000–$125,000). The salary sample is too small for a stable market estimate. This is one weekly baseline pull; temporal change needs later pulls.

## Run locally

1. Install Python 3.10+.
2. Run `python -m venv .venv`, activate it, and install `pip install -r requirements.txt`.
3. Collect the current API search sample: `python src/collect.py`.
4. Generate reports: `python src/analyze.py`.
5. Repeat weekly using `run_weekly.ps1`; optionally register the Windows task with `./register_weekly_task.ps1`. The published portfolio repository also has a weekly GitHub Actions workflow that stores the database as a private workflow artifact and publishes only aggregate reports.

No key or account is required. Collection pauses between requests and paginates through the results available at collection time. The API's public allowance is shared; avoid frequent polling. The feed refreshes daily, so weekly collection is sufficient for this study.

## Outputs

- `data/himalayas_jobs.db`: local history; ignored by Git. Job descriptions are processed in memory for skill extraction and are not stored in the database.
- `reports/skill_demand_latest.csv`: mention count and share per skill.
- `reports/salary_coverage_latest.csv`: total postings and salary coverage.
- `reports/salary_by_experience.csv`: salary groups split by experience label, currency, and pay period. Do not compare different currencies or pay periods directly.
- `reports/posting_counts_over_time.csv`: counts across weekly pulls.
- `reports/dashboard.html` and charts: aggregate dashboard and figures.

## Definitions and caveats

- **Skill demand:** keyword matches in listing title, excerpt, and description HTML after stripping markup. A listing can mention several skills, so percentages do not add to 100%.
- **Experience:** use the API seniority label when it is specific; otherwise use conservative explicit wording rules. Ambiguous postings are `unspecified`.
- **Salary:** keep API minimum/maximum, currency, and period as reported. Unreported salary stays missing; no conversion or imputation.
- **Weekly change:** compares returned search results, not total labor demand. New listings, ranking, query coverage, and roles leaving the platform can change counts.
- **Geography:** India eligibility is not a city/worksite location. No Chennai inference is made.

## Repository data policy

The public repository contains code and aggregate reporting only. The database and generated raw job data are local. Do not commit individual descriptions or bulk job listing exports.

## Power BI dashboard

A step-by-step Power BI Desktop guide and teal theme are available in [powerbi/README.md](powerbi/README.md). The guide covers the skill-demand page, role comparison page, salary caveats, and when it is valid to add a trends page. A genuine `.pbix` file must be authored and saved in Power BI Desktop on Windows; Android can view the HTML dashboards and source data but cannot run Power BI Desktop natively.

To prepare the role comparison data, from this project directory run:

```powershell
sqlite3 data/himalayas_jobs.db < powerbi/export_role_skill.sql
```

Check `reports/role_skill_latest.csv` before importing it. The SQLite database is kept private as a GitHub Actions artifact. The weekly workflow restores the previous database, collects the latest API snapshot, and regenerates this aggregate CSV automatically. The public repository contains only the aggregate output, not the database or individual listings.
