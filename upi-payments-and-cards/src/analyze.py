from __future__ import annotations

from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "monthly_payments.csv"
REPORTS = ROOT / "reports"


def main():
    if not CSV.exists():
        raise SystemExit("No data found. Run python src/collect.py first.")
    REPORTS.mkdir(exist_ok=True)
    df = pd.read_csv(CSV, parse_dates=["month"]).sort_values("month").reset_index(drop=True)
    channels = ["upi", "credit_card", "debit_card"]
    for channel in channels:
        df[f"{channel}_volume_mn"] = df[f"{channel}_volume_lakh"] / 10
        df[f"{channel}_avg_ticket_rupees"] = df[f"{channel}_value_crore"] * 100 / df[f"{channel}_volume_lakh"]
        df[f"{channel}_volume_yoy_pct"] = df[f"{channel}_volume_mn"].pct_change(12) * 100
        df[f"{channel}_value_yoy_pct"] = df[f"{channel}_value_crore"].pct_change(12) * 100
    total = df[[f"{c}_volume_mn" for c in channels]].sum(axis=1)
    df["upi_share_of_three_channels_pct"] = df.upi_volume_mn / total * 100
    df["upi_value_lakh_crore"] = df.upi_value_crore / 100000
    df.to_csv(REPORTS / "monthly_channel_metrics.csv", index=False, date_format="%Y-%m-%d")

    df[["month", "upi_volume_mn", "credit_card_volume_mn", "debit_card_volume_mn", "upi_share_of_three_channels_pct"]].to_csv(REPORTS / "channel_volume.csv", index=False, date_format="%Y-%m-%d")
    df[["month", "upi_avg_ticket_rupees", "credit_card_avg_ticket_rupees", "debit_card_avg_ticket_rupees"]].to_csv(REPORTS / "average_ticket.csv", index=False, date_format="%Y-%m-%d")
    with sqlite3.connect(ROOT / "upi_payments.db") as conn:
        df.to_sql("monthly_payments", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_month ON monthly_payments(month)")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for channel, label, color in [("upi", "UPI", "#176B87"), ("credit_card", "Credit cards", "#64CCC5"), ("debit_card", "Debit cards", "#F4A261")]:
        ax.plot(df.month, df[f"{channel}_volume_mn"], label=label, color=color, linewidth=2)
    ax.set(title="Monthly transaction volume by payment channel", xlabel="Month", ylabel="Transactions (millions)")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=.25)
    fig.tight_layout()
    fig.savefig(REPORTS / "channel_volume.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for channel, label, color in [("upi", "UPI", "#176B87"), ("credit_card", "Credit cards", "#64CCC5"), ("debit_card", "Debit cards", "#F4A261")]:
        ax.plot(df.month, df[f"{channel}_avg_ticket_rupees"], label=label, color=color, linewidth=2)
    ax.set(title="Average transaction value by payment channel", xlabel="Month", ylabel="Rupees per transaction")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=.25)
    fig.tight_layout()
    fig.savefig(REPORTS / "average_ticket.png", dpi=160)
    plt.close(fig)

    first, last = df.iloc[0], df.iloc[-1]
    year_ago = df.loc[df.month.eq(last.month - pd.DateOffset(years=1))]
    yoy = year_ago.iloc[0] if len(year_ago) else None
    months = (last.month.year - first.month.year) * 12 + last.month.month - first.month.month
    upi_multiple = last.upi_volume_mn / first.upi_volume_mn if first.upi_volume_mn else float("nan")
    latest_upi_yoy = last.upi_volume_yoy_pct
    latest_credit_yoy = last.credit_card_volume_yoy_pct
    latest_debit_yoy = last.debit_card_volume_yoy_pct
    upi_avg = last.upi_avg_ticket_rupees
    first_upi_avg = first.upi_avg_ticket_rupees
    yoy_period = f"{yoy.month:%B %Y}" if yoy is not None else "not available"
    report = f"""# Findings: UPI and cards\n\n## Coverage and units\n\n- RBI DBIE monthly observations: **{len(df)}**, from **{first.month:%B %Y}** through **{last.month:%B %Y}**.\n- Reported volume is normalized from lakh transactions to millions; reported value is ₹ crore.\n- Average transaction value = value (₹ crore) × 100 / volume (lakh).\n\n## Findings\n\n1. **UPI scale:** monthly UPI volume rose from **{first.upi_volume_mn:,.1f} million** to **{last.upi_volume_mn:,.1f} million**, about **{upi_multiple:.1f}×** over {months} months. Latest year-over-year growth was **{latest_upi_yoy:.1f}%**.\n2. **Card comparison:** in {last.month:%B %Y}, credit-card transaction volume was **{last.credit_card_volume_mn:,.1f} million** and debit-card volume was **{last.debit_card_volume_mn:,.1f} million**. Their latest year-over-year changes were **{latest_credit_yoy:.1f}%** and **{latest_debit_yoy:.1f}%**, respectively.\n3. **Ticket size:** latest average UPI transaction value was **₹{upi_avg:,.0f}** versus **₹{first_upi_avg:,.0f}** in {first.month:%B %Y}. {f'Compared with {yoy_period}, UPI volume changed {last.upi_volume_yoy_pct:.1f}% and UPI value changed {last.upi_value_yoy_pct:.1f}%.' if yoy is not None else ''}\n4. **Channel mix:** UPI was **{last.upi_share_of_three_channels_pct:.1f}%** of the combined UPI, credit-card, and debit-card transaction count in the latest month. This denominator covers these three channels only.\n\n## Interpretation\n\nUPI grew rapidly while card usage remained a distinct and sizeable channel. Aggregate trends cannot show that UPI directly replaced card payments: the RBI series combine different transaction types and uses. The UPI share metric is a limited three-channel comparison, not a share of every payment in India.\n\n## Data cautions\n\nRBI notes that card statistics from November 2019 onward use more granular definitions and may not be comparable with earlier data; the analysis begins in that month. Figures are provisional. The latest RBI DBIE table observation may lag the newest NPCI UPI monthly release.\n\n## Charts\n\n![Channel volume](channel_volume.png)\n\n![Average ticket](average_ticket.png)\n"""
    (REPORTS / "findings.md").write_text(report, encoding="utf-8")
    print(f"Analyzed {len(df)} monthly records. Findings saved to {REPORTS / 'findings.md'}")


if __name__ == "__main__":
    main()
