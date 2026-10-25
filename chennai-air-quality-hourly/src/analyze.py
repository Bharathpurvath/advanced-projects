from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "chennai_hourly.csv"
REPORTS = ROOT / "reports"


def main() -> None:
    if not DATA.exists():
        raise SystemExit("No data found. Run: python src/collect.py --past-days 14")
    REPORTS.mkdir(exist_ok=True)
    df = pd.read_csv(DATA, parse_dates=["time"])
    df = df.dropna(subset=["pm2_5"]).sort_values("time")
    df["hour"] = df.time.dt.hour
    df["date"] = df.time.dt.strftime("%Y-%m-%d")
    df["weekday"] = df.time.dt.day_name()
    df["is_sunday"] = df.time.dt.day_of_week.eq(6)
    df["is_commute"] = df.hour.between(7, 9) | df.hour.between(17, 19)
    df["is_rain"] = df.precipitation.fillna(0).gt(0)
    df["rain_next_hour"] = df.precipitation.shift(-1).fillna(0).gt(0)

    by_hour = df.groupby("hour", as_index=False).agg(pm2_5_mean=("pm2_5", "mean"), pm2_5_median=("pm2_5", "median"), hours=("pm2_5", "size"))
    by_day = df.groupby("date", as_index=False).agg(pm2_5_mean=("pm2_5", "mean"), rainfall_mm=("precipitation", "sum"), hours=("pm2_5", "size"))
    rain = df.groupby("is_rain", as_index=False).agg(pm2_5_mean=("pm2_5", "mean"), pm2_5_median=("pm2_5", "median"), hours=("pm2_5", "size"))
    rain["condition"] = rain.is_rain.map({True: "Rain hour", False: "Dry hour"})
    sunday = df.groupby(["hour", "is_sunday"], as_index=False).agg(pm2_5_mean=("pm2_5", "mean"), hours=("pm2_5", "size"))
    sunday["day_group"] = sunday.is_sunday.map({True: "Sunday", False: "Monday-Saturday"})
    by_hour.to_csv(REPORTS / "pm25_by_hour.csv", index=False)
    by_day.to_csv(REPORTS / "daily_pm25_and_rain.csv", index=False)
    rain.to_csv(REPORTS / "rain_vs_dry.csv", index=False)
    sunday.to_csv(REPORTS / "sunday_comparison.csv", index=False)

    commute = df.groupby("is_commute").pm2_5.agg(["mean", "median", "count"])
    rain_lag = df.groupby("rain_next_hour").pm2_5.agg(["mean", "median", "count"])
    hour_peak = by_hour.loc[by_hour.pm2_5_mean.idxmax()]
    rain_rows = rain.set_index("condition")
    sunday_rows = sunday.groupby("day_group").pm2_5_mean.mean()
    start = df.time.min().strftime("%Y-%m-%d %H:%M")
    end = df.time.max().strftime("%Y-%m-%d %H:%M")

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(by_hour.hour, by_hour.pm2_5_mean, marker="o", color="#176B87")
    ax.set(title="Modelled PM2.5 by hour of day — Chennai", xlabel="Local hour (IST)", ylabel="PM2.5 (µg/m³)", xticks=range(0, 24, 2))
    ax.grid(alpha=.25)
    fig.tight_layout()
    fig.savefig(REPORTS / "pm25_by_hour.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(pd.to_datetime(by_day.date), by_day.pm2_5_mean, marker="o", color="#176B87", label="Mean PM2.5")
    ax.set(title="Daily mean modelled PM2.5 and rainfall", xlabel="Date", ylabel="PM2.5 (µg/m³)")
    ax.tick_params(axis="x", rotation=35)
    ax2 = ax.twinx()
    ax2.bar(pd.to_datetime(by_day.date), by_day.rainfall_mm, alpha=.25, color="#64CCC5", label="Rainfall")
    ax2.set_ylabel("Rainfall (mm)")
    fig.tight_layout()
    fig.savefig(REPORTS / "pm25_rain_daily.png", dpi=160)
    plt.close(fig)

    commute_mean = commute.loc[True, "mean"] if True in commute.index else float("nan")
    noncommute_mean = commute.loc[False, "mean"] if False in commute.index else float("nan")
    commute_median = commute.loc[True, "median"] if True in commute.index else float("nan")
    dry = rain_rows.loc["Dry hour"] if "Dry hour" in rain_rows.index else None
    wet = rain_rows.loc["Rain hour"] if "Rain hour" in rain_rows.index else None
    next_rain_mean = rain_lag.loc[True, "mean"] if True in rain_lag.index else float("nan")
    no_next_rain_mean = rain_lag.loc[False, "mean"] if False in rain_lag.index else float("nan")
    report = f"""# Findings: Chennai air quality, hour by hour\n\n## Sample and provenance\n\n- Coverage: **{start}** to **{end} IST**, {len(df):,} hourly timestamps.\n- Requested coordinates: **13.0827° N, 80.2707° E**; the returned model grid coordinates are preserved in `data/chennai_hourly.csv`.\n- PM2.5 is a gridded CAMS model estimate served through Open-Meteo, not a station reading. Weather is Open-Meteo historical reanalysis.\n\n## Findings\n\n1. **Hour-of-day pattern:** highest hourly mean was at **{int(hour_peak.hour):02d}:00 IST** ({hour_peak.pm2_5_mean:.2f} µg/m³). Commute windows (07:00–09:59 and 17:00–19:59) averaged **{commute_mean:.2f} µg/m³** (median {commute_median:.2f}) versus **{noncommute_mean:.2f} µg/m³** at other hours.\n2. **Rain comparison:** rain hours averaged **{wet.pm2_5_mean:.2f} µg/m³** across {int(wet.hours):,} hours and dry hours averaged **{dry.pm2_5_mean:.2f} µg/m³** across {int(dry.hours):,} hours. Hours immediately before a rainy next hour averaged **{next_rain_mean:.2f} µg/m³** versus **{no_next_rain_mean:.2f} µg/m³** otherwise. These are descriptive associations, not evidence that rain caused a change.\n3. **Sunday:** mean of hourly PM2.5 averages was **{sunday_rows.get('Sunday', float('nan')):.2f} µg/m³** on Sundays and **{sunday_rows.get('Monday-Saturday', float('nan')):.2f} µg/m³** Monday–Saturday. Interpret cautiously with this short sample.\n\n## Caveats\n\nOpen-Meteo documents the global CAMS air-quality product at roughly 45 km and 3-hour native resolution; hourly output does not imply local sensor precision. This is not ground-truth monitoring. Weather rain is gridded reanalysis, not a gauge observation. Commute-hour comparisons do not measure traffic volume, and rain associations do not establish causality. The small date range cannot establish a seasonal pattern.\n\n## Charts\n\n![PM2.5 by hour](pm25_by_hour.png)\n\n![PM2.5 and rain by day](pm25_rain_daily.png)\n"""
    (REPORTS / "findings.md").write_text(report, encoding="utf-8")
    print(f"Analyzed {len(df):,} timestamps from {start} to {end} IST. Findings saved in {REPORTS}.")


if __name__ == "__main__":
    main()
