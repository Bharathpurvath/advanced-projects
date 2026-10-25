from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
LAT, LON = 13.0827, 80.2707
TZ = "Asia/Kolkata"


def fetch(url: str, params: dict) -> dict:
    with urlopen(f"{url}?{urlencode(params)}", timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("error"):
        raise RuntimeError(payload.get("reason", "Open-Meteo returned an error"))
    return payload


def flatten(payload: dict, wanted: list[str], source: str) -> pd.DataFrame:
    hourly = payload["hourly"]
    out = pd.DataFrame({"time": hourly["time"]})
    for column in wanted:
        out[column] = hourly.get(column)
    out["source"] = source
    out["grid_latitude"] = payload.get("latitude")
    out["grid_longitude"] = payload.get("longitude")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect hourly Chennai PM2.5 and weather from Open-Meteo.")
    parser.add_argument("--past-days", type=int, default=14, help="Days to backfill (1-14 for this project).")
    args = parser.parse_args()
    if not 1 <= args.past_days <= 14:
        raise SystemExit("--past-days must be between 1 and 14")
    DATA.mkdir(exist_ok=True)
    RAW.mkdir(exist_ok=True)
    now = datetime.now(ZoneInfo(TZ))
    end = now.date() - timedelta(days=1)
    start = end - timedelta(days=args.past_days - 1)
    stamp = now.strftime("%Y%m%dT%H%M%S%z")

    air = fetch("https://air-quality-api.open-meteo.com/v1/air-quality", {
        "latitude": LAT, "longitude": LON, "hourly": "pm2_5", "past_days": args.past_days,
        "forecast_days": 0, "timezone": TZ,
    })
    weather = fetch("https://archive-api.open-meteo.com/v1/archive", {
        "latitude": LAT, "longitude": LON, "start_date": start.isoformat(), "end_date": end.isoformat(),
        "hourly": "precipitation,temperature_2m", "timezone": TZ,
    })
    (RAW / f"air_quality_{stamp}.json").write_text(json.dumps(air, ensure_ascii=False, indent=2), encoding="utf-8")
    (RAW / f"weather_{stamp}.json").write_text(json.dumps(weather, ensure_ascii=False, indent=2), encoding="utf-8")
    aq = flatten(air, ["pm2_5"], "Open-Meteo Air Quality API / CAMS")
    wx = flatten(weather, ["precipitation", "temperature_2m"], "Open-Meteo Historical Weather API")
    merged = aq.merge(wx[["time", "precipitation", "temperature_2m", "grid_latitude", "grid_longitude"]], on="time", how="left", suffixes=("", "_weather"))
    merged = merged.rename(columns={"grid_latitude_weather": "weather_grid_latitude", "grid_longitude_weather": "weather_grid_longitude"})
    merged["collected_at"] = now.isoformat()
    merged["requested_latitude"] = LAT
    merged["requested_longitude"] = LON
    target = DATA / "chennai_hourly.csv"
    if target.exists():
        old = pd.read_csv(target)
        merged = pd.concat([old, merged], ignore_index=True)
        merged = merged.drop_duplicates("time", keep="last")
    merged.sort_values("time").to_csv(target, index=False)
    print(f"Collected {len(aq):,} PM2.5 hours for {start} through {end}; combined dataset has {len(merged):,} timestamps.")


if __name__ == "__main__":
    main()
