# Project portfolio — Bharath B

[Personal portfolio](https://bharathpurvath.github.io/bharath-portfolio/) · [Project gallery](https://bharathpurvath.github.io/advanced-projects/)

This repository contains six data-analytics case studies and 20 educational software-engineering labs. Each case study documents its question, data source, method, results, and limits.

## Data analytics case studies

| Project | Published work | Data and current scope |
| --- | --- | --- |
| [Online retail sales deep dive](online-retail-sales-deep-dive/README.md) | [Findings](online-retail-sales-deep-dive/reports/findings.md) · SQL · Python analysis · charts | UCI transaction sample; source workbook and SQLite database are downloaded/generated locally, not published. |
| [WhatsApp group chat, decoded](whatsapp-group-chat-decoded/README.md) | [Synthetic demo findings](whatsapp-group-chat-decoded/reports/findings.md) · local-only parser | Public sample is entirely fictional. A real chat export and identifying outputs must stay private unless reviewed and anonymized. |
| [Chennai air quality, hour by hour](chennai-air-quality-hourly/README.md) | [Findings](chennai-air-quality-hourly/reports/findings.md) · hourly sample · charts | Open-Meteo/CAMS model estimates and gridded weather, not local station readings. Daily collection and report refresh are scheduled. |
| [UPI and cards](upi-payments-and-cards/README.md) | [Findings](upi-payments-and-cards/reports/findings.md) · RBI-derived monthly series · charts | RBI DBIE table, November 2019–July 2026 in the latest retrieved snapshot. Monthly refresh is scheduled. |
| [Zomato vs Swiggy price gap](zomato-swiggy-price-gap/README.md) | [Synthetic demo findings](zomato-swiggy-price-gap/reports/findings.md) · blank collection workbook · Python analysis | All public demo values are invented. Real findings require manual, matched observations from the user's chosen neighbourhood; the project does not scrape the apps. |
| [India data-analyst job-market capstone](india-data-analyst-job-market-capstone/README.md) | [Live dashboard](https://bharathpurvath.github.io/advanced-projects/india-data-analyst-job-market-capstone/reports/dashboard.html) · [Power BI report (.pbix)](https://bharathpurvath.github.io/advanced-projects/india-data-analyst-job-market-capstone/powerbi/job-market-dashboard.pbix) · [Two-page dashboard preview](https://bharathpurvath.github.io/advanced-projects/india-data-analyst-job-market-capstone/reports/powerbi_preview.html) · [Role-skill CSV](india-data-analyst-job-market-capstone/reports/role_skill_latest.csv) · [findings](india-data-analyst-job-market-capstone/reports/findings.md) · SQL · Python pipeline | Himalayas public API, no API key. First filtered baseline: 44 remote analyst-title listings open to applicants in India. Weekly report refresh is scheduled. |

Personal inputs are not included. The public repository contains only allowed source material, aggregate reporting, and explicitly synthetic examples. Raw UCI files, SQLite databases, raw API payloads, real WhatsApp exports, and real food-app observations stay out of Git.

### Scheduled data refreshes

GitHub Actions workflows live in the repository-root `.github/workflows/` directory:

- `chennai-air-quality.yml` collects the most recent two days daily, appends the public hourly series, and regenerates aggregate findings.
- `upi-monthly-refresh.yml` refreshes the RBI series monthly and regenerates the report.
- `job-market-weekly.yml` collects weekly, keeps the listing database as a private workflow artifact for history, and publishes aggregate outputs only.

Each workflow supports manual dispatch. Source allowances and update timing apply; scheduled jobs may start late.

## Software engineering labs

The 20 advanced labs each include an interactive browser demo in `<project>/frontend/`, a FastAPI starter in `<project>/backend/main.py`, and setup notes. They are educational prototypes using local sample data, not production services. Live payments, cloud storage, GitHub writes, and paid AI APIs are not enabled. Never place real credentials in frontend code.

Run a lab backend from its `backend` directory:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

The API docs are at `http://127.0.0.1:8000/docs` while the backend is running.
