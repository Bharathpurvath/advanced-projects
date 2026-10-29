# Power BI dashboard

This folder contains the finished Power BI Desktop report, its aggregate source workbook, theme, and build notes.

## Latest snapshot

The report uses the snapshot collected on 27 October 2026: 45 remote analyst listings open to applicants in India and 12 tracked skills. SQL leads the skill list at 35 listings (77.8%). Only 3 of 45 listings disclose salary. Those ads use different currencies, so their amounts are not directly comparable. Two successful weekly snapshots are available; that is not enough for strong long-term trend claims.

These are India-eligible remote roles, not Chennai-specific or on-site vacancies. A listing can mention multiple skills, so skill shares can sum to more than 100%.

## Files

- `job-market-dashboard.pbix` — finished two-page report, authored in Power BI Desktop.
- `job_market_dashboard_source.xlsx` — aggregate-only workbook used by the report. It contains `SkillDemand`, `RoleSkill`, and `Snapshot` tables; it contains no individual listings or job descriptions.
- `theme.json` — teal report theme.
- `export_role_skill.sql` — query used by the project pipeline to prepare role-family skill counts.

## Report pages

### Skill demand

Shows the 45-listing snapshot, top skill share, number of tracked skills, descending skill-share bars with labels, and a detail table with counts and shares. It notes the limited salary disclosure and currency caveat.

### Role comparison

Compares skill posting counts for Analytics analyst, BI analyst, and Data analyst. The families come from a basic title-keyword classification and may not perfectly represent every job.

## Opening and refreshing

Open `job-market-dashboard.pbix` in Power BI Desktop to view the embedded model and report. The report remains viewable after download. To refresh its imported data, point the Excel source to the downloaded `job_market_dashboard_source.xlsx` in this folder using **Transform data > Data source settings** if Power BI cannot find the original local path.

The workbook holds aggregate data only. Do not add raw listings or job descriptions to the public repository. Regenerate the workbook when the report data changes, then refresh and save the PBIX in Power BI Desktop.

## Limits

Salary is disclosed in only 3 of 45 listings, across different currencies. The weekly search results are a platform sample, not a census of the Indian job market. With only two snapshots, do not present the change as a long-term trend.
