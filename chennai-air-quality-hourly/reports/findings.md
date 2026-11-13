# Findings: Chennai air quality, hour by hour

## Sample and provenance

- Coverage: **2026-10-11 00:00** to **2026-11-12 23:00 IST**, 792 hourly timestamps.
- Requested coordinates: **13.0827° N, 80.2707° E**; the returned model grid coordinates are preserved in `data/chennai_hourly.csv`.
- PM2.5 is a gridded CAMS model estimate served through Open-Meteo, not a station reading. Weather is Open-Meteo historical reanalysis.

## Findings

1. **Hour-of-day pattern:** highest hourly mean was at **19:00 IST** (24.43 µg/m³). Commute windows (07:00–09:59 and 17:00–19:59) averaged **22.73 µg/m³** (median 17.00) versus **21.98 µg/m³** at other hours.
2. **Rain comparison:** rain hours averaged **11.19 µg/m³** across 333 hours and dry hours averaged **30.12 µg/m³** across 459 hours. Hours immediately before a rainy next hour averaged **11.11 µg/m³** versus **30.18 µg/m³** otherwise. These are descriptive associations, not evidence that rain caused a change.
3. **Sunday:** mean of hourly PM2.5 averages was **20.43 µg/m³** on Sundays and **22.47 µg/m³** Monday–Saturday. Interpret cautiously with this short sample.

## Caveats

Open-Meteo documents the global CAMS air-quality product at roughly 45 km and 3-hour native resolution; hourly output does not imply local sensor precision. This is not ground-truth monitoring. Weather rain is gridded reanalysis, not a gauge observation. Commute-hour comparisons do not measure traffic volume, and rain associations do not establish causality. The small date range cannot establish a seasonal pattern.

## Charts

![PM2.5 by hour](pm25_by_hour.png)

![PM2.5 and rain by day](pm25_rain_daily.png)
