from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "Online Retail.xlsx"
REPORTS = ROOT / "reports"
DB = ROOT / "retail.db"


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Expected source workbook at {SOURCE}")
    REPORTS.mkdir(exist_ok=True)
    raw = pd.read_excel(SOURCE)
    raw.columns = [c.strip().lower().replace(" ", "_") for c in raw.columns]
    raw["invoice_no"] = raw["invoiceno"].astype("string").str.strip()
    raw["invoice_date"] = pd.to_datetime(raw["invoicedate"], errors="coerce")
    raw["description"] = raw["description"].astype("string").str.strip()
    raw["country"] = raw["country"].astype("string").str.strip()
    raw["is_cancellation"] = raw["invoice_no"].str.upper().str.startswith("C", na=False).astype(int)
    raw["line_revenue"] = raw["quantity"] * raw["unitprice"]

    sales = raw.loc[
        (raw["is_cancellation"] == 0)
        & raw["invoice_date"].notna()
        & raw["quantity"].gt(0)
        & raw["unitprice"].gt(0)
    ].copy()
    sales = sales.rename(columns={"stockcode": "stock_code", "unitprice": "unit_price"})
    source_cols = ["invoice_no", "invoice_date", "stockcode", "description", "quantity",
                   "unitprice", "customerid", "country", "is_cancellation", "line_revenue"]
    sales_cols = ["invoice_no", "invoice_date", "stock_code", "description", "quantity",
                  "unit_price", "customerid", "country"]

    with sqlite3.connect(DB) as conn:
        raw[source_cols].to_sql("source_lines", conn, if_exists="replace", index=False)
        sales[sales_cols].to_sql("sales", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(invoice_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_invoice ON sales(invoice_no)")

    monthly = sales.assign(month=sales.invoice_date.dt.to_period("M").astype(str)).groupby("month", as_index=False).agg(
        revenue=("line_revenue", "sum"), invoices=("invoice_no", "nunique"))
    products = sales.groupby(["stock_code", "description"], dropna=False, as_index=False).agg(
        units_sold=("quantity", "sum"), revenue=("line_revenue", "sum"))
    products = products.sort_values("units_sold", ascending=False)
    revenue_products = products.sort_values("revenue", ascending=False)
    countries = sales.groupby("country", dropna=False, as_index=False).agg(
        revenue=("line_revenue", "sum"), invoices=("invoice_no", "nunique"))
    countries = countries.sort_values("revenue", ascending=False)
    cancellations = raw.groupby("invoice_no", dropna=False).agg(is_cancellation=("is_cancellation", "max")).reset_index()
    canceled_n = int(cancellations.is_cancellation.sum())
    invoice_n = int(cancellations.invoice_no.nunique())
    dup_rows = int(raw.duplicated().sum())
    nov = monthly.loc[monthly.month.eq("2011-11"), "revenue"]
    octv = monthly.loc[monthly.month.eq("2011-10"), "revenue"]
    nov_change = (nov.iloc[0] / octv.iloc[0] - 1) * 100 if len(nov) and len(octv) and octv.iloc[0] else float("nan")

    monthly.to_csv(REPORTS / "monthly_revenue.csv", index=False)
    products.head(20).to_csv(REPORTS / "top_products.csv", index=False)
    countries.head(20).to_csv(REPORTS / "top_countries.csv", index=False)
    plt.figure(figsize=(10, 5))
    plt.plot(monthly.month, monthly.revenue, marker="o", color="#176B87")
    plt.title("Monthly sales revenue (cancellations and invalid sale lines excluded)")
    plt.ylabel("Revenue (GBP)")
    plt.xlabel("Invoice month")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=.25)
    plt.tight_layout()
    plt.savefig(REPORTS / "monthly_revenue.png", dpi=160)
    plt.close()

    top = products.head(10).sort_values("units_sold")
    plt.figure(figsize=(9, 6))
    plt.barh(top.description.fillna("(missing description)").str.slice(0, 45), top.revenue, color="#64CCC5")
    plt.title("Top 10 products by units sold")
    plt.xlabel("Units sold")
    plt.tight_layout()
    plt.savefig(REPORTS / "top_products.png", dpi=160)
    plt.close()

    total_rev = float(sales.line_revenue.sum())
    nov_text = f"{nov.iloc[0]:,.2f} GBP" if len(nov) else "not available"
    change_text = f"{nov_change:.1f}%" if pd.notna(nov_change) else "not available"
    revenue_leader = revenue_products.iloc[0] if len(revenue_products) else None
    top_item = products.iloc[0] if len(products) else None
    non_uk = countries.loc[countries.country.ne("United Kingdom")]
    report = f"""# Findings: Online Retail\n\n## Dataset and cleaning\n\n- Source lines: **{len(raw):,}**; sale lines retained: **{len(sales):,}**.\n- Distinct invoices: **{invoice_n:,}**; cancellation invoices: **{canceled_n:,}** (**{(100*canceled_n/invoice_n if invoice_n else 0):.2f}%**).\n- Exact duplicate rows flagged for review (not automatically removed): **{dup_rows:,}**.\n- Revenue definition: quantity × unit price for non-cancellation rows with positive quantity and price, in GBP.\n- Total analyzed sales revenue: **{total_rev:,.2f} GBP**.\n\n## Findings\n\n1. **November 2011 revenue:** {nov_text}; change from October: **{change_text}**. December is partial and should not be compared as a full month.\n2. **Top item by units:** {top_item.description if top_item is not None else 'not available'} ({int(top_item.units_sold):,} units). The revenue leader is {revenue_leader.description if revenue_leader is not None else 'not available'} ({revenue_leader.revenue:,.2f} GBP), which is a postage line rather than a gift item.\n3. **Top non-UK market:** {non_uk.iloc[0].country if len(non_uk) else 'not available'} by revenue, excluding the UK.\n\n## Interpretation limits\n\nCancellation share is invoice-based, not value-based. The revenue metric excludes cancellation invoices and nonpositive quantities/prices; it is not a complete accounting net-sales measure. Missing customer IDs remain in the transaction totals. December 2011 ends on 9 December. Exact duplicate-looking rows are flagged for review but retained because repeated identical items can be legitimate purchases.\n\n## Charts\n\n![Monthly revenue](monthly_revenue.png)\n\n![Top products by units sold](top_products.png)\n"""
    (REPORTS / "findings.md").write_text(report, encoding="utf-8")
    print(f"Analyzed {len(raw):,} rows. Revenue: GBP {total_rev:,.2f}. Cancellation invoice share: {100*canceled_n/invoice_n:.2f}%.")


if __name__ == "__main__":
    main()
