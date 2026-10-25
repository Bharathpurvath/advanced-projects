from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze manually collected Zomato/Swiggy price observations.")
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "observations.csv")
    args = parser.parse_args()
    if not args.input.exists():
        raise SystemExit(f"Observations not found: {args.input}\nExport the workbook Collection sheet to data/observations.csv first.")
    REPORTS.mkdir(exist_ok=True)
    df = pd.read_csv(args.input)
    synthetic_demo = (
        "data_type" in df.columns
        and not df.empty
        and df["data_type"].astype("string").str.casefold().eq("synthetic_demo").all()
    )
    normalized_headers = {str(column).strip().casefold(): column for column in df.columns}
    rename = {
        "observation date": "date", "observation time": "time", "day type": "day_type",
        "restaurant id": "restaurant_id", "restaurant name": "restaurant",
        "matched dish and portion": "dish", "menu price (₹)": "menu_price_inr",
        "delivery fee (₹)": "delivery_fee_inr", "packaging fee (₹)": "packaging_fee_inr",
        "rating shown": "rating", "distance shown (km)": "distance_km",
        "offer or context note": "offer_notes",
    }
    df = df.rename(columns={original: rename[key] for key, original in normalized_headers.items() if key in rename})
    required = {"week", "date", "restaurant", "dish", "app", "menu_price_inr", "delivery_fee_inr", "packaging_fee_inr", "rating"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit("Missing required columns: " + ", ".join(sorted(missing)))
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["app"] = df["app"].astype("string").str.strip().str.casefold()
    df = df[df.app.isin(["zomato", "swiggy"])].copy()
    numeric = ["menu_price_inr", "delivery_fee_inr", "packaging_fee_inr", "rating", "distance_km"]
    for column in numeric:
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    df["observed_total_inr"] = df[["menu_price_inr", "delivery_fee_inr", "packaging_fee_inr"]].sum(axis=1, min_count=3)
    if "restaurant_id" in df:
        df["pair_restaurant"] = df["restaurant_id"].fillna("").astype(str).str.strip()
        use_id = df.pair_restaurant.ne("")
        df.loc[use_id, "pair_restaurant"] = "id:" + df.loc[use_id, "pair_restaurant"]
        df.loc[~use_id, "pair_restaurant"] = "name:" + df.loc[~use_id, "restaurant"].astype(str).str.strip().str.casefold()
        key = ["week", "date", "pair_restaurant", "dish"]
    else:
        key = ["week", "date", "restaurant", "dish"]
    counts = df.groupby(key + ["app"]).size().unstack("app", fill_value=0).reset_index()
    for app in ("zomato", "swiggy"):
        if app not in counts:
            counts[app] = 0
    counts["pair_status"] = counts.apply(lambda r: "Paired" if r.zomato == 1 and r.swiggy == 1 else "Duplicate app row" if r.zomato > 1 or r.swiggy > 1 else "Missing app partner", axis=1)
    valid_keys = counts.loc[counts.pair_status.eq("Paired"), key]
    paired = df.merge(valid_keys, on=key, how="inner").drop_duplicates(key + ["app"])
    wide = paired.pivot(index=key, columns="app", values=["menu_price_inr", "delivery_fee_inr", "packaging_fee_inr", "observed_total_inr", "rating"])
    wide.columns = [f"{metric}_{app}" for metric, app in wide.columns]
    wide = wide.reset_index()
    if len(wide):
        for metric in ("menu_price_inr", "delivery_fee_inr", "packaging_fee_inr", "observed_total_inr", "rating"):
            a, b = f"{metric}_zomato", f"{metric}_swiggy"
            if a in wide and b in wide:
                wide[f"{metric}_gap_zomato_minus_swiggy"] = wide[a] - wide[b]
                if metric in ("menu_price_inr", "observed_total_inr"):
                    wide[f"{metric}_gap_pct_vs_swiggy"] = (wide[a] / wide[b] - 1) * 100
    wide.to_csv(REPORTS / "paired_comparisons.csv", index=False)
    counts.to_csv(REPORTS / "pairing_coverage.csv", index=False)
    by_app = df.groupby("app", as_index=False).agg(
        observations=("app", "size"),
        median_menu_price_inr=("menu_price_inr", "median"),
        median_delivery_fee_inr=("delivery_fee_inr", "median"),
        median_packaging_fee_inr=("packaging_fee_inr", "median"),
        median_rating=("rating", "median"),
    )
    by_app.to_csv(REPORTS / "summary_by_app.csv", index=False)

    if len(wide):
        menu_gap = wide.get("menu_price_inr_gap_zomato_minus_swiggy", pd.Series(dtype=float)).dropna()
        total_gap = wide.get("observed_total_inr_gap_zomato_minus_swiggy", pd.Series(dtype=float)).dropna()
        share_zomato_higher = (menu_gap.gt(0).mean() * 100) if len(menu_gap) else float("nan")
        gap_text = f"₹{menu_gap.median():,.2f}" if len(menu_gap) else "not available"
        total_text = f"₹{total_gap.median():,.2f}" if len(total_gap) else "not available"
        by_week = wide.groupby("week", as_index=False).agg(menu_gap_median_inr=("menu_price_inr_gap_zomato_minus_swiggy", "median"))
        by_week.to_csv(REPORTS / "weekly_price_gap.csv", index=False)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.axhline(0, color="#77808A", linewidth=1)
        ax.plot(by_week.week, by_week.menu_gap_median_inr, marker="o", color="#176B87", linewidth=2)
        ax.set(title="Median listed menu-price gap by collection week", xlabel="Week", ylabel="Zomato minus Swiggy (₹)")
        ax.grid(axis="y", alpha=.25)
        fig.tight_layout()
        fig.savefig(REPORTS / "weekly_price_gap.png", dpi=160)
        plt.close(fig)
    else:
        menu_gap = pd.Series(dtype=float)
        share_zomato_higher = float("nan")
        gap_text = total_text = "not available"

    date_span = "not available"
    valid_dates = df.date.dropna()
    if len(valid_dates):
        date_span = f"{min(valid_dates)} to {max(valid_dates)}"
    paired_n = len(wide)
    completed = (counts.pair_status == "Paired").sum()
    demo_note = (
        "## Demonstration data notice\n\n"
        "This report uses **synthetic demonstration values** and invented restaurant labels. No prices were observed in either app, and the figures do not support a claim about Zomato or Swiggy. Replace the demo with your own manually recorded, same-time observations before drawing conclusions.\n\n"
        if synthetic_demo else ""
    )
    report = f"""# Findings: Zomato vs Swiggy price gap\n\n{demo_note}## Sample and coverage\n\n- Observations: **{len(df):,}**; paired restaurant/dish/week/date sets: **{paired_n:,}**.\n- Coverage: **{date_span}**.\n- Complete app pairs: **{int(completed):,}**; unmatched or duplicate keys are in `pairing_coverage.csv`.\n\n## Findings\n\n1. **Listed menu price:** median paired gap (Zomato minus Swiggy) was **{gap_text}**. Zomato listed a higher price in **{share_zomato_higher:.1f}%** of pairs.\n2. **Observed pre-tax total:** median paired gap was **{total_text}**, including delivery and packaging fees where all three inputs were recorded.\n3. **App summaries:** see `summary_by_app.csv` for median observed menu prices, fees, and ratings. Rating differences should be interpreted cautiously because the apps may display ratings on different scales or populations.\n\n## Method limits\n\nOnly same-date, same-week, same-restaurant, same-standardized-dish observations with one row per app are paired. Missing delivery/packaging fees are not imputed as zero. The sample is manually collected and may be affected by timing, delivery location, app promotions, and account status. This is not a causal test or a population-wide comparison.\n\n## Chart\n\n![Weekly paired menu price gap](weekly_price_gap.png)\n"""
    (REPORTS / "findings.md").write_text(report, encoding="utf-8")
    print(f"Analyzed {len(df):,} observations with {paired_n:,} matched pairs. Findings saved to {REPORTS}.")


if __name__ == "__main__":
    main()
