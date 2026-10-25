# Chennai air quality, hour by hour

Explore hourly PM2.5 and rainfall around Chennai, with questions about commute-hour patterns, rain, and weekday/Sunday differences. The initial sample is a 14-day API backfill; the included GitHub Actions workflow can extend it with a daily pull after this folder is added to a GitHub repository.

## Data sources and limits

- [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) provides the PM2.5 series. It is a **modelled estimate**, not a CPCB station measurement. Chennai uses Open-Meteo's global CAMS product; the underlying source is documented at about 45 km and 3-hour resolution, even though the endpoint returns an hourly series. Use the values to explore patterns, not for health or regulatory decisions.
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) supplies hourly precipitation and temperature for the same dates. Rainfall is gridded reanalysis, not a local rain gauge.
- Coordinates requested: Chennai city centre, 13.0827° N, 80.2707° E. Each API may select a different grid cell; both returned coordinates are saved in the raw JSON and combined CSV.
- The two-week backfill is useful for a reproducible initial analysis. The Actions workflow is configured to pull recent days on a daily schedule so the time series can grow. Scheduled GitHub workflows require a GitHub repo and can run late.

## Run locally

```powershell
python -m pip install -r requirements.txt
python src/collect.py --past-days 14
python src/analyze.py
```

The collector writes a combined `data/chennai_hourly.csv` and raw API responses under `data/raw/`. The analysis writes summary tables, charts, and `reports/findings.md`.

## Method

- Commute window is defined in advance as 07:00–10:00 and 17:00–20:00 local time. Compare its median PM2.5 to other hours; this is not proof that traffic causes a difference.
- “Rain hour” means precipitation greater than zero in that hour. Compare against dry hours; this does not establish that rain caused a PM2.5 change. A lagged comparison is included as a descriptive view.
- Sunday is compared with Monday–Saturday at matching hours where the sample has coverage.
- Air-quality data may be hourly interpolations of a coarser model. State the model source, dates and grid cell in any portfolio write-up.

## GitHub Actions

In the portfolio monorepo, `.github/workflows/chennai-air-quality.yml` runs once daily, appends the latest two days to the public hourly CSV, regenerates aggregate reports, and commits only the combined CSV and report outputs. Raw API response files are not published. The workflow needs repository Actions enabled with `contents: write` (the permission is declared in the workflow).

## Attribution

Attribute Open-Meteo and the Copernicus Atmosphere Monitoring Service (CAMS) air-quality forecast data in dashboards and reports. See the Air Quality API documentation for the full CAMS attribution and source details.
