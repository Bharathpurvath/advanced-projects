# Power BI dashboard

This folder contains the reproducible build guide and theme for a local Power BI Desktop report based on the aggregate CSVs in `../reports/`.

## Current snapshot

Data checked on 27 October 2026. The latest snapshot was collected on 26 October 2026 and contains 46 India-eligible remote analyst listings. Skill mentions overlap, so percentages do not sum to 100%. Only 3 of 46 listings disclose salary: 2 INR annual ads and 1 USD annual ad. There is only one successful weekly snapshot, so do not present a trend line as a trend yet.

## Requirements

- Windows 10 or later
- Power BI Desktop
- This repository cloned or downloaded locally

Power BI Desktop is free for local authoring. A Power BI account is not needed to build and save a local `.pbix`. Public interactive publishing has separate account, tenant, and licensing requirements; do not make publication a blocker.

## 1. Open Power BI Desktop

Install Power BI Desktop from the Microsoft Store or Microsoft's official download page: https://powerbi.microsoft.com/desktop/

Open a blank report. Optionally import `theme.json` through View > Themes > Browse for themes.

## 2. Import data

Use Home > Get data > Text/CSV and load these files from the local project directory:

- `reports/skill_demand_latest.csv`
- `reports/salary_by_experience.csv`
- `reports/salary_coverage_latest.csv`
- `reports/posting_counts_over_time.csv`
- `reports/pull_history.csv`
- `reports/role_skill_latest.csv` after generating it with the SQL file in this folder

For each CSV, select Transform Data if you need to verify types. Set `postings`, `pct_postings`, `salary_ads`, `mean_midpoint`, `salary_min`, and `salary_max` to numeric types as appropriate. Keep `collected_at` as Date/Time/Timezone or convert a duplicate column to Date for chart axes. Keep salary currency and period as text categories.

These files are snapshots, not a normalized relational model. You can build the skill page without relationships. Do not create relationships between unrelated rows just because they share a pull ID.

## 3. Page: Skill demand

Rename page to **Skill demand**.

### KPI cards

Create three Card visuals:

1. Listings in latest snapshot: use `salary_coverage_latest[postings]` (46)
2. Top skill share: use a measure based on the maximum skill percentage
3. Skills tracked: distinct count of `skill_demand_latest[skill]` (12)

Create these measures from Modeling > New measure. If your table names differ, update the names to match the names shown in the Data pane.

```DAX
Listings in Snapshot =
MAX ( salary_coverage_latest[postings] )

Top Skill Share (%) =
MAX ( skill_demand_latest[pct_postings] )

Skills Tracked =
DISTINCTCOUNT ( skill_demand_latest[skill] )
```

Format Top Skill Share as a decimal with one decimal place and append a % in the visual title, because the CSV stores percentage points (78.3), not a fraction (0.783).

### Main bar chart

Add a Clustered bar chart. Set Y-axis to `skill_demand_latest[skill]` and X-axis to `skill_demand_latest[pct_postings]`. Sort descending by pct_postings. Turn on data labels and set the X-axis maximum to 100. Title: **Share of listings mentioning each skill**.

### Detail table

Add a Table visual with `skill`, `postings`, and `pct_postings`. Sort descending by pct_postings. Format pct_postings as a percentage-point value with one decimal and label the column **Listings mentioning skill (%)**.

Add a small text note: “One listing can mention multiple skills. Percentages may sum to more than 100%. Snapshot collected 26 Oct 2026.”

## 4. Page: Role comparison

Create a new page named **Role comparison**. Import `reports/role_skill_latest.csv` after running `export_role_skill.sql` from the project root as described below.

Add a Clustered column chart:
- X-axis: `role_family`
- Y-axis: `postings` (Sum)
- Legend: `skill`

Use a visual-level Top N filter on skill, Top 6 by Sum of postings. Check the generated CSV first. The role family mapping is a simple title keyword rule, not a validated occupational taxonomy.

### Salary disclosure section

Use `salary_by_experience.csv` and `salary_coverage_latest.csv` to show disclosure context. The snapshot has only three salary ads. Do not title any salary figure “market average”. Label figures **Advertised salary midpoint (sample of disclosed ads)** and show currency and pay period explicitly. Do not compare INR and USD values on a common axis or in a single numeric KPI.

A safer layout is a table with experience level, currency, pay period, salary ad count, midpoint, minimum and maximum. Filter each currency to its own visual if using cards.

## 5. Trends page — defer until more data exists

`posting_counts_over_time.csv` currently contains one successful snapshot. A line chart with one point is not evidence of a trend. After at least 3–4 weekly pulls, add a page named **Snapshot history** with collected date on X-axis and postings on Y-axis. Keep the title factual: **Listings returned by each weekly search snapshot**. Re-run the role export after each collection if role comparisons should reflect the latest pull.

## 6. Save and verify

Save the report in this directory as `job-market-dashboard.pbix`. The PBIX is a local binary report and must be created by Power BI Desktop; this repository guide cannot fabricate a valid PBIX without running Desktop.

Before committing screenshots, verify:
- all visuals show the 26 Oct 2026 snapshot
- skill shares use the CSV values and are sorted descending
- the salary sample size and currency are visible
- no individual job descriptions, URLs, or bulk listing data are included
- trends are marked as not yet available until several snapshots exist

For portfolio sharing, commit screenshots and the PBIX only if you are comfortable with the file size and repository policy. For public interactive access, evaluate Looker Studio or current Microsoft sharing requirements separately. Public embedding exposes the underlying semantic model to viewers; never include raw listings or private data.
